# Routing and evaluation records

Record concise decisions and observable evidence, not private deliberation. Do not generate telemetry for routine work unless useful or requested.

```json
{
  "task_type": "",
  "complexity": 0,
  "risk": "low",
  "context_size": "small",
  "needs_web": false,
  "needs_files": false,
  "needs_code": false,
  "needs_deep_reasoning": false,
  "available_models": [],
  "recommended_model": null,
  "actual_model": null,
  "reasoning_effort": "low",
  "mode": "auto",
  "automatic_invocation": null,
  "paper_phase": null,
  "writing_workflow": null,
  "delegation": {
    "eligible": false,
    "reason": null,
    "attempted": false,
    "cap": 0,
    "subagent_count": 0,
    "roles": [],
    "integration_status": "skipped",
    "failure_reason": null
  },
  "escalation_allowed": false,
  "escalation_reason": null
}
```

```json
{
  "quality_score": null,
  "confidence": null,
  "critical_errors": null,
  "minor_errors": null,
  "unresolved_questions": [],
  "validation_evidence": [],
  "repair_cycles": 0,
  "repairable_by_gpt56": null,
  "gpt6_required": false
}
```

Scores are heuristics, not measured accuracy. Unknown error counts should be null rather than zero. Success requires evidence that material requirements passed.

Set `automatic_invocation` to `true` only after this policy was actually applied; use `null` when invocation was unavailable or not evaluated. A zero error count means the relevant validation verified that no such errors were present; use `null` before that validation. For delegation, distinguish eligibility, attempt, cap, and outcome. Use `skipped`, `delegated`, `completed`, or `failed` for `integration_status`, and count all subagents in the single delegation wave for that user task.

For manuscript work, `paper_phase` may be `discovery`, `outline`, `drafting`, `revision`, or `submission`. `writing_workflow` should identify whether the wave handled `preparation`, `audit`, or `language_pass`, plus the evidence and validation paths used. Keep source pointers and unresolved issues instead of storing invented or unverified bibliographic details.

Optional necessity score: +2 for two failed GPT-5-family repairs; +2 critical contradiction; +2 failed executable validation; +1 competing expert solutions; +1 high-impact decision; +1 unresolved evidence; +3 explicit GPT-6 request; -2 mainly rewriting; -2 mainly summarization; -2 simple retrieval; -1 resolvable through further search. Below 3: normally deny; 3–4: repair first; 5 or above: eligible. This diagnostic never overrides explicit user model selection, Fast restrictions, actual-attempt requirements, or the quality gate.

When runtime telemetry is available, track task count, attempted/successful calls by model, input/output/cached tokens, GPT-6 escalation count/rate, repair count/success rate, rescue success rate, average cost per task, and cost per successful task. Use null for unavailable measurements. Never infer exact token usage or cost from prose length, or claim savings without a comparable baseline and current prices. Define a rescue as a previously failing deliverable passing the same meaningful validation after escalation; improvement is not proof that GPT-6 was uniquely necessary.

The user's optional allocation targets are Luna 40–55%, Terra 20–30%, Sol 15–25%, GPT-6 2–8%. These are planning ranges, not benchmarks or quotas. GPT-6 above 10–15% may motivate inspecting routing, retrieval, repair, and duplicated work, but workload mix can justify it. No recurring monitoring is configured by installing this skill.

Suggested rolling task state: project, objective, confirmed_facts, decisions, constraints, completed_work, open_questions, recent_changes. Preserve relevant source pointers and distinguish confirmed facts from assumptions.

## Paper evidence records

Use this compact record when a manuscript task includes source retrieval or claim auditing. Keep unknown values `null`; do not infer bibliographic details from a plausible title or an unresolved URL.

```json
{
  "source_key": "",
  "title": "",
  "authors": [],
  "year": null,
  "venue": null,
  "identifiers": {
    "doi": null,
    "arxiv": null,
    "openalex": null
  },
  "version_status": "unknown",
  "source_url": null,
  "checked_at": null,
  "claims_supported": [],
  "evidence_locations": [],
  "access_status": "unknown",
  "license": null,
  "verification": "needs-check",
  "notes": ""
}
```

For a claim matrix, use `claim`, `section`, `source_key_or_result`, `evidence_location`, `strength`, `caveat`, and `repair_action`. A `verified` source must have a checked record and a source-backed evidence location; a `needs-check` source must not support a final material claim. Record whether a result was reproduced, quoted from a source, or proposed for future testing.
