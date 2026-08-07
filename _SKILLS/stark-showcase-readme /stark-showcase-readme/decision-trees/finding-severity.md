# Decision Tree — Finding Severity

Applied to every sweep finding before it enters the report. The operator triages at a glance;
consistent labels are what make that possible.

---

## The tree

```
Is the finding a CREDENTIAL, or does it grant access?
│
├─ YES
│  │
│  Is it public-by-design? (anon/publishable key, client-side token, public
│  project URL — already ships in the browser bundle)
│  │
│  ├─ YES ──────────────────────────► 🟡 JUDGMENT — repo hygiene
│  │                                    Templatize it out. Rotation is usually
│  │                                    disproportionate; say so plainly.
│  │
│  └─ NO (service-role, secret, webhook secret, password, admin token)
│     │
│     Has the repo ever been public, or is it about to be?
│     │
│     ├─ YES ───────────────────────► 🔴 BLOCKER — rotate FIRST, then clean
│     │                                 Rotation is the mitigation; file edits
│     │                                 and untracking are hygiene that follow.
│     │
│     └─ NO ────────────────────────► 🟠 HIGH — clean before it goes public
│
└─ NO
   │
   Does it identify a REAL PERSON or a CLIENT?
   │
   ├─ YES
   │  │
   │  Is it a client's identity, correspondence, or internal decisions
   │  about their staff?
   │  │
   │  ├─ YES ───────────────────────► 🔴 BLOCKER — confidentiality
   │  │                                 Outranks IP loss. Clean-room if in history.
   │  │
   │  └─ NO (demo seed using a real public figure, operator persona,
   │         internal branding)
   │     └──────────────────────────► 🟡 JUDGMENT — optics
   │                                    Recommend replacement; operator decides.
   │
   └─ NO
      │
      Is it REAL DATA — production records, logs, registry-valid identifiers?
      │
      ├─ YES
      │  │
      │  Does it contain personal data (names, emails, phones, health,
      │  financial identifiers tied to a person)?
      │  │
      │  ├─ YES ────────────────────► 🔴 BLOCKER
      │  └─ NO (opaque record IDs, volume metrics, business figures)
      │     └───────────────────────► 🟠 HIGH — untrack + gitignore
      │
      └─ NO
         │
         Is it FACTORY INTERNAL (agent docs, skills, briefs, session logs,
         security findings, decision records)?
         │
         ├─ YES ───────────────────► 🔴 BLOCKER — proprietary IP + client context
         │                             Clean-room if tracked in public history.
         │
         └─ NO
            │
            Is it INFRASTRUCTURE topology (project IDs/numbers, service
            accounts, secret names, staging hosts)?
            │
            ├─ YES ────────────────► 🟠 HIGH — templatize
            │
            └─ NO (fossils, stale claims, clutter, dead scripts)
               └───────────────────► 🟡 JUDGMENT — recommend, don't block
```

---

## Severity meanings

| Severity | Meaning | Operator action |
|---|---|---|
| 🔴 **BLOCKER** | Publishing this causes real harm — access, confidentiality, or IP loss | Stop. Remediate before any push. |
| 🟠 **HIGH** | Real identifiers or topology; harmful in aggregate or over time | Fix before push. |
| 🟡 **JUDGMENT** | Optics, hygiene, clutter, stale claims | Operator's call. |
| 🟢 **CLEAN** | Verified absent, with the check named | Report the negative — it has value. |

## Rules that override the tree

**Anything in history on a public repo escalates.** File edits do not undo publication. If a
BLOCKER-class item is in a public history, rotation and/or clean-room enter the recommendation
regardless of what the current tree looks like.

**Aggregation escalates.** Individually harmless coordinates — a project ID here, a service
account there, a domain in a third file — combine into a reconnaissance map. When you find
three or more infrastructure items, report them as one HIGH finding, not three JUDGMENT ones.

**Uncertainty escalates one level, then asks.** If you cannot determine whether a mock
identifier is real, treat it as the higher severity and mark it QUESTION. Checksum-verify
where a public registry exists; a valid checksum may resolve to a real person.

## What never gets softened

Do not downgrade a finding because the operator is in a hurry, because the repo is old,
because "nobody visits," or because the app is retired. Retired-with-a-live-endpoint is
unattended, not safe. Low traffic is not low findability — scanners and crawlers read
everything.
