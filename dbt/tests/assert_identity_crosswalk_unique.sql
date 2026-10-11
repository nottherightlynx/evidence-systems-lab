select source_system, source_entity_id
from {{ ref('bridge_identity') }}
group by source_system, source_entity_id
having count(*) > 1
