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
    lines = [f"🚨 <b>{e(job.title)}</b>",
             f"🏢 {e(job.company or '-')}",
             f"📍 {e(job.location or '-')}  ·  💼 {e(work_type(job))}"]
    if job.posted_text: lines.append(f"⏱ {e(job.posted_text)}")
    if job.applicants:  lines.append(f"👥 {e(job.applicants)}")
    lines.append(f"🌐 {e(job.source)}")
    _post("sendMessage", chat_id=config.TELEGRAM_CHAT_ID, text="\n".join(lines), parse_mode="HTML",
          disable_web_page_preview=True,
          reply_markup={"inline_keyboard": [[{"text": "⚡ قدّمي دلوقتي", "url": job.url}]]})

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
