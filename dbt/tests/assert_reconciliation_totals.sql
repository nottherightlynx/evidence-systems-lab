select * from {{ ref('mart_reconciliation') }}
where source_rows <> resolved_rows + unresolved_rows
