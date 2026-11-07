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
    for card in soup.select("div.base-card, li div.job-search-card"):
        urn = card.get("data-entity-urn", "")
        m = re.search(r"(\d+)$", urn)
        a = card.select_one("a.base-card__full-link, a[href*='/jobs/view/']")
        title = card.select_one(".base-search-card__title")
        if not (m and a and title):
            continue
        comp = card.select_one(".base-search-card__subtitle")
        loc = card.select_one(".job-search-card__location")
        t = card.select_one("time")
        jobs.append(Job(
            source="linkedin", id=m.group(1),
            title=title.get_text(" ", strip=True),
            company=comp.get_text(" ", strip=True) if comp else "",
            location=loc.get_text(" ", strip=True) if loc else "",
            url=a["href"].split("?")[0],
            posted_text=t.get_text(" ", strip=True) if t else "",
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
