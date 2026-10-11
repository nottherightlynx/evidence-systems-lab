# Governed analytical questions — Engineering evidence

**Implemented:** A deterministic alias router, versioned fictional rule documents, three approved metric operations, source/definition references, and explicit refusals.

**Not implemented:** A hosted or local language model, free-text RAG/vector search, production authentication, per-user authorization enforcement, or a certified privacy/compliance boundary. The local-LLM chart in this repository illustrates a possible future architecture.

## Verified synthetic outputs

- Two verified engaged constituents; one unresolved engagement event.
- One received contribution of $25 gross; a refund tracked separately.
- State A and B simulation fixtures were processed, while Federal Register was `NOT_FETCHED_OFFLINE` (not stale, and not a confirmed empty result).

## Observed guardrails

Requests to infer donation causality from time sequence, read restricted reviewer notes, execute arbitrary SQL, override definitions, or apply an unsupported quarter filter were rejected. The baseline's public rule corpus contains 12 public demonstration rules and one restricted test item.

## Expanded evaluation

The local deterministic suite executed 20 predefined supported and refusal cases and recorded **20 PASS / 0 FAIL / 0 BLOCKED**. Full per-case outcomes are in [`artifacts/assistant_evaluation_results.csv`](../artifacts/assistant_evaluation_results.csv); rerun with `python scripts/evaluate_assistant.py` to verify in a new environment. This evaluation does not demonstrate security of a deployed system or resistance to prompt injection of a real LLM.

## Future design

Introduce authorization-aware retrieval, scoped approved tools and parameterized queries, version/change-control metadata, audit logging and privacy review first. A locally hosted language model could then interpret questions and explain results, but it must not decide access permissions or redefine metrics.

## Career context

The design parallels program engagement, investment and renewal reporting governance at CFLeads: metric meaning belongs in a documented analytical layer, not in the phrasing of a user question.
