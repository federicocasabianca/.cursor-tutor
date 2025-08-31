# signal.schema.md (with business/user/execution context)

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

# Targeting
market: string                       # e.g., "DACH"
buyer_journey_phase: string          # from buyer_journey.yaml
structural_layer: string             # from buyer_journey.yaml
segments: array[string]              # optional; from buyer_segments.yaml

# Time semantics
window_start: YYYY-MM-DD             # rolling windows (e.g., NPS 30d)
window_end: YYYY-MM-DD
observed_at: YYYY-MM-DD              # point-in-time

# Provenance
source_hash: string
links:
  from: array[string]
  to: array[string]

# Quantitative summaries (optional)
metrics:
  - name: string
    value: number
    unit: string
    window: string
    sample_n?: number
    metric_def_id?: string
    delta_vs_prev_window?: number     # +/− vs prior window (same length)

# Qualitative summaries (optional)
themes?:                              # lightweight theme counts
  - name: string
    count: number
feedback_examples?:                   # e.g., from NPS or interviews
  language: string
  promoters: array[string]
  passives:  array[string]
  detractors: array[string]
feedback_examples_non_en?:            # optional fallback
  promoters: array[string]
  passives:  array[string]
  detractors: array[string]

# NEW — Business/User/Execution context (all optional)
business_context?:
  related_okrs: array[string]
  revenue_impact: string              # e.g., "€250k/q potential", "unknown"
  competitive_threat: string          # short note
  market_opportunity_size: string     # e.g., "large", "€1–2M/yr", "TBD"

user_context?:
  pain_severity: low | medium | high | critical
  user_intent: string
  alternative_solutions: array[string]
  success_criteria: array[string]

execution_context?:
  implementation_effort: low | medium | high
  technical_constraints: array[string]
  dependencies: array[string]

# Data quality (optional)
data_quality_notes?: array[string]
```
