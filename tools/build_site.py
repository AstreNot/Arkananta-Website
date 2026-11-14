"""Build index.html (technical dark/light theme with Nivo charts) from the content below and the synthetic demos.

Usage:  cd tools/nivo && npm ci   then   python tools/build_site.py
Set PORTFOLIO_DEMOS to the folder holding the demo projects (default: ../portfolio-demos next to this repo).
"""
from html import escape as e
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

NAME, ROLE = "Daffa Arkananta", "Data Scientist"
HEADLINE = "Plans that run, numbers you can trust."
INTRO = ("I build optimization models and the pipelines around them for manufacturers with scarce materials "
         "and data that doesn't reconcile. Seven examples below, all on synthetic data. Each ships with its own checks.")
PROBLEM = ("A model can look right in a notebook and fail in production. A dashboard can disagree with its source. "
           "A plan can miss a material and nobody notices until the line stops.")
GUIDE = ("I'm a Data Scientist at one of Indonesia's largest halal beauty and personal-care manufacturers. "
         "I test before I quote, so each project here has self-checks, reconciliation or tests, and says what it leaves out.")
PLAN = [("Frame the decision", "What are we maximising, and what can't we break?"),
        ("Build it and prove it", "A solver, explicit constraints, and checks that fail loudly."),
        ("Ship it", "A dashboard, a scheduled report, a plan people can use.")]
OUTCOME = ("Without this, stock expires and demand goes unserved. With it, a plan covers demand with fewer machines "
           "and a page matches its source.")
CTA = "Email me, or open any project's README to see the method."
LINKS = [("GitHub", "https://github.com/AstreNot"),
         ("LinkedIn", "https://www.linkedin.com/in/daffa-arkananta-09653b125"),
         ("Email", "mailto:daffarkananta23@gmail.com")]

EXPERIENCE = [
    ("Jan 2026 – Present", "Data Scientist", "PT Paragon Technology and Innovation",
     "An Indonesian halal beauty and personal-care manufacturer, one of the country's largest, founded in 1985, with its own research and innovation center."),
    ("Aug 2025 – Dec 2025", "Assistant Project Manager", "PT Cipta Mikro Material", ""),
    ("May 2024 – Apr 2025", "AI Training for Indonesia Writers", "Outlier.ai · freelance, remote", ""),
    ("Jan 2023 – Feb 2023", "Data Analyst (internship)", "PT Solusi Sinergi Digital, Tbk", ""),
]

# (group, title, blurb, tools, link or None)
S = "synthetic example"
PROJECTS = [
    ("Optimization", "Production Planning under Material Scarcity",
     "Whole-batch minimums cost fill rate. The LP bound reaches 67.9%, naive rounding drops to 65.7%, and a recovery pass brings it back to 66.9%.",
     "Python · LP/MILP · HiGHS", None),
    ("Optimization", "Multi-Year, Two-Site Capacity Planning",
     "Demand grows and a second site opens in year 3. The baseline serves everything with 2 new machines and 1 moved. A harder scenario is proven infeasible instead of hidden.",
     "Python · MILP · SciPy", None),
    ("Optimization", "Distribution Network Optimization",
     "+20% demand pushes demand to 2,857 against 2,700 of factory capacity, so service drops from 100% to 94.5%. Larger DCs change nothing, because they can't ship what isn't made.",
     "Python · network flow · scenarios", None),
    ("Optimization", "FEFO Expiry Planning",
     "With supporting stock tight, 31.4% of the at-risk value is recovered.",
     "Python · MILP · HiGHS", None),
    ("Applied analytics", "Commercial Analytics Dashboard",
     "Four customers report four different ways. One rule handles each case, and totals match an independent reference within 0.1%.",
     "Python · DuckDB · FastAPI", None),
    ("Applied analytics", "Automated Report Pipeline",
     "A deck that builds itself and refuses to run on fake data unless told.",
     "Python · python-pptx · Airflow", None),
    ("Applied analytics", "Product Name Matching",
     "87.3% top-1 accuracy on generated listings with known answers.",
     "Python · BM25 · fuzzy matching", None),
    ("Research and public case studies", "XRD Image Identification (VGG16)",
     "Classifies materials from X-ray diffractograms with a VGG16-based model.",
     "Python · Keras", "https://github.com/AstreNot/Research-Image-Identification-Model-From-X-Ray-Diffractograms-Based-On-VGG16"),
    ("Research and public case studies", "Kaggle Sales Forecasting",
     "Sticker sales prediction with XGBoost and radial basis functions, final RMSE 0.62.",
     "Python · XGBoost · sklego", "https://github.com/AstreNot/Project-Sales-Forecasting-Kaggle-Competition"),
    ("Research and public case studies", "Bellabeat User Habits",
     "User habit analysis for marketing insight.",
     "SQL · Tableau", "https://github.com/AstreNot/Bellabeat-User-Habit"),
    ("Research and public case studies", "AtliQ Sales Insight",
     "Sales performance analysis for a hardware business.",
     "Power BI · MySQL", "https://github.com/AstreNot/Projects-Sales-Insight-Power-BI-Dashboard"),
]
GROUPS = []
for p in PROJECTS:
    if p[0] not in GROUPS:
        GROUPS.append(p[0])

REAL = GROUPS[:-1]
PUBLIC = [p for p in PROJECTS if p[0] == GROUPS[-1]]


def more_list():
    items = "".join(f'<li><a href="{l}">{e(t)}</a> <span class="more-t">{e(tools)}</span></li>' for _, t, b, tools, l in PUBLIC)
    return f'<ul class="more">{items}</ul>'


COMMON_HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Daffa Arkananta · Data Scientist</title>
<meta name="color-scheme" content="dark light">
<meta name="description" content="Data scientist: optimization models, forecasting, pipelines and dashboards.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
"""


def exp_rows(fmt):
    return "".join(fmt(*x) for x in EXPERIENCE)


def link_list(cls="", sep=""):
    return sep.join(f'<a class="{cls}" href="{u}">{n}</a>' for n, u in LINKS)


# ---------------------------------------------------------------- B: technical dark + light, with charts
import csv as _csv, json as _json, os as _os, re as _re, subprocess as _sp, sys as _sys

DEMO = Path(_os.environ.get("PORTFOLIO_DEMOS", ROOT.parent / "portfolio-demos"))
NIVO_DIR = Path(__file__).parent / "nivo"


def _run(folder, *args):
    env = {**_os.environ, "REPORT_DUMMY": "1", "PYTHONIOENCODING": "utf-8"}
    r = _sp.run([_sys.executable, *args], cwd=DEMO / folder, capture_output=True, text=True, env=env)
    assert r.returncode == 0, (folder, r.stderr[-400:])
    return r.stdout


def _num(s):
    return float(s.replace(",", ""))


def collect():
    """Run the synthetic demos and read the numbers the charts show (nothing is typed in by hand)."""
    d = {}
    o = _run("04-production-planning-lp", "run.py")
    d["fill"] = [(n, float(_re.search(rf"{k}\s+fill\s+([\d.]+)%", o).group(1)))
                 for n, k in [("LP", "LP relaxation"), ("Rounded", "after MPQ rounding"), ("Recovered", "after recovery")]]
    o = _run("05-capacity-planning-milp", "run.py").split("high_must_serve")[0]
    d["cap"] = [(int(a), int(b)) for a, b in _re.findall(r"year \d: new site0 (\d+), new site1 (\d+)", o)][:5]
    d["moved"] = int(_re.search(r"moved to the second site (\d+)", o).group(1))
    _run("06-network-optimization", "run.py")
    with open(DEMO / "06-network-optimization" / "scenario_summary.csv", newline="") as f:
        d["svc"] = [(n, float(r["service_level"]) * 100) for n, r in zip(["Baseline", "+20% demand", "+20%, +DCs"], _csv.DictReader(f))]
    _run("08-fefo-expiry-planning", "generate_data.py")
    m = _re.search(r"at-risk value ([\d,]+)\s+expired value ([\d,]+)", _run("08-fefo-expiry-planning", "run.py"))
    risk, lost = _num(m.group(1)), _num(m.group(2))
    d["fefo"] = [("At risk", risk, 1), ("Expired", lost, 1), ("Recovered", risk - lost, 0)]
    _run("01-analytics-dashboard", "generate_data.py")
    rows = _json.loads(_run("01-analytics-dashboard", "-c", "import app,json;print(json.dumps(app.summary()))"))
    d["st"] = [(r["channel"], r["sell_through"] * 100) for r in rows]
    _run("07-report-pipeline", "pipeline.py")
    rep = _json.loads((DEMO / "07-report-pipeline" / "cache" / "report.json").read_text())
    d["rep"] = [(r["name"], r["actual"]) for r in rep["regions"]]
    d["rep_target"] = rep["regions"][0]["target"]
    _run("02-product-matching", "generate_data.py")
    d["acc"] = float(_re.search(r"top-1 accuracy: ([\d.]+)%", _run("02-product-matching", "run.py")).group(1))
    return d


def bars(rows, vmax, fmt, label, ref=None, ref_label=""):
    rows = [(tuple(r) + (0,))[:3] for r in rows]
    n = len(rows)
    h = n * 24 + (16 if ref is not None else 4)
    x0, wmax = 92, 100
    out = [f'<svg class="svg" viewBox="0 0 250 {h}" role="img" aria-label="{e(label)}">']
    for i, (name, val, s) in enumerate(rows):
        y = i * 24 + 2
        w = max(1.0, val / vmax * wmax)
        out.append(f'<text class="lb" x="0" y="{y + 13}">{e(name)}</text><rect class="s{s}" x="{x0}" y="{y + 1}" width="{w:.1f}" height="15" rx="2"/>'
                   f'<text class="vl" x="{x0 + w + 6:.1f}" y="{y + 13}">{fmt(val)}</text>')
    if ref is not None:
        rx = x0 + ref / vmax * wmax
        out.append(f'<line class="rf" x1="{rx:.1f}" x2="{rx:.1f}" y1="0" y2="{n * 24}"/><text class="lb" x="{rx:.1f}" y="{h - 3}" text-anchor="middle">{e(ref_label)}</text>')
    return "".join(out) + "</svg>"


def columns(pairs, label):
    unit = 56 / max(2, max(a + b for a, b in pairs))
    out = [f'<svg class="svg" viewBox="0 0 250 112" role="img" aria-label="{e(label)}">']
    for i, (a, b) in enumerate(pairs):
        x = 14 + i * 46
        y = 74
        for val, s in ((a, 1), (b, 0)):  # site 1 (existing) at the bottom, site 2 on top
            hh = val * unit
            if hh:
                out.append(f'<rect class="s{s}" x="{x}" y="{y - hh:.1f}" width="30" height="{hh:.1f}" rx="2"/>')
            y -= hh
        out.append(f'<text class="vl" x="{x + 15}" y="{y - 5:.1f}" text-anchor="middle">{a + b}</text>'
                   f'<text class="lb" x="{x + 15}" y="90" text-anchor="middle">Y{i + 1}</text>')
    out.append('<rect class="s1" x="14" y="99" width="10" height="10" rx="2"/><text class="lb" x="29" y="108">site 1</text>'
               '<rect class="s0" x="84" y="99" width="10" height="10" rx="2"/><text class="lb" x="99" y="108">site 2</text></svg>')
    return "".join(out)


def charts(d):
    """Charts are rendered by Nivo (@nivo/bar) to static SVG at build time via node, so the page ships no chart JS."""
    rows = lambda items: [{"label": n, "value": v, "series": (r[0] if r else 0)} for n, v, *r in items]
    specs = {
        "Production Planning under Material Scarcity": dict(type="hbar", rows=rows(d["fill"]), max=100, format="pct",
            aria="Fill rate by stage: " + ", ".join(f"{n} {v:.1f}%" for n, v in d["fill"])),
        "Multi-Year, Two-Site Capacity Planning": dict(type="stack", keys=["site 1", "site 2"], max=max(2, max(a + b for a, b in d["cap"])),
            data=[{"year": f"Y{i + 1}", "site 1": a, "site 2": b} for i, (a, b) in enumerate(d["cap"])],
            aria="New machines open by year, baseline: " + ", ".join(f"year {i + 1}: site 1 {a}, site 2 {b}" for i, (a, b) in enumerate(d["cap"]))),
        "Distribution Network Optimization": dict(type="hbar", rows=rows(d["svc"]), max=100, format="pct",
            aria="Service level by scenario: " + ", ".join(f"{n} {v:.1f}%" for n, v in d["svc"])),
        "FEFO Expiry Planning": dict(type="hbar", rows=rows(d["fefo"]), max=d["fefo"][0][1], format="money",
            aria="At-risk value " + f"{d['fefo'][0][1]:,.0f}" + ", expired " + f"{d['fefo'][1][1]:,.0f}" + ", recovered " + f"{d['fefo'][2][1]:,.0f}"),
        "Commercial Analytics Dashboard": dict(type="hbar", rows=rows(d["st"]), max=120, format="pct",
            aria="Sell-through by channel: " + ", ".join(f"{n} {v:.1f}%" for n, v in d["st"])),
        "Automated Report Pipeline": dict(type="hbar", rows=rows(d["rep"]), max=150, format="int",
            ref={"value": d["rep_target"], "label": "target"}, aria="Actual by region against a target of " + str(d["rep_target"])),
        "Product Name Matching": dict(type="hbar", rows=rows([("Top-1", d["acc"])]), max=100, format="pct", aria=f"Top-1 accuracy {d['acc']:.1f}%"),
    }
    r = _sp.run(["node", "gen.mjs"], cwd=NIVO_DIR, input=_json.dumps(specs), capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0, r.stderr[-500:]
    svg = _json.loads(r.stdout)
    caps = {
        "Production Planning under Material Scarcity": "Fill rate by stage",
        "Multi-Year, Two-Site Capacity Planning": f"New machines open by year (baseline; site 1 below, site 2 above), plus {d['moved']} existing machine moved to site 2",
        "Distribution Network Optimization": "Service level by scenario (last bar: +20% demand with larger DCs)",
        "FEFO Expiry Planning": "At-risk value, expired and recovered",
        "Commercial Analytics Dashboard": "Sell-through by channel",
        "Automated Report Pipeline": "Actual vs target by region",
        "Product Name Matching": "Top-1 accuracy on generated listings",
    }
    return {t: f'<figure class="chart">{svg[t]}<figcaption>{e(caps[t])}</figcaption></figure>' for t in specs}


THEME_DARK = "--bg:#0F172A;--card:#1B2336;--fg:#F8FAFC;--muted:#94A3B8;--line:#334155;--accent:#22C55E;--on-accent:#0F172A;--bar:rgba(15,23,42,.92);--ring:#FFFFFF;--c1:#22C55E;--c2:#64748B"
THEME_LIGHT = "--bg:#F8FAFC;--card:#FFFFFF;--fg:#0F172A;--muted:#475569;--line:#CBD5E1;--accent:#15803D;--on-accent:#FFFFFF;--bar:rgba(248,250,252,.92);--ring:#0F172A;--c1:#15803D;--c2:#64748B"


def page_b():
    css = ":root{" + THEME_DARK + "}\n@media (prefers-color-scheme:light){:root:not([data-theme=dark]){" + THEME_LIGHT + "}}\n:root[data-theme=light]{" + THEME_LIGHT + "}" + """
*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:72px}
body{margin:0;background:var(--bg);color:var(--fg);font:400 1rem/1.65 'IBM Plex Sans',system-ui,sans-serif}
.mono{font-family:'JetBrains Mono',ui-monospace,monospace}
.wrap{max-width:1040px;margin:0 auto;padding:0 16px}
a{color:var(--accent);text-underline-offset:3px}a:focus-visible,button:focus-visible{outline:2px solid var(--ring);outline-offset:3px}
.skip{position:absolute;left:-999px}.skip:focus{left:16px;top:8px;background:var(--bg);padding:8px}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}
.bar{border-bottom:1px solid var(--line);position:sticky;top:0;background:var(--bar);backdrop-filter:blur(6px);z-index:5}
.bar .wrap{display:flex;justify-content:space-between;align-items:center;min-height:56px;gap:16px;flex-wrap:wrap}
.bar nav{display:flex;align-items:center;flex-wrap:wrap}
.bar nav a{color:var(--muted);text-decoration:none;margin-left:20px;display:inline-block;padding:12px 0}.bar nav a:hover{color:var(--fg)}
.theme{margin-left:20px;min-height:44px;padding:8px 14px;background:transparent;color:var(--fg);border:1px solid var(--line);border-radius:6px;font:500 .8rem 'JetBrains Mono',monospace;cursor:pointer}
.theme:hover{border-color:var(--accent)}
.hero{padding:80px 0 56px}
.prompt{color:var(--accent);font-size:.9rem;margin:0 0 16px}
h1{font:700 clamp(2rem,5vw,3.2rem)/1.15 'JetBrains Mono',monospace;margin:0 0 16px;letter-spacing:-.02em}
.lede{color:var(--muted);max-width:62ch;font-size:1.1rem;margin:0 0 28px}
.btn{display:inline-block;min-height:44px;padding:10px 18px;border:1px solid var(--accent);color:var(--accent);text-decoration:none;border-radius:6px;margin:0 8px 8px 0;font-family:'JetBrains Mono',monospace;font-size:.9rem;transition:background .2s,color .2s}
.btn:hover{background:var(--accent);color:var(--on-accent)}
section{padding:48px 0}
.story p{max-width:68ch;margin:0 0 16px}.story .k{font:500 .8rem 'JetBrains Mono',monospace;color:var(--muted);margin:24px 0 6px;text-transform:lowercase}
.plan{list-style:none;counter-reset:step;padding:0;margin:20px 0;display:grid;gap:16px;grid-template-columns:repeat(auto-fit,minmax(min(240px,100%),1fr))}
.plan li{counter-increment:step;background:var(--card);border:1px solid var(--line);border-radius:8px;padding:16px}
.plan li::before{content:counter(step,decimal-leading-zero);font:500 .8rem 'JetBrains Mono',monospace;color:var(--muted)}
.plan b{display:block;font-weight:600;margin:2px 0 4px}.plan span{color:var(--muted)}
h2{font:600 1.1rem 'JetBrains Mono',monospace;margin:0 0 24px;color:var(--fg)}h2::before{content:'## ';color:var(--accent)}
.log{border-left:2px solid var(--line);padding-left:20px}
.entry{position:relative;padding:0 0 22px}.entry::before{content:'';position:absolute;left:-26px;top:9px;width:10px;height:10px;border-radius:50%;background:var(--accent)}
.when{color:var(--muted);font-size:.85rem;font-variant-numeric:tabular-nums}
.entry h3{margin:2px 0;font-size:1.05rem}.entry p{margin:0;color:var(--muted)}
.grp{color:var(--muted);font:500 .85rem 'JetBrains Mono',monospace;margin:32px 0 12px;text-transform:lowercase}
.grid{display:grid;gap:16px;grid-template-columns:repeat(auto-fill,minmax(min(290px,100%),1fr))}
.card{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:20px;display:flex;flex-direction:column;gap:10px;transition:transform .2s,border-color .2s}
.card:hover{transform:translateY(-3px);border-color:var(--accent)}
.card h4{margin:0;font-size:1.05rem}.card p{margin:0;color:var(--muted)}
.chart{margin:4px 0 0}.svg{width:100%;height:auto;display:block;overflow:visible}
.chart figcaption{color:var(--muted);font-size:.8rem;margin-top:6px}
.svg .lb{fill:var(--muted);font:12px 'JetBrains Mono',monospace}.svg .vl{fill:var(--fg);font:12px 'JetBrains Mono',monospace;font-variant-numeric:tabular-nums}
.svg rect{stroke:var(--card);stroke-width:1}.svg .s0{fill:var(--c1)}.svg .s1{fill:var(--c2)}.svg .rf{stroke:var(--muted);stroke-dasharray:3 3}
.tools{font:400 .8rem 'JetBrains Mono',monospace;color:var(--fg);margin-top:auto}
.chip{align-self:flex-start;font:500 .75rem 'JetBrains Mono',monospace;border:1px solid var(--line);color:var(--muted);border-radius:99px;padding:2px 10px}
.card a.go{font:500 .85rem 'JetBrains Mono',monospace}
ul.more{list-style:none;padding:0;margin:0}.more li{padding:10px 0;border-top:1px solid var(--line)}.more-t{color:var(--muted);font:400 .8rem 'JetBrains Mono',monospace;margin-left:8px}
footer{border-top:1px solid var(--line);padding:32px 0 56px;color:var(--muted)}footer a{display:inline-block;min-height:44px;padding:12px 8px}
@media (max-width:640px){.bar{position:static}}
@media (prefers-reduced-motion:reduce){.card,.btn{transition:none}.card:hover{transform:none}html{scroll-behavior:auto}}
"""
    data = collect()
    copy = " ".join(p[2] for p in PROJECTS)
    risk, lost = data["fefo"][0][1], data["fefo"][1][1]
    for label, n in [*(("fill", f"{v:.1f}%") for _, v in data["fill"]), ("service", f"{data['svc'][1][1]:.1f}%"),
                     ("recovery", f"{(risk - lost) / risk * 100:.1f}%"), ("accuracy", f"{data['acc']:.1f}%")]:
        assert n in copy, f"copy says something different from the demo ({label}: expected {n})"
    ch = charts(data)
    cards = ""
    for g in REAL:
        cards += f'<h3 class="grp">// {e(g)}</h3><div class="grid">'
        for gr, t, b, tools, link in (p for p in PROJECTS if p[0] == g):
            foot = f'<a class="go" href="{link}">view repo →</a>' if link else f'<span class="chip">{S}</span>'
            cards += f'<article class="card"><h4>{e(t)}</h4><p>{e(b)}</p>{ch.get(t, "")}<span class="tools">{e(tools)}</span>{foot}</article>'
        cards += "</div>"
    exp = exp_rows(lambda w, r, c, d: f'<div class="entry"><span class="when mono">{w}</span><h3>{e(r)}</h3><p>{e(c)}</p>{f"<p>{e(d)}</p>" if d else ""}</div>')
    btns = "".join(f'<a class="btn" href="{u}">{n}</a>' for n, u in LINKS)
    plan = "".join(f"<li><b>{e(t)}</b><span>{e(d)}</span></li>" for t, d in PLAN)
    boot = "<script>try{var t=localStorage.getItem('theme');if(t)document.documentElement.dataset.theme=t}catch(e){}</script>"
    toggle = """<script>(function(){var r=document.documentElement,b=document.getElementById('theme');
function cur(){return r.dataset.theme||(matchMedia('(prefers-color-scheme: light)').matches?'light':'dark')}
function paint(){b.textContent='switch to '+(cur()==='light'?'dark':'light')}
b.onclick=function(){var n=cur()==='light'?'dark':'light';r.dataset.theme=n;try{localStorage.setItem('theme',n)}catch(e){}paint()};paint()})()</script>"""
    head = COMMON_HEAD.replace('<meta name="description"', '<meta name="color-scheme" content="dark light">\n<meta name="description"')
    return (head + '<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">'
            f"{boot}<style>{css}</style></head><body><a class=\"skip\" href=\"#work\">Skip to work</a>"
            f'<div class="bar"><div class="wrap"><span class="mono" aria-hidden="true">arka@portfolio:~$</span><strong class="sr">Daffa Arkananta</strong>'
            f'<nav aria-label="Primary"><a href="#experience">experience</a><a href="#work">work</a><a href="#contact">contact</a><button class="theme" id="theme" type="button">switch theme</button></nav></div></div>'
            f'<main class="wrap"><div class="hero"><p class="prompt mono">{NAME} · {ROLE}</p><h1>{e(HEADLINE)}</h1><p class="lede">{e(INTRO)}</p>{btns}</div>'
            f'<section id="how" class="story"><h2>How I work</h2><p class="k">the problem</p><p>{e(PROBLEM)}</p><p class="k">who is writing</p><p>{e(GUIDE)}</p>'
            f'<p class="k">the plan</p><ol class="plan">{plan}</ol><p>{e(OUTCOME)}</p></section>'
            f'<section id="experience"><h2>Experience</h2><div class="log">{exp}</div></section>'
            f'<section id="work"><h2>Work</h2><p class="lede" style="font-size:.95rem">Cards marked "synthetic example" use generated data and fictional companies. Charts show results from those runs.</p>{cards}'
            f'<h3 class="grp">more: public case studies</h3>{more_list()}</section>'
            f'<section id="cta"><h2>Contact</h2><p class="lede">{e(CTA)}</p>{btns}</section></main>'
            f'<footer id="contact"><div class="wrap mono" style="font-size:.85rem">{link_list(sep=" · ")}</div></footer>{toggle}</body></html>')




if __name__ == "__main__":
    (ROOT / "index.html").write_text(page_b(), encoding="utf-8")
    print("wrote", ROOT / "index.html")
