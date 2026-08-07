# Decision Tree — Flow Selection

Consulted during Phase 0, before the Plan is presented. Three flows. The default is full.

---

## The tree

```
Does the sweep evidence (or Phase 0 discovery) show factory internals, client
identity, or a credential TRACKED in a repo that is or was public?
│
├─ YES ─────────────────────────────────────────► CLEAN-ROOM FLOW
│                                                  references/CLEAN_ROOM_FLOW.md
│
└─ NO
   │
   Did the operator explicitly request express mode?
   │
   ├─ NO ──────────────────────────────────────► FULL FLOW (default)
   │                                              workflow/00 → 04
   │
   └─ YES
      │
      Does the repo QUALIFY for express?
      (all four must be true)
      │  · No production history, or swept within the last week
      │  · No client contact — no client data, names, or correspondence
      │  · No committed logs, uploads, or data directories
      │  · No factory internals tracked
      │
      ├─ ALL TRUE ─────────────────────────────► EXPRESS FLOW
      │                                           references/EXPRESS_FLOW.md
      │
      └─ ANY FALSE ────────────────────────────► FULL FLOW
                                                  Surface the mismatch to the
                                                  operator: express was requested,
                                                  the repo does not qualify, here
                                                  is why. Operator Override
                                                  Protocol applies if he insists.
```

---

## Why the default is full

Express is a speed choice about **low-risk repos**, not a risk appetite. The operator asking
for speed is not evidence that the repo is low-risk — it is evidence that he is busy, which
is precisely when a miss is most likely to get published.

If express is requested and the repo does not qualify, say so plainly and name which of the
four conditions failed. He can override; he overrides consciously.

## Escalating mid-flow

Express escalates to full — and full escalates to clean-room — the moment evidence appears.
Do not finish a compressed sweep out of tidiness after finding a blocker.

Escalate from express to full on any of:

- A tracked env file containing any real characters
- Factory internals tracked
- A committed log, upload, or data directory with real identifiers
- A client name, mailbox, or business domain
- Evidence the repo was ever a production system with real users

Escalate from full to clean-room when the remediation list would touch most of the tree, or
when anything in the **history** must never have been published. A scrub commit does not
undo a public history; see `CLAUDE.md` §4, The Album Lesson.

## Announce the flow in the Plan

State which flow you selected and the evidence that selected it. If you escalate mid-mission,
stop, report the escalation and its trigger, and get the operator's acknowledgment before
continuing under the new flow.
