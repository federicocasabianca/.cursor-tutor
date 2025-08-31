---
type: schema
name: strategy_generic_v3
version: 3
---

artifact: strategy
framework: generic
project: string                      # e.g., buyer_experience
id: string                           # e.g., DACH-2025Q3
version: integer
date: YYYY-MM-DD
owner: string                        # DRI(s)
market: string                       # e.g., DACH
timeframe:
  start: YYYY-MM-DD
  end:   YYYY-MM-DD
okrs: array[string]                  # OKR ids/titles
scope:
  in: array[string]
  out: array[string]
constraints: array[string]           # tech/legal/budget
tags: array[string]
confidence: low | medium | high

# --- RUMMELT: Problem & governing rules (WHAT & WHY) ---
diagnosis:
  challenge: string                  # core problem/opportunity
  root_causes: array[string]
  obstacles: array[string]
guiding_policy:
  approach: string                   # how we'll address the challenge
  strategic_logic: string            # why this approach should work
  trade_offs: array[string]          # explicit won't-do choices

# --- PLAY-TO-WIN: Strategic choices (WHERE & HOW) ---
where_to_play:
  market_segments: array[string]
  customer_segments: array[string]
  geographies: array[string]
how_to_win:
  advantage_hypothesis: string       # concise statement of how we win in W2P

# Minimal, non-overlapping enablement
enablers:
  critical_capabilities: array[string]
  capability_gaps: array[string]

# --- 7 POWERS: Durability (WHY THIS LASTS) ---
seven_powers:
  chosen: array[string]              # network effects | scale economies | switching costs | branding | cornered resource | process power | counter-positioning
  status: string                     # none | emerging | established
  path_to_power: array[string]       # concrete steps to build/strengthen

# --- REFORGE: Measurement & mechanics (HOW WE GROW/MEASURE) ---
north_star_metric:
  name: string
  baseline: number
  target: number
  unit: string
  by: YYYY-MM-DD
input_metrics:
  - name: string
    baseline: number
    target: number
    unit: string
    by: YYYY-MM-DD
loops_impact:
  acquisition: string                # how the strategy strengthens this loop
  retention: string
  monetization: string

# --- PORTFOLIO: Focused execution ---
pillars:
  - id: string
    label: string
    rationale: string
initiatives_ranked:
  - pillar_id: string
    name: string
    owner: string
    expected_impact: string          # metric -> delta (with evidence/insight refs)
    evidence_insights: array[string] # insight ids
    resources: string                # headcount/budget summary
    dependencies: array[string]
    milestones:                      # Now / Next / Later
      now: array[string]
      next: array[string]
      later: array[string]
    priority?:                       # optional but helpful to force focus
      impact: high | medium | low
      confidence: high | medium | low
      effort: high | medium | low

# --- GOVERNANCE, RISK & TESTS ---
review_cadence:
  frequency: string                  # e.g., monthly
  owner: string
  dashboard: string
risk_assessment:
  key_risks: array[string]
  mitigation_strategies: array[string]
  assumptions: array[string]
test_plan:
  experiments: array[string]
  kill_criteria: array[string]
counter_moves:
  anticipated_competitor_responses: array[string]
  our_responses: array[string]

# --- EVIDENCE ---
links:
  from: array[string]                # source insight ids/docs
  to: array[string]