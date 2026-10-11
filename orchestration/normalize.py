"""Normalize heterogeneous records, reject unexpected schemas, preserve provenance."""
import hashlib, json
from datetime import datetime, timezone

def utc_now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')

def normalize(raw_feeds):
    now=utc_now(); output=[]
    for feed in raw_feeds:
        name=feed['filename']; data=feed['payload']
        if name=='state_A.json':
            source='SIMULATED_STATE_A'; jurisdiction='SIM-A'
            for item in data['records']:
                for key in ('id','title','published_at','url'):
                    if not item.get(key):raise ValueError(f'{name}: missing required field {key}')
                output.append(make_record(source,jurisdiction,item['id'],item['title'],item['published_at'],item['url'],now,'SIMULATED'))
        elif name=='state_B.json':
            source='SIMULATED_STATE_B';jurisdiction='SIM-B'
            for item in data['items']:
                for key in ('reference','heading','posted_on','link'):
                    if not item.get(key):raise ValueError(f'{name}: unexpected schema or missing {key}')
                output.append(make_record(source,jurisdiction,item['reference'],item['heading'],item['posted_on'],item['link'],now,'SIMULATED'))
        else:
            source='FEDERAL_REGISTER';jurisdiction='US'
            for item in data.get('results',[]):
                for key in ('document_number','title','publication_date','html_url'):
                    if not item.get(key): raise ValueError(f'Official record missing {key}')
                output.append(make_record(source,jurisdiction,item['document_number'],item['title'],item['publication_date'],item['html_url'],now,'PUBLIC_OFFICIAL'))
    if len({(d['source_id'],d['document_id']) for d in output})!=len(output):
        raise ValueError('Duplicate source/document ID in input')
    return output

def make_record(source,jurisdiction,docid,title,published,url,retrieved,kind):
    normalized={'source_id':source,'jurisdiction':jurisdiction,'document_id':docid,
      'title':title,'published_at':published,'retrieved_at':retrieved,'source_url':url,'source_kind':kind}
    normalized['content_hash']=hashlib.sha256(json.dumps({k:v for k,v in normalized.items() if k!='retrieved_at'},sort_keys=True,ensure_ascii=False).encode()).hexdigest()
    return normalized

def validate(records):
    required=('source_id','jurisdiction','document_id','title','published_at','retrieved_at','source_url','content_hash','source_kind')
    for item in records:
        if not all(item.get(k) for k in required): raise ValueError('Missing normalized fields')
        if item['source_kind']=='SIMULATED' and not item['source_url'].startswith('synthetic://'):
            raise ValueError('Synthetic source not clearly labeled')
    return records
