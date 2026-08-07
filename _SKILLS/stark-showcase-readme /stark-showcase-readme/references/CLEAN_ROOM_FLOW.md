# CLEAN-ROOM FLOW — Contaminated Repo Rebuild

When the sweep finds material that must never have been published, a scrub commit does not
help. See CLAUDE.md, **The Album Lesson**: history is not the working tree.

The clean-room path is faster than history surgery and more reliable than hoping nobody
looks.

---

## When to invoke

Any of these, on a repo that is or was public:

- Factory internals tracked — `agent_docs/`, `_SKILLS/`, session logs, briefs, decision
  records, agent config files
- Client identity in history — full names, business mailboxes, internal correspondence
- A working credential ever committed (rotate **and** clean-room)
- Real personal data in fixtures, seeds, or logs
- So many findings that a fix-list would touch most of the tree

**Not** required for: fossils, stale claims, infra strings that can be templatized in place,
or anything on a repo that has always been private.

---

## The sequence

The agent prepares. **The operator executes every git and platform step.**

### Step 1 — Operator: rotate first

Before anything else, rotate any credential that was ever committed. Rotation is what makes
the old history harmless. Renaming, deleting, and re-publishing do not.

### Step 2 — Operator: retire the old repo

Rename the existing repo (e.g. `{name}-legacy`) and **flip it private**. This does two
things at once: it takes the contaminated history off the public internet, and it frees the
original name.

Note honestly: forks, clones, caches, and crawlers may already hold the old content. This is
why Step 1 comes first.

### Step 3 — Operator: create the fresh repo under the original name

Keeping the original name means existing profile links and references keep working. No
downstream edits needed.

### Step 4 — Agent: prepare the carve-out tree

Copy forward only what belongs to the **app**:

**SHIPS**
- `src/` or equivalent application source
- `public/`, static assets
- `tests/`, `e2e/`
- Config files — package manifest, lockfile, framework config, tsconfig, linter, test config
- `docs/` — *only* if it is application documentation, not factory documentation. Inspect it.

**STAYS HOME (private lab repo)**
- `agent_docs/`, `_SKILLS/`, `_design/`
- `SESSION_*.md`, `RECOVERY.md`, `*_PLAN.md`, phase plans
- `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, `WINDSURF.md`
- Changelogs that name people or record internal decisions
- Deployment runbooks and checklists carrying live identifiers
- `temp/`, stray dumps from other projects

**SHIPS ONLY AFTER TEMPLATIZING**
- `deploy.sh`, `cloudbuild.yaml`, `init-app.sh` → `YOUR_PROJECT_ID`,
  `your-project-ref.{provider}.co`, `<SA_NAME>`, `<SECRET_NAME>`, `your-domain.com`
- If templatizing is more work than it is worth, drop them. A showcase does not need deploy
  scripts to be impressive.

**REBUILT FROM SCRATCH**
- `.env.example` — shape-only placeholders, word-style, never filler characters
- `.gitignore` — the fence, from commit zero:

```gitignore
.env*
!.env.example
agent_docs/
_SKILLS/
_design/
session_*.md
test-results/
temp/
```

### Step 5 — Agent: scrub on the way in

While preparing the tree, fix the findings the sweep produced:

- Genericize people in code comments and type files — "the domain expert's schema", not a name
- Neutralize demo seeds — invented names, `.example` domains, checksum-invalid identifiers
- Replace test passwords with placeholders
- Remove stale backup files and dead scripts
- Correct stale claims in any doc that ships

### Step 6 — Agent: verify the fence before handoff

```bash
git ls-files | grep -E "agent_docs|_SKILLS|_design|session_|test-results"   # must be EMPTY
git log --oneline --all                                                      # short, clean
```

Then re-run the **full sweep** against the new tree. All classes must pass. A clean-room that
is not re-swept is an assumption, not a result.

### Step 7 — Operator: single initial commit

The agent hands over the command block. The operator commits and pushes.

### Step 8 — Operator: update downstream links

Profile links, portfolio entries, anywhere the repo URL appears.

---

## Verification gate

Before the README is written:

- [ ] Credentials rotated
- [ ] Old repo renamed and private
- [ ] Fresh repo created under the original name
- [ ] Carve-out complete; blacklist verified absent from the shippable set
- [ ] `.gitignore` fence present from commit zero
- [ ] `.env.example` rebuilt with word-style placeholders
- [ ] Deploy files templatized or omitted
- [ ] Full sweep re-run against the new tree — all classes pass
- [ ] Operator has committed and pushed

Only then does Phase 2 (facts) begin.

---

## Why not just rewrite history?

`filter-repo` across hundreds of files on an already-public repo is a war, and it does not
reliably un-publish — forks, clones, caches, and archive crawlers may already hold the old
commits. The clean room takes an hour, produces a tree the operator can reason about, and
pairs with rotation, which is the only mitigation that actually works.

> "You cannot un-publish. You can only make what was published worthless."
