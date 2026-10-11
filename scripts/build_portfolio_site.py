#!/usr/bin/env python3
"""Portfolio: create a static, evidence-first portfolio with sanitized public material.
No remote API, telemetry, LLM or production credentials; Python stdlib only.
"""
from pathlib import Path
from datetime import datetime, timezone
import csv, html, json, shutil
ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'site';ART=ROOT/'artifacts';ASSETS=SITE/'assets'
SITE.mkdir(exist_ok=True);ASSETS.mkdir(exist_ok=True)

def esc(s):return html.escape(str(s),quote=True)

def evaluation():
    path=ART/'assistant_evaluation_summary.json'
    if not path.exists():
        return {'total_tests':20,'pass':0,'fail':0,'blocked':0,'not_run':20,'all_pass':False,'evaluated_at_utc':None,
            'status_label':'Not yet evaluated here'}
    s=json.loads(path.read_text())
    s['status_label']='20 / 20 checks passed on last run' if s.get('all_pass') else 'Partial evaluation — fix blockers before publishing as complete'
    return s

CASES=[
 {'id':'01','eyebrow':'DBT + SQL · CRM migration','title':'Preserving identity and financial meaning across systems',
  'short':'Reconcile constituents, engagement and contributions while retaining source keys and unmatched events.',
  'question':'What is lost when a CRM migration treats source IDs and financial stages as interchangeable?',
  'architecture':'Legacy/new CRM and event/donation seeds → staging → reviewed identity crosswalk → event and contribution facts → dbt tests → lifecycle mart.',
  'decisions':['Keep original source IDs while relating verified identities through a bridge.',
              'LEFT JOIN source events to the crosswalk for reconciliation, preserving unmatched interactions.',
              'Keep received cash, pledges and refunds as different observed financial facts.'],
  'evidence':['Four fictional interactions, three matched events and one unresolved identity.',
             'A duplicate event ID produced a dbt uniqueness-test failure; restoring the clean seed allowed the build to pass.',
             'Two verified engaged people, one unresolved engagement, one $25 received payment, a $100 pledge and a $25 refund are present in the synthetic baseline.'],
  'boundary':'Prototype uses fixed fictional identities, not inferred matches or real CRM constituent data.',
  'career':'CFLeads Salesforce investment/renewal logic, TLC donor reconciliation, NAACP LDF CRM integrations.'},
 {'id':'02','eyebrow':'PYTHON + DAGSTER · Public-source reliability','title':'Distinguishing missing data from missing events',
  'short':'Normalize inconsistent state-style feeds and expose freshness, schema changes and retrieval history.',
  'question':'If a jurisdiction returns no records, is the finding truly empty—or did ingestion fail?',
  'architecture':'Simulated State A/B feeds (+ optional official Federal Register metadata) → Python normalization → validation → source-status report → analyst review.',
  'decisions':['Keep source publication time distinct from retrieval time.',
              'Reject unexpected source-schema changes rather than silently discarding a jurisdiction.',
              'Label simulated sources as simulated and an unfetched official source as NOT_FETCHED_OFFLINE.'],
  'evidence':['An intentional State B field rename caused the normalizer to raise a ValueError.',
             'After fixture restoration: three normalized simulated records; State A=2 and State B=1.',
             'The official Federal Register was NOT_FETCHED_OFFLINE in the recorded offline run; a separate successful Dagster five-asset run was documented.'],
  'boundary':'Demonstrates source-quality handling, not comprehensive monitoring of real state legislation; the schema-failure example ran in the Python pipeline.',
  'career':'NCTE cross-state legislative monitoring and CFLeads geographic engagement reporting.'},
 {'id':'03','eyebrow':'GOVERNED QUERIES · Evidence boundary','title':'Answers that preserve approved definitions',
  'short':'A deterministic question interface routes to allowlisted metrics, reports rule versions, and refuses unsupported requests.',
  'question':'Can natural-language-like queries access useful analytical results without changing the rules behind them?',
  'architecture':'Question → alias-based metric selection → simulated rule filtering → approved DuckDB/CSV calculation → traceable result or refusal.',
  'decisions':['The interface does not invent its own financial definitions.',
              'Refuse unsupported causal, restricted, raw-SQL and date-filter requests.',
              'Distinguish synthetic rule references from verified public source citations.'],
  'evidence':['Recorded results: two engaged people plus one unresolved event, and a $25 receipt with a separate refund.',
             'The source-status answer reports zero stale feeds and one official feed not fetched.',
             'The deterministic suite recorded 20/20 checks passing, covering supported metrics and explicit refusals.'],
  'boundary':'Deterministic phrase router; no LLM, general RAG, true authentication, or production authorization implemented.',
  'career':'CFLeads Data Wiki, investor and program metric governance, responsible AI pilot design.'},
]

def render_case(c):
    lis=lambda ar:'\n'.join(f'<li>{esc(i)}</li>' for i in ar)
    return f'''<article class="case" id="project-{c['id']}">
 <div class="case-meta">{esc(c['eyebrow'])} <span>PROJECT {esc(c['id'])}</span></div>
 <h3>{esc(c['title'])}</h3><p class="case-short">{esc(c['short'])}</p>
 <p class="question">{esc(c['question'])}</p>
 <div class="case-detail"><div><h4>Technical flow</h4><p>{esc(c['architecture'])}</p></div>
 <div><h4>Engineering decisions</h4><ul>{lis(c['decisions'])}</ul></div></div>
 <details><summary>Open observed evidence and limitations</summary><div class="expanded"><h4>Evidence</h4><ul>{lis(c['evidence'])}</ul>
 <h4>What is not claimed</h4><p>{esc(c['boundary'])}</p><h4>Experience it connects to</h4><p>{esc(c['career'])}</p></div></details>
 </article>'''

def render_tests():
    path=ART/'assistant_evaluation_results.csv'
    if not path.exists():
        import sys
        sys.path.insert(0, str(ROOT/'scripts'))
        from evaluate_assistant import GOLD_SET
        entries='\n'.join(f'<tr><td>{esc(tid)}</td><td>{esc(category)}</td><td><span class="status blocked">PENDING</span></td></tr>' for tid,category,*_ in GOLD_SET)
        return '<p>The expanded evaluation set is prepared but has not yet been run on this installation.</p><div class="table-scroll"><table><caption>20 predefined cases — pending local execution</caption><thead><tr><th>ID</th><th>Question class</th><th>Result</th></tr></thead><tbody>'+entries+'</tbody></table></div>'
    with path.open(newline='',encoding='utf8') as f: rows=list(csv.DictReader(f))
    cells='\n'.join(f'<tr><td>{esc(r["test_id"])}</td><td>{esc(r["category"])}</td><td><span class="status {esc(r["pass_fail"].lower())}">{esc(r["pass_fail"])}</span></td></tr>' for r in rows)
    return f'<div class="table-scroll"><table><caption>20-question baseline evaluation — local execution, not a generative-AI penetration test</caption><thead><tr><th>ID</th><th>Question class</th><th>Result</th></tr></thead><tbody>{cells}</tbody></table></div>'

def render_site(summary):
    test_text=(f'{summary["pass"]} passed · {summary["fail"]} failed · {summary["blocked"]} blocked'
                if summary.get('evaluated_at_utc') else 'Evaluation not run in this copy')
    date=(summary.get('evaluated_at_utc') or 'Not yet run')
    content='\n'.join(render_case(c) for c in CASES)
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="Evidence-first portfolio of three synthetic-data analytics engineering case studies: CRM/dbt, public data/Dagster, and governed analytical questions.">
<title>Evidence Systems Lab — Analytics Engineering Portfolio</title><link rel="stylesheet" href="styles.css"></head>
<body><a class="skip" href="#main">Skip to content</a>
<header class="nav"><div class="wrap nav-inner"><a class="brand" href="#top"><span class="brand-mark">E/</span> EVIDENCE SYSTEMS LAB</a>
<nav aria-label="Main navigation"><a href="#projects">Projects</a><a href="#proof">Checks</a><a href="#method">Methods</a></nav></div></header>
<main id="main"><section class="hero wrap" id="top"><p class="overline">ANALYTICS ENGINEERING · TECHNICAL CASE STUDIES</p>
<h1>From source record<br>to <em>defensible answer.</em></h1>
<p class="intro">Three connected prototypes demonstrate how I approach identity reconciliation, observable data pipelines, and governed analytical access—grounded in experience spanning philanthropic infrastructure and legal advocacy data systems.</p>
<div class="hero-pills"><span>Python &amp; SQL</span><span>dbt + DuckDB</span><span>Dagster architecture</span><span>Governed analytics</span></div>
<div class="hero-rule"><strong>Scope:</strong> All demonstration constituent data and state feeds are fictional. The NLP prototype is deterministic; the local-LLM layer is proposed, not implemented.</div></section>
<section class="flow-section"><div class="wrap"><p class="overline">THE SHARED ENGINEERING QUESTION</p>
<h2>Can every number be traced?</h2><div class="flow-grid" aria-label="Data lineage flow">
<div><b>01</b><strong>Source</strong><small>Origin and retrieval</small></div><span aria-hidden="true">→</span>
<div><b>02</b><strong>Identity</strong><small>Verified relationships</small></div><span aria-hidden="true">→</span>
<div><b>03</b><strong>Model</strong><small>Tested definitions</small></div><span aria-hidden="true">→</span>
<div><b>04</b><strong>Answer</strong><small>Evidence + uncertainty</small></div></div></div></section>
<section class="projects wrap" id="projects"><p class="overline">THREE CONNECTED DEMONSTRATIONS</p><h2>Build the relationships. Test the boundaries.</h2>
{content}
</section>
<section class="proof-section" id="proof"><div class="wrap"><p class="overline">REPRODUCIBLE EVIDENCE</p><h2>Quality checks, including deliberate failure.</h2>
<p class="lead">Baseline recorded output confirmed approved query results and explicit refusals. The expanded evaluation suite records 20 predefined questions, expected metrics, cited-rule metadata and reasons for refusal.</p>
<div class="eval-bar"><div><strong>{esc(test_text)}</strong><small>{esc(summary['status_label'])}</small></div><div class="eval-date">Last expanded run<br>{esc(date)}</div></div>
{render_tests()}
<div class="media-pair"><figure><img src="assets/evidence_assistant_baseline_flow.png" loading="lazy" alt="Implemented assistant architecture: question routed through approved metric, permission and supported-operation checks to result or refusal"><figcaption>Implemented deterministic baseline. Rule retrieval is constrained in this demo.</figcaption></figure>
<figure><img src="assets/proposed_local_llm_architecture.png" loading="lazy" alt="Future design: natural-language question, locally hosted LLM, authorized retrieval, approved metric selection, validation, dbt DuckDB, evidence-backed response"><figcaption>Future proposal, <strong>not implemented</strong>: local inference and authorized document retrieval.</figcaption></figure></div>
</div></section>
<section class="method wrap" id="method"><p class="overline">METHOD AND LIMITATIONS</p><h2>What the experiments do—and don't—prove.</h2>
<div class="method-cols"><div><h3>Engineering approach</h3><p>Preserve source identifiers and unmatched records; declare event grain; distinguish financial statuses; monitor geographic data-source health; keep queries within documented metric definitions.</p></div>
<div><h3>Limits disclosed</h3><p>No employer data, real voter information, complete source coverage, causal attribution, production authorization or deployed LLM is represented. A local language model does not independently establish privacy compliance.</p></div>
<div><h3>Professional throughline</h3><p>CRM investment and program data at CFLeads, data systems at TLC and NAACP LDF, legislative and voter analytics at NCTE, and SQL/data modeling experience at Quicken/Rocket Mortgage.</p></div></div>
<div class="method-links"><a href="https://docs.getdbt.com/docs/build/data-tests" rel="noopener noreferrer" target="_blank">dbt testing documentation ↗</a><a href="https://docs.dagster.io/" rel="noopener noreferrer" target="_blank">Dagster documentation ↗</a><a href="https://www.federalregister.gov/developers/documentation/api/v1" rel="noopener noreferrer" target="_blank">Federal Register API ↗</a></div></section></main>
<footer><div class="wrap"><strong>EVIDENCE SYSTEMS LAB</strong><span>Static case-study prototype · No trackers · Synthetic demo data only</span></div></footer>
</body></html>'''

STYLE='''
:root{--ink:#132238;--muted:#52667a;--teal:#087e80;--mint:#d5f4ed;--line:#dce5e9;--pale:#f4f7fa;--navy:#0b182b}*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;color:var(--ink);font:16px/1.65 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:#fff}a{color:inherit}a:hover{color:var(--teal)}.wrap{max-width:1120px;margin:0 auto;padding:0 28px}.skip{position:absolute;left:-9999px;top:10px;background:#fff;padding:6px}.skip:focus{left:12px;z-index:99}.nav{border-bottom:1px solid var(--line);background:rgba(255,255,255,.96);position:sticky;top:0;z-index:50}.nav-inner{height:72px;display:flex;align-items:center;justify-content:space-between;gap:16px}.brand{text-decoration:none;font-size:.84rem;font-weight:800;letter-spacing:.09em}.brand-mark{background:var(--navy);color:#a5f6e5;border-radius:9px;padding:8px;margin-right:9px}.nav nav{display:flex;gap:25px}.nav nav a{text-decoration:none;font-size:.9rem}.hero{padding-top:92px;padding-bottom:80px}.overline{letter-spacing:.14em;color:var(--teal);font-size:.75rem;font-weight:800;text-transform:uppercase}.hero h1{max-width:860px;font-size:5.3rem;font-size:clamp(3.5rem,7vw,6.1rem);letter-spacing:-.063em;line-height:1.07;margin:18px 0 28px}.hero h1 em{color:var(--teal);font-style:normal}.intro{color:var(--muted);max-width:810px;font-size:1.27rem;line-height:1.65}.hero-pills{display:flex;flex-wrap:wrap;gap:10px;margin:30px 0}.hero-pills span{border:1px solid #b8dcd7;background:#effaf7;padding:6px 13px;border-radius:20px;font-weight:650;font-size:.82rem}.hero-rule{border-left:4px solid var(--teal);background:var(--pale);padding:14px 19px;max-width:810px;font-size:.88rem}.flow-section{background:var(--navy);color:white;padding:60px 0 74px}.flow-section h2{font-size:2.2rem}.flow-section .overline{color:#a5f6e5}.flow-grid{display:flex;align-items:stretch;gap:12px}.flow-grid div{border:1px solid #477b83;border-radius:15px;padding:24px;flex:1;display:flex;flex-direction:column;gap:3px;background:#142d41}.flow-grid div b{color:#b8f8e6;font-size:.75rem}.flow-grid div strong{font-size:1.15rem}.flow-grid div small{color:#c7d7e0}.flow-grid>span{display:flex;align-items:center;color:#a4d5cc;font-size:1.5rem}.projects{padding-top:92px;padding-bottom:90px}.projects h2,.proof-section h2,.method h2{font-size:2.6rem;font-size:clamp(2rem,3vw,3rem);letter-spacing:-.03em;line-height:1.2;margin-top:9px;margin-bottom:32px}.case{padding:42px 0;border-top:1px solid var(--line)}.case-meta{display:flex;justify-content:space-between;gap:8px;color:var(--teal);font-weight:800;font-size:.78rem;letter-spacing:.08em}.case-meta span{color:var(--muted)}.case h3{font-size:2.04rem;letter-spacing:-.035em;line-height:1.2;margin:18px 0 10px}.case-short{font-size:1.08rem;color:var(--muted);margin:0}.question{border-left:3px solid var(--teal);padding-left:16px;margin:20px 0;font-weight:600}.case-detail{display:grid;grid-template-columns:1fr 1fr;gap:32px;margin:20px 0}.case-detail h4,.expanded h4{margin-bottom:6px}.case-detail p,.case-detail li,.expanded{color:var(--muted)}.case details{border:1px solid var(--line);border-radius:9px;overflow:hidden}.case summary{cursor:pointer;padding:14px 18px;font-weight:750;background:#f8fbfc}.expanded{padding:10px 20px 18px}.proof-section{padding:80px 0 90px;background:#f3f7fa}.lead{max-width:850px;color:var(--muted)}.eval-bar{display:flex;justify-content:space-between;gap:15px;background:white;border:1px solid var(--line);border-radius:14px;padding:22px;margin:28px 0}.eval-bar strong{font-size:1.17rem}.eval-bar small{display:block;color:var(--muted)}.eval-date{text-align:right;font-size:.8rem;color:var(--muted)}.table-scroll{overflow-x:auto;background:white;border-radius:12px;border:1px solid var(--line)}table{border-collapse:collapse;width:100%;font-size:.91rem}caption{text-align:left;padding:16px;color:var(--muted)}th,td{text-align:left;padding:9px 17px;border-top:1px solid var(--line)}th{background:#e9f0f3}.status{font-weight:800;font-size:.75rem}.status.pass{color:#06725d}.status.blocked{color:#996309}.status.fail{color:#ae3939}.media-pair{display:grid;grid-template-columns:1fr 1fr;gap:22px;margin-top:40px}.media-pair figure{margin:0;border:1px solid var(--line);border-radius:12px;background:white;padding:20px}.media-pair img{display:block;width:100%;max-height:400px;object-fit:contain}.media-pair figcaption{font-size:.83rem;color:var(--muted);padding-top:12px}.method{padding-top:90px;padding-bottom:90px}.method-cols{display:grid;grid-template-columns:repeat(3,1fr);gap:34px}.method h3{font-size:1.15rem}.method-cols p{color:var(--muted)}.method-links{display:flex;flex-wrap:wrap;gap:15px;margin-top:30px}.method-links a{font-size:.86rem;color:var(--teal)}footer{background:#0a1a2b;color:#d4e1e7;padding:32px 0;font-size:.8rem}footer .wrap{display:flex;justify-content:space-between;gap:15px}@media(max-width:740px){.nav-inner{height:auto;min-height:68px;flex-wrap:wrap;padding-top:15px;padding-bottom:15px}.nav nav{gap:15px}.hero{padding-top:64px}.hero h1{font-size:3.3rem}.flow-grid{flex-direction:column}.flow-grid>span{justify-content:center;transform:rotate(90deg)}.case-detail,.media-pair,.method-cols{grid-template-columns:1fr}.eval-bar{flex-direction:column}.eval-date{text-align:left}footer .wrap{flex-direction:column}}@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}'''

def main():
    for filename in ('evidence_assistant_baseline_flow.png','proposed_local_llm_architecture.png'):
        source=ART/'images'/filename
        if source.exists():shutil.copy2(source,ASSETS/filename)
        elif not (ASSETS/filename).exists():raise SystemExit(f'Missing {source}; unzip your completed Project 3 evidence images first.')
    summary=evaluation()
    (SITE/'projects.json').write_text(json.dumps({'summary':summary,'projects':CASES},indent=2,ensure_ascii=False)+'\n',encoding='utf8')
    (SITE/'styles.css').write_text(STYLE,encoding='utf8')
    (SITE/'index.html').write_text(render_site(summary),encoding='utf8')
    print('PASS: built static portfolio at site/index.html; site/projects.json and diagram assets synced')
    print('EVALUATION STATUS:',summary['status_label'])
    print('PREVIEW: python -m http.server 8000 --directory site (then http://localhost:8000)')

if __name__=='__main__':main()
