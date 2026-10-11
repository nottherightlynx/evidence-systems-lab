"""Deterministic governed assistant baseline; optional language model is NOT used.
Run: python -m assistant.ask --question 'Which sources are stale?'
After dbt build: python -m assistant.ask --question 'How many people engaged?'
"""
from pathlib import Path
import argparse,csv,json,re,datetime
ROOT=Path(__file__).resolve().parent.parent

def load_registry():
    # JSON is valid YAML; the .yml file intentionally remains stdlib-readable.
    return json.loads((ROOT/'assistant/metrics_registry.yml').read_text())

def retrieve(domain, role='public'):
    rules=[json.loads(line) for line in (ROOT/'assistant/rules.jsonl').read_text().splitlines() if line.strip()]
    return [r for r in rules if r['domain'] in (domain,'governance') and (r['access_class']=='public' or role=='reviewer')]

def query_duckdb(metric):
    try:
        import duckdb
    except ImportError as exc:
        raise RuntimeError('DuckDB is not installed. Activate .venv and install requirements from requirements.txt.') from exc
    dbpath=ROOT/'artifacts/lab.duckdb'
    if not dbpath.exists():
        raise RuntimeError('dbt output not found. Run dbt seed and dbt build first; do not make up a metric.')
    conn=duckdb.connect(str(dbpath),read_only=True)
    try:
        if metric=='unique_constituents':
            value=conn.execute("select count(distinct constituent_id) from fct_interaction where constituent_id is not null").fetchone()[0]
            unresolved=conn.execute("select count(*) from fct_interaction where constituent_id is null").fetchone()[0]
            return {'count':value,'unresolved_events':unresolved}
        if metric=='received_contributions':
            row=conn.execute("select count(*) as n, coalesce(sum(received_cash),0) from fct_contribution where status='received'").fetchone()
            refunds=conn.execute("select count(*) from fct_contribution where status='refunded'").fetchone()[0]
            return {'received_transactions':row[0],'received_cash':float(row[1]),'refund_transactions_separate':refunds}
        raise ValueError('Unrecognized approved metric')
    finally:
        conn.close()

def query_source_status():
    path=ROOT/'artifacts/source_observability.csv'
    if not path.exists():
        raise RuntimeError('Source observability missing. First run python -m orchestration.pipeline')
    with path.open(newline='',encoding='utf8') as f:rows=list(csv.DictReader(f))
    return {'sources':[{k:r[k] for k in ('source_id','status','kind','document_count')} for r in rows],
            'not_current_count':sum(r['status']!='CURRENT' for r in rows),
            'stale_count':sum(r['status']=='STALE' for r in rows),
            'not_fetched_count':sum(r['status']=='NOT_FETCHED_OFFLINE' for r in rows)}

def answer(q,role='public'):
    question=q.lower().strip()
    def refuse(reason):return {'answer':'Insufficient authorized evidence: '+reason,'metric_id':None,'cited_chunks':[],'review_required':True}
    if any(x in question for x in ('cause donations','caused contributions','prove causation','make someone donate')):
        return refuse('observed sequences do not establish causation')
    if any(x in question for x in ('restricted reviewer','private memo','sensitive note')) and role!='reviewer':
        return refuse('access restricted before retrieval')
    if re.search(r'\b(select|drop|delete|insert|update)\s+.+\b(from|table|into)\b',question):
        return refuse('raw SQL is not an approved interface')
    if any(x in question for x in ('last quarter','last month','last year','this month','this year','in 2025','in 2026','during 2026')):
        return refuse('this demo does not implement date filters; no unfiltered result substituted')
    if '2024 definition' in question or 'ignore the rules' in question:
        return refuse('requested rule override not authorized')
    matches=[]
    for key,entry in load_registry().items():
        if any(alias in question for alias in entry['aliases']):matches.append(key)
    if len(matches)!=1:return refuse('no unique approved metric found')
    key=matches[0]
    domain='jurisdiction' if key=='stale_sources' else 'supporter'
    rules=retrieve(domain,role)
    citations=[{'doc_id':r['doc_id'],'version':r['version'],'source_url':r['source_url']} for r in rules]
    try:
        outcome=query_source_status() if key=='stale_sources' else query_duckdb(key)
    except Exception as exc:
        return refuse(str(exc))
    return {'answer':outcome,'metric_id':key,'filters':{},
       'evaluated_at':datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat(),
       'data_as_of':('review source-observability retrieved_at values' if key=='stale_sources' else 'see input event timestamps; historical completeness not established'),
       'definition_version':load_registry()[key]['definition_version'],
       'cited_chunks':citations,'unresolved_count':outcome.get('unresolved_events',None),
       'limitations':('Synthetic data and demonstration metrics only. No causal or historical-completeness claims.'),
       'review_required':False}

def main():
    p=argparse.ArgumentParser();p.add_argument('--question',required=True);p.add_argument('--role',default='public',choices=['public','reviewer']);args=p.parse_args()
    print(json.dumps(answer(args.question,args.role),indent=2))
if __name__=='__main__':main()
