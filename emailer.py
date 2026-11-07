import html, smtplib, ssl, os
from email.message import EmailMessage
import config
from filters import work_type

def enabled():
    return bool(config.SMTP_USER and config.SMTP_APP_PASSWORD and config.EMAIL_TO)

def build(job, extras):
    e = html.escape
    t, ref = extras.get("tailored"), extras["ref"]
    rows = [f"<h2>{e(job.title)}</h2>", f"<p><b>{e(job.company or '-')}</b> — {e(job.location or '-')} — {e(work_type(job))}<br>"
            f"{e(job.posted_text)} {e(job.applicants)} ({e(job.source)})</p>",
            f'<p><a href="{e(job.url)}" style="background:#0a66c2;color:#fff;padding:10px 18px;border-radius:6px;'
            f'text-decoration:none">⚡ قدّمي دلوقتي</a></p>']
    if t:
        rows.append(f"<p>Match: <b>{int(t.get('match_score', 0))}%</b><br>"
                    f"Matched: {e(', '.join(t.get('matched_keywords', [])))}<br>"
                    f"Missing (مش في الـ CV، متضيفيهاش إلا لو عندك فعلاً): {e(', '.join(t.get('missing_keywords', [])) or '-')}</p>")
    rows.append("<h3>Referral</h3><ul>" + "".join(f'<li><a href="{e(u)}">{e(n)}</a></li>' for n, u in ref["links"].items()) + "</ul>")
    rows.append(f"<p><b>Connection note:</b><br><i>{e(ref['note'])}</i></p>")
    rows.append(f"<p><b>Referral message:</b></p><pre style='white-space:pre-wrap;font-family:inherit'>{e(ref['message'])}</pre>")
    return "\n".join(rows)

def send_job(job, extras):
    msg = EmailMessage()
    msg["Subject"] = f"🚨 {job.title} @ {job.company or job.source}"
    msg["From"], msg["To"] = config.SMTP_USER, config.EMAIL_TO
    msg.set_content(f"{job.title} @ {job.company}\n{job.location}\nApply: {job.url}")
    msg.add_alternative(build(job, extras), subtype="html")
    p = extras.get("docx")
    if p and os.path.exists(p):
        with open(p, "rb") as f:
            msg.add_attachment(f.read(), maintype="application",
                               subtype="vnd.openxmlformats-officedocument.wordprocessingml.document",
                               filename=os.path.basename(p))
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ssl.create_default_context(), timeout=30) as s:
        s.login(config.SMTP_USER, config.SMTP_APP_PASSWORD)
        s.send_message(msg)
