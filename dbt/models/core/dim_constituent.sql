with all_rows as (
 select c.canonical_entity_id as constituent_id, s.full_name, s.jurisdiction
 from {{ ref('stg_legacy_constituents') }} s
 join {{ ref('bridge_identity') }} c
   on s.source_system=c.source_system and s.source_entity_id=c.source_entity_id
   and c.review_status='verified' and c.canonical_entity_id is not null
 union all
 select c.canonical_entity_id as constituent_id, s.full_name, s.jurisdiction
 from {{ ref('stg_new_constituents') }} s
 join {{ ref('bridge_identity') }} c
   on s.source_system=c.source_system and s.source_entity_id=c.source_entity_id
   and c.review_status='verified' and c.canonical_entity_id is not null
)
select constituent_id, min(full_name) as demo_name,
       min(jurisdiction) as demo_jurisdiction
from all_rows group by constituent_id
