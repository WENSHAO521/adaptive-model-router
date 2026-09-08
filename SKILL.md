---
name: adaptive-model-router
description: Automatically apply capability-aware GPT-5.6-first routing, bounded subagent delegation, quality repair, and compressed GPT-6 escalation under a model budget.
---

# Adaptive Model Router

Prefer the least costly capable model under the user's chosen policy. Treat the tier ordering below as a user preference, not verified pricing or a benchmark claim. Preserve correctness and explicit model choices.

## Execution boundary

Inspect the current host's available model IDs, supported reasoning levels, and dispatch tools before routing. This skill is guidance, not a runtime model switch. Never claim another model executed work without a successful dispatch result. It cannot change the model already running the current turn, erase injected context, enforce platform billing limits, or guarantee automatic invocation on every request.

Use model selection only through an available, authorized tool. Do not create a new user-visible task merely to route work. Delegate only when applicable tool rules permit it and a bounded independent subtask can run concurrently or provide independent validation; avoid delegation overhead for trivial tasks. Do not recursively create routers. If dispatch is unavailable, explain the limitation briefly when relevant and finish feasible work on the active model; do not simulate a cheaper-model attempt or repeatedly retry unavailable models.

Do not hard-code the host inventory. At routing time, inspect the active dispatch surface for available model IDs, aliases, and supported reasoning levels. Use the complexity table and selected mode to choose the first attempt. Within the models capable of that task, prefer the least-cost available candidate; the `gpt-5.6-luna` → `gpt-5.6-terra` → `gpt-5.6-sol` sequence is a fallback cost and availability order, not a universal first-attempt sequence. Reserve `gpt-6-astra` for the escalation gate. On hosts that expose older or different GPT-5-family models, use the best available compatible candidate such as `gpt-5.4-mini`, `gpt-5.5`, `gpt-5`, or `gpt-5-codex` for coding work. These are compatibility candidates, not a promise that every host offers them. Do not silently substitute for an explicitly requested unavailable model; report the unavailable ID and ask for a choice when the distinction matters.

The model shown in the current UI or system banner identifies the active turn; it is not proof that the same ID can be selected for a delegated call. Treat a model as actually used only after the dispatch surface confirms it.

## Automatic behavior

Invoke this skill implicitly whenever a request involves model choice, cost-aware orchestration, writing or revising an academic paper, multi-stage research or coding, quality repair, or independent work that could run in parallel. The user does not need to type `$adaptive-model-router`, select a mode, or choose a model. Choose the route internally and keep routine routing invisible unless a short status notice helps.

Automatic invocation does not mean unconditional delegation. After local classification, automatically delegate when all of these are true: the task is complexity 3 or higher, it contains at least two separable deliverables or checks, collaboration tools are available, and either the root agent has useful local work that can proceed concurrently or independent validation is likely to materially improve confidence. Skip delegation for a single indivisible task, routine complexity 0–2 work, unavailable tools, conflicting workspace edits, or when the user explicitly requests single-agent or no delegation. The latest explicit user instruction overrides this automatic policy; Fast also disables GPT-6 and unnecessary delegation.

When automatic delegation is eligible, use at most `max(0, min(3, available_parallel_slots - 1))` subagents, where `available_parallel_slots` includes the root agent and reflects currently free collaboration slots. Automatic delegation may run in one wave per user task; count every spawned subagent against that task's cap. Later repair or validation stages reuse existing results or run locally. Assign each subagent one bounded role, such as retrieval/evidence extraction or verification/critique. Assign implementation only when an isolated worktree or equivalent write isolation is confirmed; otherwise keep every subagent read-only and let the root agent edit. Give each subagent only the objective, relevant files or source pointers, constraints, and a concrete deliverable. Do not pass the entire conversation by default. Delegated agents are leaves: they must not invoke this router or spawn further agents.

The root agent owns integration and the final response. A file has one writer at a time; subagents are read-only by default, and separate worktrees or other isolation are required before parallel edits when the tool supports them. Subagents return concise findings, changed paths, test evidence, and unresolved issues. The root agent resolves disagreements, applies or reviews changes, and runs the final meaningful validation. If collaboration tools are absent or fail, continue with a single agent and record that delegation was unavailable rather than pretending it occurred.

## Select a route

Classify locally; do not spend a model call just to classify an obvious request. Do not mechanically run every tier.

| Complexity | Work | Preferred model | Reasoning |
|---|---|---|---|
| 0 | Formatting, categorization, metadata | Luna | low |
| 1 | Short drafting, basic translation, simple summary | Luna; Terra if needed | low |
| 2 | Standard writing, document analysis, ordinary comparison | Terra | medium |
| 3 | Professional research, methods, coding, synthesis | Sol | medium |
| 4 | Difficult debugging, architecture, contradictory evidence | Sol | high |
| 5 | Exceptional reasoning or unresolved repeated failures | Sol, then critique/repair before GPT-6 | high |

Modes:
- **Fast:** use the lowest-cost available GPT-5-family model, normally Luna/Terra or a compatible mini model; GPT-6 is disabled. If quality requirements cannot be met, report the unresolved limitation rather than return a defective result as complete.
- **Auto (default):** use the table and escalation gate.
- **Deep:** start with Sol high, validate, and repair as needed.
- **Max:** explicit user selection permits GPT-6 directly. A request for detail alone does not mean Max. If Fast conflicts with an explicit GPT-6 request, follow the latest clear instruction or clarify the conflict.

Ordinary rewriting, website copy, email, translation, and academic polishing usually need Luna/Terra. Conceptual academic drafting and methodology usually need Sol. Length, references, files, search, and technical terminology alone never justify escalation.

## Academic paper writing

When the user is drafting, revising, translating, or preparing a journal manuscript, apply the following workflow automatically. Keep the root agent as the sole author of the integrated manuscript unless an isolated worktree is confirmed.

- For a new paper, use one delegation wave for separable preparation: evidence/retrieval planning, contribution and theoretical framing, and methods/design review. Use Luna for query planning or metadata filtering, Terra for evidence extraction, and Sol for theory, methodology, and difficult synthesis when those models are available.
- For an existing draft, use one delegation wave for independent audits: citation-to-claim alignment, argument and methods consistency, and journal/section/style compliance. Each audit must return exact locations, severity, evidence, and a repair recommendation; it must not rewrite the whole manuscript by default.
- After the wave, the root agent integrates the findings, drafts or repairs the affected sections, preserves the target journal's structure, and runs the final academic-writing validation locally. Reuse the same evidence matrix and do not start another delegation wave for ordinary line edits.
- Never invent references, findings, identifiers, quotations, page numbers, datasets, or publication credentials. Mark missing evidence and uncertainty explicitly. Separate source-backed claims, interpretations, and proposed wording.
- For empirical or methodological claims, verify operational definitions, identification assumptions, temporal ordering, limitations, and whether the proposed wording exceeds the evidence. For citations, verify that each material claim has an appropriate source and that bibliographic details match the retrieved record.

If the task is only sentence polishing after the argument and sources are settled, keep it single-agent or use one bounded language pass. If the paper requires live retrieval, use the relevant retrieval skill or tool before synthesis; do not ask a reasoning subagent to compensate for missing sources.

## Validate and repair

For difficult work, check deliverable completeness, instructions, factual evidence, citations, contradictions, unresolved issues, and relevant executable/schema checks. Prefer objective evidence over confidence. Use critique only when it can resolve a specific concern; avoid mandatory reviews of routine successful work.

Heuristic quality bands (not calibrated probabilities):
- At least 0.90: return if required checks pass.
- 0.80–0.89: return only if material requirements pass and risk is acceptable.
- 0.65–0.79: critique and repair with the strongest available GPT-5-family model.
- Below 0.65: Sol high, or the strongest available compatible model, repair first.
- Still below 0.75 after repair: escalation becomes eligible, not mandatory.

Critical errors or unmet requirements block a success claim regardless of score. Record the actual evidence behind any score; leave it null when unjustified. Allow at most two GPT-5-family repair cycles. Retrieval gaps, missing permissions, unavailable data, and broken tools should be resolved at their source rather than treated as reasoning failures.

## GPT-6 gate

Except for explicit GPT-6/Max selection, require an actual GPT-5-family attempt, validation, and targeted repair before escalation. Prefer GPT-5.6 when available; if it is unavailable, record the compatible model and its limitation. Escalate only for a remaining material problem: repeated failure of the strongest available GPT-5-family model, conflicting plausible solutions, unresolved critical contradictions, failing executable validation attributable to reasoning, or expert adjudication with a concrete expected benefit. Level 5 alone does not bypass this sequence.

Default budget: one GPT-6 dispatch per user task. A second is eligible only for technically invalid output, failed tool execution, new material information, or explicit user request. Track attempted and successful dispatches separately; avoid unbounded retries. After expert review, validate the result without automatic GPT-6 self-review loops. Report remaining limitations honestly if unresolved.

Before dispatch, send only an expert context package:

```text
TASK / USER OBJECTIVE
CURRENT STATE
RELEVANT FACTS AND SOURCE POINTERS
PREVIOUS GPT-5-FAMILY RESULT
CRITIC FINDINGS / VALIDATION EVIDENCE
FAILED APPROACHES
UNRESOLVED ISSUES
CONSTRAINTS
REQUIRED OUTPUT
```

Retain exact identifiers, source attribution, uncertainty, and constraints. Exclude duplicate passages and unrelated history. Do not omit evidence that could change the conclusion. Pass only the residual question rather than restarting the complete task.

## Context and records

Retrieve relevant material before expensive synthesis. Reuse verified work, process changed sections, and keep stable prompt prefixes where the runtime supports caching. Maintain a compact task state in the conversation or authorized task artifacts; do not write persistent user memory without explicit authorization.

For audit records, schemas, and optional operational metrics, read [references/records.md](references/records.md) only when needed. Do not display hidden reasoning. User-facing routing notices must describe actual actions, and should be brief.
