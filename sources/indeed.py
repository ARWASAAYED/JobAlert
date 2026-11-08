import logging
from models import Job
import config

log = logging.getLogger("jobalert.indeed")

def fetch():
    """
    Fetches fresh junior/frontend job postings from Indeed using JobSpy.
    Resilient fallback: returns [] if dependencies or network fail.
    """
    try:
        from jobspy import scrape_jobs
    except ImportError:
        log.warning("JobSpy not installed; skipping Indeed scraper.")
        return []

    searches = getattr(config, "INDEED_SEARCHES", [
        {"term": "react developer", "location": "Cairo", "country": "egypt", "remote": False},
        {"term": "frontend developer", "location": "Cairo", "country": "egypt", "remote": False},
        {"term": "react developer", "location": "", "country": "usa", "remote": True},
    ])

    out = []
    seen_ids = set()

    for s in searches:
        try:
            params = {
                "site_name": ["indeed"],
                "search_term": s["term"],
                "results_wanted": 10,
                "country_indeed": s.get("country", "egypt"),
            }
            if s.get("location"):
                params["location"] = s["location"]
            if s.get("remote"):
                params["is_remote"] = True

            df = scrape_jobs(**params)
            if df is None or len(df) == 0:
                continue

            for _, row in df.iterrows():
                jid = str(row.get("id") or "").replace("in-", "").strip()
                if not jid or jid in seen_ids:
                    continue
                seen_ids.add(jid)

                title = str(row.get("title") or "").strip()
                company = str(row.get("company") or "Company").strip()
                loc = str(row.get("location") or "Cairo, Egypt").strip()
                url = str(row.get("job_url_direct") or row.get("job_url") or "").strip()
                posted_at = str(row.get("date_posted") or "").strip()
                desc = str(row.get("description") or "").strip()
                is_remote = bool(row.get("is_remote")) or s.get("remote", False)

                out.append(
                    Job(
                        source="indeed",
                        id=jid,
                        title=title,
                        company=company,
                        location=loc,
                        url=url,
                        posted_text="Recent",
                        posted_at=posted_at,
                        description=desc,
                        remote_search=is_remote,
                    )
                )
        except Exception as e:
            log.warning("Indeed search '%s' (%s) failed: %s", s.get("term"), s.get("country"), e)

    return out
