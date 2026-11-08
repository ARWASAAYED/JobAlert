"""Wuzzuf scraper مع استخراج بيانات SSR State الغنية (مستوحى من RTJobs)."""
import re, json, logging
from bs4 import BeautifulSoup
import config
from models import Job

log = logging.getLogger("jobalert.wuzzuf")

URL = "https://wuzzuf.net/search/jobs/"
_STATE_MARKER = re.compile(r'"job"\s*:\s*\{\s*"collection"\s*:')

def _extract_state(html: str) -> dict:
    """استخراج كائن البيانات المضمن مباشرة من سكريبت Wuzzuf SSR."""
    m = _STATE_MARKER.search(html or "")
    if not m:
        return {}
    start = html.find("{", m.start())
    try:
        obj, _ = json.JSONDecoder().raw_decode(html, start)
        return obj.get("collection") or {}
    except Exception:
        return {}

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
    entities = _extract_state(html_text)
    
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
        jid_match = re.search(r"/jobs/p/([^-/]+)", href)
        jid = jid_match.group(1) if jid_match else href
        
        import datetime as _dt
        posted_at = (_dt.datetime.now() - _dt.timedelta(minutes=age)).strftime("%Y-%m-%d %H:%M") if age is not None else ""
        
        salary_str = ""
        career_level_str = ""
        
        # دمج البيانات الغنية لو وجدت في SSR State
        if jid in entities:
            attrs = (entities[jid] or {}).get("attributes") or {}
            sal = attrs.get("salary") or {}
            if sal.get("min") or sal.get("max"):
                salary_str = f"{sal.get('min', '')} - {sal.get('max', '')} {sal.get('currency', 'EGP')}".strip()
            career = attrs.get("careerLevel") or {}
            if career.get("name"):
                career_level_str = career["name"]
        
        jobs.append(Job(
            source="wuzzuf", id=jid, title=a.get_text(" ", strip=True),
            company=(comp.get_text(" ", strip=True).rstrip(" -") if comp else ""),
            location="Egypt", url=href, posted_text=f"{age} minutes ago", posted_at=posted_at,
            description=text, salary=salary_str, career_level=career_level_str
        ))
    return jobs

def fetch():
    try:
        from curl_cffi import requests as cr
    except ImportError:
        return []
        
    out = []
    for q in ("react", "frontend"):
        try:
            r = cr.get(URL, params={"q": q, "a": "hpb", "filters[post_date][0]": "within_24_hours"},
                       impersonate="chrome", timeout=15)
            if r.status_code == 200:
                out += parse(r.text)
            else:
                log.info("wuzzuf query '%s' status %s", q, r.status_code)
        except Exception as e:
            log.info("wuzzuf search '%s' failed: %s", q, e)
    return out
