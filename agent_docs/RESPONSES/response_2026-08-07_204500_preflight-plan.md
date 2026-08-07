# Response: Showcase Preflight Plan

**Project:** project-bibo-youtube-v2 (VidGen)
**Skill:** stark-showcase-readme
**Phase:** 0 — Orient / Plan Mode
**Status:** PENDING_APPROVAL

---

## 🔵 ENTERING PLAN MODE

Task: Prepare `project-bibo-youtube-v2` for public showcase using `stark-showcase-readme` skill.

---

## 📋 PLAN

### Observed

- **Repo:** `project-bibo-youtube-v2` (VidGen) — YouTube video automation pipeline
- **Remote:** `github.com/ahmedmusawir/project-bibo-youtube-v2.git`
- **Stack:** Python 3.12.3, Streamlit 1.54+, Google Gemini/Vertex AI, MoviePy, yt-dlp, pydub, pytest
- **Tree state:** Branch `main`, up to date with origin. Modified `CLAUDE.md`, untracked `RECOVERY.md`, `_SKILLS/`, `session_2026-08-07.md`
- **Existing README:** "VidGen Documentation Index" — an internal doc index for AI factory agents, **not** a showcase README. Contains a pipeline diagram, tech stack summary, and a doc table.
- **Content classes present:**
  - `docs/` — 8 factory-style docs (architecture, decisions, patterns, testing strategy, vertex AI integration, etc.)
  - `plan_docs/` — **tracked** factory internals (app_factory_vision.md, extraction_playbook.md, progress_tracker.md)
  - Tracked session files: `session-2026-01-30.md` through `session-2026-03-12.md` (12 logs)
  - `.windsurf.md` — tracked IDE config / session log agreement
  - `CLAUDE.md` — tracked project instructions
  - `credentials/README.md` — tracked credential placement guide
  - `_SKILLS/` — currently **untracked** (new)
- **`.gitignore`:** Standard Python + output/audio/image ignores + Google Cloud credential filename (`cyberize-vertex-api.json`) + Windows creds. Does **not** ignore session files, plan_docs, or factory internals.

**Repo Classification:** **LEGACY / MANUAL-ERA**
Hand-built end-to-end, later brought under the AI App Factory methodology. Pre-doctrine structure with tracked session files and plan docs.

---

### Intended Flow

Per `decision-trees/flow-selection.md`:

> "Does the sweep evidence show factory internals, client identity, or a credential **tracked** in a repo that is or was public?"

Factory internals (12 session files, plan_docs, .windsurf.md, CLAUDE.md) are **tracked**. The remote is a GitHub URL. The decision tree says **YES → CLEAN-ROOM FLOW**.

**However**, I cannot verify from disk whether the repo is currently **public** or **private** on GitHub.

| Scenario | Flow | What happens |
|---|---|---|
| **Public** | **CLEAN-ROOM** | You retire the old repo (rename + private), create a fresh repo under the original name. I prepare a carve-out tree with only app-level files, rebuild `.gitignore` fence and `.env.example`, re-sweep, then build the README. |
| **Private** | **FULL FLOW** | Phase 1 sweep → disposition decisions (untrack factory internals + add to `.gitignore`) → Phase 2 facts → Phase 3 assets → Phase 4 build README. |

---

### Unknown

1. **Is this repo currently public or private on GitHub?** This is the dispositive question for clean-room vs full flow.
2. Is the app live, retired, or never deployed?
3. Is this repo yours to show without client constraints?
4. Anything you want claimed or specifically not claimed?
5. Do you have screenshots, diagrams, or video walkthroughs you want included?

---

### Risks

- **If public:** 12 session files + plan_docs + `.windsurf.md` + `CLAUDE.md` are already on the internet. Session files contain references to credential filenames (`cyberize-vertex-api.json`), internal decisions about shipping credentials, and factory workflow details. Per `finding-severity.md`, this is **🔴 BLOCKER** — proprietary IP + operational context exposed.
- `pyproject.toml` contains email `tony@starkindustries.com` — domain reference in a public-facing manifest.
- `.env.example` uses correct placeholder style (`your-gcp-project-id`, `your-gcs-bucket-name`) — **🟢 CLEAN**.
- No actual hardcoded API keys found in quick grep of `src/` and `app/` — but session files reference credential workflows extensively.

---

**Awaiting your APPROVED before proceeding.**
