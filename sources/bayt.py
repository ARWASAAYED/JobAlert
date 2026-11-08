"""Bayt job board scraper (Egypt, Saudi Arabia, UAE, International).
يدعم الترتيب حسب التاريخ (?sort=d) للوصول للوظائف فور نشرها، واستخدام الكوكيز/الحسابات عند توفرها.
"""
import logging, re, time
from bs4 import BeautifulSoup
import config, filters
from models import Job

log = logging.getLogger("jobalert.bayt")

SEARCH_TARGETS = [
    {"url": "https://www.bayt.com/en/egypt/jobs/frontend-jobs/", "country": "Egypt"},
    {"url": "https://www.bayt.com/en/egypt/jobs/react-jobs/", "country": "Egypt"},
    {"url": "https://www.bayt.com/en/saudi-arabia/jobs/frontend-jobs/", "country": "Saudi Arabia"},
    {"url": "https://www.bayt.com/en/international/jobs/react-jobs/", "country": "Worldwide"},
]

def _parse_card(card, default_country="Egypt"):
    try:
        jid = card.get("data-job-id")
        t_tag = card.select_one("h2 a")
        if not t_tag:
            return None
        title = t_tag.get_text(" ", strip=True)
        href = t_tag.get("href", "")
        if href.startswith("/"):
            href = "https://www.bayt.com" + href

        if not jid:
            m = re.search(r"-(\d+)/?$", href)
            jid = m.group(1) if m else href

        comp_tag = card.select_one(".job-company-location-wrapper a, .t-nowrap")
        company = comp_tag.get_text(" ", strip=True) if comp_tag else "Confidential Company"

        loc_tag = card.select_one(".jb-label-location, .job-company-location-wrapper")
        location = loc_tag.get_text(" ", strip=True) if loc_tag else default_country

        desc_tag = card.select_one(".jb-descr")
        desc = desc_tag.get_text(" ", strip=True) if desc_tag else ""

        # استخراج وقت النشر بدقة بالدقائق
        date_span = card.select_one("[data-automation-id='job-active-date']")
        posted_text = date_span.get_text(" ", strip=True) if date_span else ""
        
        # لو متوفر unix timestamp
        unix_ts = date_span.get("data-automation-jobactivedate") if date_span else None
        age = None
        if unix_ts and unix_ts.isdigit():
            age = max(0, int((time.time() - int(unix_ts)) / 60))
            posted_text = f"{age} min ago" if age < 60 else f"{age//60} h ago"
        elif posted_text:
            age = filters.age_minutes(posted_text)

        # استبعاد الوظائف القديمة فوراً
        if age is not None and age > config.MAX_AGE_MINUTES:
            return None

        # استخراج الراتب إن وجد
        salary = filters.extract_salary(type("Dummy", (), {"title": title, "location": location, "description": desc})())

        return Job(
            source="bayt",
            id=str(jid),
            title=title,
            company=company,
            location=location,
            url=href,
            posted_text=posted_text or "Recently",
            description=desc,
            salary=salary,
            country=default_country
        )
    except Exception as e:
        log.debug("Error parsing Bayt card: %s", e)
        return None

def fetch():
    try:
        from curl_cffi import requests as cr
    except ImportError:
        import requests as cr

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
        "Referer": "https://www.bayt.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    }

    # إضافة كوكيز الجلسة إن توفرت من الحساب
    bayt_cookie = getattr(config, "BAYT_COOKIE", "")
    if bayt_cookie:
        headers["Cookie"] = bayt_cookie

    out = []
    seen = set()

    for target in SEARCH_TARGETS:
        try:
            params = {"sort": "d"}  # دائمًا مرتب بالأحدث أولاً (Date Descending)
            kwargs = {"headers": headers, "timeout": 12, "params": params}
            if hasattr(cr, "Session"):
                # استخدام محاكاة متصفح Chrome لتخطي Cloudflare
                r = cr.get(target["url"], impersonate="chrome124", **kwargs)
            else:
                r = cr.get(target["url"], **kwargs)

            if r.status_code != 200:
                log.info("Bayt '%s' status %s", target["url"], r.status_code)
                continue

            soup = BeautifulSoup(r.text, "html.parser")
            cards = soup.select("li[data-js-job]")
            for c in cards:
                job = _parse_card(c, default_country=target["country"])
                if job and job.id not in seen:
                    seen.add(job.id)
                    out.append(job)
        except Exception as e:
            log.warning("Bayt fetch error for %s: %s", target["url"], e)

    return out

