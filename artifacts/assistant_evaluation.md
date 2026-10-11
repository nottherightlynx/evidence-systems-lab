# Governed Analytical Interface — Recorded Evaluation

**Recorded execution (UTC):** 2026-10-11T19:46:16+00:00
**Outcome:** 20/20 PASS; 0 FAIL; 0 BLOCKED.
**Engine:** deterministic alias/phrase routing to approved synthetic metric operations; no deployed LLM, RAG, or authentication system.

## Tested question types

| ID | Test focus | Outcome |
|---|---|---|
| Q01 | supported-source | PASS |
| Q02 | supported-source | PASS |
| Q03 | supported-source | PASS |
| Q04 | supported-identity | PASS |
| Q05 | supported-identity | PASS |
| Q06 | supported-identity | PASS |
| Q07 | supported-finance | PASS |
| Q08 | supported-finance | PASS |
| Q09 | unsupported-causal | PASS |
| Q10 | unsupported-causal | PASS |
| Q11 | restricted | PASS |
| Q12 | restricted | PASS |
| Q13 | raw-sql | PASS |
| Q14 | raw-sql | PASS |
| Q15 | unsupported-filter | PASS |
| Q16 | unsupported-filter | PASS |
| Q17 | wrong-rule-version | PASS |
| Q18 | wrong-rule-version | PASS |
| Q19 | unknown-question | PASS |
| Q20 | ambiguous-metric | PASS |

## What this establishes

- Supported analytical questions returned expected results from the local synthetic fixtures with rule IDs and version metadata.
- The test set also confirmed the deliberate refusal of unsupported causal inference, access to restricted notes, arbitrary SQL, unimplemented time windows, unapproved rule versions and ambiguous requests.
- The source-status answer properly distinguished `NOT_FETCHED_OFFLINE` from `STALE` or a verified zero count.

## What this does not establish

The 20 checks target only the known small deterministic application. They do not validate production access control, LLM prompt injection resistance, external data freshness, real voter identity matching, causal attribution, or compliance. Answers cite *fictional rule identifiers*, not authenticated public legal documents.

## How to reproduce

```bash
python scripts/generate_shared_fixtures.py
python scripts/generate_project_fixtures.py
dbt seed --project-dir dbt --profiles-dir dbt
dbt build --project-dir dbt --profiles-dir dbt
python -m orchestration.pipeline
python scripts/evaluate_assistant.py
```

An independent environment may return a BLOCKED result if DuckDB/dbt is not installed or the database has not been built. Do not change expected values to hide that dependency. The full per-case records are in [`assistant_evaluation_results.csv`](assistant_evaluation_results.csv).
