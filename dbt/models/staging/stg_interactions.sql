select event_id, source_system, source_entity_id, source_record_id,
       event_type, try_cast(occurred_at as timestamptz) as occurred_at,
       jurisdiction
from {{ ref('interactions') }}
