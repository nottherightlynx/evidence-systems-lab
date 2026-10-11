with interaction_summary as (
 select constituent_id,
        min(occurred_at) as first_observed_interaction_at,
        count(*) as interaction_events
 from {{ ref('fct_interaction') }}
 where constituent_id is not null
 group by constituent_id
), contribution_summary as (
 select constituent_id,
        count(*) filter (where status='received') as received_transactions,
        coalesce(sum(received_cash),0) as received_cash,
        coalesce(sum(net_cash_effect),0) as net_cash_effect
 from {{ ref('fct_contribution') }}
 where constituent_id is not null
 group by constituent_id
)
select d.constituent_id, d.demo_name,
       i.first_observed_interaction_at, coalesce(i.interaction_events,0) as interaction_events,
       coalesce(c.received_transactions,0) as received_transactions,
       coalesce(c.received_cash,0) as received_cash,
       coalesce(c.net_cash_effect,0) as net_cash_effect
from {{ ref('dim_constituent') }} d
left join interaction_summary i on d.constituent_id=i.constituent_id
left join contribution_summary c on d.constituent_id=c.constituent_id
