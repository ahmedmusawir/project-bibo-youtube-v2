# 00 — Orient

**Goal:** Know what you are holding. Present a Plan the operator can approve or correct.

Nothing is written in this phase. No questions are asked before discovery runs.

---

## Discovery sequence

Run all of it before forming any question. Every answer you find here is an answer you must
not ask for — that is Anti-Pattern 6 in the factory playbook.

```bash
pwd
ls -la
find . -maxdepth 2 -type d -not -path "*/node_modules*" -not -path "*/.git*" | sort

git remote -v
git status --short | head -20
git log --oneline -5
git ls-files | wc -l

cat package.json 2>/dev/null || cat pyproject.toml requirements.txt 2>/dev/null
cat .gitignore 2>/dev/null
cat README.md 2>/dev/null

ls -la docs/ agent_docs/ _SKILLS/ _design/ logs/ temp/ uploads/ 2>/dev/null
git ls-files | grep -iE "\.env|SESSION|RECOVERY|-org\.|CLAUDE\.md|AGENTS\.md"
```

## What discovery must tell you

- **Tree state.** Is this committed, partially committed, or a fresh working tree? This
  changes how the sweep must be scoped in Phase 1. A tree with one committed file and 115
  untracked ones will pass every tracked-file check vacuously.
- **Stack and versions.** From the manifest, not from the README's claims.
- **Existing README.** What is already there — diagrams, screenshots, videos, structure. You
  may be augmenting. Read it before you plan to replace anything.
- **Content classes present.** Factory internals, logs, uploads, temp dirs, `-org` fossils,
  design folders.
- **Existing fence.** What `.gitignore` already covers, and what it conspicuously does not.

## Repo classification

Classify before planning. The class weights the sweep.

| Class | Signals | Sweep weight |
|---|---|---|
| **Production client app** | Live URL, payments, deploy configs, client naming | Customer data, live credentials, client identity, infra topology |
| **FFM / staged** | Mock layer with a service-boundary swap point, real auth, staging deploy | Compliance wording, seeded demo people, mock-data doctrine |
| **Lab / harness** | Eval receipts, test corpora, API-key tooling, CLI entry points | Personal documents in corpora, API keys, store IDs, receipts |
| **Legacy / manual-era** | Pre-doctrine structure, `-org` backups, tracked session files, committed logs | Committed logs, fossils, session files, pre-doctrine auth patterns |

If the repo straddles two classes, sweep for both. Classification is a weighting, not an
exemption.

## Flow selection

Consult `decision-trees/flow-selection.md`. Default is the full flow. Express requires an
explicit operator request *and* a repo that qualifies. Clean-room is selected by evidence,
not preference.

## The Plan

Present four blocks and one closing line.

**Observed** — repo name and remote, tree state, class, stack and versions, what the existing
README already contains, which content classes are present. Concrete, not narrative.

**Intended** — the flow selected and why, the phases in order, what artifacts you will
produce, what you will and will not touch.

**Unknown** — only what disk cannot answer. Typically:
- Is the deployment live, staged, or retired? (changes badges and tense)
- Is the code the operator's to show, and are there constraints on what may be claimed?
- Production dates, client context, hand-built vs factory-built history
- Anything he wants specifically claimed or not claimed

**Risks** — anything discovery already surfaced that is likely to become a blocker. Naming
it now saves an hour later.

**Closing line** — *"Awaiting your APPROVED before proceeding."*

## Stop Gate

No file writes. No Phase 1. Wait for explicit approval. If the operator answers questions or
pushes back, revise and re-present.

## Output

Plan Mode summary in chat.
