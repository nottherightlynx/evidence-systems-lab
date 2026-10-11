select source_system, source_entity_id,
       nullif(trim(canonical_entity_id), '') as canonical_entity_id,
       match_method, review_status
from {{ ref('identity_crosswalk') }}
