# CRM identity migration — Engineering evidence

**Scope:** Small, reproducible, fictional CRM / engagement / financial seed dataset using dbt and DuckDB.

## Problem and model

Multiple upstream IDs may refer to one constituent. Loss of identity mapping can silently reduce row counts; excessive joins can duplicate event or financial facts. The design distinguishes source-system identifiers and reviewed canonical IDs with an explicit crosswalk; facts declare event or transaction grain.

**Synthetic baseline:** Four interactions; three resolved interaction rows; one unresolved; two verified engaged people; three financial transactions (one $25 received, one $100 pledge, one $25 refund). Gross received cash and refunds remain separately visible.

## Decisions

- Preserve source IDs instead of overwriting them with canonical IDs.
- Use reconciliation-oriented `LEFT JOIN` mapping, with unresolved identities visible.
- Aggregate engagement and contributions separately to avoid multiplication of counts when combining domains.
- Keep pledge, receipt and refund statuses distinct, with declared reporting periods and financial grain.
- Express uniqueness, referential and monetary consistency as tests.

## Observed fail-and-recover evidence

A duplicate interaction ID was injected into the dbt seed data. The local build reported `unique_fct_interaction_event_id: FAIL 1`, with downstream operations skipped. After regenerating the four unique interaction rows, the dbt build completed successfully. This is an observed quality-test failure and recovery, not a production CRM migration.

## Limitations

The identity crosswalk encodes invented identities; the project does not train a matching model or establish causal attribution from participation to giving. It does not evaluate production scale. The supplied reproducible models and tests should be rerun on any new machine.

## Career context

At CFLeads I worked on Account/Opportunity investor definitions, renewal-period logic, and current-versus-prior investor reporting. The principle carried into this lab is that mechanically correct aggregation is not trustworthy if underlying business definitions or identity assumptions are wrong.
