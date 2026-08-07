# SWEEP REPORT — {repo-name}

**Date:** {timestamp} · **Branch:** {branch} · **Repo class:** {class}
**Method:** grep/read-only. No files modified, no git commands run.
**Swept set:** {tracked only | tracked ∪ untracked-not-ignored — N files}

> If the tree is largely uncommitted, say so here. Checks against `git ls-files` pass
> vacuously on an unstaged tree and the report would be worthless without this note.

---

## VERDICT: {🟢 CLEAN | 🟡 JUDGMENT ITEMS | 🟠 HIGH | 🔴 BLOCKED}

{One paragraph: what the operator needs to know before deciding. If there is a single
finding that outranks everything else — a live credential, a working login, real personal
data — lead with it here, above the table.}

| # | Class | Result |
|---|-------|--------|
| 1 | Credentials | {✅ CLEAN / 🔴 FLAGGED} |
| 2 | People | {…} |
| 3 | Real data | {…} |
| 4 | Factory internals | {…} |
| 5 | Infrastructure | {…} |
| 6 | Fossils | {…} |
| 7 | Stale claims | {…} |

---

## 🔴 BLOCKER — {finding title}

**EVIDENCE:** `{file}:{line}`

{What it is, in plain language. Redact the value — prove existence, do not reprint the
secret.}

**Blast radius:** {what an attacker could actually do with this, realistically}
**Time budget:** {is this minutes, hours, or days? Do not inflate; do not shrug.}

**Recommendation (operator executes):**
1. {rotate / remove / templatize / clean-room}
2. {note if history rewriting is implicated — see The Album Lesson}

---

## 🟠 HIGH — {finding title}

{Same structure, proportionate detail.}

---

## 🟡 JUDGMENT — {finding title}

{Optics, fossils, internal branding. State the trade-off; let the operator choose.}

---

## 🟢 CLEAN — verified negatives

Report these explicitly. A proven negative has value.

- **{class}** — {what you searched for, how, and what came back}. Note any *disconfirming*
  check you ran (e.g. "phone-shaped hits verified as hex identifiers, not phone numbers").
- **{class}** — {…}

**False positives cleared:** {e.g. JWT-shaped strings were image-URL query params and a
lockfile integrity hash; `Tant` matched inside "important"}.

---

## Out of scope — flagged, not fixed

{Findings outside a README mission that the operator should know about anyway: auth
architecture weaknesses, dead code that is a loaded gun, unreachable middleware, missing
server-side guards. Diagnose precisely with file:line. These become Solution Modules.}

---

## Decisions needed from operator

1. {decision} — recommendation: {yours}
2. {decision} — recommendation: {yours}
3. {decision} — recommendation: {yours}

## Command block (operator executes — Rule Zero)

```bash
# {what this does}
{command}
{command}
```

> ⚠️ {Any history implication: untracking does not remove from history; rotation is the
> mitigation; a flagged commit must be replaced not fixed forward.}

---

**STOPPED. Awaiting operator decisions. No files modified, no git commands run.**
