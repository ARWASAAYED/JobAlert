from urllib.parse import quote

NETWORK = "&network=%5B%22F%22%2C%22S%22%5D"   # اتصالات درجة 1 و 2 بس

def _link(company, role):
    return ("https://www.linkedin.com/search/results/people/?keywords="
            + quote(f"{company} {role}") + NETWORK + "&origin=GLOBAL_SEARCH_HEADER")

def build(job, tailored=None):
    company = job.company or ""
    links = {
        "Frontend / Software Engineers": _link(company, "frontend engineer"),
        "Engineering Managers": _link(company, "engineering manager"),
        "Recruiters / Talent": _link(company, "recruiter OR talent acquisition"),
    }
    title = job.title[:60]
    note = (f"Hi! I'm Arwa, a React/Next.js frontend developer. I saw the {title} opening at "
            f"{company} and would love to connect and learn more about the team.")[:200]
    msg = (f"Hi [Name],\n\nI'm Arwa, a frontend developer (React, Next.js, TypeScript). I noticed {company} "
           f"is hiring for {job.title}, and it matches my background closely. I've built several production-style "
           f"React/Next.js apps and completed internships in full-stack/React development.\n\n"
           f"Would you be open to referring me, or pointing me to the right person? I'd be happy to send my CV "
           f"and any details you need. Thank you for your time!\n\nArwa Ahmed\nlinkedin.com/in/arwa-ahmed-659b952a6")
    if tailored:
        note = (tailored.get("connection_note") or note)[:200]
        msg = tailored.get("referral_message") or msg
    return {"links": links, "note": note, "message": msg}
