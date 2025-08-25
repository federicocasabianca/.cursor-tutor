---
type: schema
name: strategy_generic
version: 1
---

# Strategy Schema — Generic (framework-agnostic)

## Purpose
A concise, framework-agnostic strategy artifact used to align teams and feed narratives/PRDs.

## Required frontmatter
- **artifact**: "strategy"
- **framework**: "generic"
- **project**: project slug (e.g., buyer_experience)
- **id**: namespaced (e.g., be-str-generic-2025-08)
- **date**: YYYY-MM-DD
- **version**: integer (start at 1)
- **owner**: person responsible
- **links.from**: list of **insight IDs** used

## Recommended frontmatter
- **tags**: array (e.g., ["buyer_experience","relevance"])
- **market**: region(s)
- **confidence**: "low" | "medium" | "high"
- **priority**: "low" | "medium" | "high"

## Body sections
### Summary
1–3 sentences: core challenge + overall approach.

### Core Challenge
What problem are we solving (for whom, where in the journey), supported by insights.

### Goals
Measurable targets (business + user); include baselines if known.

### Pillars
3–5 themes that structure the work (short label + one-line rationale).

### Initiatives
Concrete efforts under pillars (bullets; each should map to a pillar and a metric).

### Risks & Assumptions
Key unknowns, trade-offs, or second-order effects.

### Evidence
Bullet list linking the insight ids (and optionally notable signal ids).
