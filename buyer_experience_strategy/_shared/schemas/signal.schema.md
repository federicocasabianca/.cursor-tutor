# signal.schema.md (Step 2 + segments)
```yaml
artifact: signal
scope: company | project
project: buyer_experience
nature: qualitative | quantitative
id: string
date: YYYY-MM-DD
source: string
summary: string
coverage: string
tags: array[string]
confidence: low | medium | high
limitations: array[string]
pii: boolean

market: string
buyer_journey_phase: string
structural_layer: string
segments: array[string]   # optional — ids from _shared/rubric/buyer_segments.yaml

window_start: YYYY-MM-DD
window_end: YYYY-MM-DD
observed_at: YYYY-MM-DD

source_hash: string
links:
  from: array[string]
  to: array[string]

metrics:
  - name: string
    value: number
    unit: string
    window: string

themes: array[string]
goals: array[string]
guardrails: array[string]
kpis: array[string]
feedback_examples:
  language: string
  promoters: array[string]
  passives: array[string]
  detractors: array[string]
feedback_examples_non_en?:
  promoters: array[string]
  passives: array[string]
  detractors: array[string]
```
