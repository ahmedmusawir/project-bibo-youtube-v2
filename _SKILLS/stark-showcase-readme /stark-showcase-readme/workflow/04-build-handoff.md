# 04 — Build & Handoff

**Goal:** A README that converts a skimmer into a believer in ninety seconds. Then a clean
handoff that leaves the operator holding the knife.

Load `templates/README_FACTORY_TEMPLATE.md` and `references/ANTI_PATTERNS.md` before writing.

---

## Preserve, don't bulldoze

If the repo already has a README with diagrams, screenshots, and working structure, **you are
augmenting it.** Keep every existing image URL and section heading. Wrap them in the factory
format — badges above, prose around, quickstart below.

Destroying the operator's prior work to impose a template's section order is a failure, not a
cleanup. The template is a format, not a demolition order.

## Section order

1. **H1 + bold one-liner** — what it is, who it's for, under 20 words
2. **Badge row** — disk-verified numbers only; live-site and video badges where they exist
3. **Video walkthrough** — clickable thumbnails via `img.youtube.com/vi/{ID}/maxresdefault.jpg`,
   `hqdefault.jpg` as fallback. GitHub does not embed players; the thumbnail-as-link is the
   standard pattern.
4. **Why This Exists** — two paragraphs. The problem, then the key architecture decision with
   its trade-off. This is where an architect-level reader decides whether you are one.
5. **Screenshots / diagrams** — per operator layout directions, captions flagged for review
6. **What's Inside** — 6–8 bullets, every claim pointing at code
7. **Stage / status** — FFM or compliance-trajectory framing, where it applies
8. **From Build to Production** — delivery, QA gate, pipeline stages, monitoring
9. **Documentation** — table of verified `/docs` filenames, no dead links
10. **Quickstart** — last. Prereqs, env setup, install, run, verify block with expected results
11. **Footer** — one line: built by, role, methodology, profile link

Delete sections that do not apply. An empty section is worse than a missing one.

## Wording rules

- **Compliance is a trajectory.** "Being built toward a HIPAA-compliant production system" —
  never "is HIPAA compliant."
- **FFM framing is doctrine, not apology.** "Domain data is mock by design at this stage; auth
  and role enforcement are real" is a feature statement, stated proudly.
- **Human-in-the-loop is the stronger claim.** In regulated or client-facing work, "every
  stage AI-executed and human-gated" beats "autonomous." Sell the gate.
- **No infra coordinates.** "A dev WordPress backend," never the hostname.
- **No bypass recipes.** Describing that access is role-gated is fine; naming the flag and the
  equality check is not.
- **Factory vocabulary once, in parentheses.** "Scoped Solution Modules (SMs)."
- **Product tone, not resume tone.** The product sells the project; the project sells the
  operator.
- **Past-tense production is still credit.** "Built and operated in production 2024–2025"
  beats a "Live" badge pointing at a dead URL.

## Badge discipline

Every badge carries a number you earned in Phase 2. No verified count, no badge. Omit the
audit badge unless the audit genuinely reads zero — a missing badge is honest, a flattering
one is a lie with a shield around it. Six to eight badges maximum.

## Render before writing

Show the complete README in chat for operator review **before** writing the file. He is
checking captions against images you could not see, and framing against history you do not
have.

## Authorized write surface

Before writing anything, state which files you are permitted to touch. The default surface is:

| File | When |
|---|---|
| `README.md` | Always — it is the mission |
| `.gitignore` | Only when a disposition decision authorized it |
| `.env.example` | Only when a disposition decision authorized it |
| Your own report artifacts | Always — plan, sweep, facts, handoff |

**Nothing else.** Not application code. Not `RECOVERY.md`, `CHANGELOG.md`, session files, or any other operator bookkeeping — those are his records of his project, and editing them silently rewrites his own account of his work. If a deferral removed `.gitignore` or `.env.example` from the surface, the surface is `README.md` and your reports.

If you believe another file needs changing, say so in the handoff and let him decide.

## Handoff

1. **Changed files** — one line each. The list should be short: `README.md`, and possibly
   `.gitignore` or `.env.example` if a disposition decision authorized them.
2. **Command block** — any git work, as copy-paste, with an explanation of what it does.
3. **History warnings** — where they apply: untracking does not remove from history; rotation
   is the mitigation; a flagged commit must be replaced rather than fixed forward.
4. **Flagged captions** — list them explicitly so he checks them against the real screenshots.
5. **Out-of-scope findings** — carried forward from Phase 1, with file:line, so they can be
   scoped as separate work.
6. **Final line:**

> **READY FOR COMMIT: [file list]**

Then a three-line closing summary: what changed, what he must execute, what he should decide
next.

## What you do not do

You do not commit. You do not stage. You do not push. You do not create a branch. You do not
"helpfully" fix the vulnerability you found in Phase 1.

The operator owns git and owns scope. You hand him the knife.
