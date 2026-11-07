"""تخصيص الـ CV لإعلان معين. القاعدة: كل الحقائق (شركات، تواريخ، أرقام، مهارات) من master_cv.json بس."""
import json, re, os, requests
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
import config

SYSTEM = """You tailor a junior frontend developer's CV to ONE specific job ad.
HARD RULES:
- Use ONLY facts that exist in MASTER_CV. NEVER invent or alter employers, dates, titles, metrics, tools, skills or years of experience. Keep every number exactly as in MASTER_CV.
- You may select, reorder and reword bullets, and mirror the ad's terminology ONLY when MASTER_CV genuinely supports it (e.g. ad says "ReactJS", CV has React.js).
- Skills: use only items that exist in MASTER_CV.skills (exact text), reorder so the ad's keywords come first.
- Requirements in the ad that MASTER_CV does not support go in missing_keywords. NEVER add them to the CV.
- Plain, ATS-friendly English. No fluff, no first-person pronouns in bullets.
Return ONLY valid JSON, no markdown fences."""

SCHEMA = """{
 "headline": "e.g. Frontend Developer (React / Next.js)",
 "summary": "2-3 sentences aligned to the ad, truthful",
 "skills": [{"category": "string", "items": ["exact items from MASTER_CV.skills"]}],
 "experience": [{"id": "exp_* id from MASTER_CV", "bullets": ["3-5 reworded bullets"]}],
 "projects": [{"id": "proj_* id", "bullets": ["1-3 bullets"]}],
 "match_score": 0,
 "matched_keywords": ["..."],
 "missing_keywords": ["..."],
 "connection_note": "<=200 chars LinkedIn connection note mentioning the role and company",
 "referral_message": "short (80-120 words) referral request with placeholder [Name]"
}
projects: pick the 3-4 most relevant ids. experience: include all ids, most relevant bullets first."""

def enabled():
    return bool(config.ANTHROPIC_API_KEY)

def load_master():
    with open(config.MASTER_CV_PATH, encoding="utf-8") as f:
        return json.load(f)

def _ensure_description(job):
    if job.source == "wuzzuf" and len(job.description or "") < 500:
        try:
            from curl_cffi import requests as cr
            from bs4 import BeautifulSoup
            r = cr.get(job.url, impersonate="chrome", timeout=30)
            if r.status_code == 200:
                job.description = BeautifulSoup(r.text, "html.parser").get_text("\n", strip=True)[:8000]
        except Exception:
            pass
    return job.description or ""

def call_claude(system, user):
    r = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={"x-api-key": config.ANTHROPIC_API_KEY, "anthropic-version": "2023-06-01",
                 "content-type": "application/json"},
        json={"model": config.CLAUDE_MODEL, "max_tokens": 3500, "system": system,
              "messages": [{"role": "user", "content": user}]},
        timeout=120)
    r.raise_for_status()
    return "".join(b.get("text", "") for b in r.json()["content"] if b.get("type") == "text")

def _parse_json(text):
    s, e = text.find("{"), text.rfind("}")
    return json.loads(text[s:e + 1])

def tailor(job, master=None):
    master = master or load_master()
    desc = _ensure_description(job)[:7000]
    user = (f"MASTER_CV:\n{json.dumps(master, ensure_ascii=False)}\n\n"
            f"JOB:\nTitle: {job.title}\nCompany: {job.company}\nLocation: {job.location}\n"
            f"Description:\n{desc}\n\nOutput JSON schema:\n{SCHEMA}")
    last = None
    for _ in range(2):
        try:
            return _sanitize(_parse_json(call_claude(SYSTEM, user)), master)
        except Exception as e:
            last = e
    raise RuntimeError(f"tailoring failed: {last}")

def _sanitize(t, master):
    """حماية: نشيل أي مهارة مش في الـ master وأي بوليت فيه رقم مش موجود في الـ CV الأصلي."""
    allowed_nums = set(re.findall(r"\d+", json.dumps(master)))
    allowed_skills = {i.lower(): i for items in master["skills"].values() for i in items}
    skills = []
    for cat in t.get("skills", []):
        items = [allowed_skills[i.lower()] for i in cat.get("items", []) if i.lower() in allowed_skills]
        if items:
            skills.append({"category": cat.get("category", ""), "items": items})
    t["skills"] = skills or [{"category": k, "items": v} for k, v in master["skills"].items()]

    def clean(blist, fallback):
        out = [b for b in (blist or []) if isinstance(b, str)
               and set(re.findall(r"\d+", b)) <= allowed_nums]
        return out[:5] or fallback
    exp_master = {e["id"]: e for e in master["experience"]}
    proj_master = {p["id"]: p for p in master["projects"]}
    t["experience"] = [{"id": e["id"], "bullets": clean(e.get("bullets"), exp_master[e["id"]]["bullets"])}
                       for e in t.get("experience", []) if e.get("id") in exp_master]
    seen = {e["id"] for e in t["experience"]}
    for eid, e in exp_master.items():
        if eid not in seen:
            t["experience"].append({"id": eid, "bullets": e["bullets"]})
    t["projects"] = [{"id": p["id"], "bullets": clean(p.get("bullets"), proj_master[p["id"]]["bullets"])}
                     for p in t.get("projects", []) if p.get("id") in proj_master][:4]
    if not t["projects"]:
        t["projects"] = [{"id": p["id"], "bullets": p["bullets"]} for p in master["projects"][:4]]
    t["summary"] = t.get("summary") or master["base_summary"]
    t["headline"] = t.get("headline") or "Frontend Developer"
    return t

def render_docx(t, job, master=None):
    m = master or load_master()
    c = m["contact"]
    d = Document()
    for s in d.sections:
        s.left_margin = s.right_margin = Inches(0.7)
        s.top_margin = s.bottom_margin = Inches(0.6)
    st = d.styles["Normal"]; st.font.name = "Calibri"; st.font.size = Pt(10)

    def para(text="", bold=False, size=None, center=False, italic=False, after=2):
        p = d.add_paragraph(); r = p.add_run(text); r.bold = bold; r.italic = italic
        if size: r.font.size = Pt(size)
        if center: p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(after); p.paragraph_format.space_before = Pt(0)
        return p
    def heading(text):
        p = para(text.upper(), bold=True, size=11, after=3); p.paragraph_format.space_before = Pt(8)
    def bullet(text):
        p = d.add_paragraph(text, style="List Bullet")
        p.paragraph_format.space_after = Pt(1); p.paragraph_format.space_before = Pt(0)
    def line(left, right):
        p = para(); r = p.add_run(left); r.bold = True
        p.add_run("  |  " + right) if right else None

    para(c["name"], bold=True, size=18, center=True, after=0)
    para(t["headline"], size=12, center=True, after=1)
    para(" | ".join([c["email"], c["phone"], c["location"]] + list(c["links"].values())), size=9, center=True, after=4)
    heading("Profile"); para(t["summary"])
    heading("Skills")
    for cat in t["skills"]:
        p = para(); r = p.add_run(cat["category"] + ": "); r.bold = True; p.add_run(", ".join(cat["items"]))
    heading("Experience")
    em = {e["id"]: e for e in m["experience"]}
    for e in t["experience"]:
        x = em[e["id"]]; line(f'{x["title"]} - {x["org"]}', x["dates"])
        for b in e["bullets"]: bullet(b)
    heading("Projects")
    pm = {p["id"]: p for p in m["projects"]}
    for p in t["projects"]:
        x = pm[p["id"]]; line(x["name"], f'{x["dates"]}  |  {x["links"]}')
        for b in p["bullets"]: bullet(b)
        para("Technologies: " + x["tech"], italic=True, size=9)
    heading("Education")
    ed = m["education"]; line(ed["degree"] + " - " + ed["school"], ed["dates"]); para(ed["details"])
    if m.get("certificates"):
        heading("Certificates"); para(" | ".join(m["certificates"]))
    os.makedirs(config.OUT_DIR, exist_ok=True)
    slug = re.sub(r"[^A-Za-z0-9]+", "_", f"{job.company}_{job.title}")[:60].strip("_") or "job"
    path = os.path.join(config.OUT_DIR, f"Arwa_Ahmed_CV_{slug}.docx")
    d.save(path)
    return path
