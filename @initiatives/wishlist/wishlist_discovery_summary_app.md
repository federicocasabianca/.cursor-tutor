## Wish List Discovery Summary (iOS & Android – Q3 2025)

- **Core insight:** Native app wishlist engagement is material (≈4.1M sessions driving 1.1M adds) yet only ~5.2% of wishlist adds continue to cart, while removals consume ~41% of add volume. The list still acts as a parking lot rather than a purchase accelerant.
- **Key friction:** Mandatory folder flows and dense item layouts create thumb-heavy, modal-heavy steps on mobile. Users skip folders (only 6.9% of adds create one, updates/removals are ~0.13%/~0.12%) and abandon mid-flow when context switches occur.
- **Behavioral intents:** App research echoes Web segmentation:
  - **Comparers** want instant, scannable cards to contrast materials.
  - **Immediate buyers** bypass the list if saving delays checkout.
  - **Discount hunters** queue materials to wait for nudges or alerts.
  - **Collectors** hoard inspiration but rarely clean up lists.
- **Experience gaps:** Users struggle to see enough items above the fold, bulk actions are buried under overflow menus, and folder navigation receives near-zero taps. Heatmaps and interaction traces show attention around search, sort, and inline controls but steep drop-off deeper in the list.
- **Strategic takeaway:** Mobile mirrors Web dynamics: low ROI from manual organization and limited conversion lift without structural changes. Prioritize friction removal and automated organization before deeper investments, and keep instrumentation aligned for downstream conversion tracking.

### Phased Approach

1. **Phase 1 – Foundations (Q3 2025):** Remove modal friction from Save to Wishlist, streamline card density for small screens, and surface navigation shortcuts (search, filters, sort) inline.
2. **Phase 2 – Conversion Optimization (Q4 2025):** Layer in price-drop alerts, back-in-stock nudges, and urgency cues once the base UX is stable to serve discount hunters without overwhelming immediate buyers.
3. **Phase 3 – Advanced Features (Q1 2026):** Explore collaborative lists, richer compare mode, and AI grouping/auto-tagging to deliver the “organized results” users actually want without resurrecting unused folder tools.

## Experiment Portfolio (Phase 1, Mobile)

### `NWF` — Wishlist: Simplified Add to Wishlist Flow
- **Goal:** Remove mandatory folder selection; offer optional organization via lightweight inline CTA.
- **Rationale for App:** With only ~6.9% of adds spawning folders and near-zero edits, keeping the modal on mobile wastes taps and screen real estate. Allowing instant saves aligns with thumb-first interactions.
- **Expectations:** Should reduce drop-offs during save flow, and — based on Web outcome — is low risk for GMV/session or downstream conversions. Requires mobile-specific QA to ensure toasts and optional organization controls are accessible yet unobtrusive.

### `NWC` — Wishlist: New Card Layout
- **Goal:** Shorten cards to expose more materials at a glance and strip non-essential copy that pushes controls below the fold.
- **Rationale for App:** The 27% add rate contrasted with 5% cart follow-through suggests people save many items but struggle to act. Tightening vertical space plus clearer CTAs can aid comparers and immediate buyers. Must watch for regressions (Web saw a mobile-web issue) and validate tap targets per platform guidelines.

### `WGV` — Wishlist: Add Grid View
- **Goal:** Provide a grid toggle for side-by-side comparison on tablets and larger phones.
- **Rationale for App:** Comparers crave quicker visual scanning, and collectors want “gallery” vibes. While Web signals were only directional, leaving grid as a preference can unlock value without forcing a layout change. Ensure persistent toggles between list/grid and measure impact on add-to-cart and removal rates.

## Outstanding Risks & Opportunities

- **Mobile performance & layout regressions:** Ensure iOS/Android parity testing for card density and toast flows; Web regressions highlight the need for platform-specific QA.
- **CRM readiness:** Phase 2 relies on price-drop/back-in-stock notifications; confirm mobile push + CRM pipelines are instrumented and stable.
- **Automatic organization:** Strong demand for “organized outcomes” suggests machine-driven grouping (tags, smart sorting, AI clusters) will outperform manual folders on mobile as well.
- **Measurement coverage:** Align native event tracking (saves, deletes, cart jumps, revisit conversions) with analytics parity so downstream revenue impact is traceable post-experiment.

