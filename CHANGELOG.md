# Changelog

## v0.3.0 — 2026-09-09

- Added a named budget controller (`max_delegates`, `max_repair_cycles`, `max_expert_calls`, `max_expensive_calls`) consolidating the existing delegation, repair, and expert-call caps with explicit soft/hard semantics; no cap values changed.
- Added a compact, reusable task-state schema (files_read, sources_verified, failed_attempts, unresolved_issues, completed_stages, reusable_results) for reuse-before-recompute within one task; explicitly not long-term user memory.
- Added an explicit stop rule to the kernel to prevent open-ended repair/escalation cycling once the deliverable, validation, and no-critical-issue conditions are all met.
- Defined the previously-unspecified `gpt6_reason` vocabulary as six escalation reason codes (REASONING_FAILURE, EVIDENCE_GAP, TOOL_FAILURE, CONTEXT_LIMIT, VALIDATION_FAILURE, USER_EXPERT_REQUEST); only two of them authorize the expert gate by themselves.
- Added optional, non-hard-dependent interoperability with an external EXECUTION_POLICY_V1 object (for example from scholarly-agent-suite): its mode maps to a policy mode and its policy fields layer onto the budget controller as soft inputs. The skill remains fully standalone.
- Hardened Codex, Claude Code, Gemini CLI, Git, and ZIP installation/update guidance, including discovery verification and pinned versions.
- Clarified the bundled default_prompt convention as repository policy.
- Added VERSION consistency checks and deterministic nine-file runtime ZIP packaging with SHA-256 and a generated manifest.
- Added source/runtime validation, allowlist and linked-path protection, extracted-package checks, and packaging regression tests (`tests/test_package_runtime.py`, 17 cases).
- Fixed a `Path.is_junction()` crash on Python versions older than 3.12 in the source/runtime validator.
- Extended CI to validate packaging and documented a publish-after-validation release checklist.
- Updated repository positioning for cost-aware cross-host orchestration. The v0.2 routing architecture is unchanged; this is an additive minor release.

## v0.2.0 — 2026-09-09

Prepared for release; no tag or GitHub release is implied.

- Refactored the lightweight Router kernel with progressively loaded routing and delegation policies.
- Separated task-vector classification, model selection, and supported reasoning effort; prefer useful same-model reasoning escalation before tier changes.
- Added long-context cost and utility gates, runtime capability discovery, and a deprecated-model guard.
- Replaced quality-score routing with evidence-based validation states and a failure taxonomy; bounded residual repairs and expert dispatches.
- Added conservative delegation ROI, minimal packets, one-wave leaf agents, and write isolation.
- Preserved the evidence-first academic workflow and existing third-party attribution.
- Added 24 routing, 8 delegation, and 10 escalation fixtures, a standard-library validator, and negative-path validator tests.
- Added minimal GitHub Actions validation on push and pull_request.
- Simplified mainstream Codex installation and clarified cross-host dispatch limitations.

## 2026-09-08

- Added mainstream Git clone, update, and ZIP installation instructions for macOS, Linux, and Windows PowerShell.
- Added an evidence-first academic paper workflow with ordinary-paper, empirical, systematic-review, and language-pass branches.
- Added claim-to-evidence, provenance, identifier, version, reproducibility, leakage, variance, and PRISMA 2020 checks.
- Added third-party notices for the openly licensed public projects whose practices informed the synthesis.
- Updated the implicit-invocation metadata and audit record schema.
