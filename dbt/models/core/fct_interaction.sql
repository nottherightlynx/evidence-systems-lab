select e.event_id, e.source_system, e.source_entity_id, e.source_record_id,
       e.event_type, e.occurred_at, e.jurisdiction,
       m.canonical_entity_id as constituent_id,
       case when m.canonical_entity_id is null then 'unresolved'
            else 'verified' end as identity_status
from {{ ref('stg_interactions') }} e
left join {{ ref('bridge_identity') }} m
  on e.source_system=m.source_system and e.source_entity_id=m.source_entity_id
  and m.review_status='verified' and m.canonical_entity_id is not null
