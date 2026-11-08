"""Indeed job board scraper (Remote & Regional).
يستخدم طريقة RTJobs لاستخراج كائن JSON المضمن (window.mosaic.providerData["mosaic-provider-jobcards"])
مع توقيت دقيق بالمللي ثانية، والترتيب بالأحدث (?sort=date)، مع دعم كوكيز الحسابات.
"""
import logging, re, json, time
from bs4 import BeautifulSoup
import config, filters
from models import Job

log = logging.getLogger("jobalert.indeed")

SEARCH_TARGETS = [
    {"url": "https://eg.indeed.com/jobs", "params": {"q": "react frontend fullstack", "sort": "date"}, "country": "Egypt"},
    {"url": "https://www.indeed.com/jobs", "params": {"q": "react developer", "l": "remote", "sort": "date"}, "country": "Worldwide"},
]

# محدد موقع كائن بيانات إنديد (مقتبس من RTJobs)
_CARDS_MARKER = re.compile(
    r'window\.mosaic\.providerData\[\'?"?mosaic-provider-jobcards\'?"?\]\s*=\s*'
)

def _extract_mosaic_jobs(html: str, default_country="Egypt") -> list:
    """استخراج الوظائف مباشرة من كائن JSON المضمن بدلاً من محددات CSS الهشة."""
    m = _CARDS_MARKER.search(html or "")
    if not m:
        return []
    start = html.find("{", m.end())
    if start == -1:
        return []

    try:
        data, _ = json.JSONDecoder().raw_decode(html, start)
    except Exception:
        return []

    results = (
        data.get("metaData", {})
        .get("mosaicProviderJobCardsModel", {})
        .get("results", [])
    )
    if not isinstance(results, list):
        return []

    jobs = []
    now_sec = time.time()

    for r in results:
        try:
            jk = r.get("jobkey")
            if not jk:
                continue

            title = r.get("displayTitle") or r.get("title") or ""
            company = r.get("company") or "Company"
            location = r.get("formattedLocation") or default_country
            href = f"https://www.indeed.com/viewjob?jk={jk}"

            # توقيت النشر الدقيق بالمللي ثانية
            pub_ms = r.get("pubDate")
            age = None
            posted_text = "Recently"
            if pub_ms and isinstance(pub_ms, (int, float)):
                age = max(0, int((now_sec - (pub_ms / 1000.0)) / 60))
                posted_text = f"{age} min ago" if age < 60 else f"{age // 60} h ago"

            # استبعاد الوظائف التي تجاوزت الحد المسموح به
            if age is not None and age > config.MAX_AGE_MINUTES:
                continue

            # استخراج الراتب من حقول إنديد الأصلية
            salary = ""
            sal_obj = r.get("extractedSalary") or r.get("salarySnippet") or {}
            if isinstance(sal_obj, dict):
                salary = sal_obj.get("formattedSalary") or sal_obj.get("text") or ""
            if not salary:
                salary = filters.extract_salary(type("Dummy", (), {"title": title, "location": location, "description": ""})())

            # استخراج ملخص الوصف
            snippet_html = r.get("snippet") or ""
            snippet = BeautifulSoup(snippet_html, "html.parser").get_text(" ", strip=True) if snippet_html else f"{title} at {company}"

            jobs.append(
                Job(
                    source="indeed",
                    id=str(jk),
                    title=title,
                    company=company,
                    location=location,
                    url=href,
                    posted_text=posted_text,
                    description=snippet,
                    salary=salary,
                    country=default_country,
                )
            )
        except Exception as e:
            log.debug("Error parsing mosaic job card: %s", e)

    return jobs

def _parse_html_fallback(html_text: str, default_country="Egypt") -> list:
    """طريقة احتياطية بالـ BeautifulSoup إذا لم يتوفر كائن mosaic."""
    soup = BeautifulSoup(html_text, "html.parser")
    cards = soup.select(".job_seen_beacon, .result, [data-jk]")
    out = []
    for card in cards:
        try:
            jk = card.get("data-jk")
            t_tag = card.select_one("h2.jobTitle a, a[data-jk], h2 a")
            if not t_tag:
                continue
            if not jk:
                jk = t_tag.get("data-jk")

            href = t_tag.get("href", "")
            if href.startswith("/"):
                href = "https://www.indeed.com" + href
            elif not href and jk:
                href = f"https://www.indeed.com/viewjob?jk={jk}"

            title = re.sub(r"^new\s+", "", t_tag.get_text(" ", strip=True), flags=re.I).strip()
            comp_tag = card.select_one("[data-testid='company-name'], .companyName, .company")
            company = comp_tag.get_text(" ", strip=True) if comp_tag else "Company"

            loc_tag = card.select_one("[data-testid='text-location'], .companyLocation, .location")
            location = loc_tag.get_text(" ", strip=True) if loc_tag else default_country

            date_tag = card.select_one("[data-testid='myJobsStateDate'], .date")
            posted_text = date_tag.get_text(" ", strip=True) if date_tag else "Recently"
            age = filters.age_minutes(posted_text)
            if age is not None and age > config.MAX_AGE_MINUTES:
                continue

            salary_tag = card.select_one("[data-testid='attribute_snippet_testid'], .salary-snippet-container")
            salary = salary_tag.get_text(" ", strip=True) if salary_tag else ""
            snippet_tag = card.select_one(".job-snippet")
            desc = snippet_tag.get_text(" ", strip=True) if snippet_tag else f"{title} at {company}"

            out.append(
                Job(
                    source="indeed",
                    id=str(jk or href),
                    title=title,
                    company=company,
                    location=location,
                    url=href,
                    posted_text=posted_text,
                    description=desc,
                    salary=salary,
                    country=default_country,
                )
            )
        except Exception:
            pass
    return out

def fetch():
    try:
        from curl_cffi import requests as cr
    except ImportError:
        import requests as cr

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.indeed.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    }

    # دعم كوكيز جلسة الحساب
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

            # 1. أولاً تجربة طريقة RTJobs لاستخراج كائن JSON (الأسرع والأدق)
            jobs = _extract_mosaic_jobs(r.text, default_country=target["country"])
            
            # 2. لو لم تتوفر، الرجوع للمحلل الاحتياطي
            if not jobs:
                jobs = _parse_html_fallback(r.text, default_country=target["country"])

            for job in jobs:
                if job.id not in seen:
                    seen.add(job.id)
                    out.append(job)
        except Exception as e:
            log.warning("Indeed fetch error for %s: %s", target["url"], e)

    return out
