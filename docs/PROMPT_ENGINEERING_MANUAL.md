# PROMPT & INSTRUCTION ENGINEERING MANUAL

### (Engneering Edition) — **v1.1**

## What this manual is for

This manual exists to help you:

- Get **better first-pass results** from AI
- Reduce back-and-forth with chatbots and agents
- Design **agentic systems** where AI gives instructions to other AI
- Stop wasting time on prompts that _sound smart but don’t work_

This is not about clever wording.
This is about **clear responsibility and intent**.

---

## Core Principle (Everything Flows From This)

AI does not fail because it is dumb.
AI fails because **humans under-specify intent**.

Your job is not to “prompt better.”
Your job is to **externalize what’s in your head**.

---

## The Two Modes You Must Recognize

Before giving instructions, always decide which mode you are in.

### Mode 1: Precision Mode (MIT mindset)

Use this when:

- There is a correct or target outcome
- You care about accuracy, structure, or constraints
- You are writing code, specs, workflows, policies, or data logic

In this mode:

- Prompt quality matters a lot
- Vague prompts waste model capability
- Automated “helpful” rewriting hurts more than it helps

**Clarification:**
Precision Mode = **high descriptive density** (clear nouns and adjectives), **not** more instructions.

Rule:
**If the task is bounded, be explicit and structured.**

---

### Mode 2: Exploration Mode (Stanford mindset)

Use this when:

- There is no single correct answer
- You are brainstorming, planning, or shaping ideas
- Tone, judgment, or direction matters more than correctness

In this mode:

- Over-engineering prompts slows you down
- Clear intent beats detailed instructions
- Let the model explore, then refine

Rule:
**If the task is unbounded, don’t over-control.**

---

## Both Modes — Practical Example

| Task                | Mode        | Prompt Style                                                                                                                                         |
| ------------------- | ----------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| Product description | Exploration | Give me 5 different angles — playful, premium, practical, etc.                                                                                       |
| Product description | Precision   | Write 50 words. Tone: rugged/professional. Must include: marine-grade aluminum, powder-coated finish, lifetime warranty. Do NOT mention competitors. |

---

## What to STOP Doing (Hard Rules)

These apply to both humans and agents.

- Stop saying “Act as an expert”
- Stop assuming the AI knows what you’re thinking
- Stop using one-size-fits-all prompt templates
- Stop expecting better results just because the model is newer
- Stop asking for “best practices” without defining constraints
- **Stop using the same prompt across model versions — prompts are perishable, not permanent**

If you wouldn’t say it to a human coworker, don’t say it to AI.

---

## What to Do Instead (This Is the Playbook)

Every instruction — human or AI — should contain **seven elements**.
You don’t need fancy wording.
You need coverage.

### 1. Problem Definition

Say:

- What you are trying to achieve
- What “done” looks like

**Humanity Test:**
If a human colleague couldn’t complete this task with only your instructions, **neither can AI**.

Example in plain language:
“I want a clear plan I can execute today, not theory.”

---

### 2. Constraints

Say:

- What tools are allowed
- What must be avoided
- Any hard limits (time, tech, style)

This prevents the AI from guessing.

---

### 3. Structure Expectations

Say:

- How the answer should be organized
- Sections, bullets, steps, or summaries

Structure guides thinking better than personas.

---

### 4. Reasoning Direction

Instead of saying “think step by step,” say:

- “First explain the big idea”
- “Then break it into parts”
- “Then explain risks or tradeoffs”

You guide **order**, not internal thoughts.

---

### 5. Evaluation Lens

Always ask:

- What could go wrong?
- What are the tradeoffs?
- What are alternatives?

This dramatically improves agent reliability.

---

### 6. Iteration Permission

Explicitly allow refinement:
“This doesn’t need to be perfect. We’ll refine after.”

This reduces overconfidence and hallucination.

---

### 7. Examples (Few-Shot)

Provide **3–5 “Greatest Hits” examples** of what _good_ looks like, plus **one bad example** to avoid.

**Good Examples (Greatest Hits):**

- A concise product blurb that hits all required features without hype
- A step-by-step execution plan with clear owners and timelines
- A customer response that matches brand voice and resolves the issue in one pass
- A code review summary that flags risks, suggests fixes, and prioritizes impact

**Bad Example (Avoid This):**

- A generic, buzzword-heavy response that sounds polished but misses required details
  If needed, ask the AI to generate the **exact opposite** of your best example and label it “Do Not Do This.”

Examples anchor expectations faster than explanations.

---

## Agentic Work: AI Prompting AI (Critical Section)

This is where most systems break if not handled deliberately.

When one AI writes instructions for another AI, you are doing **delegation**, not prompting.

Treat it like this:

- Planner AI defines intent and constraints
- Executor AI performs the task
- Reviewer AI evaluates against goals

**Critical Rule:**
In AI-to-AI chains, the **instructor AI must transfer ALL implicit context explicitly** — voice, constraints, and examples.
If it doesn’t, downstream output reverts to the **average of the internet**.

The most important rule here:
**The AI that writes the prompt must explain the job, not the wording.**

Bad:
“Write a prompt for another AI to do X.”

Good:
“Write instructions another AI can follow without guessing intent.”

This keeps agent chains stable.

---

## Chatbots: How This Applies

For chatbots and assistants:

- Default to Stanford mindset for conversation
- Switch to MIT mindset for actions
- Always make the transition explicit

Example:
“Now switch to execution mode. Do not explain. Just perform.”

This prevents “chatty execution” and “sloppy actions.”

---

## Mental Models to Remember (Coach-Friendly)

- AI is a smart intern, not a mind reader
- Prompts are job descriptions, not magic spells
- Better models increase the cost of bad instructions
- Clarity compounds more than cleverness
- Humans are still responsible for outcomes

---

## One Rule to Rule Them All

If you remember only one thing from this manual, remember this:

**Good AI output comes from clear responsibility, not clever prompts.**

---

## How Coach Can Use This Immediately

Coach does not need to learn prompting.

He only needs to:

- Say what he wants
- Say what matters
- Say what must not happen
- Say how success will be judged

That’s it.
Everything else is optimization.

---

## Closing

This manual is not finished — it is **alive**.

As models change:

- Prompts must change
- Humans must adapt
- Systems must evolve

What does not change is this:

**Clear intent beats clever wording. Always.**
