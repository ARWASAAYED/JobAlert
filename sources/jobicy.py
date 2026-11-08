import logging
import requests
from bs4 import BeautifulSoup
import config
from models import Job

log = logging.getLogger("jobalert.jobicy")

UA = "jobalert-personal/1.0"

def fetch():
    tags = getattr(config, "JOBICY_TAGS", ["react", "frontend"])
    out = []
    seen_ids = set()

    for tag in tags:
        try:
            r = requests.get(
                "https://jobicy.com/api/v2/remote-jobs",
                params={"count": 15, "tag": tag},
                headers={"User-Agent": UA},
                timeout=6,
            )
            if not r.ok:
                log.warning("Jobicy tag '%s' returned %s", tag, r.status_code)
                continue

            data = r.json()
            for item in data.get("jobs", []):
                jid = str(item.get("id"))
                if not jid or jid in seen_ids:
                    continue
                seen_ids.add(jid)

                title = item.get("jobTitle", "").strip()
                company = item.get("companyName") or "Company"
                url = item.get("url") or ""
                location = item.get("jobGeo") or "Worldwide"
                posted_at = item.get("pubDate") or ""

                desc_raw = item.get("jobDescription") or ""
                if desc_raw:
                    desc = BeautifulSoup(desc_raw, "html.parser").get_text("\n", strip=True)
                else:
                    desc = ""

                out.append(
                    Job(
                        source="jobicy",
                        id=jid,
                        title=title,
                        company=company,
                        location=location,
                        url=url,
                        posted_text="Recent",
                        posted_at=posted_at,
                        description=desc,
                        remote_search=True,
                    )
                )
        except Exception as e:
            log.warning("Jobicy tag '%s' failed: %s", tag, e)

    return out

