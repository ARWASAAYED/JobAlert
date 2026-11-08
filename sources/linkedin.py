import re, requests, datetime as dt
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
import config
from models import Job

SEARCH = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
DETAIL = "https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{}"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}
# لو كوكي الجلسة li_at متوفر، نضيفه فوراً للهيدر
if getattr(config, "LINKEDIN_LI_AT", None):
    HEADERS["Cookie"] = f"li_at={config.LINKEDIN_LI_AT};"

class RateLimited(Exception): pass

def parse_cards(html_text, remote_search=False, now=None):
    import filters
    now = now or dt.datetime.now(dt.timezone.utc)
    soup = BeautifulSoup(html_text, "html.parser")
    jobs = []
    for card in soup.select("div.base-card, li div.job-search-card"):
        urn = card.get("data-entity-urn", "")
        m = re.search(r"(\d+)$", urn)
        a = card.select_one("a.base-card__full-link, a[href*='/jobs/view/']")
        title = card.select_one(".base-search-card__title")
        href = a["href"] if a else ""
        job_id = m.group(1) if m else card.get("data-job-id")
        if not job_id and href:
            mh = re.search(r"/jobs/view/(?:[^/]+-)?(\d+)", href) or re.search(r"(\d{8,})", href)
            job_id = mh.group(1) if mh else None
        if not (job_id and title):
            continue
        comp = card.select_one(".base-search-card__subtitle")
        loc = card.select_one(".job-search-card__location")
        t = card.select_one("time")
        posted_text = t.get_text(" ", strip=True) if t else ""
        job = Job(
            source="linkedin", id=job_id,
            title=title.get_text(" ", strip=True),
            company=comp.get_text(" ", strip=True) if comp else "",
            location=loc.get_text(" ", strip=True) if loc else "",
            url=f"https://www.linkedin.com/jobs/view/{job_id}/",
            posted_text=posted_text, remote_search=remote_search,
        )
        # استخراج الوقت الحقيقي من النص ("5 minutes ago")
        age = filters.age_minutes(job, now)
        if age is not None:
            job.posted_at = (now - dt.timedelta(minutes=age)).strftime("%Y-%m-%d %H:%M")
        jobs.append(job)
    return jobs

def _search(args):
    kw, loc, wt = args
    max_seconds = max(1800, config.MAX_AGE_MINUTES * 60)
    params = {
        "keywords": kw, "location": loc, "sortBy": "DD", "start": 0,
        "f_TPR": f"r{max_seconds}"
    }
    if wt:
        params["f_WT"] = wt
    try:
        r = requests.get(SEARCH, params=params, headers=HEADERS, timeout=15)
        if r.status_code != 200:
            return []
        return parse_cards(r.text, remote_search=(wt == "2"))
    except Exception:
        return []

def fetch():
    combos = [(kw, loc, wt) for kw in config.LINKEDIN_KEYWORDS for loc, wt in config.LINKEDIN_SEARCHES]
    out, seen = [], set()
    with ThreadPoolExecutor(max_workers=4) as ex:
        for cards in ex.map(_search, combos):
            for job in cards:
                if job.id not in seen:
                    seen.add(job.id); out.append(job)
    return out

def fetch_description(job):
    try:
        r = requests.get(DETAIL.format(job.id), headers=HEADERS, timeout=15)
        if r.status_code != 200:
            return
        soup = BeautifulSoup(r.text, "html.parser")
        d = soup.select_one(".show-more-less-html__markup, .description__text")
        job.description = d.get_text("\n", strip=True) if d else ""
        ap = soup.select_one(".num-applicants__caption, .num-applicants__figure")
        if ap:
            job.applicants = ap.get_text(" ", strip=True)
    except Exception:
        pass
