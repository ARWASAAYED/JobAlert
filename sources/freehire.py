import logging
import requests
from bs4 import BeautifulSoup
import config
from models import Job

log = logging.getLogger("jobalert.freehire")

UA = "ai-job-search-dev/ai-job-search/1.0 (freehire-search)"

def fetch():
    queries = getattr(config, "FREEHIRE_QUERIES", ["React", "Frontend", "Full Stack", "Next.js"])
    out = []
    seen_ids = set()

    for q in queries:
        try:
            r = requests.get(
                "https://freehire.me/api/v1/jobs/search",
                params={"q": q, "limit": 20, "posted_within_days": 7},
                headers={"User-Agent": UA},
                timeout=15,
            )
            if not r.ok:
                log.warning("Freehire query '%s' returned %s", q, r.status_code)
                continue

            data = r.json()
            for item in data.get("data", []):
                jid = str(item.get("id"))
                if not jid or jid in seen_ids:
                    continue
                seen_ids.add(jid)

                title = item.get("title", "").strip()
                company = item.get("company") or item.get("company_slug") or "Company"
                url = item.get("url") or ""
                location = item.get("location") or "Worldwide"
                posted_at = item.get("date") or ""

                desc_raw = item.get("description") or ""
                if desc_raw:
                    desc = BeautifulSoup(desc_raw, "html.parser").get_text("\n", strip=True)
                else:
                    desc = ""

                work_mode = item.get("work_mode")
                is_remote = work_mode == "remote" or "remote" in location.lower()

                out.append(
                    Job(
                        source="freehire",
                        id=jid,
                        title=title,
                        company=company,
                        location=location,
                        url=url,
                        posted_text="Recent",
                        posted_at=posted_at,
                        description=desc,
                        remote_search=is_remote,
                    )
                )
        except Exception as e:
            log.warning("Freehire query '%s' failed: %s", q, e)

    return out

