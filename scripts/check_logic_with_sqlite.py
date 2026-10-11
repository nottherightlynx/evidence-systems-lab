"""Independent *logical* test with sqlite; native dbt build is still required.
This loads the prepared seeds into SQLite to check the intended SQL semantics.
"""
from pathlib import Path
import csv,sqlite3
ROOT=Path(__file__).resolve().parent.parent
conn=sqlite3.connect(':memory:')
for file,table in [('identity_crosswalk.csv','x'),('interactions.csv','i'),('contributions.csv','c')]:
 with (ROOT/'dbt/seeds'/file).open(newline='',encoding='utf8') as f:
  reader=csv.DictReader(f);fields=reader.fieldnames;rows=list(reader)
 conn.execute(f"create table {table} ({','.join(k+' text' for k in fields)})")
 conn.executemany(f"insert into {table} values ({','.join('?' for _ in fields)})",[[r[k] for k in fields] for r in rows])
match=conn.execute('''select count(*),
 sum(case when x.canonical_entity_id is not null then 1 else 0 end),
 sum(case when x.canonical_entity_id is null then 1 else 0 end),
 count(distinct x.canonical_entity_id)
 from i left join x on i.source_system=x.source_system and i.source_entity_id=x.source_entity_id
 and x.review_status='verified' and x.canonical_entity_id<>'' ''').fetchone()
assert match==(4,3,1,2),match
finance=conn.execute('''select count(*), sum(case when status='received' then cast(amount as real) else 0 end),
 sum(case when status='refunded' then cast(amount as real) else 0 end),
 sum(case when status='pledged' then cast(amount as real) else 0 end)
 from c''').fetchone()
assert finance==(3,25,25,100),finance
print('PASS: SQL logic keeps 4 engagement events, resolves 3, retains 1 unresolved; 2 verified people.')
print('PASS: finance distinguishes $25 received, $25 refunded, and $100 pledged.')
print('NOTE: This is SQLite validation, NOT a dbt/DuckDB build.')
