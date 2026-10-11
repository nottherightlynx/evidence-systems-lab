select source_system, source_entity_id, name as full_name,
       lower(trim(email)) as normalized_email, jurisdiction
from {{ ref('legacy_constituents') }}
