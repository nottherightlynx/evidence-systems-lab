"""Offline-reproducible normalized public-data files for Pages 6-7.
   Set FETCH_FEDERAL_REGISTER=1 to additionally ingest a bounded batch from the official API.
"""
from pathlib import Path
from datetime import datetime, timezone
import os, csv, json
from orchestration.sources import load_sources
from orchestration.normalize import normalize, validate, utc_now
ROOT=Path(__file__).resolve().parent.parent
FIELDS=['source_id','jurisdiction','document_id','title','published_at','retrieved_at','source_url','source_kind','content_hash']

def save_csv(path,rows,fields):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',newline='',encoding='utf8') as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)

def make_observability(rows,fetch_federal=False):
    report=[]
    for sid,juris,kind in [('SIMULATED_STATE_A','SIM-A','SIMULATED'),('SIMULATED_STATE_B','SIM-B','SIMULATED'),('FEDERAL_REGISTER','US','PUBLIC_OFFICIAL')]:
        records=[x for x in rows if x['source_id']==sid]
        report.append({'source_id':sid,'jurisdiction':juris,'kind':kind,'document_count':len(records),
                       'last_retrieved_at':max((x['retrieved_at'] for x in records),default=''),
                       'status':'CURRENT' if records else ('NOT_FETCHED_OFFLINE' if sid=='FEDERAL_REGISTER' and not fetch_federal else 'EMPTY'),
                       'coverage_note':'SIMULATED: only fixture records; not jurisdiction coverage' if kind=='SIMULATED' else
                       ('Not fetched in offline demo' if not fetch_federal else 'Bounded batch only; not a complete Federal Register corpus')})
    return report

def run_pipeline(fetch_federal=False):
    raw=load_sources(fetch_federal=fetch_federal)
    normalized=validate(normalize(raw))
    artifacts=ROOT/'artifacts'
    save_csv(artifacts/'normalized_documents.csv',normalized,FIELDS)
    report=make_observability(normalized,fetch_federal=fetch_federal)
    save_csv(artifacts/'source_observability.csv',report,['source_id','jurisdiction','kind','document_count','last_retrieved_at','status','coverage_note'])
    save_csv(artifacts/'public_review_queue.csv',normalized,FIELDS)
    return normalized,report
if __name__=='__main__':
    fetch=os.environ.get('FETCH_FEDERAL_REGISTER','0')=='1'
    docs,report=run_pipeline(fetch_federal=fetch)
    print(f'PASS: {len(docs)} normalized document records; {len(report)} source statuses')
    for row in report:print(row['source_id'],row['status'],row['document_count'])
    print('Saved artifacts/normalized_documents.csv, source_observability.csv, public_review_queue.csv')
