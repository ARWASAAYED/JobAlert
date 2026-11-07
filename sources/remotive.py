import datetime as dt
import requests
from bs4 import BeautifulSoup
import config
from models import Job

SEARCH_URLS = [
    "https://remotive.com/api/remote-jobs?category=software-dev&search=frontend",
    "https://remotive.com/api/remote-jobs?category=software-dev&search=react",
]

def fetch():
    out = []
    seen_ids = set()
    now = dt.datetime.now(dt.timezone.utc)
    
    for url in SEARCH_URLS:
        try:
            r = requests.get(url, headers={"User-Agent": "jobalert-personal/1.0"}, timeout=20)
            if r.status_code != 200:
                continue
            jobs = r.json().get("jobs", [])
            for j in jobs:
                jid = str(j.get("id"))
                if jid in seen_ids:
                    continue
                pub_date_str = j.get("publication_date", "")
                if not pub_date_str:
                    continue
                pub_dt = dt.datetime.fromisoformat(pub_date_str)
                if not pub_dt.tzinfo:
                    pub_dt = pub_dt.replace(tzinfo=dt.timezone.utc)
                age_hours = (now - pub_dt).total_seconds() / 3600
                if age_hours > 72:  # 3 days window
                    continue
                seen_ids.add(jid)
                desc = BeautifulSoup(j.get("description", ""), "html.parser").get_text("\n", strip=True)
                out.append(Job(
                    source="remotive",
                    id=jid,
                    title=j.get("title", ""),
                    company=j.get("company_name", ""),
                    location=j.get("candidate_required_location") or "Worldwide",
                    url=j.get("url", ""),
                    posted_text=f"{int(age_hours)} hours ago",
                    posted_at=pub_dt.strftime("%Y-%m-%d %H:%M"),
                    description=desc,
                    remote_search=True
                ))
        except Exception:
            pass
            
    return out
