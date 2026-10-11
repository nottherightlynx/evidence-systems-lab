select event_id, source_system, source_entity_id, source_record_id,
       event_type, try_cast(occurred_at as timestamptz) as occurred_at,
       jurisdiction, try_cast(amount as decimal(18,2)) as amount, status
from {{ ref('contributions') }}
