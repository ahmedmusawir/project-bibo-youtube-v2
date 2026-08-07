# stark-showcase-readme

**Type:** Stark Skill (guidance, semi-execution) · **Version:** 1.0

Prepares a repository for public showcase: sweeps it for exposure, verifies its facts against
disk, and builds a factory-standard README with images, diagrams, and video walkthroughs.

## Activation

```
Go read _SKILLS/stark-showcase-readme/CLAUDE.md and follow it.
```

That is the whole activation contract. No magic prompt, no pre-baked context block. The skill
runs its own environment discovery, classifies the repo, and asks only for what disk cannot
answer.

## What it does

| Phase | Output |
|---|---|
| 0 — Orient | Discovery, repo classification, Plan Mode → **awaits APPROVED** |
| 1 — Sweep | Labeled, severity-triaged findings report → **stops for decisions** |
| 2 — Facts | Every badge-bound number earned off disk |
| 3 — Assets | Asks for images, diagrams, videos, story context → **stops** |
| 4 — Build | README rendered for review, then written → **READY FOR COMMIT** |

## What it does not do

- **Run git.** Ever. Rule Zero. The operator commits, pushes, and untracks; the agent hands
  over copy-paste command blocks.
- **Fix what it finds.** Vulnerabilities, auth weaknesses, and architectural debt are reported
  with file:line and scoped as separate work.
- **Modify the repo** beyond `README.md`, `.gitignore`, and `.env.example` — and the latter two
  only when a disposition decision authorizes it.
- **Deploy, migrate, or refactor.** Different skills, different missions.

## Install

Copy the folder into the repo's `.claude/skills/` for auto-discovery, or point the agent at
its path in `_SKILLS/`. Note the Launch-CWD Rule: skills resolve from the directory the agent
was launched from, not the repo root you have in mind.

## Structure

```
CLAUDE.md          doctrine — read first, always
SKILL.md           methodology spine, phases and gates
workflow/          phase detail, 00 → 04
references/        sweep checklist, anti-patterns, express and clean-room flows
decision-trees/    flow selection, finding severity
templates/         README format, sweep report format
examples/          populated after successful runs
```

## Companion

`stark-benchmark/` — the eval scorecard and ledger template used when scoring a model that
ran this skill. Separate concern, separate folder, deliberately not bundled here.
