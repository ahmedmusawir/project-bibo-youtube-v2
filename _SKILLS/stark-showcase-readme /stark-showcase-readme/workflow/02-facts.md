# 02 — Facts

**Goal:** Earn every number the README will print.

Runs only after the operator clears Phase 1 and executes any remediation he chose.

---

## The standard

Every figure destined for a badge, a bullet, or a verify-block traces to a command you ran or
a file you read **in this session**. Not a changelog. Not a previous README. Not a config
file that mentions a framework. Not memory.

A number that happens to be correct but was not verified is still a failure. Right-by-luck
is not discipline.

## What to collect

**Versions** — read the manifest. Record the *installed* version where it differs from the
declared range.

**Build** — run it cold. Record exit code and route/page count. If it fails without
environment variables, that is a Quickstart caveat the operator's future cloners will hit —
capture the exact failure.

**Types** — run the typechecker if the stack has one.

**Tests** — run them. Record passing count and suite count. If no suite exists, the output is
**"no test suite exists"** and there is no test badge. A framework named in a config or a doc
is not a suite.

**Audit** — run the dependency scan. Record the real result, including the production-only
result where the tooling distinguishes it. Note fixable versus upstream-blocked. An audit
summary count is not an inventory — capture the full advisory list, because grepping for the
package you already suspect hides every other one in the same count.

**Architecture** — read code, do not paraphrase docs. Map:
- Entry points and route structure
- Service boundaries and integration flows
- Auth enforcement points — where roles resolve, where guards actually run
- State management and data contracts
- The mock/real boundary if this is an FFM

**Docs inventory** — real filenames from disk, one line each. Every link in the README's docs
table gets verified before it ships.

## When a check cannot run

Say so plainly. Do not substitute a doc's claim. Mark any dependent figure `[VERIFY: claim]`
and surface it in the fact sheet so the operator can settle it or authorize the environment
setup.

If running a check requires installing dependencies and the operator has not authorized it,
ask — that is a legitimate question because it is an action, not an inference.

## Gate

Every badge-bound number has a provenance. You can name the command that produced it.

## Output

Fact sheet in chat: versions, build result and route count, typecheck result, test counts,
audit result, architecture map, docs inventory. Flag anything unverifiable.
