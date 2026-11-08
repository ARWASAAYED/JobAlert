"""Indeed job board scraper (Remote & Regional).
يدعم الترتيب حسب التاريخ (?sort=date) للحصول على أحدث الوظائف فور نشرها، واستخدام الكوكيز/الحسابات عند توفرها.
"""
import logging, re
from bs4 import BeautifulSoup
import config, filters
from models import Job

log = logging.getLogger("jobalert.indeed")

SEARCH_TARGETS = [
    {"url": "https://eg.indeed.com/jobs", "params": {"q": "react frontend", "sort": "date"}, "country": "Egypt"},
    {"url": "https://www.indeed.com/jobs", "params": {"q": "react developer", "l": "remote", "sort": "date"}, "country": "Worldwide"},
]

def _parse_card(card, default_country="Egypt"):
    try:
        # استخراج معرف الوظيفة
        jk = card.get("data-jk")
        t_tag = card.select_one("h2.jobTitle a, a[data-jk], h2 a")
        if not t_tag:
            return None

        if not jk:
            jk = t_tag.get("data-jk") or card.get("data-mobtk")
        
        href = t_tag.get("href", "")
        if href.startswith("/"):
            href = "https://www.indeed.com" + href
        elif not href and jk:
            href = f"https://www.indeed.com/viewjob?jk={jk}"

        if not jk:
            m = re.search(r"jk=([a-zA-Z0-9]+)", href)
            jk = m.group(1) if m else href

        title = t_tag.get_text(" ", strip=True)
        # إزالة بادئة New لو وجدت
        title = re.sub(r"^new\s+", "", title, flags=re.I).strip()

        comp_tag = card.select_one("[data-testid='company-name'], .companyName, .company")
        company = comp_tag.get_text(" ", strip=True) if comp_tag else "Company"

        loc_tag = card.select_one("[data-testid='text-location'], .companyLocation, .location")
        location = loc_tag.get_text(" ", strip=True) if loc_tag else default_country

        # استخراج تاريخ ووقت النشر
        date_tag = card.select_one("[data-testid='myJobsStateDate'], .date, .underShelfFooter .date")
        posted_text = date_tag.get_text(" ", strip=True) if date_tag else "Recently"
        posted_text = re.sub(r"^(posted|employer|active)\s+", "", posted_text, flags=re.I).strip()

        age = filters.age_minutes(posted_text)
        if age is not None and age > config.MAX_AGE_MINUTES:
            return None

        # استخراج الراتب من كارت إنديد إن وجد
        salary_tag = card.select_one("[data-testid='attribute_snippet_testid'], .salary-snippet-container")
        salary = salary_tag.get_text(" ", strip=True) if salary_tag else ""
        if not salary:
            salary = filters.extract_salary(type("Dummy", (), {"title": title, "location": location, "description": ""})())

        # مقتطف الوصف
        snippet_tag = card.select_one(".job-snippet, .underShelfFooter")
        desc = snippet_tag.get_text(" ", strip=True) if snippet_tag else f"{title} at {company}"

        return Job(
            source="indeed",
            id=str(jk),
            title=title,
            company=company,
            location=location,
            url=href,
            posted_text=posted_text,
            description=desc,
            salary=salary,
            country=default_country
        )
    except Exception as e:
        log.debug("Indeed card parse error: %s", e)
        return None

def fetch():
    try:
        from curl_cffi import requests as cr
    except ImportError:
        import requests as cr

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    }

    # إضافة كوكيز حساب Indeed إن توفرت
    indeed_cookie = getattr(config, "INDEED_COOKIE", "")
    if indeed_cookie:
        headers["Cookie"] = indeed_cookie

    out = []
    seen = set()

    for target in SEARCH_TARGETS:
        try:
            kwargs = {"headers": headers, "params": target["params"], "timeout": 12}
            if hasattr(cr, "Session"):
                r = cr.get(target["url"], impersonate="chrome124", **kwargs)
            else:
                r = cr.get(target["url"], **kwargs)

            if r.status_code != 200:
                log.info("Indeed '%s' status %s", target["url"], r.status_code)
                continue

            soup = BeautifulSoup(r.text, "html.parser")
            cards = soup.select(".job_seen_beacon, .result, [data-jk]")
            for c in cards:
                job = _parse_card(c, default_country=target["country"])
                if job and job.id not in seen:
                    seen.add(job.id)
                    out.append(job)
        except Exception as e:
            log.warning("Indeed fetch error for %s: %s", target["url"], e)

    return out
