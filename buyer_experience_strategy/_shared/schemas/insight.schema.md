# insight.schema.md (business relevance, 5 whys, richer actionability)

```yaml
artifact: insight
project: buyer_experience
id: string
date: YYYY-MM-DD
type: opportunity | problem | risk | observation
owner: string

# Targeting
market: string
buyer_journey_phase: string
structural_layer: string
segments: array[string]

# Core
claim: string                         # one-sentence, falsifiable
strength: weak | medium | strong
evidence_strength: low | medium | high

# Business alignment
business_relevance:
  related_okrs: array[string]
  strategic_priority: low | medium | high | critical
  estimated_impact: string            # revenue/cost/user growth (free text)

# Depth (5 whys)
root_cause_analysis:
  primary_cause: string
  contributing_factors: array[string]
  why_analysis: array[string]         # ordered (What, Why1, Why2, Why3, ...)

# Novelty
novelty_factor: incremental | significant | disruptive

# Customer impact
customer_impact:
  affected_segments: array[string]
  pain_severity: low | medium | high | critical
  opportunity_size: small | medium | large | massive

# Measurability
baseline?:
  metric: string
  current: number
  unit: string
  source_signal: string
target?:
  value: number
  timeframe: string
expected_impact?: string

# Actionability
recommended_actions:
  immediate: array[string]            # next 2 weeks
  short_term: array[string]           # this quarter
  long_term: array[string]            # 6–12 months
  success_metrics: array[string]      # how we will measure

# Evidence & craft
tags: array[string]
evidence:
  signals: array[string]              # IDs
behavior:
  observed_actions: array[string]
  frequency: string
  recency: string
  intensity: string
assumptions_unknowns: array[string]
counter_evidence: array[string]
implications: array[string]
experiments: array[string]
metrics_to_watch: array[string]
links:
  from: array[string]
  to: array[string]
```
