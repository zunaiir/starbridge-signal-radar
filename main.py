import os
import json
from datetime import datetime, timezone
from urllib.parse import urlparse

import requests
from flask import Flask, jsonify, request, Response

app = Flask(__name__)

DEMO_SIGNALS = [
    {
        "company": "VIDIZMO",
        "domain": "vidizmo.ai",
        "signal_type": "Multiple public-sector sales hires",
        "signal": "Expanding its Public Safety sales organization across Account Executive, Strategic AE, Federal, State & Local, Justice/Prosecution and business development roles.",
        "signal_date": "2026-08-10",
        "score": 98,
        "why_now": "A multi-role public-sector hiring push usually means the team needs repeatable territory prioritization and pipeline creation fast, not more manual agency research.",
        "starbridge_angle": "Give incoming public-sector sellers prioritized agencies, procurement context, verified buyers and pre-RFP signals from day one.",
        "target_persona": "VP Sales / Head of Public Safety Sales",
        "source_url": "https://builtin.com/job/public-sector-account-executive/10598699",
        "source_name": "Built In",
    },
    {
        "company": "Envisio",
        "domain": "envisio.com",
        "signal_type": "Public-sector AE hiring",
        "signal": "Hiring a Senior Account Executive – Public Sector to drive new customer acquisition and expand its public-sector footprint.",
        "signal_date": "2026-08-01",
        "score": 96,
        "why_now": "Envisio is explicitly investing in public-sector new-logo acquisition, creating an immediate need for better account selection and earlier buying signals.",
        "starbridge_angle": "Help the new seller focus on in-market agencies and act on pre-RFP buying signals instead of prospecting a broad public-sector TAM.",
        "target_persona": "CRO / VP Sales",
        "source_url": "https://envisio.breezy.hr/p/4622052ea6b3-senior-account-executive-public-sector",
        "source_name": "Envisio Careers",
    },
    {
        "company": "Elastic",
        "domain": "elastic.co",
        "signal_type": "New SLED territory coverage",
        "signal": "Posted a Public Sector Account Executive – SLED Texas role focused on selling into state and local government.",
        "signal_date": "2026-08-31",
        "score": 94,
        "why_now": "Adding dedicated SLED coverage creates a near-term need to identify which agencies in the territory are actually showing demand and which stakeholders matter.",
        "starbridge_angle": "Turn a broad Texas SLED territory into an intent-ranked book of agencies with buying context and actionable outreach triggers.",
        "target_persona": "VP Public Sector / SLED Sales Leader",
        "source_url": "https://jobera.com/job/elastic-public-sector-account-executive-sled-texas-6544c9d9/",
        "source_name": "Jobera",
    },
    {
        "company": "Commvault",
        "domain": "commvault.com",
        "signal_type": "Multiple SLED openings",
        "signal": "Current careers activity includes multiple SLED Account Executive roles plus SLED sales leadership coverage.",
        "signal_date": "2026-08-01",
        "score": 92,
        "why_now": "Adding both sellers and leadership suggests a scaled SLED motion where territory intelligence and consistent signal-based prospecting can compound across the team.",
        "starbridge_angle": "Give every SLED rep the same system for prioritizing agencies, identifying procurement context and acting on timely buying signals.",
        "target_persona": "SVP / VP Public Sector",
        "source_url": "https://www.commvault.com/careers/jobs",
        "source_name": "Commvault Careers",
    },
    {
        "company": "Freshworks",
        "domain": "freshworks.com",
        "signal_type": "Higher-ed SLED expansion",
        "signal": "Hiring an Enterprise SLED Account Executive specifically to expand Freshworks' footprint within higher-education institutions.",
        "signal_date": "2026-08-21",
        "score": 90,
        "why_now": "A dedicated higher-ed expansion role needs a fast way to distinguish institutions with active IT priorities from the rest of the market.",
        "starbridge_angle": "Surface universities showing relevant IT buying signals, map the buying committee and give the seller a timely reason to engage.",
        "target_persona": "VP Public Sector / SLED Sales Leader",
        "source_url": "https://jobs.smartrecruiters.com/Freshworks/744000144138719-account-executive-enterprise-sled-",
        "source_name": "Freshworks Careers",
    },
]

QUERIES = [
    '"SLED Account Executive" software',
    '"Public Sector Account Executive" SaaS',
    '"State and Local Government" "Account Executive" software',
    '"Higher Education" "Account Executive" SaaS',
    '"VP Public Sector" software sales',
    '"Public Sector Sales Director" software',
]

HTML = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Starbridge Signal Radar</title>
<style>
:root{
  --bg:#fbfaff;
  --panel:#ffffff;
  --panel-soft:#f7f3ff;
  --line:#e7e0f2;
  --text:#21163a;
  --muted:#746b87;
  --purple:#6c3bf2;
  --purple-dark:#4e2796;
  --lavender:#eee6ff;
  --lavender-2:#f7f3ff;
  --yellow:#fff4ad;
  --yellow-line:#f0df7c;
  --ink:#ffffff;
  --shadow:0 10px 35px rgba(77,39,150,.08);
}
*{box-sizing:border-box}
html,body{margin:0;background:var(--bg);color:var(--text);font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
body{min-height:100vh;background:radial-gradient(circle at 72% -8%,rgba(151,111,255,.24),transparent 31%),linear-gradient(180deg,#f3edff 0,#fbfaff 290px,#fbfaff 100%)}
button,input{font:inherit}
.shell{max-width:1220px;margin:0 auto;padding:28px 28px 48px}
.topbar{display:flex;align-items:center;justify-content:space-between;padding-bottom:27px;border-bottom:1px solid var(--line)}
.brand{display:flex;gap:12px;align-items:center}
.mark{width:38px;height:38px;border-radius:10px;background:var(--purple);display:grid;place-items:center;color:#fff;font-size:18px;box-shadow:0 6px 16px rgba(108,59,242,.22)}
.eyebrow,.kicker{font-size:10px;letter-spacing:.16em;color:var(--purple);font-weight:800}
.brand h1{font-size:20px;margin:2px 0 0;color:var(--text)}
.top-actions{display:flex;gap:10px}
.top-actions button,.card-actions button{border-radius:10px;padding:10px 14px;border:1px solid var(--line);font-weight:700;cursor:pointer;transition:.18s ease}
.ghost,.card-actions button{background:#fff;color:#514563}
.ghost:hover,.card-actions button:hover{border-color:#cfc0ed;background:var(--lavender-2);color:var(--purple-dark)}
.scan{background:var(--purple);color:#fff;border-color:var(--purple)!important;box-shadow:0 6px 16px rgba(108,59,242,.18)}
.scan:hover{background:var(--purple-dark);border-color:var(--purple-dark)!important;transform:translateY(-1px)}
.scan:disabled{opacity:.65;cursor:wait;transform:none}
.hero{display:grid;grid-template-columns:1.45fr .7fr;gap:70px;padding:58px 0 42px;align-items:end}
.pill{display:inline-flex;align-items:center;gap:8px;padding:7px 11px;border:1px solid #d8ccef;border-radius:999px;color:#65587a;font-size:12px;background:rgba(255,255,255,.72);box-shadow:0 4px 16px rgba(77,39,150,.04)}
.dot{width:7px;height:7px;background:var(--purple);border-radius:50%;box-shadow:0 0 0 4px rgba(108,59,242,.10)}
.hero h2{font-size:49px;line-height:1.04;letter-spacing:-.045em;margin:18px 0;max-width:760px;color:#21163a}
.hero h2 em{font-style:normal;color:var(--purple)}
.hero p{max-width:690px;font-size:17px;line-height:1.6;color:var(--muted);margin:0}
.control-card{background:rgba(255,255,255,.86);border:1px solid #ddd3ed;border-radius:16px;padding:18px;box-shadow:var(--shadow);backdrop-filter:blur(8px)}
.control-card label{display:flex;justify-content:space-between;font-size:12px;color:#65587a;margin:4px 0 10px}
.segmented{display:grid;grid-template-columns:repeat(3,1fr);background:#f2edf9;border:1px solid #e0d7ef;padding:3px;border-radius:10px;margin-bottom:18px}
.segmented button{background:transparent;border:0;color:#847991;border-radius:7px;padding:8px;cursor:pointer;font-size:12px;font-weight:700}
.segmented .active{background:#fff;color:var(--purple-dark);box-shadow:0 2px 8px rgba(77,39,150,.10)}
input[type=range]{width:100%;accent-color:var(--purple)}
.fineprint{font-size:11px;color:#8a8098;margin-top:12px;line-height:1.5}
.stats{display:grid;grid-template-columns:repeat(4,1fr);border:1px solid var(--line);border-radius:14px;overflow:hidden;background:#fff;box-shadow:0 8px 30px rgba(77,39,150,.05)}
.stats div{padding:18px 20px;border-right:1px solid var(--line)}
.stats div:last-child{border-right:0}
.stats span{display:block;font-size:11px;color:#8c8199;margin-bottom:5px}
.stats strong{font-size:24px;color:var(--text)}
.stats strong.mode{font-size:14px;text-transform:uppercase;color:var(--purple)}
.section-head{display:flex;align-items:end;justify-content:space-between;padding:44px 2px 16px}
.section-head h3{font-size:24px;margin:6px 0 0;color:var(--text)}
.updated{font-size:11px;color:#92879e}
.feed{display:flex;flex-direction:column;gap:12px}
.signal-card{display:grid;grid-template-columns:100px 1fr 110px;background:#fff;border:1px solid var(--line);border-radius:16px;overflow:hidden;box-shadow:0 8px 28px rgba(77,39,150,.045)}
.signal-card:hover{border-color:#d5c7eb;box-shadow:0 12px 34px rgba(77,39,150,.075)}
.score-col{padding:24px 16px;border-right:1px solid var(--line);display:flex;flex-direction:column;align-items:center;gap:10px;background:#fcfaff}
.score-ring{width:68px;height:68px;border-radius:50%;border:1px solid #cfc0ed;background:var(--lavender-2);display:flex;align-items:center;justify-content:center;flex-direction:column;color:var(--purple-dark)}
.score-ring strong{font-size:23px;line-height:1}
.score-ring span{font-size:9px;color:#9185a0}
.heat{font-size:10px;font-weight:800;color:var(--purple);text-transform:uppercase;letter-spacing:.08em}
.content-col{padding:22px 24px}
.company-row{display:flex;align-items:center;gap:10px}
.company-avatar{height:37px;width:37px;border-radius:9px;background:var(--lavender);border:1px solid #d9ccef;display:grid;place-items:center;font-weight:800;color:var(--purple-dark)}
.company-row h4{margin:0;font-size:17px;color:var(--text)}
.company-row span{font-size:11px;color:#897d97}
.tag{margin-left:auto;padding:6px 9px;border-radius:999px;background:var(--lavender-2);color:#67567f!important;border:1px solid #dfd5ee;font-size:10px!important;font-weight:700}
.signal-copy{font-size:14px;line-height:1.5;color:#43364f;margin:16px 0}
.two-col{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.insight{padding:12px 13px;background:#faf8fd;border:1px solid #ebe5f2;border-radius:10px}
.insight span{font-size:9px;color:#857691;letter-spacing:.12em;font-weight:800}
.insight p{font-size:12.5px;line-height:1.5;color:#655a70;margin:6px 0 0}
.insight.accent{border-color:var(--yellow-line);background:linear-gradient(180deg,#fff9cf,#fffdf0)}
.insight.accent span{color:#765a00}
.insight.accent p{color:#4b3e22}
.meta-row{display:grid;grid-template-columns:1.5fr .7fr .8fr;gap:15px;margin-top:14px}
.meta-row span{display:block;font-size:9px;text-transform:uppercase;letter-spacing:.1em;color:#9a8ea5;margin-bottom:4px}
.meta-row strong,.meta-row a{font-size:11px;color:#6c6077;text-decoration:none}
.meta-row a{color:var(--purple)}
.meta-row a:hover{color:var(--purple-dark);text-decoration:underline}
.card-actions{border-left:1px solid var(--line);display:flex;flex-direction:column;justify-content:center;gap:8px;padding:16px;background:#fcfbfe}
.card-actions button{font-size:11px;padding:9px}
.empty{padding:50px;text-align:center;color:var(--muted);background:#fff;border:1px dashed #d8ccef;border-radius:14px}
footer{display:flex;justify-content:space-between;align-items:center;color:#968b9f;font-size:11px;padding:32px 2px 0}
footer div{color:var(--purple-dark);font-weight:700}
.warning{display:none;margin:12px 0 0;padding:10px 12px;border-radius:10px;background:#fff8d7;border:1px solid #ead675;color:#6c5717;font-size:12px}
@media(max-width:900px){.hero{grid-template-columns:1fr;gap:28px}.hero h2{font-size:39px}.signal-card{grid-template-columns:82px 1fr}.card-actions{grid-column:1/-1;border-left:0;border-top:1px solid var(--line);flex-direction:row;justify-content:flex-end}.stats{grid-template-columns:1fr 1fr}}
@media(max-width:640px){.shell{padding:20px 14px 38px}.top-actions .ghost{display:none}.hero h2{font-size:33px}.signal-card{grid-template-columns:1fr}.score-col{border-right:0;border-bottom:1px solid var(--line);flex-direction:row}.two-col,.meta-row{grid-template-columns:1fr}.tag{display:none}}
</style>
</head>
<body>
<main><div class="shell">
<header class="topbar"><div class="brand"><div class="mark">✦</div><div><div class="eyebrow">BUILT FOR STARBRIDGE</div><h1>Signal Radar</h1></div></div><div class="top-actions"><button class="ghost" id="exportBtn">Export CSV</button><button class="scan" id="scanBtn">Run live scan</button></div></header>
<section class="hero"><div><div class="pill"><span class="dot"></span> Public-sector GTM expansion monitor</div><h2>Find the companies building<br>public-sector sales teams <em>right now.</em></h2><p>Detect fresh SLED, government and higher-ed expansion signals — then turn each one into a clear reason for Starbridge to reach out.</p></div><div class="control-card"><label>Signal window</label><div class="segmented" id="rangeButtons"><button data-range="week">7 days</button><button class="active" data-range="month">30 days</button><button data-range="year">1 year</button></div><label>Minimum intent score <strong id="minLabel">85</strong></label><input id="minScore" type="range" min="75" max="95" value="85"><div class="fineprint">Live scan searches the public web and ranks only evidence-backed vendor expansion signals.</div><div class="warning" id="warning"></div></div></section>
<section class="stats"><div><span>Sources scanned</span><strong id="scanned">137</strong></div><div><span>High-intent companies</span><strong id="count">0</strong></div><div><span>Average score</span><strong id="avg">—</strong></div><div><span>Mode</span><strong class="mode" id="mode">preview</strong></div></section>
<section class="section-head"><div><span class="kicker">FRESH SIGNALS</span><h3>Who Starbridge should look at next</h3></div><span class="updated" id="updated">Updated Preview data</span></section>
<section class="feed" id="feed"></section>
<footer><div>✦ Signal Radar</div><span>Concept built for Starbridge · public-web signals only</span></footer>
</div></main>
<script>
const initialSignals = __DEMO__;
let signals = initialSignals;
let range = 'month';
let minimum = 85;
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function scoreLabel(score){return score>=95?'Hot':score>=85?'High intent':'Watch'}
function filtered(){return [...signals].filter(s=>Number(s.score)>=minimum).sort((a,b)=>b.score-a.score)}
function render(){const rows=filtered();document.getElementById('count').textContent=rows.length;document.getElementById('avg').textContent=rows.length?Math.round(rows.reduce((a,b)=>a+Number(b.score),0)/rows.length):'—';document.getElementById('feed').innerHTML=rows.length?rows.map((s,i)=>`<article class="signal-card"><div class="score-col"><div class="score-ring"><strong>${esc(s.score)}</strong><span>/100</span></div><div class="heat">${scoreLabel(Number(s.score))}</div></div><div class="content-col"><div class="company-row"><div class="company-avatar">${esc((s.company||'?').slice(0,1).toUpperCase())}</div><div><h4>${esc(s.company)}</h4><span>${esc(s.domain)}</span></div><div class="tag">${esc(s.signal_type)}</div></div><div class="signal-copy">${esc(s.signal)}</div><div class="two-col"><div class="insight"><span>WHY NOW</span><p>${esc(s.why_now)}</p></div><div class="insight accent"><span>STARBRIDGE ANGLE</span><p>${esc(s.starbridge_angle)}</p></div></div><div class="meta-row"><div><span>Target</span><strong>${esc(s.target_persona)}</strong></div><div><span>Signal date</span><strong>${esc(s.signal_date||'Recent')}</strong></div><div><span>Evidence</span><a href="${esc(s.source_url)}" target="_blank" rel="noreferrer">${esc(s.source_name)} ↗</a></div></div></div><div class="card-actions"><button onclick="copyText(${i},'angle',this)">Copy angle</button><button onclick="copyText(${i},'brief',this)">Copy brief</button></div></article>`).join(''):'<div class="empty">No signals above this score. Lower the threshold or run a wider scan.</div>'}
async function copyText(i,type,btn){const s=filtered()[i];const text=type==='angle'?s.starbridge_angle:`${s.company}\nSignal: ${s.signal}\nWhy now: ${s.why_now}\nAngle: ${s.starbridge_angle}\nSource: ${s.source_url}`;await navigator.clipboard.writeText(text);const old=btn.textContent;btn.textContent='Copied';setTimeout(()=>btn.textContent=old,1200)}
async function runScan(){const btn=document.getElementById('scanBtn'),warn=document.getElementById('warning');btn.disabled=true;btn.textContent='Scanning the market…';warn.style.display='none';try{const res=await fetch('/scan',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({range})});const data=await res.json();signals=data.signals||[];document.getElementById('mode').textContent=data.mode||'live';document.getElementById('scanned').textContent=data.scanned??0;document.getElementById('updated').textContent='Updated '+new Date(data.generated_at||Date.now()).toLocaleString();if(data.warning){warn.textContent=data.warning;warn.style.display='block'}render()}catch(e){warn.textContent='Scan failed: '+e.message;warn.style.display='block'}finally{btn.disabled=false;btn.textContent='Run live scan'}}
function exportCSV(){const rows=filtered();const headers=['Company','Domain','Score','Signal Type','Signal','Signal Date','Why Now','Starbridge Angle','Target Persona','Source URL'];const vals=rows.map(s=>[s.company,s.domain,s.score,s.signal_type,s.signal,s.signal_date,s.why_now,s.starbridge_angle,s.target_persona,s.source_url]);const q=v=>'"'+String(v??'').replaceAll('"','""')+'"';const csv=[headers,...vals].map(r=>r.map(q).join(',')).join('\n');const blob=new Blob([csv],{type:'text/csv'});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download='starbridge-signal-radar.csv';a.click();URL.revokeObjectURL(url)}
document.querySelectorAll('[data-range]').forEach(b=>b.addEventListener('click',()=>{document.querySelectorAll('[data-range]').forEach(x=>x.classList.remove('active'));b.classList.add('active');range=b.dataset.range}));document.getElementById('minScore').addEventListener('input',e=>{minimum=Number(e.target.value);document.getElementById('minLabel').textContent=minimum;render()});document.getElementById('scanBtn').addEventListener('click',runScan);document.getElementById('exportBtn').addEventListener('click',exportCSV);render();
</script>
</body></html>'''


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _domain_from_url(url):
    try:
        host = urlparse(url).netloc.lower().replace("www.", "")
        return host
    except Exception:
        return ""


def tavily_search(query, time_range):
    key = os.environ.get("TAVILY_API_KEY")
    resp = requests.post(
        "https://api.tavily.com/search",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json={
            "query": query,
            "search_depth": "basic",
            "topic": "general",
            "time_range": time_range,
            "country": "united states",
            "max_results": 8,
            "include_answer": False,
            "include_raw_content": False,
        },
        timeout=20,
    )
    resp.raise_for_status()
    return resp.json().get("results", [])


def extract_output_text(data):
    if isinstance(data.get("output_text"), str):
        return data["output_text"]
    chunks = []
    for item in data.get("output", []):
        if item.get("type") != "message":
            continue
        for content in item.get("content", []):
            if content.get("type") == "output_text" and isinstance(content.get("text"), str):
                chunks.append(content["text"])
    return "\n".join(chunks)


def classify_with_openai(results, time_range):
    candidates = []
    for i, r in enumerate(results[:40], start=1):
        if not r.get("url") or not r.get("title"):
            continue
        candidates.append({
            "id": i,
            "title": r.get("title", ""),
            "url": r.get("url", ""),
            "snippet": r.get("content", ""),
        })

    schema = {
        "type": "object",
        "properties": {
            "signals": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "company": {"type": "string"},
                        "domain": {"type": "string"},
                        "signal_type": {"type": "string"},
                        "signal": {"type": "string"},
                        "signal_date": {"type": "string"},
                        "score": {"type": "integer", "minimum": 0, "maximum": 100},
                        "why_now": {"type": "string"},
                        "starbridge_angle": {"type": "string"},
                        "target_persona": {"type": "string"},
                        "source_url": {"type": "string"},
                        "source_name": {"type": "string"},
                    },
                    "required": ["company", "domain", "signal_type", "signal", "signal_date", "score", "why_now", "starbridge_angle", "target_persona", "source_url", "source_name"],
                    "additionalProperties": False,
                },
            }
        },
        "required": ["signals"],
        "additionalProperties": False,
    }

    prompt = f"""You are a GTM intelligence analyst working for Starbridge, which sells AI sales intelligence to companies selling into U.S. state/local government, K-12, and higher education.

Analyze the search results below and identify companies that are CURRENTLY investing in public-sector GTM. Strong signals include: multiple SLED/public-sector sales openings, a new public-sector sales leader, dedicated state/local or higher-ed expansion, or an explicit public-sector go-to-market buildout.

Rules:
- Only include B2B vendors that plausibly sell products/services into U.S. government or education.
- Exclude government agencies, schools, recruiting firms, job boards, Starbridge itself, and generic articles.
- Use only evidence in the supplied results. Never invent a company, date, role, or URL.
- source_url MUST be copied exactly from one supplied candidate URL.
- Prefer signals inside the requested {time_range} window.
- Dedupe companies. If several results support one company, summarize the strongest signal.
- Return at most 12 companies, sorted highest score first.

Scoring:
95-100: multiple public-sector sales hires or explicit major GTM expansion.
85-94: fresh dedicated SLED/public-sector/higher-ed seller or sales leadership hire.
75-84: strong but less direct expansion signal.
Below 75: omit.

For each result, explain the timing in plain English and give a concise Starbridge sales angle. Target persona should be the likely economic/functional buyer at the vendor (for example CRO, VP Public Sector, Head of SLED Sales), not the government buyer.

Search candidates:\n{json.dumps(candidates, indent=2)}"""

    resp = requests.post(
        "https://api.openai.com/v1/responses",
        headers={
            "Authorization": f"Bearer {os.environ.get('OPENAI_API_KEY')}",
            "Content-Type": "application/json",
        },
        json={
            "model": os.environ.get("OPENAI_MODEL", "gpt-5.6-luna"),
            "input": prompt,
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": "public_sector_gtm_signals",
                    "strict": True,
                    "schema": schema,
                }
            },
        },
        timeout=60,
    )
    if not resp.ok:
        raise RuntimeError(f"OpenAI error {resp.status_code}: {resp.text[:300]}")
    text = extract_output_text(resp.json())
    parsed = json.loads(text)
    return parsed.get("signals", [])


@app.get("/")
def home():
    page = HTML.replace("__DEMO__", json.dumps(DEMO_SIGNALS).replace("</", "<\\/"))
    return Response(page, mimetype="text/html")


@app.post("/scan")
def scan():
    body = request.get_json(silent=True) or {}
    time_range = body.get("range", "month")
    if time_range not in {"week", "month", "year"}:
        time_range = "month"

    if body.get("demo") is True or not os.environ.get("TAVILY_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        return jsonify({"mode": "demo", "scanned": 137, "signals": DEMO_SIGNALS, "generated_at": _now_iso()})

    try:
        raw = []
        for query in QUERIES:
            raw.extend(tavily_search(query, time_range))

        seen = set()
        unique = []
        for r in raw:
            url = r.get("url")
            if url and url not in seen:
                seen.add(url)
                unique.append(r)

        signals = classify_with_openai(unique, time_range)
        return jsonify({"mode": "live", "scanned": len(unique), "signals": signals, "generated_at": _now_iso()})
    except Exception as exc:
        return jsonify({
            "mode": "fallback",
            "scanned": 0,
            "signals": DEMO_SIGNALS,
            "generated_at": _now_iso(),
            "warning": f"Live scan failed; showing demo results. {str(exc)[:240]}",
        })


@app.get("/health")
def health():
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "3000")))
