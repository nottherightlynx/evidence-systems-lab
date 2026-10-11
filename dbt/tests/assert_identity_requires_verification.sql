select * from {{ ref('bridge_identity') }}
where (review_status='verified' and canonical_entity_id is null)
   or (review_status='unresolved' and canonical_entity_id is not null)
