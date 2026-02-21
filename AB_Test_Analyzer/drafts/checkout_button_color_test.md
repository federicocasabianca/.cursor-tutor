# A/B Test: Checkout Button Color

## Problem
Checkout conversion is a key lever for revenue. Current checkout conversion rate baseline is 7.8%. We have qualitative feedback that the current blue CTA may not stand out enough on the page. We want to test whether a more salient button color (yellow) improves conversion by making the primary action more visible and reducing friction in the final step.

## Create a Hypothesis
1. **Cause:** By changing the checkout button from blue to yellow on the checkout page
2. **Effect:** we will observe an increase in checkout conversion rate
3. **Rationale:** because a higher-contrast, more salient CTA will draw attention to the primary action and reduce drop-off at the last step.

## Predict a Result
1. **Primary Metric:** Checkout conversion rate. Should **increase**.
2. **Specify MDE (Minimal Detectable Effect):** We expect a relative improvement of ~1% (e.g. from 7.8% to ~7.9% absolute, or ~1.3% relative). MDE for design: ~1% absolute.
3. **Secondary Metrics:** Add-to-cart rate, basket value, time to checkout (monitor for unintended shifts).
4. **Guardrails:** Bounce rate, error rate, and checkout abandonment at each step—ensure we don’t break the flow or confuse users.

## Determine the scope of the Exposure
1. **Variants:**
   - **Control:** Current blue checkout button.
   - **Treatment:** New yellow checkout button (same copy, placement, and size).
2. **Targeting and Allocation:** 50% of traffic to control, 50% to treatment. Target: all users who reach the checkout page (no region or segment restriction unless needed for power).
3. **Timelines:** [TBD – e.g. 2 weeks or until 80% power reached.]

## Analysis
- Did checkout conversion rate increase in treatment vs control?
- Was the effect consistent across segments (e.g. new vs returning, device)?
- Any movement in guardrails or secondary metrics that would change the decision?

## Future Work
1. **Significant results (variant success):** Roll out yellow button (e.g. 100% or gradual by segment). Document learnings for future CTA tests.
2. **Significant results (variant failure):** Keep blue. Document why yellow underperformed (visibility, contrast, brand fit) for future design decisions.
3. **Non-significant results:** Decide whether to re-test with longer duration or different variant (e.g. another color). If not re-testing, capture learnings and keep current experience.

## What Do We Expect to Learn
- Whether button color meaningfully affects checkout conversion at our baseline.
- Signal on how much CTA salience matters at the final step of the funnel.
- Input for future CTA and checkout UX tests.
