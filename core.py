import logging
from concurrent.futures import ThreadPoolExecutor, wait
import config, filters, notifier, emailer, cvgen, referral
from models import Job
from sources import linkedin, remoteok, wwr, remotive

log = logging.getLogger("jobalert")

def get_sources():
    s = []
    if config.ENABLE_LINKEDIN: s.append(("linkedin", linkedin.fetch))
    if config.ENABLE_WUZZUF:
        from sources import wuzzuf
        s.append(("wuzzuf", wuzzuf.fetch))
    if config.ENABLE_REMOTEOK: s.append(("remoteok", remoteok.fetch))
    if config.ENABLE_WWR:      s.append(("wwr", wwr.fetch))
    s.append(("remotive", remotive.fetch))
    return s

def enrich(job, dry=False):
    """CV مخصص + ريفرال + إيميل (بعد التنبيه الفوري)."""
    extras = {"docx": None, "tailored": None}
    if cvgen.enabled():
        try:
            extras["tailored"] = cvgen.tailor(job)
            extras["docx"] = cvgen.render_docx(extras["tailored"], job)
        except Exception as e:
            log.warning("CV tailoring failed for %s: %s", job.title, e)
    extras["ref"] = referral.build(job, extras["tailored"])
    if dry:
        return extras
    if notifier.enabled():
        try: notifier.send_followup(job, extras)
        except Exception as e: log.error("telegram followup failed: %s", e)
    if emailer.enabled():
        try: emailer.send_job(job, extras)
        except Exception as e: log.error("email failed: %s", e)
    return extras

def run_round(store, dry=False, pool=None, wait_timeout=None):
    stats = {"candidates": 0, "matched": [], "skipped": 0, "errors": {}}
    own = pool is None
    pool = pool or ThreadPoolExecutor(max_workers=3)
    futs = []
    for name, fn in get_sources():
        try:
            jobs = fn()
        except Exception as e:
            stats["errors"][name] = str(e)[:200]; log.warning("%s failed: %s", name, e); continue
        stats["candidates"] += len(jobs)
        for job in jobs:
            if store.has(job.key):
                continue
            ok, why = filters.title_ok(job)
            if ok and not filters.egypt_or_remote(job):
                ok, why = False, "location"
            if ok and job.source == "linkedin":
                try: linkedin.fetch_description(job)
                except Exception: pass
            if ok: ok, why = filters.full_ok(job)
            store.add(job.key)
            if not ok:
                stats["skipped"] += 1; log.info("skip %s | %s (%s)", job.title, job.company, why); continue
            try:
                if not dry and notifier.enabled():
                    notifier.send_job(job)                 # التنبيه الفوري
                stats["matched"].append(f"{job.title} | {job.company}")
                futs.append(pool.submit(enrich, job, dry))
            except Exception as e:
                log.error("alert failed: %s", e); store.remove(job.key)
    if wait_timeout is not None and futs:
        wait(futs, timeout=wait_timeout)
    if own:
        pool.shutdown(wait=False)
    return stats

def test_alert():
    import datetime as _dt
    now_str = _dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    job = Job(source="linkedin", id="4485506218", title="Shopify developer (TEST)", company="Republic- Job Company", location="Cairo, Egypt",
              url="https://www.linkedin.com/jobs/view/4485506218/", posted_text="Just now", posted_at=now_str,
              description="Shopify, Liquid, React, JavaScript, CSS. 0-2 years of experience. Cairo, Egypt.")
    if notifier.enabled(): notifier.send_job(job)
    enrich(job)
    return {"test": "sent", "telegram": notifier.enabled(), "email": emailer.enabled(), "cv_ai": cvgen.enabled()}
