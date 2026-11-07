import re, time, requests
from bs4 import BeautifulSoup
import config
from models import Job

def fetch():
    r = requests.get("https://remoteok.com/api", headers={"User-Agent": "jobalert-personal/1.0"}, timeout=20)
    r.raise_for_status()
    out, now = [], time.time()
    for j in r.json():
        if not isinstance(j, dict) or "position" not in j:
            continue
        age = (now - int(j.get("epoch", 0))) / 60
        if age > config.MAX_AGE_MINUTES:
            continue
        desc = BeautifulSoup(j.get("description", ""), "html.parser").get_text("\n", strip=True)
        raw_url = j.get("url") or j.get("apply_url", "")
        url = raw_url if raw_url.startswith("http") else f"https://remoteok.com{raw_url}"
        epoch = int(j.get("epoch", 0))
        import datetime as _dt
        posted_at = _dt.datetime.fromtimestamp(epoch, _dt.timezone.utc).strftime("%Y-%m-%d %H:%M") if epoch else ""
        out.append(Job(source="remoteok", id=str(j["id"]), title=j["position"], company=j.get("company", ""),
                       location=j.get("location", "") or "Worldwide", url=url,
                       posted_text=f"{int(age)} minutes ago", posted_at=posted_at, description=desc, remote_search=True))
    return out
