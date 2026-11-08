"""
Report Generator for JobAlert.
Generates self-contained HTML and Markdown reports identical to the Job Hunter format.
"""

import os
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import List, Dict, Any

CAIRO = timezone(timedelta(hours=2))

def get_cairo_time():
    now = datetime.now(CAIRO)
    date_dir = now.strftime("%Y-%m-%d")
    ts = now.strftime("%Y-%m-%d-%H-%M")
    return now, date_dir, ts

def generate_reports(jobs: List[Any], stats: Dict[str, Any], out_dir: str = None) -> Dict[str, str]:
    """
    Generates both Markdown and HTML reports in a date-named directory.
    Returns dict with paths: {'md': path, 'html': path}
    """
    if out_dir is None:
        out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")

    now, date_dir, ts = get_cairo_time()
    target_dir = os.path.join(out_dir, date_dir)
    os.makedirs(target_dir, exist_ok=True)

    md_path = os.path.join(target_dir, f"jobs-{ts}.md")
    html_path = os.path.join(target_dir, f"jobs-{ts}.html")

    # Sort jobs by score descending
    sorted_jobs = sorted(jobs, key=lambda j: getattr(j, "score", 0), reverse=True)

    # 1. Write Markdown
    md_content = _build_markdown(sorted_jobs, stats, now.strftime("%Y-%m-%d %H:%M"))
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    # 2. Write HTML
    html_content = _build_html(sorted_jobs, stats, now.strftime("%Y-%m-%d %H:%M"))
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    return {"md": md_path, "html": html_path}

def _build_markdown(jobs: List[Any], stats: Dict[str, Any], date_str: str) -> str:
    lines = [
        "# Job Hunter Report — Full Stack Developer",
        "",
        "**Persona:** `full-stack` (Full Stack Developer)  ",
        "**Candidate:** Arwa Ahmed — Cairo, Egypt  ",
        f"**Run date:** {date_str} (Cairo, GMT+2)  ",
        "",
        "## Run Summary",
        "",
        "| Metric | Value |",
        "|---|---|",
        f"| Total candidates fetched | {stats.get('candidates', len(jobs))} |",
        f"| Matches identified | {len(jobs)} |",
        f"| Skipped / Out of Market | {stats.get('skipped', 0)} |",
        "",
        "---",
        "",
        "## Top Matches",
        "",
    ]

    for idx, j in enumerate(jobs[:10], 1):
        score = getattr(j, "score", 0)
        verdict = getattr(j, "verdict", "Good Fit")
        title = j.title
        comp = j.company
        loc = j.location
        url = j.url
        source = j.source

        lines.extend([
            f"### {idx}. {title} — {comp}",
            "",
            "| Field | Value |",
            "|---|---|",
            f"| **Fit Score** | **{score} — {verdict}** |",
            f"| **Company** | {comp} |",
            f"| **Location** | {loc} |",
            f"| **Source** | {source} |",
            f"| **Work Mode** | {'Remote' if getattr(j, 'remote_search', False) else 'Onsite / Hybrid'} |",
            f"| **Direct Link** | [Apply Here]({url}) |",
            "",
            "**Key Matches**",
        ])
        for s in getattr(j, "strengths", []):
            lines.append(f"- {s}")
        if not getattr(j, "strengths", []):
            lines.append("- Strong fundamental overlap with required frontend/backend skills.")

        lines.extend(["", "**Gaps**"])
        for g in getattr(j, "gaps", []):
            lines.append(f"- {g}")
        if not getattr(j, "gaps", []):
            lines.append("- Standard competitive applicant pool.")

        lines.extend(["", "**Tailored CV Suggestions**"])
        for cv in getattr(j, "cv_suggestions", []):
            lines.append(f"- {cv}")
        if not getattr(j, "cv_suggestions", []):
            lines.append("- Highlight your core full-stack project architecture and RESTful API experience.")

        lines.extend(["", "---", ""])

    return "\n".join(lines)

def _build_html(jobs: List[Any], stats: Dict[str, Any], date_str: str) -> str:
    cards_html = []
    for idx, j in enumerate(jobs[:10], 1):
        score = getattr(j, "score", 0)
        verdict = getattr(j, "verdict", "Good Fit")
        badge_cls = "strong" if score >= 85 else ("good" if score >= 70 else "moderate")

        strengths_li = "".join(f"<li>{s}</li>" for s in getattr(j, "strengths", [])) or "<li>Core stack alignment.</li>"
        gaps_li = "".join(f"<li>{g}</li>" for g in getattr(j, "gaps", [])) or "<li>Competitive applicants.</li>"
        cv_tips = "<br>&bull; ".join(getattr(j, "cv_suggestions", [])) or "Highlight your primary full stack projects."

        card = f"""
<div class="job-card {badge_cls}">
  <div class="job-header">
    <div>
      <div class="job-title">{idx}. {j.title} — {j.company}</div>
      <div class="job-meta">
        <span>📍 {j.location}</span>
        <span>🏢 {j.company}</span>
        <span>🌐 {j.source}</span>
      </div>
    </div>
    <div>
      <span class="score-badge {badge_cls}">{score}% &bull; {verdict}</span>
    </div>
  </div>

  <div class="section-label">Key Matches</div>
  <ul>{strengths_li}</ul>

  <div class="section-label">Gaps</div>
  <ul>{gaps_li}</ul>

  <div class="section-label">Tailored CV Suggestions</div>
  <div class="cv-suggestion">&bull; {cv_tips}</div>

  <a class="apply-btn" href="{j.url}" target="_blank" rel="noopener">Apply &rarr;</a>
</div>
"""
        cards_html.append(card)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Job Alert Report — {date_str}</title>
<style>
  :root {{ --accent: #2563eb; --green: #16a34a; --amber: #d97706; --red: #dc2626; --bg: #f8fafc; --card: #fff; --border: #e2e8f0; --text: #1e293b; --muted: #64748b; }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: var(--bg); color: var(--text); line-height: 1.6; padding: 2rem; max-width: 960px; margin: 0 auto; }}
  h1 {{ font-size: 1.75rem; margin-bottom: .25rem; }}
  .meta {{ color: var(--muted); font-size: .9rem; margin-bottom: 1.5rem; }}
  .summary-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: .5rem 2rem; background: var(--card); border: 1px solid var(--border); border-radius: 8px; padding: 1rem 1.5rem; margin-bottom: 1.5rem; }}
  .summary-grid dt {{ font-weight: 600; color: var(--muted); font-size: .85rem; }}
  .summary-grid dd {{ margin-bottom: .4rem; }}
  .job-card {{ background: var(--card); border: 1px solid var(--border); border-radius: 10px; padding: 1.5rem; margin-bottom: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,.04); }}
  .job-card.strong {{ border-left: 4px solid var(--green); }}
  .job-card.good {{ border-left: 4px solid var(--accent); }}
  .job-card.moderate {{ border-left: 4px solid var(--amber); }}
  .score-badge {{ display: inline-block; padding: 2px 10px; border-radius: 12px; font-weight: 700; font-size: .85rem; color: #fff; }}
  .score-badge.strong {{ background: var(--green); }}
  .score-badge.good {{ background: var(--accent); }}
  .score-badge.moderate {{ background: var(--amber); }}
  .job-header {{ display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: .5rem; }}
  .job-title {{ font-size: 1.15rem; font-weight: 700; }}
  .job-meta {{ font-size: .85rem; color: var(--muted); }}
  .job-meta span {{ margin-right: 1rem; }}
  ul {{ margin: .5rem 0 .5rem 1.25rem; }}
  li {{ margin-bottom: .3rem; }}
  a {{ color: var(--accent); text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}
  .apply-btn {{ display: inline-block; background: var(--accent); color: #fff; padding: 6px 18px; border-radius: 6px; font-weight: 600; font-size: .9rem; margin-top: .75rem; }}
  .apply-btn:hover {{ background: #1d4ed8; text-decoration: none; }}
  .section-label {{ font-weight: 700; font-size: .9rem; color: var(--muted); text-transform: uppercase; letter-spacing: .05em; margin-top: 1rem; margin-bottom: .25rem; }}
  .cv-suggestion {{ background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 6px; padding: .75rem 1rem; margin-top: .5rem; font-size: .9rem; }}
  footer {{ margin-top: 3rem; padding-top: 1rem; border-top: 1px solid var(--border); color: var(--muted); font-size: .8rem; text-align: center; }}
</style>
</head>
<body>
<h1>Job Alert Report — Full Stack Developer</h1>
<div class="meta">Candidate: Arwa Ahmed &bull; Generated: {date_str} (Cairo Time)</div>

<dl class="summary-grid">
  <div><dt>Total Candidates Fetched</dt><dd>{stats.get('candidates', len(jobs))}</dd></div>
  <div><dt>Qualified Matches</dt><dd>{len(jobs)}</dd></div>
  <div><dt>Skipped (Out of Market / Unqualified)</dt><dd>{stats.get('skipped', 0)}</dd></div>
  <div><dt>Report Type</dt><dd>Automated Fit Evaluation</dd></div>
</dl>

<h2>Top Matches</h2>
{"".join(cards_html)}

<footer>JobAlert &bull; Generated on {date_str} Cairo Time</footer>
</body>
</html>
"""

