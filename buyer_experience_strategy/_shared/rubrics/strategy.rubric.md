# Strategy Rubric (v3 — Framework-informed, schema-aligned, with Focus Gate)

Use this to assess `strategy_generic_v3` artifacts.

---

## 0) FOCUS GATE (enabling constraint — must pass)
**Purpose:** enforce scope discipline so we don’t die by “too many good things.”

Defaults if not specified in the strategy:
- `max_core_problems = 5`
- `max_pillars = 3`
- `max_now_initiatives = 5`

**Checks**
- `len(diagnosis.core_problems) ≤ max_core_problems`
- `len(pillars) ≤ max_pillars`
- `count(initiatives with any milestones.now item) ≤ max_now_initiatives`
- Every **NOW** initiative:
  - maps to exactly **one** pillar,
  - states an **expected impact** on the **north_star_metric** or an **input_metric**.

If any check fails → **Not Ready** (reduce scope or re-prioritize).

---

## CORE GATES (all must pass → else **Not Ready**)

1) **Rummelt Triad + Logic**
   - **Diagnosis**: specific challenge with root causes & obstacles.
   - **Guiding Policy**: clear approach **with explicit trade-offs**.
   - **Coherent Actions**: actions/pillars are recognizable precursors to the outcome.
   - **Strategic Logic**: shows how actions + policy resolve the diagnosis.  
   > Evidence: `diagnosis.*`, `guiding_policy.*`, `coherent_actions_summary`.

2) **Play-to-Win Choices**
   - **Where-to-Play**: market/customer/geos are explicit and bounded.
   - **How-to-Win**: single **advantage hypothesis** (not a grab-bag).  
   > Evidence: `where_to_play.*`, `how_to_win.advantage_hypothesis`.

3) **7 Powers (Durability)**
   - ≥1 **chosen** power with **status** and a credible **path_to_power**.  
   > Evidence: `seven_powers.chosen|status|path_to_power`.

4) **Measurability (Reforge discipline)**
   - **North-Star Metric**: baseline → target by date.
   - **Input Metrics**: each with baseline → target by date.  
   > Evidence: `north_star_metric.*`, `input_metrics[]`.

If any core gate fails → **Not Ready** and list what is missing.

---

## QUALITY DIMENSIONS (score 0–2 each; total /16)

1) **Policy Coherence & Trade-offs**  
   - 0: Vague/conflicting actions; no clear won’t-do list.  
   - 1: Direction present; some trade-offs.  
   - 2: Actions clearly ladder to policy; explicit won’t-do choices.

2) **Differentiation (How-to-Win)**  
   - 0: Generic; no edge vs. alternatives.  
   - 1: Some differentiation.  
   - 2: Crisp, hard-to-copy advantage.

3) **Loop Leverage (Reforge)**  
   - 0: No clear impact on acquisition/retention/monetization loops.  
   - 1: Impacts one loop loosely.  
   - 2: Strengthens ≥1 loop with explicit mechanism & metrics.

4) **Sequencing & Dependencies**  
   - 0: Big list; no ordering/deps.  
   - 1: Partial sequencing or deps.  
   - 2: Now/Next/Later with realistic ordering; critical deps identified.

5) **Resource Realism & Capability Fit**  
   - 0: Unclear owners/resources; capability gaps ignored.  
   - 1: Owners set; rough resources; gaps noted.  
   - 2: Owners + resource needs per initiative; gaps feasible to close.

6) **Risk & Test Plan**  
   - 0: Generic risks; no experiments/kill criteria.  
   - 1: Key risks; shallow tests.  
   - 2: Top risks tied to concrete experiments **and** kill criteria.

7) **Counter-moves**  
   - 0: No competitor response considered.  
   - 1: Some responses, no plan.  
   - 2: Likely responses listed **and** our responses prepared.

8) **Clarity & Communicability**  
   - 0: Dense, jargon; hard to brief.  
   - 1: Mostly clear.  
   - 2: Crisp; easily briefable to execs/teams.

**Assessment Bands**  
- **Weak**: ≤8/16 (even if gates pass) — revise.  
- **Medium**: 9–12/16 — acceptable; tighten.  
- **Strong**: ≥13/16 — publish & execute.

---

### Notes
- The Focus Gate expects `diagnosis.core_problems` and sensible WIP limits (`focus_constraints`) or it applies defaults.
- Resource allocation is judged **per initiative** (`resources`, owners, dependencies, milestones), not via a top-level budget block.
- If baselines/targets are unknown, include a **measurement plan** under `success_metrics.measurement_plan`; **Measurability gate** still fails until set.