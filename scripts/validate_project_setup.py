"""Dependency-light preflight. Does NOT claim dbt/Dagster have executed.
The native dbt and Dagster runs must be independently verified in the target environment.
"""
from pathlib import Path
import csv,json,subprocess,sys
ROOT=Path(__file__).resolve().parent.parent
required=['dbt/dbt_project.yml','dbt/profiles.yml','dbt/models/core/fct_interaction.sql',
          'dbt/models/core/fct_contribution.sql','dbt/models/marts/mart_lifecycle.sql',
          'orchestration/definitions.py','orchestration/pipeline.py',
          'assistant/rules.jsonl','assistant/metrics_registry.yml']
assert all((ROOT/p).exists() for p in required)
for file,count in [('legacy_constituents.csv',1),('new_constituents.csv',2),
                   ('identity_crosswalk.csv',8),('interactions.csv',4),('contributions.csv',3)]:
  with (ROOT/'dbt/seeds'/file).open(newline='',encoding='utf8') as f:rows=list(csv.DictReader(f))
  assert len(rows)==count,(file,len(rows),count)
with (ROOT/'assistant/rules.jsonl').open() as f: rules=[json.loads(x) for x in f if x.strip()]
assert len(rules)==13
print('PASS: prepared dbt seeds, model definitions, public-data scripts, and governance corpus.')
print('NEXT: run dbt build and Dagster assets; this preflight only checks structure and fixture counts.')
