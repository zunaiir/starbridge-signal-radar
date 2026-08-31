import os
import json
from datetime import datetime, timezone, timedelta
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from flask import Flask, jsonify, request, Response

app = Flask(__name__)

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
<section class="stats"><div><span>Sources scanned</span><strong id="scanned">0</strong></div><div><span>High-intent companies</span><strong id="count">0</strong></div><div><span>Average score</span><strong id="avg">—</strong></div><div><span>Mode</span><strong class="mode" id="mode">ready</strong></div></section>
<section class="section-head"><div><span class="kicker">FRESH SIGNALS</span><h3>Who Starbridge should look at next</h3></div><span class="updated" id="updated">Not scanned yet</span></section>
<section class="feed" id="feed"></section>
<footer><div>✦ Signal Radar</div><span>Concept built for Starbridge · public-web signals only</span></footer>
</div></main>
<script>
const initialSignals = [];
let signals = initialSignals;
let range = 'month';
let minimum = 85;
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function scoreLabel(score){return score>=95?'Hot':score>=85?'High intent':'Watch'}
function filtered(){return [...signals].filter(s=>Number(s.score)>=minimum).sort((a,b)=>b.score-a.score)}
function render(){const rows=filtered();document.getElementById('count').textContent=rows.length;document.getElementById('avg').textContent=rows.length?Math.round(rows.reduce((a,b)=>a+Number(b.score),0)/rows.length):'—';document.getElementById('feed').innerHTML=rows.length?rows.map((s,i)=>`<article class="signal-card"><div class="score-col"><div class="score-ring"><strong>${esc(s.score)}</strong><span>/100</span></div><div class="heat">${scoreLabel(Number(s.score))}</div></div><div class="content-col"><div class="company-row"><div class="company-avatar">${esc((s.company||'?').slice(0,1).toUpperCase())}</div><div><h4>${esc(s.company)}</h4><span>${esc(s.domain)}</span></div><div class="tag">${esc(s.signal_type)}</div></div><div class="signal-copy">${esc(s.signal)}</div><div class="two-col"><div class="insight"><span>WHY NOW</span><p>${esc(s.why_now)}</p></div><div class="insight accent"><span>STARBRIDGE ANGLE</span><p>${esc(s.starbridge_angle)}</p></div></div><div class="meta-row"><div><span>Target</span><strong>${esc(s.target_persona)}</strong></div><div><span>Signal date</span><strong>${esc(s.signal_date||'Recent')}</strong></div><div><span>Evidence</span><a href="${esc(s.source_url)}" target="_blank" rel="noreferrer">${esc(s.source_name)} ↗</a></div></div></div><div class="card-actions"><button onclick="copyText(${i},'angle',this)">Copy angle</button><button onclick="copyText(${i},'brief',this)">Copy brief</button></div></article>`).join(''):'<div class="empty">No live results yet. Click <strong>Run live scan</strong> to search the web now.</div>'}
async function copyText(i,type,btn){const s=filtered()[i];const text=type==='angle'?s.starbridge_angle:`${s.company}\nSignal: ${s.signal}\nWhy now: ${s.why_now}\nAngle: ${s.starbridge_angle}\nSource: ${s.source_url}`;await navigator.clipboard.writeText(text);const old=btn.textContent;btn.textContent='Copied';setTimeout(()=>btn.textContent=old,1200)}
async function runScan(){const btn=document.getElementById('scanBtn'),warn=document.getElementById('warning');btn.disabled=true;btn.textContent='Scanning the market…';warn.style.display='none';try{const res=await fetch('/scan',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({range})});const data=await res.json();if(!res.ok){throw new Error(data.error||data.warning||('HTTP '+res.status))}signals=data.signals||[];document.getElementById('mode').textContent=data.mode||'live';document.getElementById('scanned').textContent=data.scanned??0;document.getElementById('updated').textContent='Updated '+new Date(data.generated_at||Date.now()).toLocaleString();if(data.warning){warn.textContent=data.warning;warn.style.display='block'}render()}catch(e){signals=[];document.getElementById('mode').textContent='error';document.getElementById('scanned').textContent='0';warn.textContent='Live scan failed: '+e.message;warn.style.display='block';render()}finally{btn.disabled=false;btn.textContent='Run live scan'}}
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


def _window_dates(time_range):
    now = datetime.now(timezone.utc)
    days = {"week": 7, "month": 30, "year": 365}[time_range]
    cutoff = now - timedelta(days=days)
    return now.date().isoformat(), cutoff.date().isoformat(), days


def search_tavily(time_range):
    """Search the live public web for public-sector GTM expansion signals."""
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        raise RuntimeError("TAVILY_API_KEY is missing in Vercel.")

    tavily_range = {"week": "week", "month": "month", "year": "year"}[time_range]

    def run_query(query):
        resp = requests.post(
            "https://api.tavily.com/search",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "query": query,
                "search_depth": "basic",
                "topic": "general",
                "time_range": tavily_range,
                "max_results": 10,
                "include_answer": False,
                "include_raw_content": False,
                "country": "united states",
            },
            timeout=25,
        )
        if not resp.ok:
            raise RuntimeError(f"Tavily API {resp.status_code} for {query}: {resp.text[:300]}")
        payload = resp.json()
        return query, payload.get("results", [])

    all_results = []
    seen_urls = set()

    # Run all discovery queries in parallel so a live scan stays fast on Vercel.
    with ThreadPoolExecutor(max_workers=len(QUERIES)) as pool:
        futures = [pool.submit(run_query, q) for q in QUERIES]
        for future in as_completed(futures):
            query, items = future.result()
            for item in items:
                url = (item.get("url") or "").strip()
                if not url or url in seen_urls:
                    continue
                seen_urls.add(url)
                all_results.append({
                    "query": query,
                    "title": item.get("title", ""),
                    "url": url,
                    "content": item.get("content", ""),
                    "relevance": item.get("score", 0),
                })

    all_results.sort(key=lambda x: float(x.get("relevance") or 0), reverse=True)
    return all_results[:60]


def classify_with_openai(results, time_range):
    """Turn Tavily search results into a ranked Starbridge prospect feed."""
    today, cutoff, days = _window_dates(time_range)

    if not results:
        return []

    # Keep enough context to be useful without making the LLM call huge.
    source_pack = []
    valid_urls = set()
    for idx, item in enumerate(results[:50], start=1):
        valid_urls.add(item["url"])
        source_pack.append(
            f"SOURCE {idx}\n"
            f"Search query: {item['query']}\n"
            f"Title: {item['title']}\n"
            f"URL: {item['url']}\n"
            f"Search relevance: {item['relevance']}\n"
            f"Snippet: {item['content'][:1200]}"
        )

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
                    "required": [
                        "company", "domain", "signal_type", "signal", "signal_date",
                        "score", "why_now", "starbridge_angle", "target_persona",
                        "source_url", "source_name"
                    ],
                    "additionalProperties": False,
                },
            }
        },
        "required": ["signals"],
        "additionalProperties": False,
    }

    prompt = f"""You are the prospect-scoring layer for Starbridge Signal Radar.

TODAY: {today}
SCAN WINDOW: {cutoff} through {today} ({days} days)

Starbridge sells AI sales intelligence to B2B vendors that sell into U.S. state/local government, K-12, and higher education.

Tavily has already searched the live web. Your ONLY job is to analyze the search results below and identify companies showing credible, recent evidence that they are investing in or expanding public-sector GTM.

QUALIFY:
- B2B software/services vendors that plausibly sell to U.S. government, K-12, or higher education.
- Fresh signals such as SLED/public-sector AE hiring, multiple public-sector sales openings, a new public-sector leader, a new government/education vertical, or explicit public-sector expansion.

EXCLUDE:
- Government agencies, schools/universities themselves, recruiters/staffing firms, generic articles, Starbridge, and companies where the public-sector angle is speculative.
- Sources that do not actually support the claimed signal.

EVIDENCE RULES:
- You may ONLY use URLs contained in the provided Tavily results.
- source_url MUST exactly match one of those URLs.
- Never invent a company, role, URL, or date.
- If the snippet does not contain an exact posting/publication date, use \"Current\" for signal_date rather than inventing one.
- Prefer official company career pages/announcements when available; otherwise reputable job boards are fine.
- Dedupe companies and keep only the strongest signal per company.

SCORING:
95-100 = multiple fresh public-sector hires, leadership + hiring, or obvious major GTM buildout.
90-94 = strong dedicated SLED/public-sector/higher-ed expansion signal.
85-89 = credible dedicated public-sector sales investment.
Below 85 = omit.

OUTPUT:
Return up to 12 companies sorted by score descending.
Keep every field concise and sales-ready.
why_now = the likely GTM problem created by the signal.
starbridge_angle = the specific reason Starbridge is relevant now.
target_persona = likely buyer at the vendor (CRO, VP Public Sector, Head of SLED Sales, etc.).

TAVILY RESULTS:\n\n""" + "\n\n---\n\n".join(source_pack)

    resp = requests.post(
        "https://api.openai.com/v1/responses",
        headers={
            "Authorization": f"Bearer {os.environ.get('OPENAI_API_KEY')}",
            "Content-Type": "application/json",
        },
        json={
            "model": os.environ.get("OPENAI_MODEL", "gpt-5.6-luna"),
            "reasoning": {"effort": "low"},
            "input": prompt,
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": "starbridge_live_signals",
                    "strict": True,
                    "schema": schema,
                }
            },
        },
        timeout=120,
    )
    if not resp.ok:
        raise RuntimeError(f"OpenAI API {resp.status_code}: {resp.text[:500]}")

    data = resp.json()
    text = extract_output_text(data)
    if not text:
        raise RuntimeError("OpenAI returned no structured output.")

    parsed = json.loads(text)
    cleaned = []
    seen_companies = set()
    for signal in parsed.get("signals", []):
        company_key = (signal.get("company") or "").strip().lower()
        source_url = (signal.get("source_url") or "").strip()
        if not company_key or company_key in seen_companies:
            continue
        if source_url not in valid_urls:
            continue
        if int(signal.get("score", 0)) < 85:
            continue
        if not signal.get("domain"):
            signal["domain"] = _domain_from_url(source_url)
        seen_companies.add(company_key)
        cleaned.append(signal)

    cleaned.sort(key=lambda x: int(x.get("score", 0)), reverse=True)
    return cleaned[:12]


@app.get("/")
def home():
    return Response(HTML, mimetype="text/html")


@app.post("/scan")
def scan():
    body = request.get_json(silent=True) or {}
    time_range = body.get("range", "month")
    if time_range not in {"week", "month", "year"}:
        time_range = "month"

    missing = []
    if not os.environ.get("TAVILY_API_KEY"):
        missing.append("TAVILY_API_KEY")
    if not os.environ.get("OPENAI_API_KEY"):
        missing.append("OPENAI_API_KEY")
    if missing:
        return jsonify({
            "mode": "error",
            "error": "Missing Vercel environment variable(s): " + ", ".join(missing) + ". Add them under Settings → Environment Variables, then redeploy.",
            "generated_at": _now_iso(),
        }), 500

    try:
        search_results = search_tavily(time_range)
        signals = classify_with_openai(search_results, time_range)
        warning = None
        if not signals:
            warning = "The live scan completed but found no qualifying signals. Try a wider window."
        return jsonify({
            "mode": "live",
            "scanned": len(search_results),
            "signals": signals,
            "generated_at": _now_iso(),
            "warning": warning,
        })
    except Exception as exc:
        return jsonify({
            "mode": "error",
            "scanned": 0,
            "signals": [],
            "generated_at": _now_iso(),
            "error": str(exc)[:700],
        }), 500


@app.get("/health")
def health():
    return jsonify({
        "ok": True,
        "app_version": "live-tavily-v2",
        "tavily_configured": bool(os.environ.get("TAVILY_API_KEY")),
        "openai_configured": bool(os.environ.get("OPENAI_API_KEY")),
        "model": os.environ.get("OPENAI_MODEL", "gpt-5.6-luna"),
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "3000")))
