"""Prepare dbt seeds from the synthetic phase inputs; safe to rerun."""
from pathlib import Path
import csv, json, datetime
ROOT=Path(__file__).resolve().parent.parent
SOURCE=ROOT/'data/synthetic'; DEST=ROOT/'dbt/seeds'
DEST.mkdir(parents=True, exist_ok=True)
inputs={
  'legacy_constituents.csv': ('raw_constituents.csv', lambda r:r['source_system']=='LEGACY_CRM'),
  'new_constituents.csv': ('raw_constituents.csv', lambda r:r['source_system']=='NEW_CRM'),
  'identity_crosswalk.csv': ('identity_crosswalk.csv', lambda r: True),
  'interactions.csv': ('raw_engagements.csv', lambda r: True),
  'contributions.csv': ('raw_contributions.csv', lambda r: True),
}
for outfile,(infile,pred) in inputs.items():
 with (SOURCE/infile).open(newline='',encoding='utf8') as f:
  reader=csv.DictReader(f); fields=reader.fieldnames; rows=[r for r in reader if pred(r)]
 with (DEST/outfile).open('w',newline='',encoding='utf8') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
 print(f'CREATED dbt/seeds/{outfile}: {len(rows)} rows')
now=datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')
stateA={'feed':'SIMULATED_STATE_A','jurisdiction':'SIM-A','retrieved_at':now,'records':[
 {'id':'SIM-A-001','title':'SIMULATED public record A1','published_at':'2026-10-01T12:00:00Z','url':'synthetic://state-a/001'},
 {'id':'SIM-A-002','title':'SIMULATED public record A2','published_at':'2026-10-03T12:00:00Z','url':'synthetic://state-a/002'}]}
stateB={'feed':'SIMULATED_STATE_B','jurisdiction':'SIM-B','fetched_at':now,'items':[
 {'reference':'SIM-B-001','heading':'SIMULATED public record B1','posted_on':'2026-10-02T12:00:00Z','link':'synthetic://state-b/001'}]}
for file,obj in [('state_A.json',stateA),('state_B.json',stateB)]:
 (SOURCE/file).write_text(json.dumps(obj,indent=2)+'\n',encoding='utf8')
 print('CREATED data/synthetic/'+file)
print('READY: dbt seeds and explicitly simulated state feeds')
