# SWEEP REPORT — project-bibo-youtube-v2 (VidGen)

**Date:** 2026-08-07 · **Branch:** main · **Repo class:** Legacy / Manual-era
**Method:** grep/read-only. No files modified, no git commands run.
**Swept set:** Tracked ∪ untracked-not-ignored — 132 files (112 tracked + 20 untracked)

---

## VERDICT: 🟠 HIGH

No active credentials or real personal data found. The tree is clean on the two highest-severity classes. However, a real-ish service account filename (`cyberize-vertex-api.json`) is referenced in 8 tracked files, and factory internals (session logs, plan_docs, agent config) are tracked in a public repo — the operator has **declined clean-room** and will handle manually later. APP_BRIEF.md contains stale stack claims describing an OpenAI/Anthropic-first architecture while the shipped code uses Google Gemini/TTS.

| # | Class | Result |
|---|-------|--------|
| 1 | Credentials | ✅ CLEAN |
| 2 | People | 🟡 JUDGMENT |
| 3 | Real data | ✅ CLEAN |
| 4 | Factory internals | 🔴 DECLINED BY OPERATOR |
| 5 | Infrastructure | 🟠 HIGH |
| 6 | Fossils | 🟡 JUDGMENT |
| 7 | Stale claims | 🟡 JUDGMENT |

---

## 🔴 BLOCKER — Factory Internals Tracked (Operator Declined)

**EVIDENCE:** Multiple tracked files across repo root

**INFERENCE:** The repo contains factory-internal artifacts tracked in git history on a public repository advertised on LinkedIn.

**Tracked factory internals found:**
- **12 session files:** `session-2026-01-30.md` through `session-2026-03-12.md`
- **3 plan_docs:** `app_factory_vision.md`, `extraction_playbook.md`, `progress_tracker.md`
- **Agent config files:** `CLAUDE.md`, `.windsurf.md`
- **Untracked but not ignored:** `_SKILLS/` (20 files) — would be published on `git add -A`

**Blast radius:** Operational context, internal decisions, and workflow details visible to anyone cloning the repo. Session files reference credential placement decisions and third-party delivery plans.
**Time budget:** Clean-room is the standard remediation. Operator has explicitly declined for this repo, same as ADK harness v2.

**Recommendation (operator executes):**
1. **Deferred to manual handling** — operator decision recorded.
2. **Note:** `.gitignore` currently does NOT fence session files or plan_docs. Even without clean-room, adding them to `.gitignore` prevents future tracking of new session files. (Operator instructed: "Do NOT edit .gitignore" — honored.)

---

## 🟠 HIGH — Infrastructure Identifier Referenced

**EVIDENCE:** `credentials/README.md:5`, `.env.example:11`, `.gitignore:203`, `APP_BRIEF.md`, `ARCHITECTURE.md`, `API.md`, `INSTALL.bat`, `README.md`

**INFERENCE:** The service account JSON filename `cyberize-vertex-api.json` appears in 8 tracked files. While the file itself is not present in the repo (verified: `credentials/` contains only `README.md`), the name reveals a real-ish project identifier and is referenced in setup instructions, env templates, batch scripts, and documentation.

**Blast radius:** The name "cyberize" is a project/org identifier. Combined with the Google services listed (Speech, TTS, Vertex AI, Storage), this forms partial reconnaissance data.
**Time budget:** Minutes — templatize to `<YOUR_SERVICE_ACCOUNT>.json` or remove the specific name from docs.

**Recommendation (operator executes):**
1. Replace `cyberize-vertex-api.json` with `YOUR_SERVICE_ACCOUNT.json` in all docs and `.env.example`
2. Update `credentials/README.md` and `INSTALL.bat` to use generic placeholder
3. The actual JSON file is already `.gitignore`d — correct

---

## 🟡 JUDGMENT — People References

**EVIDENCE:** `session-2026-02-17.md`

**INFERENCE:** The name "Coach" appears in session files as a third party who received the Windows-packaged app. No full name, email, or phone number found. This is a role/persona reference rather than identifiable personal data.

**EVIDENCE:** `pyproject.toml:5`

**INFERENCE:** Email `tony@starkindustries.com` appears in the package manifest. Operator states this is a fictional persona placeholder, not a real address. In a public-facing manifest, it reads as a real domain.

**Recommendation:** Operator's call. The email is harmless but may read oddly to showcase visitors.

---

## 🟡 JUDGMENT — Fossils

**EVIDENCE:** `src/archive/img_prompt_generator-org.py`, `src/archive/summarizer-org.py`

**INFERENCE:** Two `-org` backup files in `src/archive/`. These are legacy versions preserved alongside OpenAI/Anthropic alternate route files. The archive directory is tracked.

**Recommendation:** Operator's call. The `-org` suffix marks them as backups. Could be removed or left as they document the evolution path.

---

## 🟡 JUDGMENT — Stale Claims

**EVIDENCE:** `APP_BRIEF.md:5` — "Successfully generated ~30 published videos"

**CLAIM:** Operator-supplied production metric. No verification path from disk. Flagged for operator confirmation.

**EVIDENCE:** `APP_BRIEF.md` throughout — describes primary stack as OpenAI Whisper + Claude 3.5 + Anthropic API

**INFERENCE:** The main modules (`src/summarization.py`, `src/text_to_speech.py`, etc.) use Google Gemini and Google Cloud TTS. OpenAI/Anthropic files exist as `*-openai.py` and `*-anthropic.py` fallbacks but are not the active primary route. APP_BRIEF.md describes the v1 architecture, not the current v2.

**EVIDENCE:** `APP_BRIEF.md` and `ARCHITECTURE.md` — "Researcher/Scraper" branch described

**CLAIM:** Operator confirmed this was **planned and never implemented**. Do not describe as existing.

**Recommendation:** APP_BRIEF.md should be either updated to reflect v2 Google-first stack or removed from the showcase tree. The Researcher/Scraper path should be captioned as roadmap, not shipped.

---

## 🟢 CLEAN — Verified Negatives

- **Credentials — hardcoded secrets:** Grep of `src/` and `app/` for provider patterns (`sk_live`, `AIza`, `eyJ`, `-----BEGIN`) returned zero matches. All API keys route through `os.getenv()` — correct pattern.
- **Credentials — env files:** Only `.env.example` is tracked; it uses proper placeholder style (`your-gemini-api-key-here`, `your-gcp-project-id`). No real `.env` files tracked.
- **Credentials — credential files:** `credentials/` directory contains only `README.md`. No JSON key files present. `cyberize-vertex-api.json` is `.gitignore`d.
- **Real data — committed logs:** No `logs/` directory found. No fixtures, seeds, or mock data with real personal information.
- **Real data — session files:** Grep of all 12 session files for email patterns returned no matches. No names beyond "Coach" found.
- **People — client identity:** No client names, business domains, or staff names found in code or docs.

**False positives cleared:** None raised.

---

## Out of scope — flagged, not fixed

- **Auth routing:** All Google API keys use `os.getenv()` in main modules. Alternate route files (`summarization-anthropic.py`, `text_to_speech_openai.py`) also use `os.getenv()` — correct pattern throughout.
- **Deploy scripts:** `run_app.sh` is a local launcher only (sets PYTHONPATH, runs Streamlit via venv). `INSTALL.bat` is a Windows setup helper. No CI config or cloud deploy scripts found.

---

## Decisions needed from operator

1. **Templatize `cyberize-vertex-api.json` references?** — Replace with generic placeholder across 8 files. **Recommendation: Yes.**
2. **Remove or update `APP_BRIEF.md`?** — Describes v1 OpenAI/Anthropic stack and unimplemented Researcher/Scraper branch. **Recommendation: Update to v2 stack or exclude from showcase.**
3. **Keep or remove `src/archive/` `-org` files?** — Legacy backups alongside alternate routes. **Recommendation: Operator's call.**
4. **Confirm "~30 published videos" claim** — Operator-supplied metric. **Recommendation: State as operator claim or omit.**
5. **`pyproject.toml` email** — `tony@starkindustries.com` is fictional per operator. **Recommendation: Leave or replace with generic.**

## Command block (operator executes — Rule Zero)

```bash
# Templatize cyberize-vertex-api.json references (run from repo root)
# NOTE: This touches APP_BRIEF.md, ARCHITECTURE.md, API.md, README.md, SETUP.md,
# .env.example, credentials/README.md, INSTALL.bat
# Review each diff before committing.
```

> ⚠️ History warning: The 12 session files, plan_docs, CLAUDE.md, and .windsurf.md are already in public git history. Untracking them now does not remove them from history. The operator has deferred clean-room to manual handling later.

---

**STOPPED. Awaiting operator decisions. No files modified, no git commands run.**
