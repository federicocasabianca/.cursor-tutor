## Wish List Discovery Summary (Q3 2025)

- **Core insight:** Wish list engagement is substantial (≈62k monthly users, 370k adds, 156k opens) but delivers <5% favorite→cart conversion and only 2.4% of total add-to-cart volume. Removal events (≈45%) outpace conversions, signaling the list behaves as a parking lot rather than a purchase driver.
- **Key friction:** Manual organization via folders is effectively unused—only ~0.2% of activity—despite repeated requests for “better organization.” Users want automatically organized outcomes, not more tools.
- **Behavioral intents:** Interviews and survey synthesis reduced initial six behavioral clusters to four intent-driven segments:
  - **Comparers** need faster side-by-side evaluation.
  - **Immediate buyers** skip wish list entirely when intent is high.
  - **Discount hunters** treat the list as a price-watch queue.
  - **Collectors** (inspiration + “maybe later”) accumulate items without acting.
- **Experience gaps:** Users struggle with comparison workflow, discoverability of bulk actions, and clarity between wish list vs. “My Materials.” Heatmaps show attention on search and item controls, near-zero usage of the left-side folder navigation, and engagement drop-off deeper in the list.
- **Strategic takeaway:** No “quick wins” surfaced; structural changes must balance high-effort UX/feature work with uncertain ROI. Recommendation is to pause major wishlist investment relative to higher-leverage MCP initiatives, while reconsidering folder removal and automated organization in longer-term roadmap.

### Phased Approach

1. **Phase 1 – Foundations (Q3 2025):** Reduce friction in save flow, improve comparison layout, and address basic navigation pain points.
2. **Phase 2 – Conversion Optimization (Q4 2025):** Target discount hunters with alerts, nudges, and urgency mechanics once foundational UX is stable.
3. **Phase 3 – Advanced Features (Q1 2026):** Explore high-effort ideas such as collaborative lists, true comparison tooling, and AI-assisted organization.

## Experiment Portfolio (Phase 1)

### `NWF` — Wishlist: Simplified Add to Wishlist Flow
- **Run:** 2025‑10‑22 → 2025‑11‑04 (Favourites)
- **Goal:** Remove mandatory folder-modal friction; offer optional organization via toast CTA.
- **Result:** Variant B became default but produced no significant lift on GMV/session, add-to-favorites, or wishlist add-to-cart rates. Folder usage and folder open rate dropped, confirming reduced organization friction does not harm business metrics.
- **Next step:** Confirms folder removal is low-risk; additional automation needed before pushing further organizational changes.

### `NWC` — Wishlist: New Card Layout
- **Run:** 2025‑09‑03 → 2025‑11‑04 (Favourites)
- **Goal:** Shorten cards to show more items simultaneously and trim non-essential information during comparison.
- **Result:** No statistically significant movement on GMV/session, conversion, or wishlist actions. Introduced a mobile web regression that must be fixed.
- **Next step:** Proceed with bug remediation; layout change alone isn’t enough to shift comparison behavior.

### `WGV` — Wishlist: Add Grid View
- **Run:** 2025‑09‑15 → 2025‑11‑04 (Favourites)
- **Goal:** Provide grid toggle to support side-by-side material comparison.
- **Result:** Minor positive signals that were not statistically significant; add-to-favorites and wishlist add-to-cart stayed flat.
- **Next step:** Grid view can remain available as a preference. Further comparison tooling (e.g., dedicated compare mode) needed to unlock measurable impact.

## Outstanding Risks & Opportunities

- **Mobile experience:** Ensure card layout fixes land to avoid further erosion on mobile web.
- **CRM reactivation:** Wishlist price-drop automation was offline until June 2025; future Phase 2 experiments depend on stable instrumentation.
- **Automatic organization:** Strong user desire for “organized results” suggests investment in auto-tagging, smart sorting, or AI grouping may outperform manual folder features.
- **Measurement coverage:** Continue validating wishlist event tracking to attribute downstream conversions that happen after users revisit material detail pages.



