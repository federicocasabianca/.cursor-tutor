# Experiment log

Lightweight log of experiment results and decisions. One section per experiment; append new blocks as tests finish. Use this to analyze results without integrations (no Notion/Statsig required).

---

## Experiment: [Short name, e.g. Checkout button color]

**Test doc:** [Link or path to the AB test spec, e.g. `drafts/checkout_button_color_test.md`]  
**Closed:** YYYY-MM-DD

### Results (lightweight input)

| Metric | Control | Treatment | Δ (abs) | Δ (rel) | Notes |
|--------|---------|-----------|---------|---------|-------|
| Primary: [e.g. Checkout CVR] | [e.g. 7.8%] | [e.g. 8.1%] | [e.g. +0.3 pp] | [e.g. +3.8%] | [sample size, confidence] |
| [Secondary / guardrail] | … | … | … | … | … |

- **Sample size (control / treatment):** [e.g. 50k / 50k]
- **Significance (primary):** [e.g. p &lt; 0.05, or "not significant"]
- **Caveats:** [e.g. one segment underpowered, seasonality]

### Decision memo

- **Decision:** [Ship treatment / Keep control / Inconclusive — re-test or drop]
- **Rationale:** [2–3 sentences: what the numbers showed, why this decision, what we’re doing next.]
- **Follow-up:** [e.g. Rollout plan, doc learnings, next test.]

---

*(Copy the block above for each new experiment; keep one running `EXPERIMENT_LOG.md` or one file per test.)*
