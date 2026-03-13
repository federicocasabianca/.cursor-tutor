---
name: ab-test-prd
description: Design A/B experiments using a standard PRD-like structure (problem, hypothesis, predicted result with guardrails, exposure, learnings, analysis, and future work). Use when the user wants to define or refine an A/B test, especially when they reference a feature PRD or requirements document.
---

# A/B Test PRD Skill

## When to Use

Use this skill when:

- The user wants to **design an A/B test** or experiment.
- The user mentions an **AB structure**, “experiment spec”, “hypothesis”, or similar.
- The user provides a **requirements or PRD markdown file** and asks to design an experiment based on it.

## Inputs and Context

When this skill is invoked, check whether the user has:

1. **Named the experiment or feature** (for example, “Next Search Token”).
2. **Provided a requirements/PRD path** in the repo (optional but preferred), for example:  
   `initiatives/explore_discover/next_search_token/PRD/requirements.md`.

Behavior:

- If a path is provided, **read that file first** and reuse its language for:
  - Problem and context.
  - Business KPIs and metrics.
  - Surfaces, audiences, and scope.
- If no path is provided, gather information via targeted questions.

## Workflow

Follow these steps in order. Ask at most **1–2 clarifying questions per step**.

### 1. Problem

Goal: Create a detailed problem description that justifies running an experiment and ties to business KPIs.

Steps:

1. If a requirements doc exists, extract:
   - Current behavior and pain points.
   - Any quantitative KPIs (conversion, CTR, revenue, etc.).
   - Any qualitative insights (user quotes, support feedback, research notes).
2. Otherwise, ask the user:
   - What behavior or outcome is underperforming now?
   - Which KPIs or qualitative signals show this (even roughly)?
3. Write a concise **Problem** section that:
   - Clearly states what is wrong or uncertain today.
   - Explicitly references **business KPIs** impacted.

### 2. Hypothesis

Goal: Define a solution-oriented hypothesis with **cause, effect, rationale**.

Steps:

1. Draft the hypothesis in three labeled bullets:
   - **Cause**: The specific change (for example, “By adding next-token suggestions in the search box…”).
   - **Effect**: Expected user behavior change and KPI movement.
   - **Rationale**: Why this is expected (prior data, benchmarks, theory).
2. If the user already gave a hypothesis, refine it into this structure rather than rewriting from scratch.

### 3. Predict a Result

Goal: Specify what metrics should move, by how much, including **guardrail metrics**.

Steps:

1. **Primary metric**
   - Identify the single most important metric and its direction (increase / decrease).
   - If the requirements doc names a primary KPI, use that.
2. **MDE (Minimal Detectable Effect)**
   - Ask the user for an expected percentage lift or range.
   - If unknown, suggest reasonable ranges (for example, 2–5%, 5–10%) and pick one with them.
3. **Secondary metrics**
   - Identify supporting metrics (for example, query length, suggestion CTR, engagement by segment).
4. **Guardrail metrics**
   - Explicitly list metrics that must **not regress** beyond acceptable bounds
     (for example, latency, error rate, zero-result searches, unsubscribe rate).
   - Prefer to reuse any guardrails already mentioned in the requirements doc.

Output this section under:

- Primary metric  
- MDE  
- Secondary metrics  
- **Guardrail metrics**

### 4. Determine Scope of Exposure

Goal: Define variants, targeting, allocation, and timelines.

Steps:

1. **Variants**
   - Always define at least:
     - `Control`: current experience.
     - `Treatment`: experience with the proposed change.
   - Add more variants only if the user explicitly wants them.
2. **Targeting and allocation**
   - Use the requirements doc to infer audience (for example, “signed-in DE teachers on web search”).
   - Ask, if needed: region, platform, login state.
   - Default allocation: 50/50 unless the user specifies otherwise.
3. **Timelines**
   - If the organization has a standard minimum duration, mention it.
   - Otherwise, ask whether timelines are **time-based** (for example, 2 weeks) or **sample-based** (for example, until N users per variant).

### 5. What We Expect to Learn

Goal: Translate hypothesis and metrics into 3–5 explicit learning goals.

Steps:

1. Summarize what the team hopes to learn, starting with phrases like:
   - “We expect to learn whether…”
2. Include:
   - Whether the change improves the primary metric.
   - How it affects user behavior (for example, query richness).
   - Any key segmentation questions (for example, by grade/subject, device, locale).

### 6. Analysis Plan

Goal: List specific questions the analysis should answer.

Steps:

1. Propose concrete analysis questions, for example:
   - “Does suggestion usage correlate with conversion uplift?”
   - “Do effects differ between new versus returning users?”
   - “Are there notable differences by segment (grade, subject, locale, device)?”
2. Use the requirements doc to align with existing priorities (for example, context battle, marketplace health).

### 7. Future Work

Goal: Decide ahead of time what to do based on different experiment outcomes.

Steps:

1. Create three sub-sections:
   - **If variant wins (significant positive result)**:
     - How rollout will proceed (for example, gradual to 100% of signed-in web, then app).
     - Any follow-up experiments (for example, personalization, new segments, additional variants).
   - **If variant fails (significant negative result)**:
     - What diagnostics to run (for example, UX confusion, latency regressions, segment-level drops).
     - Whether to iterate and re-test, or pivot away from this direction.
   - **If results are non-significant**:
     - Whether to re-test (and under what conditions: longer duration, different audience, stronger treatment).
     - How to document and use learnings even without changes to the experience.

## Output Format Template

When you finish, output a markdown document like:

```markdown
# [Experiment Title]

Based on requirements in: `[optional/path/to/requirements.md]`

## Problem
[Detailed problem aligned with KPIs]

## Hypothesis
- **Cause**:
- **Effect**:
- **Rationale**:

## Predicted Result
- **Primary metric**:
- **MDE**:
- **Secondary metrics**:
- **Guardrail metrics**:

## Exposure
- **Variants**:
- **Targeting and allocation**:
- **Timelines**:

## What We Expect to Learn
- ...

## Analysis Plan
- ...

## Future Work
### If variant wins
- ...

### If variant fails
- ...

### If results are non-significant
- ...
```

