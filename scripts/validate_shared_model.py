import csv
from pathlib import Path
import sqlite3

folder = Path(__file__).resolve().parent.parent / 'data' / 'synthetic'
def rows(name):
    with (folder/name).open(newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

source = rows('source_registry.csv')
raw = rows('raw_engagements.csv')
bridge = rows('identity_crosswalk.csv')
facts = rows('event_fact.csv')
records = rows('source_record.csv')
assert len(source) == 5
assert len(raw) == 4
assert len(facts) == 7
assert len(records) == 10
assert len({(r['source_system'],r['source_entity_id']) for r in bridge}) == len(bridge)
assert len({r['event_id'] for r in facts}) == len(facts)
assert len({(r['source_id'],r['source_record_id']) for r in records}) == len(records)
assert all(len(r['checksum'])==64 for r in records)
source_set = {(r['source_id'],r['source_record_id']) for r in records}
assert all((r['source_id'],r['source_record_id']) in source_set for r in facts)

conn=sqlite3.connect(':memory:')
conn.execute('CREATE TABLE e (event_id TEXT, source_system TEXT, source_entity_id TEXT)')
conn.execute('CREATE TABLE m (source_system TEXT, source_entity_id TEXT, canonical_entity_id TEXT, review_status TEXT)')
conn.executemany('INSERT INTO e VALUES (?,?,?)',[(x['event_id'], x['source_system'],x['source_entity_id']) for x in raw])
conn.executemany('INSERT INTO m VALUES (?,?,?,?)',[(x['source_system'],x['source_entity_id'],x['canonical_entity_id'] or None,x['review_status']) for x in bridge])
q='''SELECT e.event_id, m.canonical_entity_id, COALESCE(m.review_status, 'missing')
FROM e LEFT JOIN m ON e.source_system=m.source_system
AND e.source_entity_id=m.source_entity_id AND m.review_status='verified'
ORDER BY e.event_id'''
found=conn.execute(q).fetchall()
assert len(found)==4
assert sum(1 for x in found if x[1] is None)==1
print('PASS: five shared tables found, unique keys confirmed, all seven facts trace to source records.')
print('ENGAGEMENT IDENTITIES (LEFT JOIN)')
for r in found: print('  ',r)
print('PASS: 4 engagement events retained; 3 matched, 1 unresolved. No rows silently lost.')
