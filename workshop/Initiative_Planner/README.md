# Initiative Planner

A system to plan, track, and make decisions on product initiatives.

## What it does

This tool helps PMs to:
- Draft initiative briefs from a short description
- Track initiative status and decisions
- Keep a decision log across all initiatives
- Generate insights from past decisions
- Support the PM in making a decision — not making the decision for the PM

## How to use

1. Describe an initiative idea in the chat
2. The AI drafts an initiative brief using the template
3. Review, refine, and finalize the brief
4. When a decision is made, create a decision memo
5. The initiative log tracks all initiatives in one place

## Project structure

```
Initiative_Planner/
├── templates/          # Reusable templates for briefs and logs
├── drafts/             # Initiative briefs in progress
├── decisions/          # Decision memos for finalized initiatives
├── initiative_log.md   # Summary table of all initiatives
└── CONTEXT_LOG.md      # Session context for continuity
```

Same initiative name across `drafts/`, `decisions/`, and `initiative_log.md` to keep things linked.
