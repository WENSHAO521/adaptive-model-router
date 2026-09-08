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

This repository is a standalone Agent Skill. Keep `SKILL.md` directly inside the `adaptive-model-router` folder. Git clone is the recommended installation; use the host-specific destination below.

### Codex

Current Codex documentation uses `~/.agents/skills` for user skills. Older or locally configured installations may use `$CODEX_HOME/skills`; set `CODEX_SKILLS_DIR` when you want to choose the destination explicitly. Repository-scoped skills go in `.agents/skills`.

macOS or Linux, user scope:

```bash
skills_dir="${CODEX_SKILLS_DIR:-${CODEX_HOME:+$CODEX_HOME/skills}}"
skills_dir="${skills_dir:-$HOME/.agents/skills}"
mkdir -p "$skills_dir"
git clone https://github.com/WENSHAO521/adaptive-model-router.git "$skills_dir/adaptive-model-router"
```

Windows PowerShell, user scope:

```powershell
$skillsDir = if ($env:CODEX_SKILLS_DIR) {
  $env:CODEX_SKILLS_DIR
} elseif ($env:CODEX_HOME) {
  Join-Path $env:CODEX_HOME "skills"
} elseif (Test-Path (Join-Path $HOME ".codex\skills")) {
  Join-Path $HOME ".codex\skills"
} else {
  Join-Path $HOME ".agents\skills"
}
New-Item -ItemType Directory -Force -Path $skillsDir | Out-Null
git clone https://github.com/WENSHAO521/adaptive-model-router.git (Join-Path $skillsDir "adaptive-model-router")
```

Repository scope, from the project root:

```bash
mkdir -p .agents/skills
git clone https://github.com/WENSHAO521/adaptive-model-router.git .agents/skills/adaptive-model-router
```

Update an existing Codex clone:

```bash
git -C "${CODEX_SKILLS_DIR:-${CODEX_HOME:-$HOME/.agents}/skills}/adaptive-model-router" pull --ff-only
```

```powershell
$skillsDir = if ($env:CODEX_SKILLS_DIR) {
  $env:CODEX_SKILLS_DIR
} elseif ($env:CODEX_HOME) {
  Join-Path $env:CODEX_HOME "skills"
} elseif (Test-Path (Join-Path $HOME ".codex\skills")) {
  Join-Path $HOME ".codex\skills"
} else {
  Join-Path $HOME ".agents\skills"
}
git -C (Join-Path $skillsDir "adaptive-model-router") pull --ff-only
```

Start a new Codex task after installing; restart Codex only if the skill still does not appear.

### Claude Code

Claude Code discovers personal skills from `~/.claude/skills/<skill-name>/SKILL.md` and project skills from `.claude/skills/<skill-name>/SKILL.md`.

macOS or Linux:

```bash
mkdir -p "$HOME/.claude/skills"
git clone https://github.com/WENSHAO521/adaptive-model-router.git "$HOME/.claude/skills/adaptive-model-router"
```

Windows PowerShell:

```powershell
$skillsDir = Join-Path $HOME ".claude\skills"
New-Item -ItemType Directory -Force -Path $skillsDir | Out-Null
git clone https://github.com/WENSHAO521/adaptive-model-router.git (Join-Path $skillsDir "adaptive-model-router")
```

Open Claude Code and run `/skills` to confirm discovery. For a project-only install, clone into `.claude/skills/adaptive-model-router` from that project root.

### Gemini CLI

Gemini CLI provides a direct installer:

```bash
gemini skills install https://github.com/WENSHAO521/adaptive-model-router
```

The equivalent user-scope Git clone is:

```bash
mkdir -p "$HOME/.gemini/skills"
git clone https://github.com/WENSHAO521/adaptive-model-router.git "$HOME/.gemini/skills/adaptive-model-router"
```

Use `/skills list` to verify it and `/skills reload` after an update. Project-only skills go in `.gemini/skills/adaptive-model-router`.

### Other Agent Skills-compatible tools

Tools that follow the open Agent Skills layout generally accept `~/.agents/skills/<skill-name>/SKILL.md` for user scope or `.agents/skills/<skill-name>/SKILL.md` for project scope:

```bash
mkdir -p "$HOME/.agents/skills"
git clone https://github.com/WENSHAO521/adaptive-model-router.git "$HOME/.agents/skills/adaptive-model-router"
```

Windows PowerShell:

```powershell
$skillsDir = Join-Path $HOME ".agents\skills"
New-Item -ItemType Directory -Force -Path $skillsDir | Out-Null
git clone https://github.com/WENSHAO521/adaptive-model-router.git (Join-Path $skillsDir "adaptive-model-router")
```

`agents/openai.yaml` is optional Codex metadata. Other hosts use the shared `SKILL.md` frontmatter and ignore that file when they do not support it.

If Git is unavailable, use GitHub's **Code → Download ZIP**, extract the repository, and place its contents in the host's skill directory. Keep `SKILL.md` directly inside the `adaptive-model-router` folder.

No package manager or Python dependency is required at runtime; the skill is Markdown plus YAML and is loaded from the skills directory.

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
