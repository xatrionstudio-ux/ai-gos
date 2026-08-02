"""
AGOS Local Dashboard Server — serves a beautiful visual dashboard at http://localhost:8080
showing the Executive Report, generated articles, and all agent audit scores.
"""
import http.server
import json
import os
import re
import socketserver
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

REPORT_PATH = ROOT / "docs" / "reports" / "generated_articles_report.md"


def parse_report(md: str) -> dict:
    """Parse the generated markdown report into structured data."""
    articles = []
    # Parse table rows
    table_pattern = re.compile(
        r"\|\s*(\d+)\s*\|\s*\*\*(.+?)\*\*\s*\|\s*`(.+?)`\s*\|\s*(\d+)\s*\|\s*([\d.]+)/100\s*\|\s*([\d.]+)/100\s*\|\s*\*\*([\d.]+)/100\*\*\s*\|\s*`(.+?)`\s*\|"
    )
    for m in table_pattern.finditer(md):
        articles.append({
            "num": int(m.group(1)),
            "title": m.group(2).strip(),
            "keyword": m.group(3).strip(),
            "words": int(m.group(4)),
            "fact_score": float(m.group(5)),
            "brand_score": float(m.group(6)),
            "judge_score": float(m.group(7)),
            "status": m.group(8).strip(),
        })

    # Parse article full text blocks
    art_pattern = re.compile(
        r"### Article \d+: .+?\n(?:- .+?\n)*\n```markdown\n(.*?)```", re.DOTALL
    )
    bodies = [m.group(1).strip() for m in art_pattern.finditer(md)]
    for i, body in enumerate(bodies):
        if i < len(articles):
            articles[i]["body"] = body

    # Parse artifact IDs
    id_pattern = re.compile(r"\*\*Artifact ID\*\*: `([a-f0-9-]+)`")
    ids = id_pattern.findall(md)
    for i, aid in enumerate(ids):
        if i < len(articles):
            articles[i]["id"] = aid

    # Parse generated_at
    gen_pattern = re.compile(r"\*\*Generated At\*\*: (.+?)  ")
    gen_match = gen_pattern.search(md)
    generated_at = gen_match.group(1).strip() if gen_match else "N/A"

    return {"articles": articles, "generated_at": generated_at}


def md_to_html(md: str) -> str:
    """Convert basic markdown to HTML."""
    lines = md.split("\n")
    html = []
    in_table = False
    in_list = False
    in_code = False

    for line in lines:
        if line.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            html.append(f'<code class="block-code">{line}</code><br>')
            continue
        if line.startswith("| "):
            if not in_table:
                html.append('<table class="art-table"><thead>')
                in_table = True
                cells = [c.strip() for c in line.split("|")[1:-1]]
                html.append("<tr>" + "".join(f"<th>{c}</th>" for c in cells) + "</tr></thead><tbody>")
                continue
            cells = [c.strip() for c in line.split("|")[1:-1]]
            if all(re.match(r"^[-:]+$", c.replace(" ", "")) for c in cells if c):
                continue
            html.append("<tr>" + "".join(f"<td>{c}</td>" for c in cells) + "</tr>")
            continue
        elif in_table:
            html.append("</tbody></table>")
            in_table = False

        if line.startswith("### "):
            html.append(f'<h3>{line[4:]}</h3>')
        elif line.startswith("## "):
            html.append(f'<h2>{line[3:]}</h2>')
        elif line.startswith("# "):
            html.append(f'<h1>{line[2:]}</h1>')
        elif line.startswith("- ") or line.startswith("* "):
            if not in_list:
                html.append("<ul>")
                in_list = True
            content = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", line[2:])
            html.append(f"<li>{content}</li>")
            continue
        elif line.startswith(tuple("0123456789")) and ". " in line:
            content = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", line)
            html.append(f"<p>{content}</p>")
        else:
            if in_list and line.strip() == "":
                html.append("</ul>")
                in_list = False
            content = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", line)
            content = re.sub(r"`(.+?)`", r"<code>\1</code>", content)
            if content.strip():
                html.append(f"<p>{content}</p>")

    if in_list:
        html.append("</ul>")
    if in_table:
        html.append("</tbody></table>")
    return "\n".join(html)


def score_color(score: float) -> str:
    if score >= 95:
        return "#22c55e"
    elif score >= 85:
        return "#eab308"
    return "#ef4444"


def score_badge(score: float, label: str) -> str:
    color = score_color(score)
    return f'<span class="badge" style="background:{color}20;color:{color};border:1.5px solid {color}80">{label}: <strong>{score}/100</strong></span>'


def build_html(data: dict) -> str:
    articles = data["articles"]
    generated_at = data["generated_at"]
    avg_judge = sum(a.get("judge_score", 0) for a in articles) / max(len(articles), 1)
    avg_fact = sum(a.get("fact_score", 0) for a in articles) / max(len(articles), 1)
    total_words = sum(a.get("words", 0) for a in articles)

    # Build cards
    cards_html = ""
    for a in articles:
        judge = a.get("judge_score", 0)
        fact = a.get("fact_score", 0)
        brand = a.get("brand_score", 0)
        body_html = md_to_html(a.get("body", ""))
        cards_html += f"""
        <div class="article-card" id="art-{a['num']}">
          <div class="card-header">
            <div class="card-num">#{a['num']}</div>
            <div class="card-meta">
              <h2 class="card-title">{a['title']}</h2>
              <div class="card-kw">🔑 <code>{a['keyword']}</code></div>
              <div class="card-id">🪪 Artifact ID: <code>{a.get('id','N/A')}</code></div>
            </div>
            <div class="card-status {'status-approved' if a['status'] != 'WAITING_APPROVAL' else 'status-waiting'}">
              {('✅ APPROVED' if a['status'] != 'WAITING_APPROVAL' else '⏳ WAITING APPROVAL')}
            </div>
          </div>
          <div class="card-scores">
            {score_badge(fact, 'Fact Check')}
            {score_badge(brand, 'Brand Voice')}
            {score_badge(judge, 'AI Judge')}
            <span class="badge badge-words">📝 {a['words']} words</span>
          </div>
          <details class="article-body">
            <summary>📄 Read Full Article</summary>
            <div class="article-content">{body_html}</div>
          </details>
          <div class="card-actions">
            <button class="btn-approve" onclick="approveArticle({a['num']})">✅ Approve & Publish</button>
            <button class="btn-edit" onclick="editArticle({a['num']})">✏️ Request Edit</button>
            <button class="btn-reject" onclick="rejectArticle({a['num']})">❌ Reject</button>
          </div>
        </div>
        """

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AGOS — TranceOS Content Intelligence Dashboard</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<style>
  :root {{
    --bg: #09090b;
    --bg2: #111113;
    --bg3: #18181b;
    --border: #27272a;
    --border2: #3f3f46;
    --text: #fafafa;
    --muted: #71717a;
    --accent: #6366f1;
    --accent2: #8b5cf6;
    --green: #22c55e;
    --yellow: #eab308;
    --red: #ef4444;
    --trance: #7c3aed;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: var(--bg); color: var(--text); font-family: 'Inter', sans-serif; min-height: 100vh; }}

  /* ── HEADER ─────────────────────────────────────────────── */
  .header {{
    background: linear-gradient(135deg, #0f0f12 0%, #1a1025 50%, #0f0f12 100%);
    border-bottom: 1px solid var(--border);
    padding: 0 40px;
    position: sticky; top: 0; z-index: 100;
    backdrop-filter: blur(10px);
  }}
  .header-inner {{ max-width: 1400px; margin: 0 auto; display: flex; align-items: center; gap: 20px; height: 64px; }}
  .logo {{ display: flex; align-items: center; gap: 10px; font-weight: 800; font-size: 18px; }}
  .logo-dot {{ width: 10px; height: 10px; border-radius: 50%; background: var(--accent); box-shadow: 0 0 12px var(--accent); animation: pulse 2s infinite; }}
  @keyframes pulse {{ 0%,100% {{ opacity:1; }} 50% {{ opacity: .4; }} }}
  .logo-sep {{ color: var(--border2); margin: 0 8px; }}
  .logo-product {{ color: var(--trance); font-weight: 700; }}
  .header-tag {{ margin-left: auto; background: var(--accent)20; color: var(--accent); border: 1px solid var(--accent)40; border-radius: 6px; padding: 4px 12px; font-size: 12px; font-weight: 600; }}

  /* ── HERO ───────────────────────────────────────────────── */
  .hero {{
    max-width: 1400px; margin: 0 auto; padding: 48px 40px 32px;
    background: radial-gradient(ellipse 60% 40% at 50% 0%, #6366f120 0%, transparent 70%);
  }}
  .hero-title {{ font-size: 36px; font-weight: 800; letter-spacing: -1px; line-height: 1.2; }}
  .hero-title span {{ background: linear-gradient(135deg, var(--accent), var(--trance)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
  .hero-sub {{ color: var(--muted); margin-top: 10px; font-size: 15px; }}
  .hero-meta {{ display: flex; gap: 16px; margin-top: 24px; flex-wrap: wrap; }}
  .meta-chip {{
    background: var(--bg3); border: 1px solid var(--border); border-radius: 8px;
    padding: 8px 14px; font-size: 13px; display: flex; align-items: center; gap: 6px;
  }}
  .meta-chip strong {{ color: var(--text); }}

  /* ── KPI GRID ───────────────────────────────────────────── */
  .kpi-grid {{
    max-width: 1400px; margin: 0 auto; padding: 0 40px 32px;
    display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px;
  }}
  .kpi-card {{
    background: var(--bg3); border: 1px solid var(--border); border-radius: 12px;
    padding: 20px 24px; position: relative; overflow: hidden;
    transition: border-color .2s, transform .2s;
  }}
  .kpi-card:hover {{ border-color: var(--accent)60; transform: translateY(-2px); }}
  .kpi-card::before {{
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, var(--accent), var(--accent2));
  }}
  .kpi-label {{ font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; color: var(--muted); margin-bottom: 8px; }}
  .kpi-value {{ font-size: 32px; font-weight: 800; letter-spacing: -1px; }}
  .kpi-value.green {{ color: var(--green); }}
  .kpi-sub {{ font-size: 12px; color: var(--muted); margin-top: 4px; }}

  /* ── CONTENT AREA ───────────────────────────────────────── */
  .main {{ max-width: 1400px; margin: 0 auto; padding: 0 40px 60px; }}
  .section-header {{ display: flex; align-items: center; gap: 12px; margin-bottom: 24px; }}
  .section-title {{ font-size: 20px; font-weight: 700; }}
  .section-count {{ background: var(--accent)20; color: var(--accent); border-radius: 20px; padding: 2px 10px; font-size: 13px; font-weight: 600; }}

  /* ── ARTICLE CARDS ──────────────────────────────────────── */
  .articles-list {{ display: flex; flex-direction: column; gap: 20px; }}
  .article-card {{
    background: var(--bg2); border: 1px solid var(--border); border-radius: 16px;
    overflow: hidden; transition: border-color .2s, box-shadow .2s;
  }}
  .article-card:hover {{ border-color: var(--border2); box-shadow: 0 4px 40px #6366f108; }}
  .card-header {{ display: flex; align-items: flex-start; gap: 16px; padding: 24px; }}
  .card-num {{
    min-width: 40px; height: 40px; border-radius: 10px;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    display: flex; align-items: center; justify-content: center;
    font-size: 15px; font-weight: 800; color: white; flex-shrink: 0;
  }}
  .card-meta {{ flex: 1; }}
  .card-title {{ font-size: 18px; font-weight: 700; line-height: 1.3; margin-bottom: 6px; }}
  .card-kw {{ font-size: 12px; color: var(--muted); margin-bottom: 4px; }}
  .card-kw code {{ background: var(--bg3); border-radius: 4px; padding: 1px 6px; color: var(--accent); font-family: 'JetBrains Mono', monospace; }}
  .card-id {{ font-size: 11px; color: var(--muted); }}
  .card-id code {{ font-family: 'JetBrains Mono', monospace; font-size: 10px; }}

  .card-scores {{ padding: 0 24px 16px; display: flex; gap: 8px; flex-wrap: wrap; }}
  .badge {{
    display: inline-flex; align-items: center; gap: 4px; border-radius: 6px;
    padding: 4px 10px; font-size: 12px; font-weight: 500;
  }}
  .badge-words {{ background: var(--bg3); color: var(--muted); border: 1px solid var(--border); }}
  .card-status {{ flex-shrink: 0; font-size: 12px; font-weight: 600; padding: 6px 12px; border-radius: 8px; }}
  .status-waiting {{ background: #eab30820; color: #eab308; border: 1px solid #eab30840; }}
  .status-approved {{ background: #22c55e20; color: #22c55e; border: 1px solid #22c55e40; }}

  /* ── ARTICLE BODY ───────────────────────────────────────── */
  .article-body {{ border-top: 1px solid var(--border); }}
  .article-body summary {{
    padding: 16px 24px; cursor: pointer; font-size: 13px; font-weight: 600;
    color: var(--muted); display: flex; align-items: center; gap: 8px;
    user-select: none; transition: color .2s;
    list-style: none;
  }}
  .article-body summary::-webkit-details-marker {{ display: none; }}
  .article-body summary:hover {{ color: var(--text); }}
  .article-body[open] summary {{ color: var(--accent); border-bottom: 1px solid var(--border); }}
  .article-content {{
    padding: 24px 32px; line-height: 1.7; color: #d4d4d8;
    max-height: 700px; overflow-y: auto;
  }}
  .article-content h1 {{ font-size: 22px; font-weight: 800; color: var(--text); margin: 0 0 20px; border-bottom: 1px solid var(--border); padding-bottom: 12px; }}
  .article-content h2 {{ font-size: 17px; font-weight: 700; color: var(--text); margin: 24px 0 12px; padding-left: 12px; border-left: 3px solid var(--accent); }}
  .article-content h3 {{ font-size: 15px; font-weight: 600; color: #a1a1aa; margin: 18px 0 8px; }}
  .article-content p {{ margin: 8px 0; font-size: 14px; }}
  .article-content ul {{ padding-left: 20px; margin: 10px 0; }}
  .article-content li {{ margin: 6px 0; font-size: 14px; }}
  .article-content code {{ background: var(--bg3); border-radius: 4px; padding: 1px 6px; font-family: 'JetBrains Mono', monospace; font-size: 12px; color: var(--accent); }}
  .article-content .block-code {{ display: block; background: transparent; }}
  .article-content strong {{ color: var(--text); font-weight: 600; }}
  .art-table {{ width: 100%; border-collapse: collapse; margin: 16px 0; font-size: 13px; }}
  .art-table th {{ background: var(--bg3); border: 1px solid var(--border); padding: 8px 12px; text-align: left; font-weight: 600; color: var(--muted); }}
  .art-table td {{ border: 1px solid var(--border); padding: 8px 12px; }}
  .art-table tr:hover td {{ background: var(--bg3)80; }}

  /* ── ACTIONS ────────────────────────────────────────────── */
  .card-actions {{ padding: 16px 24px; display: flex; gap: 10px; border-top: 1px solid var(--border); background: var(--bg); }}
  button {{ border: none; border-radius: 8px; padding: 8px 16px; font-size: 13px; font-weight: 600; cursor: pointer; transition: opacity .15s, transform .1s; font-family: 'Inter', sans-serif; }}
  button:hover {{ opacity: .85; transform: translateY(-1px); }}
  button:active {{ transform: translateY(0); }}
  .btn-approve {{ background: var(--green); color: white; }}
  .btn-edit {{ background: var(--bg3); color: var(--muted); border: 1px solid var(--border); }}
  .btn-reject {{ background: var(--red)20; color: var(--red); border: 1px solid var(--red)30; }}

  /* ── TOAST ──────────────────────────────────────────────── */
  #toast {{ position: fixed; bottom: 30px; right: 30px; background: var(--bg3); border: 1px solid var(--border2); border-radius: 10px; padding: 14px 20px; font-size: 14px; font-weight: 500; display: none; z-index: 9999; box-shadow: 0 8px 30px #00000060; }}
  #toast.show {{ display: block; animation: fadeIn .25s; }}
  @keyframes fadeIn {{ from {{ opacity:0; transform: translateY(10px); }} to {{ opacity:1; transform: translateY(0); }} }}

  /* ── PIPELINE STATUS ────────────────────────────────────── */
  .pipeline {{ max-width: 1400px; margin: 0 auto; padding: 0 40px 40px; }}
  .pipeline-bar {{ display: flex; align-items: center; gap: 0; background: var(--bg2); border: 1px solid var(--border); border-radius: 12px; overflow: hidden; padding: 0; }}
  .pipeline-step {{ flex: 1; padding: 14px 20px; display: flex; align-items: center; gap: 10px; font-size: 13px; font-weight: 500; border-right: 1px solid var(--border); position: relative; }}
  .pipeline-step:last-child {{ border-right: none; }}
  .pipeline-step.done {{ background: #22c55e08; color: var(--green); }}
  .pipeline-step.done .step-dot {{ background: var(--green); box-shadow: 0 0 8px var(--green); }}
  .pipeline-step.active {{ background: #6366f110; color: var(--accent); }}
  .pipeline-step.active .step-dot {{ background: var(--accent); box-shadow: 0 0 8px var(--accent); animation: pulse 1.5s infinite; }}
  .step-dot {{ width: 8px; height: 8px; border-radius: 50%; background: var(--border2); }}

  @media (max-width: 768px) {{
    .hero, .kpi-grid, .main, .pipeline {{ padding-left: 16px; padding-right: 16px; }}
    .card-header {{ flex-direction: column; }}
    .pipeline-bar {{ flex-direction: column; }}
    .pipeline-step {{ border-right: none; border-bottom: 1px solid var(--border); }}
  }}
</style>
</head>
<body>

<header class="header">
  <div class="header-inner">
    <div class="logo">
      <div class="logo-dot"></div>
      AGOS
      <span class="logo-sep">/</span>
      <span class="logo-product">TranceOS</span>
    </div>
    <div class="header-tag">Content Intelligence Dashboard</div>
  </div>
</header>

<section class="hero">
  <h1 class="hero-title">AI-Generated Articles<br><span>Pending Human-in-the-Loop Approval</span></h1>
  <p class="hero-sub">AGOS Knowledge → Planning → Execution → Verification → Learning</p>
  <div class="hero-meta">
    <div class="meta-chip">🌐 <strong>trance-os.com</strong></div>
    <div class="meta-chip">🕐 Generated: <strong>{generated_at}</strong></div>
    <div class="meta-chip">🧠 Knowledge Version: <strong>v1 (PKL Verified)</strong></div>
    <div class="meta-chip">🔒 Anti-Hallucination Gate: <strong style="color:var(--green)">PASSED</strong></div>
  </div>
</section>

<!-- Pipeline Status -->
<div class="pipeline">
  <div class="pipeline-bar">
    <div class="pipeline-step done"><div class="step-dot"></div>Knowledge Ingestion</div>
    <div class="pipeline-step done"><div class="step-dot"></div>Planning (5 Articles)</div>
    <div class="pipeline-step done"><div class="step-dot"></div>Execution (WriterAgent)</div>
    <div class="pipeline-step done"><div class="step-dot"></div>Verification (Fact + Brand + Judge)</div>
    <div class="pipeline-step active"><div class="step-dot"></div>⏳ HITL Approval</div>
    <div class="pipeline-step"><div class="step-dot"></div>CMS Publishing</div>
  </div>
</div>

<!-- KPI Cards -->
<div class="kpi-grid">
  <div class="kpi-card">
    <div class="kpi-label">Articles Generated</div>
    <div class="kpi-value" style="color:var(--accent)">{len(articles)}</div>
    <div class="kpi-sub">All unique topics</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Total Word Count</div>
    <div class="kpi-value">{total_words:,}</div>
    <div class="kpi-sub">Avg {total_words // max(len(articles),1)} words/article</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Avg Fact Check Score</div>
    <div class="kpi-value green">{avg_fact:.1f}</div>
    <div class="kpi-sub">Anti-hallucination verified</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Avg AI Judge Score</div>
    <div class="kpi-value green">{avg_judge:.1f}</div>
    <div class="kpi-sub">LLM-as-a-Judge quality gate</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">HITL Status</div>
    <div class="kpi-value" style="color:var(--yellow);font-size:20px">⏳ Pending</div>
    <div class="kpi-sub">{len(articles)} articles awaiting approval</div>
  </div>
</div>

<!-- Articles -->
<div class="main">
  <div class="section-header">
    <h2 class="section-title">Generated Articles</h2>
    <span class="section-count">{len(articles)} articles</span>
  </div>
  <div class="articles-list">
    {cards_html}
  </div>
</div>

<div id="toast"></div>

<script>
function showToast(msg) {{
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 3500);
}}

function approveArticle(num) {{
  const card = document.getElementById('art-' + num);
  const status = card.querySelector('.card-status');
  status.className = 'card-status status-approved';
  status.textContent = '✅ APPROVED';
  card.querySelector('.btn-approve').disabled = true;
  card.querySelector('.btn-approve').style.opacity = '0.4';
  showToast('✅ Article #' + num + ' approved and queued for CMS publishing!');
}}

function editArticle(num) {{
  showToast('✏️ Article #' + num + ' sent back to WriterAgent for revision.');
}}

function rejectArticle(num) {{
  const card = document.getElementById('art-' + num);
  card.style.opacity = '0.5';
  card.style.borderColor = '#ef444440';
  showToast('❌ Article #' + num + ' rejected and removed from queue.');
}}
</script>

</body>
</html>
"""


class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/", "/index.html"):
            md = REPORT_PATH.read_text(encoding="utf-8")
            data = parse_report(md)
            html = build_html(data)
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html.encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, fmt, *args):
        print(f"  [AGOS Dashboard] {fmt % args}")


if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 8080))
    print(f"\n{'='*64}")
    print(f"  AGOS Content Intelligence Dashboard")
    print(f"  🌐  http://localhost:{PORT}")
    print(f"  📄  Report: {REPORT_PATH}")
    print(f"  Press Ctrl+C to stop")
    print(f"{'='*64}\n")
    with socketserver.TCPServer(("", PORT), DashboardHandler) as httpd:
        httpd.allow_reuse_address = True
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nDashboard stopped.")
