# Extraction Playbook

**Purpose:** Step-by-step process for extracting patterns from Python/ADK repositories

**Created:** 2026-02-22

---

## Mission

Extract architectural patterns, design decisions, and integration strategies from existing Python/ADK projects to inform manual creation.

**NOT creating manuals yet** - just documenting what exists.

---

## Process Overview

For each repository:
1. Understand context
2. Document architecture
3. Extract patterns
4. Capture decisions
5. Document integrations
6. Record testing strategies
7. Create docs in `/docs` folder
8. Update session file
9. Move to next repo

---

## Step-by-Step Extraction

### Step 1: Context Understanding

**Read:**
- `README.md` - What does this project do?
- `requirements.txt` / `pyproject.toml` - What dependencies?
- Main entry point - How does it start?

**Document:**
- Project purpose
- Tech stack
- Primary use case

**Questions to answer:**
- What problem does this solve?
- Who uses this?
- What's the scope (CLI, API, agent, library)?

---

### Step 2: Architecture Documentation

**Examine:**
- File/folder structure
- Module organization
- Entry points and flow
- State management approach

**Document in `/docs/architecture.md`:**

```markdown
# Architecture

## File Structure
[Describe layout and why]

## Core Abstractions
[Main classes, concepts, patterns]

## Data Flow
[How data moves through the system]

## State Management
[How state is tracked - files, DB, memory]

## Key Design Decisions
[Architecture choices and rationale]
```

**Key Questions:**
- Why this structure over alternatives?
- What are the core abstractions?
- How does state flow?
- What's the separation of concerns?

---

### Step 3: Pattern Extraction

**Look for:**
- Repeated code structures
- Common imports
- Standard utilities
- Configuration patterns
- Error handling approaches
- Logging conventions

**Document in `/docs/patterns.md`:**

```markdown
# Patterns

## Import Conventions
[Standard imports, common patterns]

## Configuration Management
[How configs are loaded/used]

## Error Handling
[Try/except patterns, custom exceptions]

## Logging
[What gets logged, how, where]

## File Operations
[Path handling, read/write patterns]

## API Calls
[How external APIs are called]

## Async Patterns
[If applicable - async/await usage]
```

**Key Questions:**
- What patterns repeat across files?
- What's the "house style"?
- What conventions are consistent?

---

### Step 4: Decision Documentation

**Identify:**
- Technology choices (why X over Y?)
- Architecture decisions (why this approach?)
- Trade-offs made (what was sacrificed for what gain?)
- Failed attempts (what was tried and discarded?)

**Document in `/docs/decisions.md`:**

```markdown
# Key Decisions

## [Decision 1 Name]
**Context:** [What was the situation?]
**Decision:** [What was chosen?]
**Alternatives:** [What else was considered?]
**Rationale:** [Why this choice?]
**Trade-offs:** [What was gained/lost?]

## [Decision 2 Name]
...
```

**Key Questions:**
- Why Python over Node.js?
- Why ADK over LangChain?
- Why file-based state over database?
- Why this API pattern?
- What constraints drove choices?

---

### Step 5: Integration Documentation

**Examine:**
- External service connections
- API integrations
- Cloud service usage
- Database interactions
- Third-party libraries

**Document in `/docs/integration_guide.md`:**

```markdown
# Integration Guide

## Vertex AI
- Which models used?
- How are they called?
- Context caching strategy?
- Rate limiting approach?

## Google Cloud Services
- Which services (Storage, Speech, TTS, etc.)?
- Authentication pattern?
- Error handling?

## External APIs
- Which APIs?
- Authentication?
- Rate limiting?
- Error handling?

## Databases
- Which database?
- ORM or raw queries?
- Migration strategy?
```

**Key Questions:**
- How does this connect to external systems?
- What's the authentication pattern?
- How are failures handled?
- What's the retry/fallback strategy?

---

### Step 6: Testing Strategy

**Examine:**
- `/tests` folder structure
- Unit tests
- Integration tests
- Mocking strategies
- Test data management

**Document in `/docs/testing_strategy.md`:**

```markdown
# Testing Strategy

## Test Structure
[How tests are organized]

## Unit Testing
- What gets unit tested?
- Mocking approach?
- Test data creation?

## Integration Testing
- What gets integration tested?
- Real APIs or mocks?
- Cost considerations?

## Evaluation (if applicable)
- How is agent performance measured?
- What metrics matter?
- How are evals run?

## CI/CD
- Automated testing?
- When do tests run?
```

**Key Questions:**
- What testing philosophy?
- What's mocked vs real?
- How is quality ensured?
- What's NOT tested (and why)?

---

### Step 7: Documentation Output

**Create in `/docs` folder:**

Minimum required:
- ✅ `architecture.md` - System structure
- ✅ `patterns.md` - Repeated conventions
- ✅ `decisions.md` - Why we chose X over Y

Optional (if applicable):
- `integration_guide.md` - External connections
- `testing_strategy.md` - Quality assurance
- `deployment_guide.md` - How to ship
- `troubleshooting.md` - Common issues

**Quality Check:**
- [ ] Can someone understand the system from these docs?
- [ ] Are patterns clear and repeatable?
- [ ] Are decisions explained (not just stated)?
- [ ] Is the "why" captured, not just the "what"?

---

### Step 8: Session File Update

**Update `session-YYYY-MM-DD.md`:**

```markdown
## Extraction Session: [Repo Name]

### What I Found
- Key architectural pattern: [description]
- Notable decision: [decision + rationale]
- Integration approach: [how external systems used]

### Docs Created
- `/docs/architecture.md` - [brief description]
- `/docs/patterns.md` - [brief description]
- `/docs/decisions.md` - [brief description]

### Insights for Manuals
- [Pattern that should be in manual]
- [Decision that represents best practice]
- [Anti-pattern to avoid]

### Questions/Gaps
- [Anything unclear or missing]

### Next Repo
[Which repo to tackle next]
```

---

## What NOT to Do

❌ **Don't create manuals yet** - That's consolidation phase
❌ **Don't summarize code** - Extract patterns, not line-by-line descriptions
❌ **Don't skip the "why"** - Decisions without rationale are useless
❌ **Don't document everything** - Focus on repeatable patterns
❌ **Don't guess** - If decision rationale unclear, mark as question

---

## Output Quality Standards

### Architecture Doc:
- Someone unfamiliar can understand system structure
- Design decisions are explained
- Flow of data/control is clear

### Patterns Doc:
- Conventions are explicit (not implicit)
- Examples are provided where helpful
- Patterns are actually repeated (not one-off)

### Decisions Doc:
- Context is provided (why was decision needed?)
- Alternatives are listed (what else was considered?)
- Rationale is clear (why this choice?)
- Trade-offs are acknowledged (what was sacrificed?)

---

## Template Usage

Use these templates as starting points, adapt as needed:

**For CLI tools:** Focus on argument parsing, command structure, output formatting

**For APIs:** Focus on endpoint design, request/response patterns, error handling

**For Agents:** Focus on state machine, tool patterns, context management, eval strategies

**For Libraries:** Focus on API design, abstraction patterns, extensibility

---

## Extraction vs Synthesis

**This phase (Extraction):**
- Document what EXISTS
- Capture PATTERNS
- Record DECISIONS
- Note QUESTIONS

**Next phase (Synthesis):**
- Identify patterns ACROSS repos
- Formulate BEST PRACTICES
- Create MANUALS
- Define STANDARDS

**Don't conflate the two.** Extraction is observation. Synthesis is prescription.

---

## Success Criteria

**Per Repo:**
- [ ] Architecture documented comprehensively
- [ ] Patterns extracted (not just listed)
- [ ] Decisions explained with rationale
- [ ] Session file updated with insights
- [ ] Docs pass quality check

**Overall:**
- [ ] Enough repos extracted to see cross-cutting patterns
- [ ] Sufficient diversity (CLI, API, agent, etc.)
- [ ] Decisions documented with context
- [ ] Ready for synthesis phase

---

## Progress Tracking

See `progress_tracker.md` for current status.

---

_Last updated: 2026-02-22_
