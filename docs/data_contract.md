# Phase 0 data contract — Evidence Systems Lab

**Purpose:** Preserve identity, observed events and verifiable source provenance across disparate synthetic systems.

**Steward:** Portfolio demo owner. **Data classification:** Synthetic; public metadata only in a future phase. **Update mode:** Regenerated locally. **Timestamp standard:** UTC ISO 8601 with Z suffix. **Missing values:** Blank CSV value means unknown, never zero or false.

| Dataset | Row grain | Key | Required columns | Rules and downstream use |
|---|---|---|---|---|
| source_registry.csv | One registered source/feed | source_id | source_id, authority, jurisdiction, URL, access_class, expected_cadence | Distinguish fictional sources from official public sources. A registered public source is not proof of successful collection. |
| source_record.csv | One captured version of a source record | source_id + source_record_id + checksum | source_id, source_record_id, observed_at, retrieved_at, checksum, payload_ref | Checksum is SHA-256 of normalized JSON row. This initial bootstrap represents one version per record; later pipelines must append revisions rather than overwrite history. |
| identity_crosswalk.csv | One source identity | source_system + source_entity_id | source_system, source_entity_id, canonical_entity_id, match_method, review_status | A source ID must resolve to at most one confirmed canonical ID. Unresolved rows retain a blank canonical ID and are never automatically merged based on name/email/geography. |
| event_fact.csv | One actual observed event | event_id | event_id, entity_id, event_type, occurred_at, jurisdiction, source_id, source_record_id | entity_id may be blank. Added source_id to the PDF's minimum list to make source provenance joins unambiguous. Event flags are observed, not probabilities. |
| metric_definition.csv | One approved metric version | metric_id + version | metric_id, version, grain, inclusion_rule, exclusion_rule, owner, effective_from | Definitions are versioned. No inferred attribution or causal inference. |

## Financial treatment
- `contribution_pledged` is an intention/commitment, not received cash.
- `payment_received` is a received transaction and must not be counted twice.
- `refund_issued` reverses cash but is not another contribution.
- Raw financial amounts remain in `raw_contributions.csv`. CRM models will develop financial fact models and reconciliation.

## Identity and disclosure
- `CAN-001` represents one fictitious person seen in old/new CRM, engagement and donation sources.
- `APP-999` intentionally has no verifiable source-to-canonical match and must remain visible.
- A successful join cannot prove that one event caused another.
- Never put actual donor, voter, constituent, employer, or restricted legal data in this portfolio.

## Acceptance checks
1. Five shared tables exist with the exact column sets above.
2. All event facts trace to a source record using source_id + source_record_id.
3. Event IDs and source crosswalk keys are unique.
4. All four synthetic engagement rows survive a LEFT JOIN; three resolve to canonical entities and one is visibly unmatched.
5. Sources and rules have named authority/owners, and dates are interpretable.
