# Skills crash course for PMs

## What are skills?

**Skills** are reusable “how-to” bundles for AI agents. Each skill is a small set of instructions (usually in a `SKILL.md` file) that teach the agent:

- **Procedures** — e.g. how to structure a PRD, run a brainstorm, or audit a page  
- **Formats** — e.g. how you want specs, tickets, or release notes written  
- **Domain knowledge** — e.g. product marketing, pricing, or CRO patterns  

When you (or your team) use an agent that supports skills, it can **automatically** use the right skill based on your request. You don’t have to re-explain your process every time.

---

## Why skills matter for PM work

| PM need | How skills help |
|--------|------------------|
| **Consistent artifacts** | PRDs, one-pagers, and specs follow the same structure and quality bar. |
| **Faster drafting** | The agent follows proven patterns (e.g. pricing strategy, launch strategy) instead of generic output. |
| **Less context pasting** | Your preferences and frameworks live in skills, so you don’t re-paste the same instructions. |
| **Team alignment** | Project skills (in the repo) make sure everyone’s AI uses the same conventions. |

---

## Where to get skills: [skills.sh](https://skills.sh/)

**[skills.sh](https://skills.sh/)** is the open agent-skills directory. You can:

- **Browse** by installs, trending, or search  
- **Install** with one command (see below)  
- Use skills across **Cursor, Codex, Cline, Windsurf**, and other supported agents  

### Install one skill

```bash
npx skills add <owner/repo>
```

Example — install the “product-marketing-context” skill from the marketing skills repo:

```bash
npx skills add coreyhaines31/marketingskills
```

That usually installs the **whole repo** (all skills in that repo). To get only one skill, check the skill’s page on skills.sh for the exact path (some tools support `owner/repo/skill-name`).

### Install multiple PM‑friendly skills (examples)

You can run `npx skills add` once per repo to pull in a whole set:

```bash
# Product & marketing context, positioning, launch, pricing, CRO, etc.
npx skills add coreyhaines31/marketingskills

# Brainstorming, writing plans, executing plans, code review workflows
npx skills add obra/superpowers

# Docs: PDF, DOCX, PPTX, XLSX, internal comms, brand guidelines
npx skills add anthropics/skills
```

After installing, **restart your agent/IDE** so it picks up the new skills.

---

## PM‑relevant skills on skills.sh (by category)

Pulled from the [skills.sh leaderboard](https://skills.sh/); install counts are approximate.

### Product & marketing

| Skill | Repo | Use when you need… |
|-------|------|---------------------|
| **product-marketing-context** | coreyhaines31/marketingskills | Positioning, messaging, PMM-style context |
| **pricing-strategy** | coreyhaines31/marketingskills | Pricing frameworks and options |
| **launch-strategy** | coreyhaines31/marketingskills | Launch plans and sequencing |
| **content-strategy** | coreyhaines31/marketingskills | Content planning and themes |
| **competitor-alternatives** | coreyhaines31/marketingskills | Competitive framing and alternatives |
| **marketing-ideas** | coreyhaines31/marketingskills | Campaign and tactic ideas |
| **copywriting** / **copy-editing** | coreyhaines31/marketingskills | Copy and editing quality |

### Experiments & growth

| Skill | Repo | Use when you need… |
|-------|------|---------------------|
| **ab-test-setup** | coreyhaines31/marketingskills | A/B test design and setup |
| **page-cro** / **onboarding-cro** / **form-cro** | coreyhaines31/marketingskills | CRO for pages, onboarding, forms |
| **paywall-upgrade-cro** / **popup-cro** | coreyhaines31/marketingskills | Monetization and popup flows |
| **analytics-tracking** | coreyhaines31/marketingskills | Event and analytics design |

### Strategy & planning

| Skill | Repo | Use when you need… |
|-------|------|---------------------|
| **brainstorming** | obra/superpowers | Structured ideation |
| **writing-plans** | obra/superpowers | Clear, stepwise plans |
| **executing-plans** | obra/superpowers | Breaking plans into actions |

### Docs & communication

| Skill | Repo | Use when you need… |
|-------|------|---------------------|
| **docx** / **pptx** / **xlsx** / **pdf** | anthropics/skills | Creating or editing Office/PDF docs |
| **doc-coauthoring** | anthropics/skills | Co-writing long-form docs |
| **internal-comms** | anthropics/skills | Internal updates and comms |
| **brand-guidelines** | anthropics/skills | On-brand copy and tone |
| **ralph-tui-prd** | subsy/ralph-tui | PRD-style structure (CLI/tooling context) |

### Research & quality

| Skill | Repo | Use when you need… |
|-------|------|---------------------|
| **audit-website** | squirrelscan/skills | Website audits |
| **seo-audit** | coreyhaines31/marketingskills | SEO review and recommendations |

---

## Example: using a skill end‑to‑end

### 1. Pick a task

Example: *“I need a one-pager for a new pricing tier and options for how to position it.”*

### 2. Install a relevant skill (once)

```bash
npx skills add coreyhaines31/marketingskills
```

Restart Cursor (or your agent) so it loads the new skills.

### 3. Ask in natural language

You don’t need to mention the skill by name. For example:

- *“Draft a one-pager for a new ‘Pro’ pricing tier. Use our positioning: [paste 2–3 sentences]. Give three positioning options and recommend one.”*
- *“Suggest a launch strategy for this feature: [brief description].”*

The agent will use **product-marketing-context**, **pricing-strategy**, or **launch-strategy** when they match your request (based on their descriptions).

### 4. Iterate

- *“Make option B more enterprise-focused.”*  
- *“Turn this into a short internal comms post for Engineering.”*

If you have **internal-comms** or **copy-editing** installed, the agent can lean on those for tone and structure.

---

## Example: brainstorming with a skill

1. **Install:**  
   `npx skills add obra/superpowers`

2. **Ask:**  
   *“Run a 10-minute brainstorm on ways we could reduce time-to-value for new users. Give me 10 ideas, then pick the top 3 and add one-line impact and effort.”*

3. The **brainstorming** skill guides the agent’s process (e.g. structure, quantity, then prioritization), so you get consistent, usable output instead of a generic list.

---

## Where skills live (Cursor)

- **Personal (all projects):** `~/.cursor/skills/`  
- **Project (this repo only):** `.cursor/skills/`  

Skills installed via `npx skills add` typically go to the personal directory (or the path your agent is configured to use). Project skills are for team-wide conventions (e.g. “how we write PRDs in this repo”).

---

## Testing a skill (e.g. brainstorming)

After installing a skill (and restarting Cursor if needed), you can confirm it’s used by asking for something that clearly matches the skill:

1. **Open a new Composer or chat** in this repo.
2. **Ask in natural language**, for example:
   - *“I want to add a ‘save for later’ feature for articles. Help me think it through before we build anything.”*
   - *“Run a short brainstorm on ways we could reduce time-to-value for new users. Give a few options and trade-offs.”*
3. **Check the behavior:** The agent should follow the skill’s process (e.g. for brainstorming: explore context, ask clarifying questions one at a time, propose approaches, then present a design and ask for approval before any implementation). If it jumps straight to code or skips the design step, the skill may not be loaded—try restarting Cursor.
4. **Optional:** Ask *“Which skill are you using for this?”* to see if it names the skill.

---

## Quick reference

| I want to… | Try this |
|------------|----------|
| Browse and search skills | [skills.sh](https://skills.sh/) |
| Install a full repo of skills | `npx skills add owner/repo` |
| Get PM/marketing skills | `npx skills add coreyhaines31/marketingskills` |
| Get planning/brainstorm skills | `npx skills add obra/superpowers` |
| Get doc/Office skills | `npx skills add anthropics/skills` |
| Use a skill | Just describe your task; the agent picks the skill by description |

---

## Summary

- **Skills** = reusable instructions so the agent follows your (or the community’s) process and format.  
- **skills.sh** = directory to find and install them; install with `npx skills add <owner/repo>`.  
- For **PM work**, start with **coreyhaines31/marketingskills** and **obra/superpowers**; add **anthropics/skills** for docs and comms.  
- You **use** skills by describing your goal in plain language; the agent chooses which skill to apply.
