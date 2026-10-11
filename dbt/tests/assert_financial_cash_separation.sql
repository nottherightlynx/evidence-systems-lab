select * from {{ ref('fct_contribution') }}
where (status <> 'received' and received_cash <> 0)
   or (status = 'received' and received_cash <> amount)
   or (status = 'refunded' and net_cash_effect <> -amount)
