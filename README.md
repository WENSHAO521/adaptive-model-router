# Adaptive Model Router

An Agent Skill defining adaptive model-routing and orchestration policy for hosts with compatible dispatch capabilities. On hosts without dispatch, it guides feasible execution on the active model; it cannot force a model switch. This working tree prepares **v0.2.0**; a version heading does not imply a published tag or release.

## What it does

For model selection, complex coding, multi-stage research, large-context analysis, evidence-intensive papers, and difficult repair, it chooses a suitable execution path, validates the result, and bounds further reasoning and delegation. Automatic discovery stays enabled; tiny writing tasks do not need routing overhead.

## Design principle

**Minimize expected total cost per successfully validated task.** Include initial execution plus expected repair, validation, delegation, and escalation. A stronger first attempt can cost less than repeated weak attempts. This is qualitative policy, not a numerical optimizer or measured savings claim.

## Routing architecture

[SKILL.md](SKILL.md) is the lightweight kernel. It loads [routing policy](references/routing-policy.md), [delegation policy](references/delegation-policy.md), [paper workflow](references/paper-workflow.md), and [records](references/records.md) only when relevant.

The task vector separates reasoning, error impact, context volume, tools, ambiguity, verification difficulty, parallelism, and latency sensitivity. Model capability and reasoning effort are separate choices. Luna, Terra, Sol, and Astra are illustrative roles; the actual host inventory, supported effort levels, deprecation status, and current prices govern real choices.

## Policy modes

| Mode | Behavior |
|---|---|
| Economy | Prefer economical capable tiers; GPT-6 disabled unless explicitly overridden by model choice |
| Balanced | Default adaptive route, validation, repair, and gated expert escalation |
| Deep | Stronger initial reasoning/checks for demanding work; expert gate still applies |
| Expert | Explicit selection permits direct appropriate expert use; bounded calls remain |

Explicit model choices take precedence when available and permitted. Requested detail does not imply Expert mode. These names are not host UI speed or effort settings.

## Installation

Requires Git for clone commands. The skill itself needs no Python or package dependency. Python 3.13+ is used for development validation. Keep SKILL.md directly inside the adaptive-model-router folder.

### Codex

Use the current user layout from the [official Codex skill documentation](https://learn.chatgpt.com/docs/build-skills).

macOS/Linux:

```bash
mkdir -p "$HOME/.agents/skills"
git clone https://github.com/WENSHAO521/adaptive-model-router.git \
  "$HOME/.agents/skills/adaptive-model-router"
```

Windows PowerShell:

```powershell
$skillsDir = Join-Path $HOME ".agents\skills"
New-Item -ItemType Directory -Force -Path $skillsDir | Out-Null
git clone https://github.com/WENSHAO521/adaptive-model-router.git `
  (Join-Path $skillsDir "adaptive-model-router")
```

Project scope, from the project root on macOS/Linux:

```bash
mkdir -p .agents/skills
git clone https://github.com/WENSHAO521/adaptive-model-router.git \
  .agents/skills/adaptive-model-router
```

Windows PowerShell, project scope:

```powershell
New-Item -ItemType Directory -Force -Path ".agents\skills" | Out-Null
git clone https://github.com/WENSHAO521/adaptive-model-router.git `
  ".agents\skills\adaptive-model-router"
```

Update an existing user clone:

```bash
git -C "$HOME/.agents/skills/adaptive-model-router" pull --ff-only
```

```powershell
git -C (Join-Path $HOME ".agents\skills\adaptive-model-router") pull --ff-only
```

Compatibility: older or locally configured hosts may load `$CODEX_HOME/skills` or `~/.codex/skills`. Use the actual configured directory for those hosts; do not install duplicate copies into both paths. Restart Codex if the skill is not detected. The optional default prompt includes `$adaptive-model-router` as required by the bundled UI metadata schema; implicit invocation remains enabled, so manual selection is not required for matching tasks.

### Claude Code

The [official skills documentation](https://code.claude.com/docs/en/skills) specifies personal and project directories.

```bash
mkdir -p "$HOME/.claude/skills"
git clone https://github.com/WENSHAO521/adaptive-model-router.git "$HOME/.claude/skills/adaptive-model-router"
```

```powershell
$skillsDir = Join-Path $HOME ".claude\skills"
New-Item -ItemType Directory -Force -Path $skillsDir | Out-Null
git clone https://github.com/WENSHAO521/adaptive-model-router.git (Join-Path $skillsDir "adaptive-model-router")
```

Project destination: `.claude/skills/adaptive-model-router`. Start a session and check the skill menu or invoke `/adaptive-model-router`. Local installation does not install it into cloud sessions.

### Gemini CLI

The [official Agent Skills guide](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/using-agent-skills.md) provides a user installer (same command in PowerShell and macOS/Linux shells):

```text
gemini skills install https://github.com/WENSHAO521/adaptive-model-router
```

Add `--scope workspace` for the current project. Use `/skills list` to inspect and `/skills reload` to refresh.

Other Agent Skills-compatible tools need their own documented discovery directory; the shared file layout does not guarantee a universal installation path or OpenAI dispatch. For ZIP installation, use GitHub **Code → Download ZIP** and extract the folder into the host's skill directory. Clone/install commands obtain the remote version, which may differ from an unpublished local working tree.

## How routing works

Inspect capabilities → respect model choice/mode → reduce irrelevant context → infer task vector → choose capable tier → choose supported effort → apply delegation ROI → execute and validate. Repair only concrete residual defects, usually within two GPT-5-family repair cycles. For reasoning failure, consider higher effort on the same capable model before changing tier. Do not mechanically walk every step or level.

Around 200K/220K/250K input tokens, inspect necessity, prefer selective retrieval, and strongly attempt compaction. These are approximate policy warnings, not provider limits or pricing facts; actual runtime limits and thresholds take precedence. Preserve exact constraints, identifiers, citations, unresolved contradictions, and original source pointers.

Validation states are PASS, PASS_WITH_LIMITATIONS, REPAIR_REQUIRED, BLOCKED_BY_MISSING_EVIDENCE, BLOCKED_BY_TOOL_FAILURE, and ESCALATION_CANDIDATE. Critical failures block a success claim. Tests, builds, source checks, calculations, or document constraints supply evidence; confidence scores do not control escalation.

## Academic workflow

The preserved [paper workflow](references/paper-workflow.md) separates ordinary manuscripts, empirical/computational work, systematic reviews, and sentence-level polishing. It retains verified sources and persistent IDs, version/provenance records, claim-evidence mapping, baseline reproduction, leakage/variance checks, PRISMA-aware reporting, limitations, and reproducibility. Missing citations require retrieval, not an automatic stronger model.

## Delegation

Default zero; use 1–2 leaf agents only when independent work, context reduction, or validation value exceeds coordination and duplicate-token/tool costs. Three is exceptional and slot-limited. One wave, minimal task packets, no recursion, read-only workers by default. Parallel implementation requires confirmed write isolation; root integrates and validates.

## GPT-6 escalation

Except explicit GPT-6/Expert selection, require an actual GPT-5-family attempt, meaningful validation, concrete residual reasoning failure, targeted repair, and a reason more GPT-5.6 effort is inefficient. Long tasks and broken tools are not sufficient. Default one successful Astra dispatch; one additional attempt only under the documented exception, with at most two attempts absent explicit larger authorization. No expert self-review loop.

## Evaluation

From the repository root:

```bash
python scripts/validate_skill.py
python -m unittest discover -s tests -v
git diff --check
```

The standard-library validator checks required structure, this repository's restricted YAML subset, required frontmatter/metadata, JSONL schemas, duplicate IDs, fenced JSON examples, and local Markdown links. It supports inline and reference-style links outside code fences; it does not check remote URLs, heading anchors, HTML links, or every Markdown/YAML extension. Unsupported YAML constructs fail with a clear error instead of being silently accepted.

Fixtures contain **24 routing**, **8 delegation**, and **10 escalation** cases. They encode policy expectations, not model-quality results. Validation parses and checks fixture consistency; it does not run model calls or prove the policy's behavioral adherence. See the [evaluation contract](references/records.md) for a blinded host evaluation procedure. Unit tests exercise meaningful validator failures with temporary copies.

[GitHub Actions](.github/workflows/validate.yml) runs validation and validator tests on push and pull_request with Python 3.13 and read-only repository permissions. Local validation does not imply a hosted CI run passed.

## Repository structure

```text
adaptive-model-router/
  SKILL.md
  README.md
  CHANGELOG.md
  LICENSE
  THIRD_PARTY_NOTICES.md
  agents/openai.yaml
  references/
    routing-policy.md
    delegation-policy.md
    paper-workflow.md
    records.md
  evals/
    routing-cases.jsonl
    delegation-cases.jsonl
    escalation-cases.jsonl
  scripts/validate_skill.py
  tests/test_validate_skill.py
  .github/workflows/validate.yml
```

## Limitations

This is policy and orchestration guidance, not an executable routing service. Dispatch, model inventory, effort controls, context limits, caching, isolation, and prices depend on the host/provider. Other hosts can use the shared instructions but may ignore Codex metadata. No API keys, background jobs, billing enforcement, automatic releases, or benchmark infrastructure are installed. No empirical dollar/token savings or calibrated routing accuracy have been established.

## License

MIT: [LICENSE](LICENSE). Existing academic-source attribution and reviewed commits remain in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). Release preparation is recorded in [CHANGELOG.md](CHANGELOG.md).
