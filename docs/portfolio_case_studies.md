# Engineering case studies

## Thesis: from source record to defensible answer

A useful data product should preserve which source a record came from, which entity it refers to, what event actually occurred, the rule applied to interpret it, and any unresolved uncertainty. These three connected **synthetic-data demonstrations** apply that principle to data migration, geographically distributed public sources, and governed analytical questions.

### 1. Constituent identity and financial reporting — dbt / DuckDB / SQL

**Question:** How do we move between two CRM schemas without inflating distinct people, losing unmatched activities, or conflating pledge, receipt, and refund?

**Design:** Stage original records, link known identities through an explicit crosswalk, retain unmatched engagement rows, define facts at event/transaction grain, and separate received cash from commitments and refunds. An intentionally duplicated event causes the uniqueness assertion to fail; restoring the four event rows allows the build to complete again. The fictional baseline includes **four engagement events, two verified engaged identities, one unresolved identity event, one $25 received transaction, one $100 pledge, and one $25 refund**.

**Professional parallel:** Salesforce investment and renewal logic at CFLeads; donor-system reconciliation in legal-advocacy organizations. A current investor relationship is not necessarily synonymous with a calendar-year payment. This lab does **not** use real CRM or financial records.

**Tradeoff:** A `LEFT JOIN` preserves unmatched source facts for review; a reporting mart that requires verified identities can exclude them explicitly while exposing the excluded count. Identity matches here are synthetic ground truth.

See [CRM model evidence](crm_model_evidence.md) and [`dbt/`](../dbt/).

### 2. Public-document freshness and provenance — Python / Dagster

**Question:** When a public-data view is empty, do we have evidence of no matching documents, or did collection fail?

**Design:** Ingest two explicitly simulated state feeds with differing metadata schemas; optionally retrieve a bounded official Federal Register result; normalize source IDs, timestamps and document links. Dagster defines the extraction → normalization → validation → observability/review dependencies. Unexpected schema drift is rejected and documented rather than silently treated as no activity.

**Observed offline fixture:** State A: two documents; State B: one document; Federal Register: `NOT_FETCHED_OFFLINE`. A documented source-drift injection failed and a restored run passed. The source status is not an assertion of real state legislative completeness.

**Professional parallel:** Public legislative-data monitoring across jurisdictions at NCTE, and geographic reporting across community foundations.

See [public-source evidence](public_data_evidence.md) and [`orchestration/`](../orchestration/).

### 3. Governed analytical access — rule registry and deterministic questions

**Question:** How can people ask plain-language analytical questions without granting unrestricted SQL access or inventing definitions?

**Design:** An explicit phrase/alias router selects one of three allowlisted metrics, retrieves appropriate simulated rule IDs, and executes bounded calculations. The result includes metric identifier, version, source references and limitations. Unsupported causal inferences, restricted notes, arbitrary SQL, unsupported date filters and ambiguous requests are refused. **There is no deployed LLM, vector RAG, authenticated authorization system, or verified production privacy boundary.** A local-LLM layer is an architectural proposal only.

**Recorded evaluation:** The synthetic deterministic test suite completed **20/20 cases**, including supported metric answers and explicit refusals. The count is about this narrow baseline, **not an AI-model accuracy, penetration-test, or privacy-compliance result**.

**Professional parallel:** CFLeads Tech Way, Data Wiki, investment and program metrics; controlled, human-reviewed reporting interfaces.

See [assistant evidence](governed_assistant_evidence.md), [evaluation](../artifacts/assistant_evaluation.md), and [`assistant/`](../assistant/).

## Responsible publication

All person and payment examples are fabricated. The two state feeds are **simulated**. The official Federal Register source is optional, is not consulted during the offline baseline, and must not be confused with the fictional documents. Workflows and comparisons are examples of technical methodology—not ACLU internal design claims or completed production deployments.
