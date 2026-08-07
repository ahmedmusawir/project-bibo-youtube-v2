# SWEEP CHECKLIST — Phase 1

Read-only. No file writes, no git commands. Label every finding. Redact values.

Sweep the **shippable set**, not just tracked files. If the tree is largely uncommitted,
`git ls-files` returns almost nothing and every grep passes *vacuously*. Use:

```bash
git ls-files                          # tracked
git ls-files -o --exclude-standard    # untracked but not ignored
```

The union of those two is what a `git add -A` would publish. That is your sweep target.
State explicitly in your report which set you swept.

---

## 1 — Credentials

```bash
git ls-files | grep -iE "\.env"
ls -la | grep -iE "\.env"
```

Open every env-shaped file found. **Placeholders only is a pass.** Any real characters —
even heavily masked — is a FLAG. A 32-character secret with 4 characters starred is a
published secret with a speed bump.

Provider patterns to grep across the shippable set:

```
sk_live|sk_test|pk_live|pk_test|whsec_|rk_live
sb_secret|sb_publishable|service_role
ck_[0-9a-f]{20,}|cs_[0-9a-f]{20,}          # WooCommerce
eyJ[A-Za-z0-9_-]{10,}                       # JWT
AIza[0-9A-Za-z_-]{30,}                      # Google
ghp_|gho_|ghs_|github_pat_                  # GitHub
xox[baprs]-                                 # Slack
-----BEGIN .*PRIVATE KEY-----
```

Plus assignment-shaped literals:

```
(api[_-]?key|secret|token|password|credential)\s*[:=]\s*['"][A-Za-z0-9_\-]{16,}['"]
```

**Filter the noise before reporting:** JWT-shaped hits are frequently image-URL query params
or lockfile integrity hashes. Verify before you flag; a false positive costs credibility.

**Also check:** are secrets correctly routed through environment variables, or hardcoded in
deploy scripts and CI config? `deploy.sh` and `cloudbuild.yaml` are repeat offenders.

---

## 2 — People

```
Frank|Coach|<known client names>|<partner first names>
@<company-domain>\.com
```

Hunt for:
- Client full names and business email domains
- Staff names, especially in decision records ("X is a superadmin for v1 — approved")
- Internal team mailboxes
- Real public figures used as demo seeds (a sitting politician as a demo account owner is an
  optics blocker, not a security one — flag it as JUDGMENT)
- The operator's own persona/branding in code comments and changelog examples

Search **code comments, type files, tests, changelogs, and design artifacts** — not just docs.
Design mockup HTML is a known blind spot.

Beware substring false positives: `Tant` matches "impor**tant**", `Mical` matches
"ato**mical**ly". Verify hits before flagging.

---

## 3 — Real data

- Committed log directories — **open the files**. Report record counts, identifier formats,
  and date ranges. Run the disconfirming check: are there names, emails, phone numbers?
  Prove the negative explicitly.
- Fixtures, seeds, mocks — realistic personal data vs obviously-fake data
- PHI-shaped fields: patient names, DOB, SSN, MRN, prescription/Rx numbers, claims
- Registry-checkable identifiers — **checksum-verify them**:
  - **NPI:** Luhn over `80840` + first 9 digits. A valid checksum may resolve to a real
    provider in the public NPPES registry.
- Third-party resource IDs from other projects (calendar IDs, location IDs, account IDs)
- Business/financial figures with a stated real provenance — reword provenance to
  "derived from an anonymized production dataset" rather than naming the source

---

## 4 — Factory internals (Two-Repo Rule)

```bash
git ls-files | grep -E "agent_docs|_SKILLS|_design|test-results|SESSION|RECOVERY"
```

Flag as BLOCKER if tracked:
- `agent_docs/` — briefs, response logs, session logs, recon reports, ticket modules
- `_SKILLS/` — proprietary methodology
- `_design/` — mockups, style tiles (also a seed-data blind spot)
- Agent config files: `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, `WINDSURF.md`
- `SESSION_*.md`, `RECOVERY.md`, `*_PLAN.md`, phase plans
- Security findings docs and security playbooks — a published security-findings file on a
  live app is an attacker's roadmap

If these are tracked, a `.gitignore` addition does not fix it — recommend
`workflows/CLEAN_ROOM_FLOW.md`.

Also verify `.gitignore` has the fence for future work:

```gitignore
.env*
!.env.example
agent_docs/
_SKILLS/
_design/
session_*.md
test-results/
```

---

## 5 — Infrastructure

Grep for and flag:
- GCP/AWS project IDs and project **numbers**
- Service account emails
- Secret Manager secret names
- Staging hostnames (`*.mystagingwebsite.com`, `*.wpenginepowered.com`, internal subdomains)
- Cloud Run / deployment service names
- Live database project refs

Recommendation is usually **templatize**, not delete: `YOUR_PROJECT_ID`,
`your-project-ref.supabase.co`, `<SA_NAME>`, `<SECRET_NAME>`, `your-domain.com`.

Note: a public production URL the operator is actively showcasing is fine — that is the
point. The topology behind it is not.

---

## 6 — Fossils and clutter

- `*-org.*`, `*.bak`, `*-old.*`, `*.copy.*` backups — **diff them** and report identical vs
  stale. Git history preserves them; the showcase tree should not.
- `temp/`, `scratch/`, stray JSON dumps from other projects
- Dead scripts referenced by nothing
- Planning docs, documentation plans, changelog fossils
- Test artifacts (`test-results/`, `.last-run.json`)
- Dead package scripts (an `test:e2e` script with no config or specs)

---

## 7 — Stale claims

Cross-check any assertion a doc makes against reality:

- Test counts stated in changelogs, READMEs, or recovery files
- "0 vulnerabilities" / audit-clean claims — **re-run the audit**
- Version numbers in prose
- Architecture claims that describe refactored-away code
- Setup instructions pointing at stale schema/config files
- Route counts, feature lists

An audit summary count is **not** an inventory. Grepping audit output for the package you
already suspect confirms that package and silently hides every other advisory in the same
count. Capture the full list.

---

## Per-Stack Variants

### Node / Next.js
- `npm audit --omit=dev` for the production tree; note fixable vs upstream-blocked
- Check whether the build requires env vars (clone-from-README experience)
- `NEXT_PUBLIC_*` audit — **anything with that prefix ships in the browser bundle.** Trace
  every one. A `NEXT_PUBLIC_` service-role or admin key is a critical finding; trace the
  imports to confirm reachability before declaring it.
- Check that admin/service clients are imported only by server-side route handlers

### Python
- `.env`, service-account JSON files (`private_key`, `client_email` content), credential files
- Committed store IDs, vector-store handles, index names
- Personal documents in `uploads/`, `docs/`, `data/`, or test corpora — lab harnesses
  routinely get tested against the operator's own resume, contracts, or private files
- Eval receipts and golden datasets built from personal corpora
- `.gitignore` covering `.env`, `__pycache__`, `venv/`, local artifacts
- Broken imports from deleted or legacy modules

### Any stack with auth
- Where does role resolution actually happen — database, or user-writable metadata?
- Are guards server-side, or client-side components that can be bypassed?
- Do signup/registration routes trust the request body for role fields?
- Are admin/service-role routes checking caller identity?
- Is the middleware file actually named what the framework loads?

Auth findings are usually **out of scope to fix** in a README mission — but always in scope
to **report**. Hand the operator a diagnosis; it becomes a Solution Module.

---

## Report Format

Use `templates/SWEEP_REPORT.template.md`. End with:

> **STOPPED. Awaiting operator decisions. No files modified, no git commands run.**
