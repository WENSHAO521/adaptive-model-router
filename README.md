# Adaptive Model Router

An automatic Codex skill for capability-aware model routing, bounded subagent delegation, evidence-first academic writing, quality repair, and controlled expert escalation.

## What it does

- Activates implicitly for model choice, research, coding, manuscript work, and multi-stage tasks.
- Discovers the host's available model IDs and reasoning levels at runtime.
- Prefers the least-cost capable GPT-5-family model under the active policy.
- Delegates separable complex work automatically when collaboration tools and useful parallel work are available.
- Uses one bounded delegation wave per user task and keeps the root agent responsible for integration and validation.
- Applies an evidence-first paper workflow: frame the contribution, search and verify sources, map claims to evidence, check methods and reproducibility, and audit the final manuscript.
- Uses a PRISMA-aware branch for systematic reviews without forcing PRISMA onto ordinary papers.
- Escalates to GPT-6 only after a validated GPT-5-family attempt and targeted repair, unless the user explicitly selects GPT-6 or Max mode.

The academic workflow is an original synthesis of openly licensed practices. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) and [references/paper-workflow.md](references/paper-workflow.md) for source commits, licenses, and the integration boundary.

## Installation

The mainstream installation is a Git clone into the Codex skills directory. Restart Codex or start a new task after installing so the skill index can refresh.

### macOS or Linux

```bash
skills_dir="${CODEX_HOME:-$HOME/.codex}/skills"
mkdir -p "$skills_dir"
git clone https://github.com/WENSHAO521/adaptive-model-router.git "$skills_dir/adaptive-model-router"
```

To update an existing clone:

```bash
git -C "${CODEX_HOME:-$HOME/.codex}/skills/adaptive-model-router" pull --ff-only
```

### Windows PowerShell

```powershell
$codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME ".codex" }
$skillsDir = Join-Path $codexHome "skills"
New-Item -ItemType Directory -Force -Path $skillsDir | Out-Null
git clone https://github.com/WENSHAO521/adaptive-model-router.git (Join-Path $skillsDir "adaptive-model-router")
```

To update an existing clone:

```powershell
$codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME ".codex" }
$skillsDir = Join-Path $codexHome "skills"
git -C (Join-Path $skillsDir "adaptive-model-router") pull --ff-only
```

If Git is unavailable, use GitHub's **Code → Download ZIP**, extract the repository, and place its contents at `$CODEX_HOME/skills/adaptive-model-router` (normally `C:\Users\<you>\.codex\skills\adaptive-model-router` on Windows). Keep `SKILL.md` directly inside that folder.

## Automatic behavior

No mode or skill selection is required. `agents/openai.yaml` enables implicit invocation. Explicit `$adaptive-model-router` invocation remains available for troubleshooting or a deliberate rerun, but it is not the normal workflow.

## Contents

- `SKILL.md` — automatic routing, delegation, paper workflow, validation, and escalation policy
- `references/paper-workflow.md` — integrated academic workflow and source boundary
- `references/records.md` — optional audit record schemas and telemetry guidance
- `agents/openai.yaml` — display metadata and implicit-invocation policy
- `THIRD_PARTY_NOTICES.md` — source, license, commit, and attribution record
- `CHANGELOG.md` — release history
- `LICENSE` — MIT license for this package

The skill is guidance for an available Codex dispatch or collaboration surface. It does not itself change the model already running a turn, create GitHub repositories, enforce billing limits, or guarantee that every host exposes the same model IDs.

## License

MIT. See [LICENSE](LICENSE). The integrated workflow contains original wording and attribution to the compatible open-source sources listed in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
