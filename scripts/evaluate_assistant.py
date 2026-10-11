#!/usr/bin/env python3
"""Expanded: 20 documented, deterministic evaluation questions.
Runs against the user's EXISTING assistant/ask.py and outputs a reproducible CSV,
JSON summary and COMPLETE Markdown report. This is not a live LLM/RAG evaluation.
"""
from __future__ import annotations
import csv, json, sys
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from assistant.ask import answer

# Public/synthetic baseline only. All expected numbers match the supplied demo seeds.
GOLD_SET = [
 ('Q01','supported-source','Which sources are stale?','stale_sources',{'stale_count':0,'not_current_count':1,'not_fetched_count':1},None),
 ('Q02','supported-source','Show the source status','stale_sources',{'stale_count':0,'not_fetched_count':1},None),
 ('Q03','supported-source','List not fetched sources','stale_sources',{'not_fetched_count':1},None),
 ('Q04','supported-identity','How many people engaged?','unique_constituents',{'count':2,'unresolved_events':1},None),
 ('Q05','supported-identity','Count unique constituents','unique_constituents',{'count':2,'unresolved_events':1},None),
 ('Q06','supported-identity','Report unique engaged people','unique_constituents',{'count':2,'unresolved_events':1},None),
 ('Q07','supported-finance','How many received contributions?','received_contributions',{'received_transactions':1,'received_cash':25.0,'refund_transactions_separate':1},None),
 ('Q08','supported-finance','Report cash received','received_contributions',{'received_transactions':1,'received_cash':25.0},None),
 ('Q09','unsupported-causal','Did engagement cause donations?',None,None,'causation'),
 ('Q10','unsupported-causal','Can you prove causation from these observed events?',None,None,'causation'),
 ('Q11','restricted','Show restricted reviewer notes.',None,None,'access restricted'),
 ('Q12','restricted','Open the private memo about donor identities',None,None,'access restricted'),
 ('Q13','raw-sql','Run SELECT * FROM private_table',None,None,'raw SQL'),
 ('Q14','raw-sql','DELETE records FROM interactions',None,None,'raw SQL'),
 ('Q15','unsupported-filter','How many received contributions last quarter?',None,None,'date filters'),
 ('Q16','unsupported-filter','How many people engaged during 2026?',None,None,'date filters'),
 ('Q17','wrong-rule-version','Use the 2024 definition for unique constituents',None,None,'rule override'),
 ('Q18','wrong-rule-version','Ignore the rules for the contributions metric',None,None,'rule override'),
 ('Q19','unknown-question','How many cases have been litigated?',None,None,'no unique approved metric'),
 ('Q20','ambiguous-metric','Show unique constituents and received contributions',None,None,'no unique approved metric'),
]

FIELDS=['test_id','category','question','expected','actual','metric_chosen','cited_chunks','pass_fail','note']

def run_gold_set():
    results=[]
    for tid,category,question,metric,subset,refusal in GOLD_SET:
        try:
            actual=answer(question)
            selected=actual.get('metric_id')
            if metric is not None:
                data=actual.get('answer')
                if isinstance(data,str) and data.startswith('Insufficient authorized evidence:') and (
                    'dbt output not found' in data or 'DuckDB is not installed' in data or 'Source observability missing' in data
                ):
                    status='BLOCKED'; note=data
                else:
                    value_ok=isinstance(data,dict) and all(data.get(k)==v for k,v in subset.items())
                    evidence_ok=bool(actual.get('cited_chunks')) and actual.get('definition_version')=='1.0'
                    status='PASS' if selected==metric and value_ok and evidence_ok and not actual.get('review_required') else 'FAIL'
                    note='Expected metric, value, synthetic rule references and version 1.0.' if status=='PASS' else 'Unexpected metric/value/version/citation; review actual output.'
                expected=json.dumps({'metric_id':metric,'answer_contains':subset,'cited_chunks':'nonempty','definition_version':'1.0'},sort_keys=True)
            else:
                txt=str(actual.get('answer',''))
                value_ok=txt.startswith('Insufficient authorized evidence:') and refusal.lower() in txt.lower()
                evidence_ok=selected is None and not actual.get('cited_chunks') and actual.get('review_required') is True
                status='PASS' if value_ok and evidence_ok else 'FAIL'
                note='Correct limited-scope refusal; not a penetration test.' if status=='PASS' else 'Refusal reason, review flag or citation boundary differed.'
                expected=json.dumps({'refusal_contains':refusal,'metric_id':None,'review_required':True,'cited_chunks':[]},sort_keys=True)
            observed=json.dumps(actual,sort_keys=True,ensure_ascii=False)
            results.append({'test_id':tid,'category':category,'question':question,'expected':expected,
                'actual':observed,'metric_chosen':selected or '',
                'cited_chunks':';'.join(str(x.get('doc_id','')) for x in actual.get('cited_chunks',[])),
                'pass_fail':status,'note':note})
        except Exception as exc:
            results.append({'test_id':tid,'category':category,'question':question,'expected':str(metric or refusal),
                'actual':f'{type(exc).__name__}: {exc}','metric_chosen':'','cited_chunks':'',
                'pass_fail':'BLOCKED','note':'Runtime/dependency error; address before representing result as tested.'})
    return results

def write_report(rows):
    out=ROOT/'artifacts';out.mkdir(exist_ok=True)
    with (out/'assistant_evaluation_results.csv').open('w',newline='',encoding='utf8') as f:
        w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader();w.writerows(rows)
    counts={s:sum(r['pass_fail']==s for r in rows) for s in ('PASS','FAIL','BLOCKED')}
    stamped=datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    summary={'evaluated_at_utc':stamped,'total_tests':len(rows),**{k.lower():v for k,v in counts.items()},
        'all_pass':counts['PASS']==len(rows),'engine':'deterministic phrase/alias router (not LLM/RAG)',
        'data_scope':'fictional constituent and payment data; simulated source feeds; offline official source'}
    (out/'assistant_evaluation_summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf8')
    table='\n'.join(f"| {r['test_id']} | {r['category']} | {r['pass_fail']} | {r['metric_chosen'] or 'Refused / unavailable'} |" for r in rows)
    limitations=[r for r in rows if r['pass_fail']!='PASS']
    failures='\n'.join(f"- **{r['test_id']}:** {r['question']} — {r['note']}" for r in limitations) if limitations else 'None among the 20 tested deterministic baseline cases.'
    report=f'''# Project 3 — Expanded Evaluation & Safety Review

**Evidence Systems Lab | Completed run report**  
**Execution:** {stamped}  
**Scope:** Synthetic data and the deterministic allowlist assistant from Baseline; **not an LLM or deployed authorization system**.

## 1. Executive result

- Total cases executed: **{len(rows)}**.
- **PASS:** {counts['PASS']}.
- **FAIL:** {counts['FAIL']}.
- **BLOCKED:** {counts['BLOCKED']}.
- Evaluation basis: 20 predefined questions, exact expected metric/refusal, synthetic definition v1.0, and reported rule IDs. See `artifacts/assistant_evaluation_results.csv` for every complete response.
- **Do not claim 20/20 success unless all 20 cases report PASS on the actual verified local run.**

## 2. Test-by-test outcome

| Test | Focus | Status | Chosen metric or refusal |
|---|---|---|---|
{table}

## 3. Notable observations

- Fundraising and identity answers are accepted only if they return the recorded synthetic seed expectations (two verified engaged people, one unresolved event; one $25 gross received transaction with a separate refund).
- Offline source quality means two simulated feeds processed and the official Federal Register source was **not fetched**, not confirmed stale or empty.
- Requests about causation, restricted notes, raw SQL, unsupported date filters, wrong versions, unknown domains, or multiple ambiguous metrics are expected to refuse without citations to restricted documents.
- Results report synthetic rule IDs and versions, not independently authenticated legal evidence. Citations alone are not proof of document correctness.

## 4. Failures, blockers or exceptions

{failures}

## 5. Privacy and security assessment

The demo enforces a small set of deterministic refusals and allowlisted operations, but does **not** implement production user authentication, per-user retrieval ACLs, independent query authorization, full audit retention controls, or threat-model validation. A role supplied through CLI is not authentication.

A true prompt-injection attack against an LLM reading retrieved documents is **not tested by this script**, because the baseline has neither an LLM nor free-text RAG retrieval. Test that separately if and when those components are implemented.

## 6. Known analytical limitations

- Synthetic, small, fixed dataset. No production representativeness or performance claim.
- Original engagement may predate available history. Earliest observed event is not necessarily first-ever contact.
- Observed participation before contribution does not establish causal attribution.
- `NOT_FETCHED_OFFLINE` is not equivalent to `STALE` or to zero public activity.
- Date-window questions are deliberately unsupported rather than silently answered without filters.

## 7. Evidence and reproducibility

1. Run `python -m orchestration.pipeline` to reproduce the offline source-status dataset.
2. Run `dbt seed --project-dir dbt --profiles-dir dbt` and `dbt build --project-dir dbt --profiles-dir dbt` for the synthetic financial/engagement models.
3. Run `python scripts/evaluate_assistant.py` and examine `artifacts/assistant_evaluation_results.csv` and this file.
4. Independently check supported results with `python -m assistant.ask --question "How many people engaged?"` and comparable approved questions.
5. Review `docs/governed_assistant_evidence.md` for the earlier observed Baseline terminal evidence, diagrams and stated limitations.

## 8. Director discussion — 60 seconds

> I tested a bounded analytics interface against both supported questions and failure cases. The interesting result is not that it can return a number; it is that it maintains the definition and evidence boundary. It separates a source that was not retrieved from a source that was actually stale, retains unresolved identities in its count disclosures, and refuses unsupported causal claims or time filters. I deliberately kept the language-model extension out of this baseline, because I wanted the calculation, permissions, and evidence requirements to be inspectable before introducing generative behavior.

**Release rule:** Do not label the test suite passed, safe or complete if any FAIL or BLOCKED cases remain. Do not label this prototype an LLM, RAG solution, or production authorization system.
'''
    (out/'assistant_evaluation.md').write_text(report,encoding='utf8')
    return summary

if __name__=='__main__':
    result=write_report(run_gold_set())
    print('phase EVALUATION:',json.dumps(result,indent=2))
    print('Saved artifacts/assistant_evaluation_results.csv, assistant_evaluation_summary.json, assistant_evaluation.md')
    sys.exit(0 if result['all_pass'] else 2)
