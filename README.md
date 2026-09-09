# Adaptive Model Router

An Agent Skill defining adaptive model-routing and orchestration policy for hosts with compatible dispatch capabilities. On hosts without dispatch, it guides feasible execution on the active model; it cannot force a model switch. Repository version: **v0.3.0**. See [GitHub Releases](https://github.com/WENSHAO521/adaptive-model-router/releases) for published versions and frozen artifacts.

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

Documentation last verified: 2026-09-09. Host-specific discovery rules take precedence if they change. **Python is not required to use this skill.** Git installs include development files; the released runtime ZIP contains only nine runtime/documentation files.

### Codex: Skill Installer

Where your Codex environment provides it, invoke:

```text
$skill-installer
```

Then ask it to install the skill at the root of:

```text
https://github.com/WENSHAO521/adaptive-model-router
```

The [official Codex documentation](https://learn.chatgpt.com/docs/build-skills) supports prompting the installer to use another repository. The installer manages the destination; inspect its reported path. Do not also clone a duplicate copy. Manual installation remains available when the installer is absent.

### Codex: manual Git installation

For a rolling user installation on macOS/Linux:

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

Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force -Path ".agents\skills" | Out-Null
git clone https://github.com/WENSHAO521/adaptive-model-router.git `
  ".agents\skills\adaptive-model-router"
```

Older/configured hosts may load `$CODEX_HOME/skills` or `~/.codex/skills`. Use the host's actual directory rather than duplicating installation. The bundled default prompt explicitly references `$adaptive-model-router` for clear manual invocation. Our validator enforces this as **repository policy**, not a universal upstream schema requirement. Implicit invocation remains enabled for matching tasks.

### Verify installation

1. Start or reopen Codex and check its available skills UI/command when supported.
2. Confirm **Adaptive Model Router** appears.
3. Optionally invoke `$adaptive-model-router` and try the following smoke test.

```text
Use $adaptive-model-router and briefly explain the policy for:
"Translate this two-sentence email."
```

Expected policy: economical capable execution, zero subagents, no new GPT-6 dispatch. Without dispatch, use the active model. Ask for a short policy explanation, not private reasoning. This is a smoke test, not evidence that a model switch occurred or a quality/cost benchmark.

For a Git installation, identify its state and installed commit:

```bash
git -C "$HOME/.agents/skills/adaptive-model-router" status
git -C "$HOME/.agents/skills/adaptive-model-router" rev-parse HEAD
```

```powershell
git -C (Join-Path $HOME ".agents\skills\adaptive-model-router") status
git -C (Join-Path $HOME ".agents\skills\adaptive-model-router") rev-parse HEAD
```

Use the project/installer-managed path instead if that is where you installed it. These checks identify checkout state; they are not exhaustive corruption checks. Runtime users do not need to run Python tests.

### Claude Code

The [official skills guide](https://code.claude.com/docs/en/skills) specifies the personal directory:

```bash
mkdir -p "$HOME/.claude/skills"
git clone https://github.com/WENSHAO521/adaptive-model-router.git "$HOME/.claude/skills/adaptive-model-router"
```

```powershell
$skillsDir = Join-Path $HOME ".claude\skills"
New-Item -ItemType Directory -Force -Path $skillsDir | Out-Null
git clone https://github.com/WENSHAO521/adaptive-model-router.git (Join-Path $skillsDir "adaptive-model-router")
```

Project destination: `.claude/skills/adaptive-model-router`. Reopen a session, check discovery, and where supported invoke `/adaptive-model-router`. Local installation does not install into cloud/web sessions.

### Gemini CLI

The [official Agent Skills guide](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/using-agent-skills.md) provides this command in either shell:

```text
gemini skills install https://github.com/WENSHAO521/adaptive-model-router
```

Add `--scope workspace` for the current project. Verify with `/skills list`, refresh with `/skills reload`, and follow the installed CLI's management instructions for updates.

Every host determines its own discovery directories and metadata support. `SKILL.md` is the portable core; `agents/openai.yaml` is Codex-specific metadata and may be ignored elsewhere. Installation does not grant model/provider access.

### Released runtime ZIP

Download the versioned runtime ZIP and matching `.sha256` attachment from [GitHub Releases](https://github.com/WENSHAO521/adaptive-model-router/releases). For v0.3.0 the names are `adaptive-model-router-v0.3.0.zip` and `adaptive-model-router-v0.3.0.zip.sha256`. The release page is authoritative about publication; a local version file alone is not a release.

Check the archive against the downloaded sidecar, in the download directory:

```bash
# Linux:
sha256sum -c adaptive-model-router-v0.3.0.zip.sha256
# macOS:
shasum -a 256 -c adaptive-model-router-v0.3.0.zip.sha256
```

```powershell
$archive = "adaptive-model-router-v0.3.0.zip"
$expected = ((Get-Content -Raw "$archive.sha256").Trim() -split '\s+')[0]
$actual = (Get-FileHash -Algorithm SHA256 -LiteralPath $archive).Hash
if ($actual -ine $expected) { throw "SHA-256 mismatch" }
"SHA-256 verified"
```

Extract to a temporary folder, then move the single inner `adaptive-model-router` folder to the host's skill directory. For Codex user scope the result must be:

```text
$HOME/.agents/skills/adaptive-model-router/SKILL.md
```

Do not accidentally create `adaptive-model-router/adaptive-model-router/SKILL.md` by copying an extra extraction wrapper. Inspect existing installations before replacement. A checksum verifies the downloaded bytes against the supplied sidecar, not independent publisher authenticity.

GitHub's automatic **Source code ZIP/tarball** includes the whole source repository and developer tooling. The custom **runtime ZIP** is the recommended frozen artifact for stable users; Git installation does not require it.

### Update an existing installation

**Tracking main:** inspect `git status` at the same installed path before updating. Commit, stash, or copy local edits first; do not discard them automatically.

```bash
git -C "$HOME/.agents/skills/adaptive-model-router" pull --ff-only
```

```powershell
git -C (Join-Path $HOME ".agents\skills\adaptive-model-router") pull --ff-only
```

For project or Claude installations, replace the destination with the actual install directory. Installer-managed non-Git installations should use the host's supported update workflow.

**Pinned Git:** after the corresponding release tag exists, use an empty destination. Create the parent directory using the earlier instructions:

```bash
git clone --branch v0.3.0 --depth 1 \
  https://github.com/WENSHAO521/adaptive-model-router.git \
  "$HOME/.agents/skills/adaptive-model-router"
```

```powershell
git clone --branch v0.3.0 --depth 1 `
  https://github.com/WENSHAO521/adaptive-model-router.git `
  (Join-Path $HOME ".agents\skills\adaptive-model-router")
```

A tag checkout is detached and fixed; `git pull` does not make it track main. To upgrade later, preserve local edits, enter that installed directory, run `git fetch --tags`, then `git checkout --detach <published-tag>` with an existing release tag. Do not type the placeholder literally. Main follows repository changes; published version tags are never moved.

**ZIP:** download and verify the chosen newer release, extract separately, back up the installed folder/local customizations, and replace it with the verified single runtime folder. Do not merge a runtime ZIP over a Git checkout. Reload the host and repeat discovery verification.

### Troubleshooting

| Symptom | Check before reinstalling |
|---|---|
| Skill does not appear | Actual discovery directory, direct SKILL.md placement, duplicate copies, host reload/restart, current host rules |
| Explicit invocation fails | Skill discovery, exact name, host-specific command syntax |
| Git update fails | Installed-path git status, local edits, detached tag, network access, moved repository |
| ZIP not discovered | Extra wrapper or double nested adaptive-model-router folder |
| Router does not switch models | Host must expose real model dispatch; the skill cannot force it |


## How routing works

Inspect capabilities → respect model choice/mode → reduce irrelevant context → infer task vector → choose capable tier → choose supported effort → apply delegation ROI → execute and validate. Repair only concrete residual defects, usually within two GPT-5-family repair cycles. For reasoning failure, consider higher effort on the same capable model before changing tier. Do not mechanically walk every step or level.

Around 200K/220K/250K input tokens, inspect necessity, prefer selective retrieval, and strongly attempt compaction. These are approximate policy warnings, not provider limits or pricing facts; actual runtime limits and thresholds take precedence. Preserve exact constraints, identifiers, citations, unresolved contradictions, and original source pointers.

Validation states are PASS, PASS_WITH_LIMITATIONS, REPAIR_REQUIRED, BLOCKED_BY_MISSING_EVIDENCE, BLOCKED_BY_TOOL_FAILURE, and ESCALATION_CANDIDATE. Critical failures block a success claim. Tests, builds, source checks, calculations, or document constraints supply evidence; confidence scores do not control escalation.

**Stop rule:** stop once the deliverable exists, validation reached PASS (or a disclosed noncritical PASS_WITH_LIMITATIONS), and no critical issue remains. Do not keep repairing, delegating, or escalating past that point, and never cycle past the [budget controller](references/routing-policy.md#budget-controller)'s repair-cycle and expert-call caps.

**Budget controller:** a named, compact view of the caps already enforced above (`max_delegates`, `max_repair_cycles`, `max_expert_calls`, `max_expensive_calls`), each marked soft (can be exceeded with a stated reason, still gated) or hard (never exceeded). See [routing policy](references/routing-policy.md#budget-controller) for defaults and an optional mapping from an external `EXECUTION_POLICY_V1` object, when a host supplies one; this skill never requires it.

**Task state:** an optional compact `files_read` / `sources_verified` / `failed_attempts` / `unresolved_issues` / `completed_stages` / `reusable_results` record for reusing already-done work within one task instead of recomputing it. See [task state](references/records.md#task-state-reuse-before-recompute); it is not long-term user memory.

**Escalation reason codes:** `gpt6_reason` uses one of REASONING_FAILURE, EVIDENCE_GAP, TOOL_FAILURE, CONTEXT_LIMIT, VALIDATION_FAILURE, or USER_EXPERT_REQUEST — see [escalation reason codes](references/routing-policy.md#escalation-reason-codes). Only the first and last authorize the expert gate by themselves.

## Academic workflow

The preserved [paper workflow](references/paper-workflow.md) separates ordinary manuscripts, empirical/computational work, systematic reviews, and sentence-level polishing. It retains verified sources and persistent IDs, version/provenance records, claim-evidence mapping, baseline reproduction, leakage/variance checks, PRISMA-aware reporting, limitations, and reproducibility. Missing citations require retrieval, not an automatic stronger model.

## Delegation

Default zero; use 1–2 leaf agents only when independent work, context reduction, or validation value exceeds coordination and duplicate-token/tool costs. Three is exceptional and slot-limited. One wave, minimal task packets, no recursion, read-only workers by default. Parallel implementation requires confirmed write isolation; root integrates and validates.

## GPT-6 escalation

Except explicit GPT-6/Expert selection, require an actual GPT-5-family attempt, meaningful validation, concrete residual reasoning failure, targeted repair, and a reason more GPT-5.6 effort is inefficient. Long tasks and broken tools are not sufficient. Default one successful Astra dispatch; one additional attempt only under the documented exception, with at most two attempts absent explicit larger authorization. No expert self-review loop.

## Runtime versus development

Runtime use needs SKILL.md, agents/openai.yaml, the four references, LICENSE, THIRD_PARTY_NOTICES.md, and optionally README. The runtime archive includes all nine. Contributors use the complete source checkout, including evals, scripts, tests, CI, CHANGELOG, and VERSION. Python 3.13+ is used only for development, validation, packaging, and CI.

## Evaluation and packaging

From the source repository root:

```bash
python scripts/validate_skill.py
python -m unittest discover -s tests -v
git diff --check
python scripts/package_runtime.py
python scripts/package_runtime.py --verify dist/adaptive-model-router-v0.3.0.zip
```

The standard-library source validator checks required structure, this repository's restricted YAML subset, required frontmatter/metadata, JSONL schemas, duplicate IDs, fenced JSON examples, and local Markdown links. It supports inline and reference-style links outside code fences; it does not check remote URLs, heading anchors, HTML links, or every Markdown/YAML extension. Unsupported YAML constructs fail with a clear error instead of being silently accepted.

Fixtures contain **24 routing**, **8 delegation**, and **10 escalation** cases. They encode policy expectations, not model-quality results. Validation parses and checks fixture consistency; it does not run model calls or prove the policy's behavioral adherence. See the [evaluation contract](references/records.md) for a blinded host evaluation procedure. Unit tests exercise meaningful validator failures with temporary copies.

[GitHub Actions](.github/workflows/validate.yml) runs source validation, all tests, and a runtime build with extracted-package validation on push and pull_request, using Python 3.13 and read-only permissions. Ordinary pushes do not publish releases.

[VERSION](VERSION) is canonical; source validation checks README and the latest CHANGELOG heading against it. Optional `--version 0.3.0` asserts the build version rather than overriding it. The builder uses an explicit nine-file allowlist, rejects linked paths, normalizes UTF-8 text to LF, sorts members, fixes ZIP timestamps/permissions, and uses stored entries to avoid compression-library differences. Development-only README links become version-tag source URLs in the runtime copy; routing policy text is unchanged.

Output in ignored `dist/`: the versioned ZIP, its SHA-256 sidecar, and `release-manifest.json` with version, file list, per-file hashes, and archive hash. The manifest is for maintainers and is not embedded or required by hosts. ZIP verification checks exact allowlisted members before extracting to a temporary directory and runs shared runtime validation. The allowlist excludes developer files and secret-named files; content review remains necessary because filenames cannot prove absence of secrets.

To validate a separately extracted runtime folder from a source checkout:

```bash
python scripts/validate_skill.py --mode runtime --root /path/to/adaptive-model-router
```

Runtime validation retains entrypoint, metadata, JSON example, and local-link checks without requiring tests/evals/CI. See [release checklist](RELEASE_CHECKLIST.md) for the manual publish-after-CI workflow. Release automation is optional; building locally needs no GitHub permissions. Local tests alone do not imply hosted CI passed.

## Repository structure

```text
adaptive-model-router/
  SKILL.md
  README.md
  CHANGELOG.md
  VERSION
  RELEASE_CHECKLIST.md
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
  scripts/package_runtime.py
  tests/test_validate_skill.py
  tests/test_package_runtime.py
  .github/workflows/validate.yml
```

## Limitations

This is policy and orchestration guidance, not an executable routing service. Dispatch, model inventory, effort controls, context limits, caching, isolation, and prices depend on the host/provider. Other hosts can use the shared instructions but may ignore Codex metadata. No API keys, background jobs, billing enforcement, automatic releases, or benchmark infrastructure are installed. No empirical dollar/token savings or calibrated routing accuracy have been established.

## Versioning

PATCH covers installation, documentation, validation, and compatibility fixes; MINOR adds routing capabilities or major policy features; MAJOR signals incompatible layout or behavior. This is a maintenance policy, not a promised roadmap.

## License

MIT: [LICENSE](LICENSE). Existing academic-source attribution and reviewed commits remain in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). Release preparation is recorded in [CHANGELOG.md](CHANGELOG.md).
