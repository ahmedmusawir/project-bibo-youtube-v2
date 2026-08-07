# EXPRESS FLOW — Trusted Repo, Compressed Sweep

For repos the operator has swept recently, or lab repos with no client contact and no
production history. **The sweep is compressed, never skipped.**

Use this only when the operator explicitly invokes it. Default to the full flow.

---

## What compresses

The sweep narrows to the four **blocker** classes. Everything else gets noted in passing and
does not stop the mission.

| Class | Express | Full |
|-------|---------|------|
| Credentials | ✅ Always | ✅ |
| Real personal data | ✅ Always | ✅ |
| Factory internals (Two-Repo Rule) | ✅ Always | ✅ |
| Client identity | ✅ Always | ✅ |
| Infrastructure topology | Note only | ✅ Block |
| Fossils / clutter | Note only | ✅ Block |
| Stale claims | Fix silently during build | ✅ Report |

## What never compresses

- **Rule Zero.** No git, ever, at any speed.
- **The Phase 1 stop.** Even a clean express sweep reports and stops. The report is short;
  the stop is not optional.
- **Earned numbers.** Speed is not a license to inherit a test count.
- **Phase 2.5 operator input gate.** You still cannot see the images.

---

## Sequence

```
0. Orient (abbreviated — README + tree + manifest)
1. Blocker sweep → [STOP, short report]
2. Facts (build / typecheck / test / audit)
2.5 Operator input gate → [STOP]
3. Build
4. Handoff → READY FOR COMMIT
```

## Express sweep — the four greps

```bash
# 1 — tracked env files
git ls-files | grep -iE "\.env"

# 2 — live key material across the shippable set
grep -rEn "sk_live|sk_test|pk_live|whsec_|sb_secret|ck_[0-9a-f]{20}|cs_[0-9a-f]{20}|AIza|ghp_|BEGIN .*PRIVATE KEY" \
  --exclude-dir={node_modules,.git,.next,dist,venv,__pycache__} .

# 3 — factory internals tracked
git ls-files | grep -E "agent_docs|_SKILLS|_design|SESSION|RECOVERY|CLAUDE\.md|AGENTS\.md|WINDSURF\.md|GEMINI\.md"

# 4 — client/personal identity
grep -rEn "{client names}|{partner names}|{internal domain}" \
  --exclude-dir={node_modules,.git,.next,dist,venv,__pycache__} .
```

Plus: **open any committed log, data, fixture, or upload directory.** That check is never
compressed — it is where the worst findings have come from, and a directory listing is not
an inspection.

---

## Express report format

Short. Four lines plus any flag.

```markdown
# EXPRESS SWEEP — {repo}
Swept set: {tracked ∪ untracked-not-ignored, N files}

1. Credentials — {✅ CLEAN / 🔴 FLAG + file:line}
2. Personal data — {…}
3. Factory internals — {…}
4. Client identity — {…}

Noted in passing (not blocking): {fossils, infra, stale claims}

STOPPED. Awaiting clearance. No files modified, no git commands run.
```

---

## Escalate to full flow when

Any of these turns up — abandon express, switch to the full sweep or clean-room:

- A tracked env file with any real characters
- Factory internals tracked (`agent_docs/`, `_SKILLS/`, session files)
- A committed log or data directory with real identifiers
- A client's name, mailbox, or business domain
- Anything suggesting the repo was ever a production system with real users

Express mode is a speed choice about *low-risk repos*, not a risk appetite. The moment
evidence says the repo is not low-risk, the speed choice expires.

> "Express is a shorter sweep, not an optional one."
