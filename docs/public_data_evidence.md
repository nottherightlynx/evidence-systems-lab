# Public-source observability — Engineering evidence

**Scope:** Python normalization and Dagster asset dependencies using two entirely simulated state-format feeds and an optional bounded official Federal Register API call.

## Problem

Absence of collected records is not proof that nothing happened. Coverage and source freshness must be observable separately from counts of documents.

## Design

- Different source field names are mapped to a consistent schema with publication and retrieval timestamps kept distinct.
- Source identifiers and provenance links remain on every normalized document.
- Dagster assets define the dependency path `raw_public_documents` → `normalized_documents` → `validated_documents` → `source_observability` / `review_queue`.
- Explicit statuses distinguish successfully processed fixtures from an official API not contacted during the offline run.

## Observed evidence

The recorded offline Python run normalized **3 simulated documents** (State A: 2, State B: 1) and recorded Federal Register status as `NOT_FETCHED_OFFLINE`, not a real-world zero count. The checker passed the provenance and artifact checks.

An injected State B field-name change caused a visible `ValueError` at the normalizer. Regenerating the approved fixture and re-running processing restored a passing result. A separate successful Dagster run and five-asset graph were documented in the supplied working project. The deliberately failed schema run was demonstrated via the Python pipeline, **not** a confirmed Dagster failure materialization.

The engineering record also describes an optional bounded official Federal Register fetch; the published offline fixture remains the reproducible default.

## Tradeoffs and limitations

Fixture cadence and coverage are simulated. This is not a comprehensive state legislative dataset. A production system would need independently maintained source-specific expectations, retry and archival policies, source data contracts, and security review.

## Career context

The approach reflects prior state-by-state legislative data monitoring and current place-based reporting work: never collapse collection failure into an apparent absence of activity.
