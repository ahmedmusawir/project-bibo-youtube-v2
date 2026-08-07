# 03 — Assets

**Goal:** Get what only the operator has. Then stop.

---

## Why this is a gate and not a guess

You cannot see screenshots, diagrams, or videos. You cannot infer the operator's intended
layout. And some of the most important framing in a README — whether an app is live or
retired, what may and may not be claimed about client work, when it ran in production — is
history, not code.

This is the one phase where asking is correct. Everything discoverable was already discovered
in Phases 0 and 2; what remains is genuinely unknowable from disk.

## Ask specifically

Do not open with a blind question list. Lead with what you have, so the operator only fills
gaps:

```
FACTS COMPLETE. Summary: {stack, versions, routes, tests, audit — one line}

To build the README I need:

1. IMAGE URLs + layout directions
   (e.g. "these 3 single-column in this order" / "these 4 in a 2-column table")
2. Architecture DIAGRAM url, and where it should sit
3. Any walkthrough VIDEO urls — I'll render them as clickable thumbnails
4. Confirm or correct my proposed one-liner:
   "{your proposed one-liner}"
5. Story context I can't read off disk:
   - live / staged / retired, and production dates if applicable
   - anything that must NOT be claimed
   - hand-built vs factory-built history

Waiting on these before I write.
```

Including your proposed one-liner is deliberate. It is the single highest-leverage sentence
in the document, and it is cheaper for the operator to correct it now than after you have
built the whole README around a wrong angle.

## Asset provenance — hard rule

**Every image, diagram, and video in the README comes from the operator or from the repo's existing README. You introduce none.**

Not a stock photo. Not an illustrative graphic. Not a URL you found in a component or a config. Not a placeholder that fits the slot. If the operator supplies three images and the template shows four cells, you build three cells.

You cannot see images. An asset you did not receive is an asset whose content you are guessing at, and a guessed image captioned as a product screen is fabricated evidence on a public page.

If the layout feels thin, say so in the handoff and let the operator add more later. Thin and true beats full and false.

## Operator facts — verbatim

The story context he gives you is the only source for claims about history, deployment, clients, and provenance. Reproduce it at its stated strength.

| He says | You write | You do NOT write |
|---|---|---|
| "staged on a droplet" | staged | "production-deployed" |
| (no date) | no date | "in production 2024" |
| nginx, SSL, DNS, CI/CD | those four | + "health checks, log monitoring" |
| hand-built, pre-methodology | hand-built, later brought under the methodology | "built as a Solution Module through the App Factory" |

He can verify every code claim you make by reading code. He is far less likely to catch an embellishment of *his own history* that sounds right — and that is the one that fails under a client's follow-up question. When his account is thinner than the section wants, the section gets thinner, or you ask him for more.

## Audit what he gives you

The operator chose each image for its subject. He did not review it for everything else on the screen.

If you have vision, open every supplied image and check for: real names, email addresses, phone numbers, account or record identifiers, internal URLs and hostnames, third-party customer or contact data, browser tabs and bookmarks, and anything else that identifies a real person or system. Report findings in the handoff as a decision for him — his data, his call — not as a blocker.

If you do not have vision, state that plainly in the handoff and hand the check back to him by name. An unstated limitation reads as an all-clear, and an all-clear on unreviewed images is how third-party personal data reaches a public page.

Observed in the wild: an operator-supplied screenshot of a CRM chat result displayed real contact names, emails, and phone numbers. It had been cleared by both the operator and the referee. The model caught it.

## Captions

If the operator supplies images without captions, you write them from route and component
code — and **flag every one for review**. You are describing screens you cannot see. Say so
explicitly in the handoff rather than letting a confident-sounding wrong caption ship.

## If the operator declines to supply assets

Build without them. A README with no screenshots is not a failure; a README with fabricated
descriptions of screenshots is. Note the gap in the handoff so he can add them later.

## Stop Gate

You have assets with layout directions, or an explicit instruction to proceed without them.

## Output

Asset request in chat, including the proposed one-liner and the facts summary.
