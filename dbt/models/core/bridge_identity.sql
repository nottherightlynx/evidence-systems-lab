select source_system, source_entity_id, canonical_entity_id,
       match_method, review_status
from {{ ref('stg_identity_crosswalk') }}
