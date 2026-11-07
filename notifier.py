import html, requests
import config
from filters import work_type

API = "https://api.telegram.org/bot{}/{}"

def enabled():
    return bool(config.TELEGRAM_TOKEN and config.TELEGRAM_CHAT_ID)


def _post(method, **payload):
    r = requests.post(API.format(config.TELEGRAM_TOKEN, method), json=payload, timeout=20)
    if r.status_code == 429:
        import time; time.sleep(r.json().get("parameters", {}).get("retry_after", 5))
        r = requests.post(API.format(config.TELEGRAM_TOKEN, method), json=payload, timeout=20)
    r.raise_for_status()
    return r.json()

def send_text(text):
    _post("sendMessage", chat_id=config.TELEGRAM_CHAT_ID, text=text, parse_mode="HTML",
          disable_web_page_preview=True)

def send_job(job):
    e = html.escape
    
    # Select appropriate flag
    loc_lower = (job.location or "").lower()
    if any(k in loc_lower for k in ["egypt", "cairo", "giza", "alexandria", "مصر", "القاهرة"]) or job.source == "wuzzuf":
        flag = "🇪🇬"
    elif job.remote_search or any(k in loc_lower for k in ["remote", "worldwide", "anywhere", "global"]):
        flag = "🌐"
    else:
        flag = "🌍"

    title = e(job.title)
    comp = e(job.company or "Company")
    loc = e(job.location or "Egypt")
    posted = e(job.posted_at or job.posted_text or "Just now")
    url = job.url

    # Direct links in message body
    if job.source == "linkedin":
        li_url = f"https://linkedin.com/jobs/view/{job.id}"
        links_block = f'<a href="{e(url)}">View</a>\n<a href="{e(li_url)}">Linkedin</a>'
    else:
        links_block = f'<a href="{e(url)}">View</a>\n<a href="{e(url)}">{e(job.source.capitalize())}</a>'

    # Build the exact message format requested
    lines = [
        f"{flag} 🆕 {title}",
        f"🏢 {comp}",
        f"🕐 Posted {posted}",
        links_block,
        f"{title} at {comp} — {loc} |",
    ]

    # Clean inline buttons that always go directly to the job
    keyboard = [[{"text": "⚡ View Job", "url": url}]]
    if job.source == "linkedin":
        keyboard[0].append({"text": "🔗 LinkedIn", "url": f"https://linkedin.com/jobs/view/{job.id}"})

    _post("sendMessage", chat_id=config.TELEGRAM_CHAT_ID, text="\n".join(lines), parse_mode="HTML",
          disable_web_page_preview=True,
          reply_markup={"inline_keyboard": keyboard})

def get_chat_id():
    data = requests.get(API.format(config.TELEGRAM_TOKEN, "getUpdates"), timeout=20).json()
    for upd in reversed(data.get("result", [])):
        msg = upd.get("message") or upd.get("channel_post")
        if msg:
            return msg["chat"]["id"]
    return None

def send_document(path, caption=""):
    with open(path, "rb") as f:
        r = requests.post(API.format(config.TELEGRAM_TOKEN, "sendDocument"),
                          data={"chat_id": config.TELEGRAM_CHAT_ID, "caption": caption[:1000]},
                          files={"document": f}, timeout=60)
    r.raise_for_status()

def send_followup(job, extras):
    e = html.escape
    t, ref = extras.get("tailored"), extras["ref"]
    if extras.get("docx"):
        cap = f"📄 CV مخصص لـ {job.title}"
        if t:
            cap += f"\n🎯 Match: {int(t.get('match_score', 0))}%"
            if t.get("missing_keywords"):
                cap += "\n⚠️ مش عندك: " + ", ".join(t["missing_keywords"][:6])
        send_document(extras["docx"], cap)
    links = "\n".join(f'• <a href="{e(u)}">{e(n)}</a>' for n, u in ref["links"].items())
    text = (f"🤝 <b>ريفرال — {e(job.company or '')}</b>\n{links}\n\n"
            f"<b>Connection note</b> (اضغطي للنسخ):\n<code>{e(ref['note'])}</code>\n\n"
            f"<b>رسالة الريفرال</b>:\n<code>{e(ref['message'])}</code>")
    send_text(text[:4000])
