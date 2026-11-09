import logging, os, json
from concurrent.futures import ThreadPoolExecutor, wait
import config, filters, notifier, emailer, cvgen, referral, tracker, reporter
from models import Job
from sources import linkedin, remoteok, wwr, remotive

log = logging.getLogger("jobalert")

def get_sources():
    s = []
    if getattr(config, "ENABLE_FREEHIRE", True):
        from sources import freehire
        s.append(("freehire", freehire.fetch))
    if getattr(config, "ENABLE_JOBICY", True):
        from sources import jobicy
        s.append(("jobicy", jobicy.fetch))
    if getattr(config, "ENABLE_INDEED", False):
        from sources import indeed
        s.append(("indeed", indeed.fetch))
    if getattr(config, "ENABLE_BAYT", True):
        from sources import bayt
        s.append(("bayt", bayt.fetch))
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

def _export_to_dashboard(jobs):
    dash_pub = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dashboard", "public")
    if not os.path.exists(dash_pub):
        return
    dash_json_path = os.path.join(dash_pub, "jobs.json")
    existing = []
    if os.path.exists(dash_json_path):
        try:
            with open(dash_json_path, "r", encoding="utf-8") as f:
                existing = json.load(f)
        except Exception:
            existing = []

    seen_ids = {j.get("id") for j in existing if isinstance(j, dict)}
    for j in jobs:
        if j.id in seen_ids:
            continue
        existing.append({
            "id": j.id,
            "source": j.source,
            "title": j.title,
            "company": j.company,
            "location": j.location,
            "posted_at": j.posted_at or "Recent",
            "url": j.url,
            "description": j.description or "",
            "remote": getattr(j, "remote_search", False),
            "work_type": getattr(j, "work_type", "On-site"),
            "country": getattr(j, "country", ""),
            "salary": getattr(j, "salary", ""),
            "recruiter": getattr(j, "recruiter", ""),
            "career_level": getattr(j, "career_level", ""),
            "match_score": getattr(j, "score", 0),
            "verdict": getattr(j, "verdict", ""),
            "matched_keywords": getattr(j, "strengths", []),
            "missing_keywords": getattr(j, "gaps", []),
            "cv_suggestions": getattr(j, "cv_suggestions", []),
            "cv_generated": bool(getattr(j, "cv_suggestions", []))
        })
    existing.sort(key=lambda x: x.get("match_score", 0), reverse=True)
    with open(dash_json_path, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2, ensure_ascii=False)


def run_round(store, dry=False, pool=None, wait_timeout=None):
    """جولة واحدة. الحجز (claim) ذرّي في Redis قبل التنبيه لمنع أي تكرار."""
    stats = {"candidates": 0, "fresh": 0, "matched": [], "skipped": 0, "errors": {}}
    matched_job_objects = []
    own = pool is None
    pool = pool or ThreadPoolExecutor(max_workers=3)
    futs = []

    sources = get_sources()
    source_results = []
    with ThreadPoolExecutor(max_workers=len(sources) or 1) as src_exec:
        fut_map = {src_exec.submit(fn): name for name, fn in sources}
        done, not_done = wait(fut_map.keys(), timeout=25)
        for fut in done:
            name = fut_map[fut]
            try:
                jobs = fut.result()
                source_results.append((name, jobs))
            except Exception as e:
                stats["errors"][name] = str(e)[:200]
                log.warning("%s failed: %s", name, e)
        for fut in not_done:
            name = fut_map[fut]
            stats["errors"][name] = "timeout (>25s)"
            log.warning("%s timed out (>25s)", name)

    batch_seen = set()
    for name, jobs in source_results:
        stats["candidates"] += len(jobs)
        for job in jobs:
            if job.key in batch_seen:
                continue
            batch_seen.add(job.key)

            # 1) فحص الحداثة فوراً: الوظيفة القديمة تستبعد بدون استهلاك Redis أو جلب التفاصيل
            fresh, why_stale = filters.is_fresh(job)
            if not fresh:
                continue
            stats["fresh"] += 1

            if store.has(job.key):
                continue

            job.work_type = filters.work_type(job)
            job.country = filters.extract_country(job)
            job.salary = getattr(job, "salary", "") or filters.extract_salary(job)
            job.career_level = getattr(job, "career_level", "") or filters.extract_career_level(job)

            ok, why = filters.title_ok(job)
            if ok and not filters.egypt_or_remote(job):
                ok, why = False, "location (not Egypt and not 100% remote)"
            if ok and job.source == "linkedin":
                try: linkedin.fetch_description(job)
                except Exception: pass
            if ok: ok, why = filters.full_ok(job)
            if ok:
                score, verdict, strengths, gaps, cv_suggs = filters.calculate_fit(job)
                job.score, job.verdict, job.strengths, job.gaps, job.cv_suggestions = score, verdict, strengths, gaps, cv_suggs
                if score < getattr(config, "MIN_FIT_SCORE", 35):
                    ok, why = False, f"low fit score ({score}%)"
            if not ok:
                if not dry:
                    store.add(job.key)
                stats["skipped"] += 1; log.info("skip %s | %s (%s)", job.title, job.company, why); continue

            label = f"{job.title} | {job.company} | {filters.age_label(job)}"
            if dry:
                stats["matched"].append(label)
                continue

            # 2) حجز ذرّي (Atomic claim) في Redis قبل التنبيه
            if not store.claim(job.key):
                continue

            if notifier.enabled():
                try:
                    notifier.send_job(job)
                except Exception as e:
                    log.error("telegram send failed: %s", e)
                    stats["errors"]["telegram"] = str(e)[:200]
                    store.remove(job.key)          # الوحيد المسموح له بإلغاء الحجز: فشل الإرسال
                    continue

            stats["matched"].append(label)
            matched_job_objects.append(job)

            # 3) التسجيل بالداشبورد والتتبع
            try: store.record(job)
            except Exception: pass
            try: tracker.track_job(job.key, job.title, job.company, job.url, status="identified", fit_score=job.score)
            except Exception as e: log.warning("tracker failed: %s", e)
            futs.append(pool.submit(enrich, job, dry))

    if matched_job_objects:
        try:
            rep_res = reporter.generate_reports(matched_job_objects, stats)
            stats["reports"] = rep_res
        except Exception as e:
            log.warning("Report generation failed: %s", e)
        try:
            _export_to_dashboard(matched_job_objects)
        except Exception as e:
            log.warning("Dashboard export failed: %s", e)

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
    job.work_type = filters.work_type(job)
    job.country = filters.extract_country(job)
    job.score, job.verdict, job.strengths, job.gaps, job.cv_suggestions = filters.calculate_fit(job)
    if notifier.enabled(): notifier.send_job(job)
    enrich(job)
    return {"test": "sent", "telegram": notifier.enabled(), "email": emailer.enabled(), "cv_ai": cvgen.enabled()}
