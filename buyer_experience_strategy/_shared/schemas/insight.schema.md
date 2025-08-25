# insight.schema.md (Step 2 + segments)
```yaml
artifact: insight
project: buyer_experience
id: string
date: YYYY-MM-DD
type: opportunity | problem | risk | observation
owner: string

market: string
buyer_journey_phase: string
structural_layer: string
segments: array[string]   # optional — ids from _shared/rubric/buyer_segments.yaml

claim: string
strength: weak | medium | strong
tags: array[string]
evidence:
  signals: array[string]
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
