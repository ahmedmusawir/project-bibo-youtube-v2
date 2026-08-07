# README FACTORY TEMPLATE

The canonical visual format. Match the badge style, section rhythm, and table layouts.
Replace `{...}` placeholders. Delete sections that do not apply — an empty section is worse
than a missing one.

> **Reference implementation:** the Next.js 16 Enterprise Starter Kit README. If the operator
> attaches it, that file wins over this skeleton.

---

## Skeleton

````markdown
# {Project Name}

**{One-line value proposition — what it is, who it's for, under 20 words.}**

[![{Framework}](https://img.shields.io/badge/{Framework}-{version}-000000?logo={logoslug}&logoColor=white)]({docs-url})
[![TypeScript](https://img.shields.io/badge/TypeScript-{version}-3178C6?logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![{Backend}](https://img.shields.io/badge/{Backend}-{capability}-3FCF8E?logo={logoslug}&logoColor=white)]({url})
[![Tests](https://img.shields.io/badge/{Runner}-{N}%20passing%20%2F%20{M}%20suites-C21325?logo=jest&logoColor=white)](#verify-the-build)
[![Audit](https://img.shields.io/badge/npm%20audit-0%20vulnerabilities-2EA043)](./docs/SECURITY.md)
[![Live](https://img.shields.io/badge/Live-{domain}-2EA043)](https://{domain})
[![Walkthrough](https://img.shields.io/badge/YouTube-Walkthrough-FF0000?logo=youtube&logoColor=white)]({video-url})

---

## Why This Exists

{Paragraph 1 — the problem. What was broken, missing, or repeatedly rebuilt before this
existed. Concrete, not abstract. If it is client work, name the business problem.}

{Paragraph 2 — the key architecture decision, stated as doctrine. This is where an
architect-level reader decides whether you are one. Explain WHY this shape, what it trades
off. One sentence on methodology: built/operated through the App Factory, an AI-augmented
delivery methodology.}

---

## 🎬 Video Walkthrough

[![{Title}](https://img.youtube.com/vi/{VIDEO_ID}/maxresdefault.jpg)]({video-url})

{One line on what the walkthrough covers.}

<!-- If maxresdefault.jpg renders gray, fall back to hqdefault.jpg -->

---

## Screenshots

{Layout per operator direction. Two common forms:}

**Single column, full width** — for architecture diagrams and wide dashboards:

![{Caption}]({image-url})

*{1–2 sentence caption describing what the screen shows.}*

**Two column table** — for app screens:

| | |
|---|---|
| ![{alt}]({url-1}) | ![{alt}]({url-2}) |
| *{caption 1}* | *{caption 2}* |
| ![{alt}]({url-3}) | ![{alt}]({url-4}) |
| *{caption 3}* | *{caption 4}* |

---

## What's Inside

- **{Feature}** — {what it does, where it lives, why it is built that way}. Every bullet
  verifiable in code.
- **{Feature}** — {…}
- **{Feature}** — {…}

{6–8 bullets. Lead with the differentiators, not the table stakes.}

---

## {Stage / Status}

{For FFM-stage apps — state it proudly, as doctrine:}

This application is being built toward a {compliance-target}-compliant production system on a
{backend} backend. The current deploy is a **Frontend-First Module (FFM)** per factory
doctrine — deployed so the client and team can finalize features, flows, and design against
the live UI before backend work begins through formal Backend Integration Modules (BIMs),
fixes, and features. Domain data is mock **by design** at this stage; auth and role
enforcement ({auth-stack}) are real.

---

## From Build to Production

{For apps with an operational pipeline. Plain English first, factory terms in parens once.}

**DELIVERY** — {How work arrives and is scoped. Solution Modules (SMs), tickets, modules.}

**QA GATE** — {Acceptance criteria, certification before production. "No certification, no
ship."}

**PIPELINE** — {Stage 1 dev environment → Stage 2 production-staging with test transactions
→ Stage 3 release with CI/CD. Describe the stages; never name the hosts.}

**MONITORING & ROLLBACK** — {One line.}

---

## Documentation

| Document | Contents |
|---|---|
| [{FILE}.md](./docs/{FILE}.md) | {one line} |
| [{FILE}.md](./docs/{FILE}.md) | {one line} |

{Verify every filename on disk. No dead links.}

---

## Quickstart

Requires **{runtime + version}** ({how it is pinned}) and {external prerequisites}.

```bash
git clone {repo-url}
cd {repo-name}

{version-manager command}
{install command}

cp .env.example .env.local   # then fill in your values
```

{Any provisioning step — schema file, migration, external service setup.}

```bash
{dev command}
```

### Verify the build

```bash
{build command}      # → {expected result}
{typecheck command}  # → {expected result}
{test command}       # → {expected result}
{audit command}      # → {expected result}
```

{Note any environment requirement that would otherwise fail a fresh clone.}

---

Built by **[Ahmed Musawir](https://github.com/ahmedmusawir)** — Software Architect & AI Engineer.
{Methodology line ONLY if the project was actually built or is currently maintained through the
App Factory. For pre-methodology work, either omit it or use the honest arc: "Hand-built end to
end; later brought under the App Factory, an AI-augmented delivery methodology." Never credit a
methodology to work that predates it.}
````

---

## Badge rules

- **Every badge carries a number you earned this session.** No verified count, no badge.
- Omit the audit badge unless the audit genuinely reads zero. A missing badge is honest; a
  flattering one is a lie with a shield around it.
- Live-site badge only if the site is actually live. Retired app → drop it and use past-tense
  production credit in the prose.
- 6–8 badges maximum. Past that it reads as decoration.

## Emoji rules

Section emoji sparingly — 3–4 in the whole document. Badges do the visual work. Emoji spam
reads junior.

## Caption rules

You cannot see the operator's images. Write captions from route and component code, then
**flag every caption for operator review** in your handoff. Never guess at visual detail.
