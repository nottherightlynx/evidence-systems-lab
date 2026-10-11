select 'interactions' as domain,
       count(*) as source_rows,
       count(*) filter (where constituent_id is not null) as resolved_rows,
       count(*) filter (where constituent_id is null) as unresolved_rows
from {{ ref('fct_interaction') }}
union all
select 'contributions' as domain,
       count(*) as source_rows,
       count(*) filter (where constituent_id is not null) as resolved_rows,
       count(*) filter (where constituent_id is null) as unresolved_rows
from {{ ref('fct_contribution') }}
