# Practice Demo Script — Live Cursor Build (60 min)

> This is the step-by-step script for the live demo portion of the workshop.
> You will build an "Initiative Planner" project from scratch in Cursor.
> The audience watches the project grow from an empty folder to a connected system.

---

## Narrative arc

**Empty folder → Structured project → Smart assistant → Connected system**

Each concept builds on the previous. The folder tree grows visibly after each beat.

---

## Before you start

### Pre-demo checklist

- [ ] Cursor is open, clean workspace, no distracting tabs.
- [ ] Font size large enough for projection (Settings > Font Size: 16-18).
- [ ] Chat panel open on the right side.
- [ ] MCP connections pre-configured and tested (Jira, Notion, or Statsig).
- [ ] The `ab-test-prd` SKILL.md is available in `.cursor/skills/ab-test-prd/`.
- [ ] An empty `Initiative_Planner/` folder ready (or create it live).
- [ ] Starter files for each beat ready in a separate folder as backup (see `workshop/Initiative_Planner/`), in case the AI generates something unexpected or you need to speed up.

### Transition from slides

Say: *"Everything I just talked about — velocity, context engineering, workflows — we're going to make it real. We'll start with an empty folder and end with a connected system. Let's go."*

---

## ACT 1: FOUNDATION (20 min)

### Beat 1 — Cursor orientation + why not web-based apps (5 min)

**Concepts covered:** #1 High-level Cursor concepts, #2 Why Cursor over web apps

#### What to show

Open Cursor. Point to four things:

1. **Editor** (left) — "This is where your files live. Just like any code editor, but you don't need to write code."
2. **Chat panel** (right) — "This is where you talk to the AI. Think of it as your co-pilot."
3. **Model selector** (top of chat) — "You can pick which AI model to use. Different models, different strengths."
4. **Mode selector** — "Ask mode is read-only: it answers questions. Agent mode can create and edit files."

#### Talking point: Why an IDE, not ChatGPT/Claude web?

Say: *"Web-based tools like ChatGPT or Claude are great for one-off questions. But when you're building a system — files that reference each other, rules that persist, templates that get reused — you need something that lives in your file system. That's the difference: a chat window forgets; a project remembers."*

Key differences to mention:
- **Persistence**: Files stay. Chat history in web apps is disposable.
- **Context**: Cursor automatically reads your project files. Web apps only know what you paste.
- **Instructions**: .cursorrules and MDC files mean the AI behaves consistently, every time.
- **Connections**: MCP lets Cursor talk to Jira, Notion, Statsig. Web apps are isolated.

#### Time check: ~5 min elapsed

---

### Beat 2 — README.md (8 min)

**Concept covered:** #3 Markdown files (part 1 — README)

#### What to do

1. Create a new folder: **File > Open Folder > Create "Initiative_Planner"**
   (Or do it from terminal: `mkdir Initiative_Planner && cd Initiative_Planner`)

2. Create `README.md`. Either type it or ask Cursor in Agent mode:

**Prompt to type:**
```
Create a README.md for a project called "Initiative Planner."
It's a system to plan, track, and make decisions on product initiatives.
It helps PMs to:
- Draft initiative briefs
- Track initiative status and decisions
- Keep a decision log across all initiatives
- Generate insights from past decisions
```

3. Review the generated README. It should contain:
   - Project title and description
   - What it does (list of capabilities)
   - How to use it (steps)
   - Folder structure (drafts/, decisions/, templates/)

**Expected AI output:** A structured markdown file with sections. If it's too long or adds things you didn't ask for, that's fine — it shows the AI's default behavior without guardrails. You'll fix that next.

#### Talking point: README as source of truth

Say: *"This is the single most important file. It tells both humans and AI what this project is, what it does, and how it's organized. If it's not in the README, the AI doesn't know about it."*

#### Demo the power of just a README

Switch to **Ask mode** (or start a new chat). Ask:

**Prompt to type:**
```
What does this project do?
```

Show the AI reads the README and answers accurately. Say: *"One file. Zero setup. The AI already understands the project."*

#### Time check: ~13 min elapsed

---

### Beat 3 — .cursorrules (7 min)

**Concept covered:** #3 Markdown files (part 2 — .cursorrules), the difference between README and .cursorrules, what's in context by default

#### What to do

1. Create `.cursorrules` in the project root. Type or ask Cursor:

**Prompt to type:**
```
Create a .cursorrules file for this project. It should include:

Project rules:
- Use README.md as the single source of truth for scope and "done."
- Work in small steps: one file, one feature, or one section per change.
- Current phase: Phase 1 - foundation. In scope: project setup, initiative brief template, decision log. Out of scope: full analysis, UI, integrations.
- When the user describes an initiative, ask for: problem, goal, success metrics. If any is missing, ask once; then generate using placeholders.

Response style:
- Default to medium-length responses. Be concise; cover what matters.
- Do not compliment or praise the user; go straight to the answer.
- Do not assume the user knows the subject. If a question is unclear or off-track, say so.
- Do not overstate confidence. If evidence is low, say so.
```

2. Show the file was created. Open it and walk through the two sections.

#### Talking point: Rules first, then build

Say: *"Rules first, then build. If you start adding features without guardrails, the AI will guess scope, style, and how much to change. .cursorrules gives it a fixed set of instructions from the very first interaction."*

#### Talking point: What's in context by default

Say: *".cursorrules is always in context — Cursor reads it automatically every time you chat. The README is NOT automatically included, but we told the AI to treat it as the source of truth, so it chooses to read it. That's the difference: .cursorrules is injected; everything else the AI decides to read based on what's relevant."*

#### Demo the before/after

Start a new chat. Ask:

**Prompt to type:**
```
I want to plan an initiative about improving the onboarding flow.
```

**Expected AI response:** The AI should ask for problem, goal, and success metrics (as instructed in .cursorrules), instead of just generating something. This is the behavior change. Say: *"See? Before, it would have just generated something. Now it asks the right questions first, because we told it to."*

#### Time check: ~20 min elapsed

---

## ACT 2: WORKFLOWS (20 min)

### Beat 4 — Templates (8 min)

**Concept covered:** #4 Using templates for document structure

#### What to do

1. Create the templates folder and file:

**Prompt to type:**
```
Create templates/initiative_brief.md with the following structure:

# [Initiative Name]

## Problem
What problem are we solving? Who is affected? What's the current impact?

## Goal
What does success look like? What's the desired outcome?

## Success Metrics
- Primary metric:
- Secondary metrics:
- Guardrail metrics (must not regress):

## Scope
### In scope
### Out of scope

## Risks and Dependencies

## Timeline
- Start:
- Key milestones:
- Expected completion:

## Decision
(To be filled after review)
```

2. Update `.cursorrules` to reference the template. Add this line:

**Prompt to type:**
```
Add this rule to .cursorrules under the Project section:
"For initiative briefs, follow the format in templates/initiative_brief.md."
```

3. Now test it. Start a new chat:

**Prompt to type:**
```
Draft an initiative brief: we want to improve the onboarding flow to reduce drop-off in the first 7 days.
```

**Expected AI response:** The AI should either ask for missing info (problem, goal, metrics) or generate a brief that follows the template structure. Show the audience that the output matches the template format.

#### Talking point: Templates mean consistency

Say: *"Templates mean you define the structure once, and every draft follows it. You're not re-explaining the format every time. The AI has a 'saved reference' — it knows what good looks like."*

#### Time check: ~28 min elapsed

---

### Beat 5 — Context rot + commands (5 min)

**Concept covered:** #5 Context rot and how to combat it with commands

#### What to explain

Say: *"We've been chatting for a while now. In a real session, after 20-30 exchanges, the AI starts getting worse. Not because it forgets, but because the 'desk' is full — too much stacked on, and the important bits get buried. That's context rot."*

#### What to do

1. Create the commands folder and files:

**Prompt to type:**
```
Create two command files:

1. .cursor/commands/save-context.md with these instructions:
"Summarize the current conversation into a structured context block. Include: key decisions made, open questions, current project state, and next steps. Append this block to CONTEXT_LOG.md with today's date as a heading. If the file doesn't exist, create it."

2. .cursor/commands/clear.md with these instructions:
"Remind the user that context has been saved to CONTEXT_LOG.md. Suggest starting a new chat and @-mentioning CONTEXT_LOG.md to recover context."
```

2. Show the commands in Cursor. Type `/` in the chat to show the command picker.

3. Run the save-context command:

**Type in chat:** `/save-context`

**Expected AI response:** The AI reads the conversation, summarizes it, and creates/appends to CONTEXT_LOG.md.

4. Open CONTEXT_LOG.md and show the saved context.

#### Talking point: Save, clear, recover

Say: *"Save what matters, clear the desk, recover in a new chat. That's it. Three steps. Your context log becomes the bridge between sessions."*

#### Time check: ~33 min elapsed

---

### Beat 6 — Decision log (7 min)

**Concept covered:** #6 Creating a decision log to track what's going on

#### What to do

1. Create the decisions folder and the initiative log:

**Prompt to type:**
```
Create the following:
1. A decisions/ folder
2. An initiative_log.md file in the root with this structure:

# Initiative Log

| Initiative | Area | Status | Decision | Primary Metric | Outcome |
|-----------|------|--------|----------|----------------|---------|
| (entries will be added as initiatives progress) |
```

3. Now create a decision memo from the initiative brief we drafted earlier:

**Prompt to type:**
```
Based on the onboarding initiative brief we drafted, create a decision memo at decisions/onboarding_flow_improvement.md.
Include: initiative name, area, decision (go/no-go), primary metric + expected outcome, rationale, what we learned so far, and next steps.
Then add a row to initiative_log.md.
```

**Expected AI response:** A decision memo file AND an updated log with a new row.

4. Show both files to the audience. Open the log and point out the horizontal view.

#### Talking point: Institutional memory

Say: *"If it's not written down, it didn't happen. The decision memo is the full story for one initiative. The log is the bird's-eye view across all of them. Together, they're your institutional memory — and the AI can query them later."*

#### Demo the power of the log

**Prompt to type:**
```
What initiatives are we tracking? What's their status?
```

The AI reads the log and summarizes. Say: *"One question, instant overview. Imagine this with 20 initiatives."*

#### Time check: ~40 min elapsed

---

## ACT 3: SCALING AND CONNECTING (20 min)

### Beat 7 — MDC files / rules (7 min)

**Concept covered:** #7 Using .mdc files (rules) to scale your system

#### What to explain

Say: *"So far we have one .cursorrules file. That works when the project is small. But as it grows, one file becomes long and mixed. MDC files let you split rules into separate files, each scoped to specific file patterns. The AI only loads them when relevant files are open."*

#### What to do

1. Create an MDC rule file:

**Prompt to type:**
```
Create .cursor/rules/initiative-brief.mdc with this content:

---
description: When writing or editing an initiative brief, keep structure and naming consistent.
globs: drafts/**/*.md, initiatives/**/*.md
alwaysApply: false
---

# Initiative brief rules

- Follow the template structure in templates/initiative_brief.md.
- Always include: Problem, Goal, Success Metrics, Scope, Risks, Timeline.
- Use the same initiative name across drafts/, decisions/, and initiative_log.md.
- When the brief is finalized, suggest creating a decision memo and adding a row to initiative_log.md.
```

2. Show the MDC file in the editor. Point to the frontmatter:
   - `description`: human-readable purpose
   - `globs`: file patterns that trigger this rule
   - `alwaysApply: false`: only activates when matching files are open

3. Demo: Open a file that matches the glob (e.g., create `drafts/onboarding_flow_improvement.md`). Start a chat and show that the MDC rule is now in context.

#### Talking point: From one file to many, scoped

Say: *"MDC is the path to scale. Instead of one giant rules file, you have focused rules that activate only where they matter. One for briefs, one for decisions, one for analysis. The AI gets the right context at the right time."*

#### Show the Cursor UI

Point out: Cursor Settings > General > Rules section, where MDC files appear with their scope indicators.

#### Time check: ~47 min elapsed

---

### Beat 8 — MCP (7 min)

**Concept covered:** #8 Interacting with MCP (Model Context Protocol)

#### What to explain

Say: *"Everything we've built so far is local — files on your machine. MCP changes that. It's an open protocol that lets Cursor talk to external tools: Jira, Notion, Statsig, Slack. The AI can read from and write to the tools you already use."*

#### What to do

1. Show the MCP configuration. Open (or reference) `.cursor/mcp.json`:

Say: *"This file tells Cursor which servers to connect to and how to authenticate. Each server exposes tools the AI can call."*

2. Show the MCP status: **Cursor > Settings > Tools & MCP**. Point out the green indicators for connected servers.

3. Demo a real MCP interaction (use whichever you have configured — pick one):

**Option A — Jira:**
```
What are the open tickets in my current sprint?
```

**Option B — Notion:**
```
Show me the latest page updates in my product workspace.
```

**Option C — Statsig:**
```
What experiments are currently running? Show me a summary.
```

**Expected AI response:** The AI calls the MCP tool, retrieves real data, and presents it in the chat. This is the "wow" moment — live data, no copy-pasting.

4. (Optional, if time) Show a write operation:

```
Create a Jira ticket for the onboarding flow improvement initiative. Use the details from the decision memo.
```

#### Talking point: From local assistant to connected system

Say: *"MCP turns your co-pilot from a local assistant into a connected one. It can pull from and push to the tools you already use. No more copy-pasting between Cursor and Jira, or switching tabs to check Statsig."*

#### Time check: ~54 min elapsed

---

### Beat 9 — Skills (6 min)

**Concept covered:** #9 Leverage the power of Skills

#### What to explain

Say: *"The last concept: Skills. A skill is a reusable, multi-step workflow that the AI follows — like a playbook. It has: when to use it, what inputs it needs, and a step-by-step process. You codify your expertise once, and the AI applies it every time."*

#### What to do

1. Show the existing SKILL.md file. Open `.cursor/skills/ab-test-prd/SKILL.md`:

Walk through the structure:
- **When to use**: conditions that trigger the skill
- **Inputs**: what context to look for
- **Workflow**: 7 steps (Problem → Hypothesis → Predict → Exposure → Learnings → Analysis → Future Work)
- **Output template**: the final markdown format

2. Demo: trigger the skill by describing an A/B test:

**Prompt to type:**
```
I want to design an A/B test: we're testing whether adding a progress bar to the onboarding flow reduces drop-off. The hypothesis is that showing progress gives users a sense of completion, increasing the 7-day retention rate.
```

**Expected AI response:** The AI follows the skill workflow — it may ask for missing info (MDE, guardrail metrics, targeting), then produces a structured A/B test spec following the template in the skill.

3. Show the output. Point out how it matches the skill's output format, not a generic AI response.

#### Talking point: Codify your expertise

Say: *"Skills turn repeated multi-step actions into one-step commands. You define the playbook once — your years of experience writing AB tests, distilled into a structured workflow — and the AI follows it every time. That's the difference between 'I asked the AI and it gave me something' and 'the AI follows my process.'"*

#### Quick mention: creating new skills

Say: *"You can create skills for anything repetitive: writing retrospectives, preparing sprint reviews, drafting go/no-go memos. The structure is always the same: when to use, what to look for, steps to follow, output format."*

#### Time check: ~60 min elapsed

---

## Wrap-up transition

Say: *"That's it. We started with an empty folder and now we have: a structured project, an AI that follows our rules, templates for consistency, commands for context management, a decision log for institutional memory, scoped rules that activate where they matter, live connections to our tools, and a codified workflow for designing experiments. Let's go back to the slides for the closing."*

Switch back to the slide deck.

---

## Emergency time management

If you're running behind:

- **Beat 5 (commands)**: Can be explained verbally without a live demo. Show the file, skip running the command. Saves ~3 min.
- **Beat 6 (decision log)**: Can create the log file only, skip the decision memo creation. Saves ~3 min.
- **Beat 8 (MCP)**: If the MCP connection is flaky, show the config file and the status screen only, explain what would happen. Saves ~4 min.

If you're running ahead:

- **Beat 4**: Ask the audience for an initiative idea and draft it live. Adds engagement.
- **Beat 8**: Show both a read and write MCP operation.
- **Beat 9**: Walk through creating a new simple skill from scratch.

---

## Final folder structure

At the end of the demo, the project should look like this:

```
Initiative_Planner/
├── .cursor/
│   ├── commands/
│   │   ├── save-context.md
│   │   └── clear.md
│   └── rules/
│       └── initiative-brief.mdc
├── .cursorrules
├── README.md
├── CONTEXT_LOG.md
├── initiative_log.md
├── templates/
│   └── initiative_brief.md
├── drafts/
│   └── onboarding_flow_improvement.md
└── decisions/
    └── onboarding_flow_improvement.md
```
