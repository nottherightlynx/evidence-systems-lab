select c.event_id, c.source_system, c.source_entity_id,
       c.source_record_id, c.event_type, c.occurred_at, c.jurisdiction,
       c.amount, c.status, m.canonical_entity_id as constituent_id,
       case when c.status='received' then c.amount else 0 end as received_cash,
       case when c.status='refunded' then -c.amount
            when c.status='received' then c.amount else 0 end as net_cash_effect
from {{ ref('stg_contributions') }} c
left join {{ ref('bridge_identity') }} m
  on c.source_system=m.source_system and c.source_entity_id=m.source_entity_id
  and m.review_status='verified' and m.canonical_entity_id is not null
