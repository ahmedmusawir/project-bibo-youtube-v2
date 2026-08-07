# 01 — Sweep

**Goal:** Find everything that must not be on a billboard.

Read-only. No file writes. No git write commands. Load `references/SWEEP_CHECKLIST.md` in
full before starting — this file is the procedure, that file is the content.

---

## Scope the sweep correctly

```bash
git ls-files                          # tracked
git ls-files -o --exclude-standard    # untracked but not ignored
```

The **union** is what `git add -A` would publish. That is your target. State in the report
which set you swept and how many files it contains.

If the tree is largely uncommitted, say so prominently at the top of the report. Otherwise
every `git ls-files | grep` check reads as CLEAN when it actually tested nothing.

## The seven classes

Run every applicable class from `references/SWEEP_CHECKLIST.md`:

1. **Credentials** — tracked env files, real key characters (masked counts as real),
   hardcoded secrets, keys in deploy scripts and CI config
2. **People** — client names, staff names, internal mailboxes, real public figures as demo
   seeds, operator persona in code comments
3. **Real data** — committed logs, fixtures, seeds, PHI-shaped fields, registry-checkable
   identifiers, third-party resource IDs
4. **Factory internals** — `agent_docs/`, `_SKILLS/`, `_design/`, session files, briefs,
   decision records, agent config files
5. **Infrastructure** — project IDs and numbers, service accounts, secret names, staging
   hostnames, deployment service names
6. **Fossils** — `-org` backups, `temp/`, stale duplicates, dead scripts, planning docs,
   test artifacts
7. **Stale claims** — doc-stated test counts, audit results, version numbers, architecture
   claims describing refactored-away code

## Verification standard

Three rules separate a finding from a guess:

**Open it.** A directory listing is not an inspection. If you flag `logs/`, you have read the
files and can state record counts, identifier formats, and date ranges.

**Run the disconfirming check.** Do not only look for what confirms the risk. Grep for the
things that would make it worse — names, emails, phone numbers — and report the negative
explicitly. "No customer names present, verified by grep" is a result with value.

**Filter your own noise.** JWT-shaped strings are frequently image-URL query parameters or
lockfile integrity hashes. Name substrings match innocent words. Verify before flagging; a
false positive costs credibility you will need on the real finding.

## Labeling and triage

Every finding carries an evidence label — EVIDENCE / INFERENCE / CLAIM / GAP / QUESTION —
with `file:line`. Triage severity per `decision-trees/finding-severity.md`.

**Redact values.** Prove the secret exists; never reprint it. Your report is a file that may
be committed by mistake.

## Sizing risk honestly

The operator needs accurate triage, not drama. State the realistic exploit path, the blast
radius, and the time budget.

A publishable-by-design anon key is repo hygiene — it already ships in the browser bundle. A
service-role key is an emergency. A test-mode payment key is lower severity than a live one
and still gets rotated. A retired app with a live endpoint and a populated database is not
retired; it is unattended, which is worse.

## Out-of-scope findings

You will encounter things outside a README mission: auth architecture weaknesses, unreachable
middleware, missing server-side guards, dead code that is a loaded gun. **Report them
precisely with file:line, then stay in your lane.** You are not the agent that fixes them.
They become separate work the operator scopes.

## Report

Use `templates/SWEEP_REPORT.template.md`. Structure: swept-set note, verdict, class table,
findings by descending severity, verified negatives, out-of-scope findings, numbered decisions
needed, and a copy-paste command block for any git work.

Attach history warnings where they apply — untracking does not remove from history; rotation
is the mitigation; a flagged commit must be replaced, not fixed forward.

## Stop Gate

End with exactly:

> **STOPPED. Awaiting operator decisions. No files modified, no git commands run.**

Stop even on a completely clean sweep. The operator confirms before paint.

## Output

Sweep report in chat. Numbered decisions. Command block if git work is implicated.
