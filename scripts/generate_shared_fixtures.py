from pathlib import Path
import csv
import hashlib
import json
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'data' / 'synthetic'
DATA.mkdir(parents=True, exist_ok=True)


def save_csv(filename, fields, rows):
    with (DATA / filename).open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f'Created data/synthetic/{filename}: {len(rows)} rows')

sources = [
    ['LEGACY_CRM', 'Fictional legacy CRM', 'US', 'synthetic://legacy-crm', 'synthetic', 'manual'],
    ['NEW_CRM', 'Fictional replacement CRM', 'US', 'synthetic://new-crm', 'synthetic', 'manual'],
    ['ENGAGEMENT_APP', 'Fictional engagement tool', 'US', 'synthetic://engagement', 'synthetic', 'manual'],
    ['DONATION_PROCESSOR', 'Fictional payment tool', 'US', 'synthetic://payments', 'synthetic', 'manual'],
    ['FEDERAL_REGISTER', 'Federal Register', 'US', 'https://www.federalregister.gov/developers/documentation/api/v1', 'public', 'daily'],
]
save_csv('source_registry.csv',
         ['source_id', 'authority', 'jurisdiction', 'URL', 'access_class', 'expected_cadence'],
         [dict(zip(['source_id', 'authority', 'jurisdiction', 'URL', 'access_class', 'expected_cadence'], row)) for row in sources])

people = [
    dict(source_system='LEGACY_CRM', source_entity_id='LEG-001', name='Avery Lane', email='avery@example.invalid', jurisdiction='DC'),
    dict(source_system='NEW_CRM', source_entity_id='NEW-201', name='Avery Lane', email='avery@example.invalid', jurisdiction='DC'),
    dict(source_system='NEW_CRM', source_entity_id='NEW-202', name='Morgan Reed', email='morgan@example.invalid', jurisdiction='MD'),
]
engagements = [
    dict(event_id='EV-001', source_system='ENGAGEMENT_APP', source_entity_id='APP-101', source_record_id='REG-001', event_type='registration', occurred_at='2026-08-01T15:00:00Z', jurisdiction='DC'),
    dict(event_id='EV-002', source_system='ENGAGEMENT_APP', source_entity_id='APP-101', source_record_id='ATT-002', event_type='attendance', occurred_at='2026-08-05T15:00:00Z', jurisdiction='DC'),
    dict(event_id='EV-003', source_system='ENGAGEMENT_APP', source_entity_id='APP-202', source_record_id='REG-003', event_type='registration', occurred_at='2026-08-03T15:00:00Z', jurisdiction='MD'),
    dict(event_id='EV-004', source_system='ENGAGEMENT_APP', source_entity_id='APP-999', source_record_id='ATT-004', event_type='attendance', occurred_at='2026-08-04T15:00:00Z', jurisdiction='VA'),
]
contributions = [
    dict(event_id='EV-005', source_system='DONATION_PROCESSOR', source_entity_id='DON-501', source_record_id='PAY-001', event_type='payment_received', occurred_at='2026-08-10T12:00:00Z', jurisdiction='DC', amount='25.00', status='received'),
    dict(event_id='EV-006', source_system='DONATION_PROCESSOR', source_entity_id='DON-502', source_record_id='PLEDGE-002', event_type='contribution_pledged', occurred_at='2026-08-05T12:00:00Z', jurisdiction='MD', amount='100.00', status='pledged'),
    dict(event_id='EV-007', source_system='DONATION_PROCESSOR', source_entity_id='DON-501', source_record_id='REF-003', event_type='refund_issued', occurred_at='2026-08-11T12:00:00Z', jurisdiction='DC', amount='25.00', status='refunded'),
]
save_csv('raw_constituents.csv', list(people[0]), people)
save_csv('raw_engagements.csv', list(engagements[0]), engagements)
save_csv('raw_contributions.csv', list(contributions[0]), contributions)

crosswalk = [
    ['LEGACY_CRM', 'LEG-001', 'CAN-001', 'fictional_verified_mapping', 'verified'],
    ['NEW_CRM', 'NEW-201', 'CAN-001', 'fictional_verified_mapping', 'verified'],
    ['NEW_CRM', 'NEW-202', 'CAN-002', 'fictional_verified_mapping', 'verified'],
    ['ENGAGEMENT_APP', 'APP-101', 'CAN-001', 'fictional_verified_mapping', 'verified'],
    ['ENGAGEMENT_APP', 'APP-202', 'CAN-002', 'fictional_verified_mapping', 'verified'],
    ['ENGAGEMENT_APP', 'APP-999', '', 'no_supportable_match', 'unresolved'],
    ['DONATION_PROCESSOR', 'DON-501', 'CAN-001', 'fictional_verified_mapping', 'verified'],
    ['DONATION_PROCESSOR', 'DON-502', 'CAN-002', 'fictional_verified_mapping', 'verified'],
]
cross_fields = ['source_system', 'source_entity_id', 'canonical_entity_id', 'match_method', 'review_status']
save_csv('identity_crosswalk.csv', cross_fields,
         [dict(zip(cross_fields, row)) for row in crosswalk])
lookup = {(r[0], r[1]): r[2] for r in crosswalk if r[4] == 'verified'}

now_utc = datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')
raw_files = [('raw_constituents.csv', people), ('raw_engagements.csv', engagements), ('raw_contributions.csv', contributions)]
source_records = []
for filename, records in raw_files:
    for r in records:
        record_id = r.get('source_record_id', r['source_entity_id'])
        content = json.dumps(r, sort_keys=True, separators=(',', ':'))
        source_records.append(dict(
            source_id=r['source_system'], source_record_id=record_id,
            observed_at=r.get('occurred_at', '2026-07-01T00:00:00Z'),
            retrieved_at=now_utc,
            checksum=hashlib.sha256(content.encode('utf-8')).hexdigest(),
            payload_ref=f'data/synthetic/{filename}#{record_id}',
        ))
save_csv('source_record.csv',
         ['source_id', 'source_record_id', 'observed_at', 'retrieved_at', 'checksum', 'payload_ref'], source_records)

facts = []
for r in engagements + contributions:
    facts.append(dict(
        event_id=r['event_id'], entity_id=lookup.get((r['source_system'], r['source_entity_id']), ''),
        event_type=r['event_type'], occurred_at=r['occurred_at'], jurisdiction=r['jurisdiction'],
        source_id=r['source_system'], source_record_id=r['source_record_id'],
    ))
save_csv('event_fact.csv',
         ['event_id', 'entity_id', 'event_type', 'occurred_at', 'jurisdiction', 'source_id', 'source_record_id'], facts)

metrics = [
    ['unique_engaged_people', '1.0', 'canonical_entity', 'Verified identity and registration or attendance in selected period', 'Unresolved identities excluded from identified-person count, but reported separately', 'Demo Data Steward', '2026-01-01'],
    ['received_contributions', '1.0', 'transaction', 'status equals received for a unique payment transaction', 'Exclude pledges; show refunds separately rather than treating them as payments', 'Demo Finance Owner', '2026-01-01'],
    ['first_observed_interaction_at', '1.0', 'canonical_entity', 'Earliest recorded verified engagement event in available history', 'Do not claim this is the first-ever interaction', 'Demo Analytics Owner', '2026-01-01'],
    ['unresolved_engagements', '1.0', 'event', 'Engagement event has no verified canonical identity', 'Do not hide missing identity rows with an inner join', 'Demo Data Steward', '2026-01-01'],
]
metric_fields = ['metric_id', 'version', 'grain', 'inclusion_rule', 'exclusion_rule', 'owner', 'effective_from']
save_csv('metric_definition.csv', metric_fields, [dict(zip(metric_fields, r)) for r in metrics])
print('DONE: five shared tables and three fictional raw source files created.')
