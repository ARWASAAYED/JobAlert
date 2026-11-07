import re, requests
from bs4 import BeautifulSoup
import config
from models import Job

SEARCH = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
DETAIL = "https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{}"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

class RateLimited(Exception): pass

def parse_cards(html_text, remote_search=False):
    soup = BeautifulSoup(html_text, "html.parser")
    jobs = []
    import datetime as _dt
    now = _dt.datetime.now()

    for card in soup.select("div.base-card, li div.job-search-card"):
        urn = card.get("data-entity-urn", "")
        m = re.search(r"(\d+)$", urn)
        a = card.select_one("a.base-card__full-link, a[href*='/jobs/view/']")
        title = card.select_one(".base-search-card__title")
        
        href = a["href"] if a else ""
        job_id = None
        if m:
            job_id = m.group(1)
        elif card.get("data-job-id"):
            job_id = card.get("data-job-id")
        elif href:
            m_href = re.search(r"/jobs/view/(?:[^/]+-)?(\d+)", href) or re.search(r"(\d{8,})", href)
            if m_href:
                job_id = m_href.group(1)

        if not (job_id and title):
            continue

        comp = card.select_one(".base-search-card__subtitle")
        loc = card.select_one(".job-search-card__location")
        t = card.select_one("time")

        # Parse posted timestamp
        posted_text = t.get_text(" ", strip=True) if t else ""
        posted_at = ""
        dt_val = t.get("datetime") if t else ""
        if dt_val:
            if "T" in dt_val:
                posted_at = dt_val.replace("T", " ").split(".")[0][:16]
            else:
                posted_at = f"{dt_val} {now.strftime('%H:%M')}"
        else:
            posted_at = now.strftime("%Y-%m-%d %H:%M")

        # Guaranteed canonical direct view URL (no tracking redirects)
        clean_url = f"https://www.linkedin.com/jobs/view/{job_id}/"

        jobs.append(Job(
            source="linkedin",
            id=job_id,
            title=title.get_text(" ", strip=True),
            company=comp.get_text(" ", strip=True) if comp else "",
            location=loc.get_text(" ", strip=True) if loc else "",
            url=clean_url,
            posted_text=posted_text,
            posted_at=posted_at,
            remote_search=remote_search,
        ))
    return jobs

def fetch():
    out = []
    secs = config.MAX_AGE_MINUTES * 60
    for kw in config.LINKEDIN_KEYWORDS:
        for loc, wt in config.LINKEDIN_SEARCHES:
            params = {"keywords": kw, "location": loc, "f_TPR": f"r{secs}", "sortBy": "DD", "start": 0}
            if wt:
                params["f_WT"] = wt
            r = requests.get(SEARCH, params=params, headers=HEADERS, timeout=20)
            if r.status_code == 429:
                raise RateLimited("LinkedIn 429")
            if r.status_code != 200:
                continue
            out += parse_cards(r.text, remote_search=(wt == "2"))
    return out

def fetch_description(job):
    r = requests.get(DETAIL.format(job.id), headers=HEADERS, timeout=20)
    if r.status_code == 429:
        raise RateLimited("LinkedIn 429")
    if r.status_code != 200:
        return
    soup = BeautifulSoup(r.text, "html.parser")
    d = soup.select_one(".show-more-less-html__markup, .description__text")
    job.description = d.get_text("\n", strip=True) if d else ""
    ap = soup.select_one(".num-applicants__caption, .num-applicants__figure")
    if ap:
        job.applicants = ap.get_text(" ", strip=True)
