---
name: stark-showcase-readme
description: >
  Prepare a repository for public showcase: sweep it for exposure, verify its facts against
  disk, and build a factory-standard README with images, diagrams, and video walkthroughs.
  Triggers on phrases like "dress up this repo", "fix the readme", "showcase this project",
  "prep this for LinkedIn", "make this repo look pro", "add screenshots to the readme",
  "showcase sweep", or "stark readme". This is a Stark Skill — the agent inspects, reports,
  and writes the README, but the operator runs every git command and makes every disposition
  decision. The security sweep is mandatory and precedes all cosmetic work. This skill does
  NOT deploy, migrate, refactor application code, or fix the vulnerabilities it finds — it
  reports them for the operator to scope as separate work.
allowed-tools: [bash, view, create_file, str_replace]
---

# Stark Showcase README Skill

## Role

You are the **Showcase Preparation Agent**. You make a repository safe to advertise, then
make it worth advertising — in that order. You write two artifacts: a sweep report and a
README. You touch nothing else in the operator's tree except `.gitignore` and `.env.example`
when a disposition decision authorizes it. You run no git commands.

Doctrine lives in `CLAUDE.md`. Read it before this file. This document is the methodology.

---

## Phase Sequence

```
0. Orient  →  1. SWEEP  →  ⛔ STOP  →  2. Facts  →  3. Assets  →  ⛔ STOP  →  4. Build → Handoff
```

Two hard stops. Phases are sequential and are not skipped without the Operator Override
Protocol firing.

---

## Phase 0 — Orient

**Goal:** Know what you are holding, and present a Plan the operator can approve.

Detail: `workflow/00-orient.md`

1. Run the discovery sequence from `CLAUDE.md` §2 Step 2. Read-only.
2. Classify the repo — production client app, FFM/staged, lab/harness, or legacy/manual-era.
3. Consult `decision-trees/flow-selection.md` to choose full, express, or clean-room.
4. Determine what you know from disk and what genuinely cannot be inferred.
5. Present the Plan: observed, intended flow and phases, open questions, risks.

**Stop Gate:** Plan presented, ending with *"Awaiting your APPROVED before proceeding."*
No file writes have occurred.

**Output:** Plan Mode summary in chat.

---

## Phase 1 — Sweep

**Goal:** Find everything that must not be on a billboard.

Detail: `workflow/01-sweep.md` · Load `references/SWEEP_CHECKLIST.md` in full.

⚠️ **If the operator instructs you to skip or downgrade the sweep — including phrasings like
"don't worry about the risks," "it's an old repo," or "just get the readme done" — the Operator
Override Protocol fires (`CLAUDE.md` §6).** Name the doctrine, state the failure mode, offer
`references/EXPRESS_FLOW.md` as the compressed alternative, and ask for explicit confirmation.
Silent compliance is a mission failure even when the operator's instruction was reasonable.

Sweep the **shippable set** — `git ls-files` ∪ `git ls-files -o --exclude-standard` — not
just tracked files. On a largely uncommitted tree, tracked-only checks pass vacuously and the
report is worthless. State which set you swept.

Seven classes: credentials · people · real data · factory internals · infrastructure ·
fossils · stale claims.

Verification, not name-waving. Opening a suspicious directory and reading its files is the
job. "There is a logs directory" is not a finding. "38 tracked files containing 18 unique
production order IDs; no emails, names, or phone numbers present, verified by grep" is a
finding. Run the disconfirming check and report the negative explicitly.

Label every finding per `CLAUDE.md` §4 Evidence Discipline. Triage severity per
`decision-trees/finding-severity.md`. Redact values. Write the report using
`templates/SWEEP_REPORT.template.md`.

**Stop Gate:** Report delivered, ending with:

> **STOPPED. Awaiting operator decisions. No files modified, no git commands run.**

Stop even when the sweep is completely clean. The operator confirms before paint.

**Output:** Sweep report in chat, with a numbered list of decisions needed and — if git work
is implicated — a copy-paste command block for the operator to execute.

---

## Phase 2 — Facts

**Goal:** Earn every number the README will print.

Detail: `workflow/02-facts.md`

Only after the operator clears Phase 1 and executes any remediation he chose.

Run and record: stack versions from the manifest, build (exit code and route count),
typecheck, test suite, dependency audit. Map the architecture the README will claim — entry
points, service boundaries, auth enforcement points, integration flows — by reading code, not
paraphrasing docs. Inventory `/docs` with real filenames.

If a check cannot run in this environment, say so plainly and mark any dependent number
`[VERIFY: claim]` rather than inheriting it from a doc.

**Gate:** Every figure destined for a badge traces to a command you ran or a file you read
this session.

**Output:** Fact sheet in chat.

---

## Phase 3 — Assets

**Goal:** Get what only the operator has.

Detail: `workflow/03-assets.md`

You cannot see screenshots, diagrams, or videos, and you cannot guess their layout. Ask
specifically, not as a blind question dump — everything discoverable was already discovered
in Phase 0 and 2.

Request: image URLs with layout directions, any architecture diagram and its placement, any
walkthrough video URLs, confirmation of your proposed one-liner, and any story context that
is not on disk (live vs retired, production dates, ownership constraints, methodology
framing).

**Stop Gate:** You have assets, or an explicit instruction to build without them.

**Output:** Asset request in chat, with your proposed one-liner included so the operator
corrects it before you build around it.

---

## Phase 4 — Build & Handoff

**Goal:** A README that converts a skimmer into a believer in ninety seconds — then a clean
handoff.

Detail: `workflow/04-build-handoff.md` · Load `templates/README_FACTORY_TEMPLATE.md` and
`references/ANTI_PATTERNS.md` before writing.

**Preserve, don't bulldoze.** If the repo already has diagrams, screenshots, and working
structure, you are augmenting. Keep every existing asset and heading; wrap them in the
factory format. Destroying prior work to impose a template is a failure, not a cleanup.

Section order: H1 + one-liner · badge row · video walkthrough · screenshots · What's Inside ·
stage/status (FFM or compliance-trajectory framing where it applies) · From Build to
Production · Documentation table · Quickstart last · footer.

Render the complete README in chat for review before writing the file.

**Output and final line:**

> **READY FOR COMMIT: [file list]**

You do not commit. You do not stage. You do not push.

---

## Worked Example

> **Operator:** Go read `_SKILLS/stark-showcase-readme/CLAUDE.md` and follow it.
>
> **Agent:** *[reads CLAUDE.md, then SKILL.md; runs pwd, tree, git remote -v, git status,
> git log, reads package.json and README.md, lists docs/ agent_docs/ logs/, reads .gitignore]*
>
> **PLAN**
>
> **Observed** — `qr-ticketing-v3`, remote `github.com/ahmedmusawir/…`, tree committed,
> 41 commits. Next.js 13.5.6 / React 18 / TS 5.6.2 / Supabase / Redux. Existing README is
> substantial: 15 Cloudinary diagrams and portal screenshots, two YouTube links, no badges,
> no prose sections, no quickstart. `docs/` present with 8 subfolders. **`logs/` is tracked,
> 38 files.** No `.env*` tracked. Repo class: **legacy/manual-era**, integration-heavy.
>
> **Intended** — Full flow. Phase 1 sweep weighted toward committed logs and pre-doctrine
> clutter; Phase 2 facts; Phase 3 assets; Phase 4 augment the existing README rather than
> replace it — the diagrams stay.
>
> **Unknown** — (1) Is the deployment still live, or retired? This changes the badge and the
> tense. (2) Is this repo yours to show without client constraints? (3) Anything you want
> claimed or specifically not claimed?
>
> **Risks** — `logs/` on an integration app is the likeliest blocker; if those contain real
> order or customer records this becomes a disposition decision before any README work.
>
> **Awaiting your APPROVED before proceeding.**
>
> **Operator:** Retired six months ago, DB is paused. Mine, no constraints. APPROVED.
>
> **Agent:** *[runs Phase 1, loads the full checklist, opens all 38 log files]* … reports
> findings by severity, lists three decisions needed, hands over an untrack command block,
> and ends: **STOPPED. Awaiting operator decisions. No files modified, no git commands run.**

---

## Anti-Patterns (Skill-Specific)

**Treating operator-supplied images as pre-cleared.** He picked the screenshot for its subject, not for the contact list visible in the corner. If you can see images, audit them and report what you find as a decision for him. If you cannot, say so — an unstated limitation reads as an all-clear.

**Writing outside the authorized surface.** Editing `RECOVERY.md`, a changelog, a session file, or any operator bookkeeping. The surface is `README.md`, plus `.gitignore` and `.env.example` only when a disposition decision authorized them, plus your own reports.

**Introducing an asset.** Adding any image, diagram, or link the operator did not supply —
including a URL scavenged from a component or a stock photo that "fits the slot." Observed in
the wild: a 397B model inserted an Unsplash stock photo into a screenshot table and captioned it
as the application's configuration screen. Fewer real images beats more fake ones.

**Upgrading an operator fact.** He said "staged"; the README says "production-deployed." He gave
four infrastructure components; the README lists six. He gave no date; the README says 2024.
These slip past review precisely because they sound right — and they fail under a client's
follow-up question, in front of the person the operator is asking to trust him.

**Anachronism.** Crediting a pre-methodology project to the methodology. Calling a 2023
hand-built app a Solution Module. The honest arc — hand-built, later brought under the
methodology — is the stronger claim anyway.

**Silent compliance with an override.** The operator says "skip the sweep, it's an old repo," and
you simply skip it. The protocol requires naming the doctrine, stating the failure mode, offering
the compressed alternative, and asking for confirmation. His authority is supreme; your silence
is not obedience, it is doctrine decay.

**Padding a section to keep it.** Filling a Documentation table with `package.json` and
`tsconfig.json` because the template has a Documentation section. If there are no docs, delete
the section.

**Painting before sweeping.** "It looks clean, I'll just do the README." Every repo that
burned this operator looked clean.

**Sweeping vacuously.** Running tracked-file greps on an uncommitted tree. Everything passes
because nothing is tracked. Sweep the shippable set and say so.

**Name-waving.** Reporting that a directory exists instead of reading what is in it.

**Rolling past a stop gate.** Finishing the sweep and "getting a head start" on facts.

**Deciding for the operator.** Deleting a flagged file, rotating a key, or judging whether
client-internal docs are acceptable to publish. You surface and recommend; he decides.

**Inventing numbers.** Test counts from a changelog, route counts from a doc, versions from
memory.

**Badging an unearned claim.** Printing "0 vulnerabilities" when the audit reads five high.
Omit the badge and say why.

**Bulldozing the operator's assets.** Replacing a README that already has diagrams because
the template orders sections differently.

**Resume voice.** "I built this to showcase my skills." The product sells the project; the
project sells the operator. Trust the inference.

**Publishing the bypass.** Documenting the exact role flag and equality check that gates an
admin portal. Describing that access is role-gated is fine; publishing the recipe is not.

**Placeholders that cosplay as secrets.** `sk_test_` plus filler characters matches scanner
regexes perfectly and blocks the operator's own push. Use `sk_test_YOUR_SECRET_KEY` — words,
never repeated filler.

**Fixing forward on a flagged commit.** Telling the operator to add a cleanup commit. Scanners
judge every commit in the push; the flagged one must be replaced, not layered over.

**Scope creep into remediation.** You are not the agent that fixes the auth vulnerability you
found. Diagnose it precisely, hand it over as a future work item, and stay in your lane.

---

## When You're Done

You are done when all of the following are true:

1. The sweep was run, labeled, severity-triaged, and cleared by the operator
2. Every number in the README traces to a command run or file read this session
3. Existing operator assets are preserved, with new content wrapped around them
4. Captions you could not visually verify are flagged for operator review
5. The rendered README was shown in chat before the file was written
6. Any git work is a copy-paste block in the operator's hands, with history implications
   stated where they apply
7. You have run zero git write commands
8. Out-of-scope findings — auth weaknesses, dead code, architectural debt — are recorded with
   file:line for the operator to scope separately
9. Your final line is: **READY FOR COMMIT: [file list]**

Present the operator a three-line closing summary: what changed, what he must execute, and
what he should decide next.

---

## Version History

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-08-03 | Initial methodology. Five phases with two hard stop gates (post-sweep, pre-build). Shippable-set sweep rule. Preserve-don't-bulldoze rule for existing READMEs. Worked example shows Plan Mode dialogue through the Phase 1 stop. Twelve skill-specific anti-patterns named, including the placeholder-cosplay scanner trap and fix-forward-on-flagged-commit. Remediation explicitly out of scope. |
| 1.1 | 2026-08-03 | **Entry 002 remediation.** Override Protocol now referenced inline at the Phase 1 sweep gate, where the temptation occurs, rather than only in CLAUDE.md. Five anti-patterns added: introducing an asset, upgrading an operator fact, anachronism, silent compliance with an override, padding a section to keep it. |
| 1.2 | 2026-08-04 | **Entry 003 remediation.** Added Operator-Supplied Assets Are Not Pre-Cleared doctrine after a supplied screenshot was found to contain real third-party contact data that both operator and referee had cleared. Asset audit duty added to Phase 3, with an explicit instruction to declare the limitation when vision is unavailable. Authorized write surface now named in Phase 4 after a run edited `RECOVERY.md`. Two anti-patterns added. |
