# ANTI-PATTERNS — How This Mission Fails

Every entry here happened on a real Stark mission. Read before Phase 3.

---

## Process failures

### ❌ Painting before sweeping
"The repo looks clean, I'll just do the README." Every repo that burned the operator looked
clean. The sweep is not a formality; it is the mission's actual value.

### ❌ Sweeping vacuously
Running `git ls-files | grep ...` on a repo whose tree is uncommitted. Every check passes
because nothing is tracked. Sweep the shippable set and say which set you swept.

### ❌ Name-waving instead of verifying
"There is a `logs/` directory" is not a finding. Open the files. Count the records. Identify
the format. Run the disconfirming check and report the negative.

### ❌ Rolling past a stop gate
Finishing the sweep and "getting a head start" on facts. Or building the README because the
operator seemed to want speed. Stop gates exist because the operator holds context you do
not have — including which findings are acceptable and which are blockers.

### ❌ Deciding for the operator
Deleting a flagged file. Rotating a key. Choosing whether client-internal docs are
acceptable to publish. You surface and recommend; he decides.

### ❌ Fixing forward on a flagged commit
Secret scanners judge every commit in the push. A cleanup commit stacked on a dirty one gets
rejected identically — same hash flagged, same line cited. The dirty commit must be
*replaced*. Tell the operator this explicitly; the failure mode looks insane from the outside
("but the file is clean!").

---

## Content failures

### ❌ Inventing numbers
Test counts inherited from a changelog. Route counts from a doc. A version from memory. If a
config mentions Jest but no suite exists, the answer is "no test suite exists."

### ❌ Right-by-luck
A number that happens to be correct but was not verified this session is still a failure. The
discipline is the point, not the outcome.

### ❌ Badging an unearned claim
"npm audit: 0 vulnerabilities" when the audit reads 5 high. Omit the badge rather than print
a flattering lie — and say why in the report.

### ❌ Spec-ware
Describing a planned feature as an existing one. Architects' briefs describe the app as
*specified*; the disk holds the app as *built*. Ship the disk.

### ❌ Bulldozing the operator's work
Replacing a README that already has diagrams, screenshots, and a working structure because a
template says the sections go in a different order. Preserve and wrap.

### ❌ Resume voice
"I built this to showcase my skills." Junior signal — it makes the repo about the author. The
product sells the project; the project sells the author. Trust the inference.

### ❌ Jargon walls
"FFM output feeds the BIM per factory doctrine." Say it in plain English, put the factory term
in parentheses once.

### ❌ Publishing the bypass
Documenting the exact role flag and equality check that gates the superadmin portal. Or the
named escape-hatch route. Describing that access is role-gated is fine; publishing the recipe
is not.

### ❌ Claiming compliance
"HIPAA-compliant application." Compliance is a property of a deployed system with a backend,
agreements, and audit controls. Claim the **trajectory**: "being built toward a
HIPAA-compliant production system."

### ❌ Claiming autonomy
"Fully automated pipeline." If a human presses the button between stages, it is
human-in-the-loop — and in regulated or client-facing work, human-gated is the *stronger*
claim. Sell the gate.

### ❌ Shipping coordinates
Naming the GCP project, service accounts, staging hostnames. Write "a dev WordPress backend,"
never the URL.

### ❌ Stale "Live" badges
A live-site badge pointing at a retired deployment invites the reader to go find an
unattended app. If it is retired, say "built and operated in production 2024–2025."

---

## Technical traps

### ❌ Placeholders that cosplay as secrets
`sk_test_` + 24 filler characters matches the scanner regex perfectly and blocks the
operator's push. Use `sk_test_YOUR_SECRET_KEY`. Words, never repeated filler.

### ❌ Assuming `.gitignore` removes tracked files
It does not. It prevents *future* tracking. Already-tracked files need an untracking command
— which the operator runs.

### ❌ Assuming untracking removes history
It does not. Only rewriting commits or **rotating the secret** makes history harmless. On a
repo that was ever public, assume permanence and rotate.

### ❌ Reprinting secrets in the report
Proving a finding exists does not require publishing the value. Redact. Your report is a file
that may itself be committed by mistake.

### ❌ Flagging JWT-shaped noise
Image URL query parameters and lockfile integrity hashes match `eyJ...`. Verify before
flagging.

### ❌ Missing `NEXT_PUBLIC_` implications
Gathering the fact ("this env var exists") without the inference ("this ships to every
visitor's browser"). Facts without inference is the most common near-miss. Trace the imports
and state the consequence.

### ❌ Trusting an audit summary count
The count aggregates multiple packages. Grepping for the one you suspect hides the rest.
Capture the full advisory list.

### ❌ Leaving dead code that is a loaded gun
A commented-out `console.log` of a service-role key is dead — until someone uncomments it.
Flag it even when it is not currently live.

---

## The meta-failure

### ❌ Assuming low traffic means low exposure
"Nobody visits my repos." Nobody browses them. **Everything** crawls them — credential
scanners within minutes of a push, training crawlers, and GitHub code search, which makes any
string in any public repo findable by anyone who types it.

Findability, not traffic, is the variable. Zero visitors and total exposure coexist
comfortably.
