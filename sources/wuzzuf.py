"""Wuzzuf محمي بـ Cloudflare. ده best-effort: لو الـ selectors اتغيرت عدّليها هنا."""
import re
from bs4 import BeautifulSoup
import config
from models import Job

URL = "https://wuzzuf.net/search/jobs/"

def _age_minutes(text):
    t = text.lower()
    if "just now" in t or "a few seconds" in t: return 0
    m = re.search(r"(\d+)\s*(minute|hour|day|week|month)", t)
    if not m: return None
    n, unit = int(m.group(1)), m.group(2)
    return n * {"minute": 1, "hour": 60, "day": 1440, "week": 10080, "month": 43200}[unit]

def parse(html_text):
    soup = BeautifulSoup(html_text, "html.parser")
    jobs = []
    for a in soup.select("h2 a[href*='/jobs/p/']"):
        card = a
        for _ in range(4):
            card = card.parent
            if card is None: break
        if card is None: continue
        text = card.get_text(" ", strip=True)
        age = None
        for el in card.find_all(["div", "span"]):
            age = _age_minutes(el.get_text(" ", strip=True)) if len(el.get_text(strip=True)) < 40 else None
            if age is not None: break
        if age is None or age > config.MAX_AGE_MINUTES:
            continue
        comp = card.select_one("a[href*='/jobs/careers/']")
        href = a["href"].split("?")[0]
        if href.startswith("/"): href = "https://wuzzuf.net" + href
        jid = re.search(r"/jobs/p/([^-/]+)", href)
        jobs.append(Job(source="wuzzuf", id=jid.group(1) if jid else href, title=a.get_text(" ", strip=True),
                        company=(comp.get_text(" ", strip=True).rstrip(" -") if comp else ""),
                        location="Egypt", url=href, posted_text=f"{age} minutes ago",
                        description=text))  # نص الكارت (فيه Remote/Hybrid/Experience أحياناً)
    return jobs

def fetch():
    from curl_cffi import requests as cr
    out = []
    for q in ("react", "frontend"):
        r = cr.get(URL, params={"q": q, "a": "hpb", "filters[post_date][0]": "within_24_hours"},
                   impersonate="chrome", timeout=30)
        if r.status_code != 200:
            raise RuntimeError(f"wuzzuf status {r.status_code}")
        out += parse(r.text)
    return out
