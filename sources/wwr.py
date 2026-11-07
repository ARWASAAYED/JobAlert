import email.utils, datetime as dt, requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import config
from models import Job

FEEDS = ["https://weworkremotely.com/categories/remote-front-end-programming-jobs.rss",
         "https://weworkremotely.com/categories/remote-programming-jobs.rss"]

def fetch():
    out, now = [], dt.datetime.now(dt.timezone.utc)
    for url in FEEDS:
        r = requests.get(url, headers={"User-Agent": "jobalert-personal/1.0"}, timeout=20)
        if r.status_code != 200:
            continue
        for item in ET.fromstring(r.content).iter("item"):
            g = lambda n: (item.findtext(n) or "").strip()
            pub = email.utils.parsedate_to_datetime(g("pubDate"))
            age = (now - pub).total_seconds() / 60
            if age > config.MAX_AGE_MINUTES:
                continue
            title = g("title")
            company, _, t = title.partition(":")
            desc = BeautifulSoup(g("description"), "html.parser").get_text("\n", strip=True)
            posted_at = pub.strftime("%Y-%m-%d %H:%M")
            out.append(Job(source="weworkremotely", id=g("guid") or g("link"), title=(t or title).strip(),
                           company=company.strip() if t else "", location=g("region") or "Worldwide",
                           url=g("link"), posted_text=f"{int(age)} minutes ago", posted_at=posted_at,
                           description=desc, remote_search=True))
    return out
