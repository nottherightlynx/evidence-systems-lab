"""Intentionally break a *generated* fixture; rerun generate_project_fixtures.py to recover."""
from pathlib import Path
import argparse,csv,json
ROOT=Path(__file__).resolve().parent.parent
p=argparse.ArgumentParser();p.add_argument('case', choices=['duplicate-interaction','wrong-state-schema']);opt=p.parse_args()
if opt.case=='duplicate-interaction':
 path=ROOT/'dbt/seeds/interactions.csv'
 with path.open(newline='',encoding='utf8') as f:
  reader=csv.DictReader(f); columns=reader.fieldnames; records=list(reader)
 records.append(records[0].copy())
 with path.open('w',newline='',encoding='utf8') as f:
  writer=csv.DictWriter(f,fieldnames=columns);writer.writeheader();writer.writerows(records)
 print('INJECTED duplicate interaction ID. dbt build should FAIL unique test.')
else:
 path=ROOT/'data/synthetic/state_B.json'; data=json.loads(path.read_text())
 row=data['items'][0];row['unexpected_posted_field']=row.pop('posted_on')
 path.write_text(json.dumps(data,indent=2)+'\n')
 print('INJECTED schema drift. Public-data normalization should FAIL.')
print('RESTORE using: python scripts/generate_project_fixtures.py')
