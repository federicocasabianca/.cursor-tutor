# AI as Your PM Co-Pilot: From Ideas to Execution

> 2h Talk + Workshop | Slide Deck Outline

---

## PART 1 — INTRO (15 min)

---

### Slide 1: Title

**AI as Your PM Co-Pilot: From Ideas to Execution**

*Speaker notes:*
Open with energy. This is not a lecture about AI hype — it's a practical session where we'll actually build something. By the end, everyone will have a mental model for using AI as a working partner.

---

### Slide 2: Who am I

- PM managing a full product stream and one team.
- Daily AI user, not an AI evangelist. Pragmatic approach.
- Background in software engineering — IDE feels like home.
- Built a 4-part series on using AI as a PM co-pilot ([Part 1](https://fedecasabianca.substack.com/p/introducing-my-ai-pm-co-pilot-cursor), [Part 2](https://fedecasabianca.substack.com/p/introducing-my-ai-co-pilot-part-2), [Part 3](https://fedecasabianca.substack.com/p/introducing-my-ai-co-pilot-part-3), [Part 4](https://fedecasabianca.substack.com/p/introducing-your-ai-co-pilot-part)).

*Speaker notes:*
Keep this to 2 minutes max. The credibility comes from the demo, not the bio. Mention the article series — people can follow up later.

---

### Slide 3: The shift

**"The friction dropped."**

- Engineers who needed an afternoon can produce a first version by lunch.
- The PM who always had ideas but depended on someone else to ship them can finally get their hands dirty.
- This is not about replacing anyone. It's about removing bottlenecks between "I have an idea" and "here's a working version."

*Speaker notes:*
This is the hook. The audience should feel recognized — whether they're PMs who've been curious, engineers who've seen the speed change, or designers watching the handoff evolve. Pause after the quote and let it land.

---

### Slide 4: What we'll cover today

**Agenda:**

| Block | Duration | What |
|-------|----------|------|
| Intro | 15 min | Why this matters now |
| Theory | 30 min | Velocity, the PM role, collaboration |
| Practice | 60 min | Build an AI co-pilot from scratch in Cursor |
| Closing | 15 min | Mental model, resources, Q&A |

**By the end:** You'll have a mental model for how to start using AI as a working partner, and you'll see a project built from zero to a connected system.

*Speaker notes:*
Set expectations clearly. The theory is curated, not exhaustive — 3 themes, 10 minutes each. The practice is a live demo: things may break, and that's fine. That's how it works in real life too.

---

## PART 2 — THEORY (30 min)

---

### Theme 1: Velocity and Speed (10 min)

---

### Slide 5: The new speed

**AI compresses the build-measure-learn cycle.**

- What used to take days (draft a spec, prototype, analyze results) can now happen in hours.
- The bottleneck shifts from **execution** to **judgment**.
- Simply adding AI tools to existing processes yields 20-40% gains. Redesigning workflows around AI produces 2-10x improvements.

*Visual suggestion:* Before/after timeline — "Draft a spec: 2 days → 2 hours. Analyze test results: 1 day → 30 minutes."

*Speaker notes:*
Ground this in something tangible. Everyone in the room has felt the "waiting for someone else to build it" pain. The key insight is not "AI is fast" — it's that the bottleneck moves. When execution is cheap, what matters is knowing what to execute. That's judgment. That's the PM's core skill.

**Source:** [McKinsey — How generative AI could accelerate software product time to market](https://www.mckinsey.com/industries/technology-media-and-telecommunications/our-insights/how-generative-ai-could-accelerate-software-product-time-to-market)

---

### Slide 6: What gets faster (and what doesn't)

| Gets faster | Does NOT get faster |
|-------------|---------------------|
| First drafts (specs, PRDs, briefs) | Strategic thinking |
| Data parsing and summarization | Stakeholder alignment |
| Boilerplate and repetitive docs | User empathy and research |
| Prototyping ideas | Organizational context |
| Analyzing experiment results | Judgment calls and trade-offs |

**The PM's value shifts from "producing artifacts" to "directing and curating."**

*Speaker notes:*
This is the nuance slide. The audience may include skeptics ("AI can't do my job") and over-optimists ("AI can do everything"). This slide addresses both. The left column is real — you'll see it in the demo. The right column is equally real — that's why the human stays in the loop.

**Source:** [McKinsey — AI fast-tracks software tasks](https://www.mckinsey.com/featured-insights/sustainable-inclusive-growth/charts/ai-fast-tracks-software-tasks) — generative AI reduces time on content-heavy tasks by ~40%, smaller impact (~15%) on analytical tasks.

---

### Slide 7: Evidence — the productivity gap

- **88%** of organizations use AI in at least one function, but **<20%** report material earnings impact. The gap: bolt-on vs. workflow redesign.
- **>50% of PMs** surveyed save at least half a day per week using AI.
- High-performing software orgs using AI see **16-30%** improvements in team productivity and time to market.
- 80% of AI value comes from **process redesign**, not the technology itself.

*Speaker notes:*
Don't dwell on every number. Pick one or two that resonate. The half-a-day-per-week stat from Lenny's survey is very tangible — ask the audience: "What would you do with an extra half day every week?" The 80/20 split on process redesign vs. technology is the setup for the practice section: what we're about to build IS the process redesign.

**Sources:**
- [Lenny Rachitsky — AI tools are overdelivering: results from our large-scale AI productivity survey](https://www.lennysnewsletter.com/p/ai-tools-are-overdelivering-results-c08)
- [McKinsey — Leading AI-driven software organizations show the way](https://www.mckinsey.com/industries/technology-media-and-telecommunications/our-insights/unlocking-the-value-of-ai-in-software-development)
- [Agentic AI Productivity Gains 2026: What the Data Actually Shows](https://www.buildmvpfast.com/blog/agentic-ai-productivity-gains-data)

---

### Theme 2: How AI Affects the PM Role (10 min)

---

### Slide 8: PM in the loop, not out of the loop

**"Helping the PM make a decision — not making the decision for the PM."**

- AI supports, it doesn't own. The human stays accountable for judgment, context, and trade-offs.
- Your job: deliver business impact by marshaling **human and AI resources** to solve customer problems.
- The most valued skill: **knowing what to build**, not building it yourself.

*Speaker notes:*
This is a direct quote from the .cursorrules file we use in the project. It's a guardrail we set for the AI, and it reflects a philosophy: AI is an amplifier, not a replacement. Pause and let the audience react. Some will nod, some will push back — that's good. The demo will show this in practice.

**Source:** [Lenny Rachitsky — Why PMs are best positioned to thrive in an AI world](https://www.lennysnewsletter.com/p/why-pms-are-best-positioned-to-thrive)

---

### Slide 9: New PM superpowers

Concrete examples (each maps to what we'll build in the practice):

1. **Draft an AB test in minutes** — describe the idea, AI fills the template.
2. **Summarize 50 experiments** — AI reads the log and gives you patterns.
3. **Generate insights from data** — drop a CSV, ask questions.
4. **Prototype ideas without engineering dependency** — show, don't describe.
5. **Keep institutional memory** — decision logs, context files, experiment histories.

*Speaker notes:*
Each bullet is something you'll see live in the practice section. Plant the seeds here so the demo feels like a payoff, not a surprise. Mention that these are real workflows, not hypothetical.

---

### Slide 10: New PM responsibilities

| Old responsibility | New responsibility |
|--------------------|--------------------|
| Write the prompt well | **Context engineering** — what you feed the AI matters more than the prompt |
| Trust the output | **Quality control** — AI output needs review, not blind trust |
| Use AI tools | **System design** — build reusable workflows, not one-off prompts |

**"AI needs more context than most teams realize. Think of it like onboarding a new intern."** — Teresa Torres

*Speaker notes:*
Context engineering is the big idea here. It's not about "prompting better" — it's about designing the information environment so the AI can do good work. This directly leads to the practice: README, .cursorrules, templates, MDC files are all context engineering.

**Sources:**
- [Teresa Torres — Context is King](https://www.producttalk.org/context-is-king-all-things-product-podcast-with-teresa-torres-petra-wille/)
- [Context Engineering: 5 Familiar Strategies from Real Product Teams](https://www.producttalk.org/context-engineering/)
- [Aman Khan / Marily Nika — PMs who use AI will replace those who don't](https://www.lennysnewsletter.com/p/this-week-on-how-i-ai-pms-who-use)

---

### Theme 3: Collaboration is Changing (10 min)

---

### Slide 11: The new handoff

**From "Can you build this?" to "Here's what I'm thinking, let's refine."**

- PMs can now **prototype and show**, not just describe.
- Designers get **concrete starting points** instead of abstract specs.
- Engineers get **clearer context** because the PM already iterated with AI.
- The conversation becomes collaborative refinement, not requirements handoff.

*Speaker notes:*
This is an optimistic slide, but ground it. The point is not that PMs become designers or engineers. It's that the gap between "idea in my head" and "something others can react to" shrinks dramatically. That changes the quality of the conversation.

---

### Slide 12: Shared context, not shared tools

- Teams don't all need to use the same AI tool.
- What matters: the **artifacts** (specs, templates, decision logs) are **structured and accessible**.
- **Markdown as a lingua franca** — human-readable, AI-readable, tool-agnostic.
- Decision logs, experiment histories, and templates become shared team knowledge — not locked in one person's head or chat history.

*Speaker notes:*
This is the setup for why we use markdown files and structured folders. It's not a technical choice — it's a collaboration choice. Anyone on the team can read a markdown file. Any AI tool can parse it. That's the point.

---

### Slide 13: What to watch out for

Three traps:

1. **Over-reliance** — AI as crutch vs. tool. If you can't explain the decision without the AI's output, you don't own it yet.
2. **Context rot** — AI performance degrades over long conversations. Manage the "desk" or the answers get worse. (We'll show how in the practice.)
3. **"It looks done"** — AI output looks polished but may lack depth. The PM's job is to catch the gap between "looks right" and "is right."

*Speaker notes:*
End the theory on a grounded note. These traps are real and the audience will encounter them. Context rot gets a direct solution in the practice section (commands). The "it looks done" trap is the most dangerous — it's why the PM stays in the loop.

**Source:** [Teresa Torres — Context Rot: Why AI Gets Worse the Longer You Chat](https://www.producttalk.org/context-rot/)

---

## PART 3 — PRACTICE (60 min)

> No slides — live Cursor demo. See `demo-script.md` for the full narrative.

**Transition slide: "Let's build."**

*Speaker notes:*
Switch from slides to Cursor. Take a breath. Say: "Everything I just talked about — velocity, context engineering, workflows — we're going to make it real. We'll start with an empty folder and end with a connected system. Let's go."

---

## PART 4 — CLOSING (15 min)

---

### Slide 14: What we built

**From empty folder to connected system in 60 minutes:**

- README.md + .cursorrules (foundation)
- Templates (consistency)
- Commands (context management)
- Decision log (institutional memory)
- MDC rules (scaling)
- MCP (external connections)
- Skills (codified expertise)

*Visual suggestion:* Screenshot of the final folder structure from Cursor.

*Speaker notes:*
Walk through the folder tree one more time. This is the "aha" moment — the audience sees that a simple, structured set of files creates a powerful system. No code, no complex setup.

---

### Slide 15: The mental model

**Foundation → Workflows → Scaling**

```
Foundation          Workflows             Scaling
┌──────────────┐    ┌──────────────────┐  ┌────────────────┐
│ README.md    │───>│ Templates        │─>│ MDC Rules      │
│ .cursorrules │    │ Commands         │  │ MCP Connections│
│              │    │ Decision Log     │  │ Skills         │
└──────────────┘    └──────────────────┘  └────────────────┘
```

You don't need all of this on day 1. Start with the left box. Move right when the pain tells you to.

*Speaker notes:*
This is the takeaway diagram. Repeat: "Start small, add when it hurts." README + .cursorrules is enough to start. Templates when you're repeating yourself. Commands when context rots. MDC when one rule file gets messy. MCP when you're tired of copy-pasting from other tools. Skills when you want to codify expertise.

---

### Slide 16: Start small

**"Design with the end in mind, but start small."**

- Day 1: Create a folder. Add a README. Add .cursorrules. Start asking questions.
- Week 1: Add a template for something you do repeatedly.
- Week 2: Notice context rot? Add save-context and clear commands.
- Month 1: Connect an MCP. Create your first skill.

*Speaker notes:*
Give them a concrete timeline. Most people won't do all 9 concepts tomorrow, and that's fine. The goal is to start with the first two files and let the system grow organically. Emphasize: "You can start today, with one folder and two files."

---

### Slide 17: Resources

**Article series:**
- [Part 1: Introducing my AI PM co-pilot](https://fedecasabianca.substack.com/p/introducing-my-ai-pm-co-pilot-cursor)
- [Part 2: Templates and drafting](https://fedecasabianca.substack.com/p/introducing-my-ai-co-pilot-part-2)
- [Part 3: Context rot, analysis, decision memos](https://fedecasabianca.substack.com/p/introducing-my-ai-co-pilot-part-3)
- [Part 4: Rules, MDC, and MCP](https://fedecasabianca.substack.com/p/introducing-your-ai-co-pilot-part)

**External references:**
- [Lenny Rachitsky — How AI will impact product management](https://www.lennysnewsletter.com/p/how-ai-will-impact-product-management)
- [Lenny Rachitsky — AI productivity survey results](https://www.lennysnewsletter.com/p/ai-tools-are-overdelivering-results-c08)
- [Teresa Torres — Context Rot](https://www.producttalk.org/context-rot/)
- [Teresa Torres — Context Engineering strategies](https://www.producttalk.org/context-engineering/)
- [McKinsey — AI-driven software organizations](https://www.mckinsey.com/industries/technology-media-and-telecommunications/our-insights/unlocking-the-value-of-ai-in-software-development)

**Tools:**
- [Cursor](https://cursor.sh)
- [MCP Protocol](https://modelcontextprotocol.io)

*Speaker notes:*
Have a QR code or short URL that links to a page with all these resources. Don't read them aloud — just say "these are in the resources slide, I'll share the deck."

---

### Slide 18: Q&A

**Questions?**

*Speaker notes:*
Open floor. If questions are slow to start, seed with: "One question I get a lot is: does this replace the need for engineering? Short answer: no. It replaces the need for you to wait before you can think out loud with a prototype." Keep answers concise — the demo spoke louder than any explanation.
