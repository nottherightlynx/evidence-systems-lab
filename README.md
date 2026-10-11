# Evidence Systems Lab

**From source record to defensible answer.** Three connected analytics-engineering prototypes for traceable identity, observable public-data ingestion and governed analytical answers.

**[View the illustrated portfolio](https://evidencesystemslapbylmchea.lovable.app/)** · [Case studies](docs/portfolio_case_studies.md) · [Data contract](docs/data_contract.md) · [Source inventory](docs/source_inventory.md)

> **Scope:** All sample constituent, investment, and engagement records are **fictional**. The two state feeds are **simulated**. The Federal Register API is optional and is not fetched in the offline default. No nonpublic employer data, real voter records, credentials, or actual ACLU systems are included. The query assistant is deterministic—**not an LLM or a deployed RAG service**.

## Three connected projects

| Prototype | Engineering focus | Reproducible demonstration |
|---|---|---|
| **CRM identity and contribution truth** | dbt, DuckDB, SQL, canonical crosswalks and quality assertions | Preserve unmatched engagement records; distinguish pledges, received payments and refunds; catch a duplicate-event error. |
| **Geographic public-data observability** | Python and Dagster asset pipeline | Normalize incompatible fictional state schemas, surface an unexpected schema and distinguish an unfetched official source from an observed zero. |
| **Governed analytical questions** | Approved metric registry and versioned rule corpus | Answer three supported metrics; refuse unsupported causality, unauthorized notes, raw SQL and undefined filters. |

## Verified demonstration evidence

- **CRM:** 4 fictional interaction records; 2 verified engaged identities; 1 unresolved event. Financial facts include a $25 receipt, $100 pledge, and $25 refund. A deliberately duplicated event ID was caught by a dbt uniqueness test; the rebuilt clean dataset passed afterward.
- **Public data:** 3 simulated state records normalize successfully in offline mode. The intentionally altered State B schema triggers a visible error; restoration clears it. A documented successful Dagster run materialized the five-asset pipeline. This is not evidence of comprehensive legislative-data coverage.
- **Governed assistant:** The recorded deterministic evaluation returned **20/20 PASS** for a narrow gold set of known synthetic data and refusal scenarios. It does not certify a deployed LLM, production access control, or privacy compliance.

See the [engineering case studies](docs/portfolio_case_studies.md), [CRM evidence](docs/crm_model_evidence.md), [public-data evidence](docs/public_data_evidence.md), [assistant evidence](docs/governed_assistant_evidence.md), and [test outcomes](artifacts/assistant_evaluation.md).

## Reproduce locally

Requires Python **3.11** or **3.12**. Commands start in this repository's root.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/generate_shared_fixtures.py
python scripts/generate_project_fixtures.py
python scripts/validate_shared_model.py
python scripts/validate_project_setup.py

dbt debug --project-dir dbt --profiles-dir dbt
dbt seed --project-dir dbt --profiles-dir dbt
dbt build --project-dir dbt --profiles-dir dbt
python scripts/check_logic_with_sqlite.py
python -m orchestration.pipeline
python scripts/check_public_pipeline.py
python scripts/check_assistant_rules.py
python scripts/evaluate_assistant.py
python scripts/build_portfolio_site.py
python scripts/validate_portfolio.py
```

To inspect the Dagster asset graph (optional):

```bash
dagster dev -f orchestration/definitions.py
```

Open the UI address printed by Dagster, then materialize the assets. To preview the static documentation site:

```bash
python -m http.server 8000 --directory site
```

The scripts generate local DuckDB and report files under `artifacts/`; binary databases, virtual environments, logs and caches are **not** checked into the repository. The committed `artifacts/assistant_evaluation_results.csv` is the recorded synthetic fixture run; rerunning the evaluation produces updated local results.

## Failure tests

From the root **after** a successful clean build:

```bash
python scripts/inject_demo_failure.py duplicate-interaction
dbt seed --project-dir dbt --profiles-dir dbt
dbt build --project-dir dbt --profiles-dir dbt  # Expected uniqueness-test failure
python scripts/generate_project_fixtures.py
dbt seed --project-dir dbt --profiles-dir dbt
dbt build --project-dir dbt --profiles-dir dbt  # Expected recovery
```

To exercise public-source schema drift, run `python scripts/inject_demo_failure.py wrong-state-schema`, then `python -m orchestration.pipeline` (expected visible failure); restore fixtures with `python scripts/generate_project_fixtures.py` before rerunning.

## Architecture and controls

```
Synthetic CRM / Engagement / Contributions → dbt SQL models → Tested marts ──┐
                                                                               ├→ Approved metric registry → Evidence-backed response or refusal
Synthetic state feeds / optional public API → Python/Dagster → source statuses ─┘
```

The identity model differentiates source IDs from validated canonical IDs; the source observability model differentiates publication from retrieval. Questions are routed to approved operations rather than free-form SQL. A **locally hosted LLM is an unimplemented design extension**, not part of this repository's runtime.

## Relationship to professional experience

This prototype illustrates engineering approaches relevant to work on investor-renewal and program-engagement definitions in Salesforce/SQL at CFLeads, public legislative-data monitoring at NCTE, and donor-system reconciliation in legal advocacy. It is independent portfolio work, not a copy of internal systems, data, or materials from any organization.

## License and contributions

This repository is shared for portfolio review. No open-source license is granted by default. Please contact the author before copying or repurposing the code.
