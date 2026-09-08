# Adaptive Model Router

An automatic Codex skill for capability-aware model routing, bounded subagent delegation, quality repair, and compressed expert escalation.

## What it does

- Invokes implicitly for model selection, research, coding, manuscript work, and multi-stage tasks.
- Prefers the least-cost available capable GPT-5-family model and discovers host capabilities at runtime.
- Automatically delegates separable complex work when collaboration tools are available.
- Uses one delegation wave per user task, with at most three subagents and no recursive delegation.
- Keeps the root agent responsible for integration, source integrity, and final validation.
- Escalates to GPT-6 only after a validated GPT-5-family attempt and targeted repair, unless the user explicitly selects GPT-6 or Max mode.

For academic papers, the automatic workflow can split evidence planning, theoretical or methodological review, citation alignment, argument consistency, and journal-format checks into bounded roles. The root agent writes and integrates the manuscript. It must not invent references, findings, identifiers, quotations, page numbers, or publication credentials.

## Installation

Copy this folder into the Codex skills directory as `adaptive-model-router`. The `agents/openai.yaml` policy enables implicit invocation. Explicit invocation with `$adaptive-model-router` remains available when useful.

## Contents

- `SKILL.md` — routing and delegation policy
- `references/records.md` — optional audit record schemas and telemetry guidance
- `agents/openai.yaml` — display metadata and implicit-invocation policy

The skill is guidance for an available Codex dispatch or collaboration surface. It does not itself change the model already running a turn, create GitHub repositories, enforce billing limits, or guarantee that every host exposes the same model IDs.

## License

MIT. See [LICENSE](LICENSE).
