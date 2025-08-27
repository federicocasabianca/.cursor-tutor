# Buyer Experience Strategy System

A structured framework for transforming raw data and company intelligence into actionable buyer experience strategies.

## Project Structure

```
buyer_experience_strategy/
├── _shared/
│   ├── prompts/           # Cursor .mdc templates for each workflow step
│   │   ├── 10_generate_insight.mdc
│   │   └── 20_generate_strategy_generic.mdc
│   ├── rubrics/           # Quality criteria and segment definitions
│   │   ├── buyer_segments.yaml    # Canonical segment catalog
│   │   ├── insight.rubric.md      # Insight quality criteria
│   │   └── strategy.rubric.md     # Strategy quality criteria
│   └── schemas/           # YAML frontmatter schemas
│       ├── insight.schema.md      # Enhanced with segments & journey
│       ├── signal.schema.md       # Enhanced with segments & journey
│       └── strategy.generic.schema.md
├── Insights/              # Generated insights from signals
├── signals/
│   ├── raw/              # Source data (NPS, company docs, KPIs)
│   ├── qualitative/      # Processed signals from text/surveys
│   └── quantitative/     # Processed signals from metrics/data
├── strategy/
│   └── generic/          # Framework-agnostic strategy documents
└── tools/                # Python CLI utilities
    ├── ingest_signals.py  # Convert raw data to structured signals
    └── tag_signal.py      # Bulk tagging with journey/market/segments
```

## Current Workflow (v1)

### 1. Signal Ingestion

**Python CLI approach** (recommended for batch processing):

```bash
# Install dependencies
pip install pyyaml

# NPS data → qualitative signal
python buyer_experience_strategy/tools/ingest_signals.py \
  --type nps_json \
  --file buyer_experience_strategy/signals/raw/nps_30d.json \
  --market DACH \
  --window_start 2025-07-17 \
  --window_end 2025-08-16

# Company documents → qualitative signals
python buyer_experience_strategy/tools/ingest_signals.py \
  --type company_text \
  --file buyer_experience_strategy/signals/raw/Company_Goals_2025.txt \
  --period_label 2025 \
  --source_title "Company Goals 2025"

python buyer_experience_strategy/tools/ingest_signals.py \
  --type company_text \
  --file buyer_experience_strategy/signals/raw/Company_Goals_Q3_2025.txt \
  --period_label 2025_Q3 \
  --source_title "Company Goals Q3 2025"

python buyer_experience_strategy/tools/ingest_signals.py \
  --type company_text \
  --file buyer_experience_strategy/signals/raw/Company_Mission_Vision.txt \
  --period_label mission_vision \
  --source_title "Company Mission & Vision"
```

**Outputs:**
- `signals/qualitative/buyer_experience-sig-nps-DACH-2025-07-17_2025-08-16.md`
- `signals/qualitative/buyer_experience-sig-company-2025.md`
- `signals/qualitative/buyer_experience-sig-company-2025_Q3.md`
- `signals/qualitative/buyer_experience-sig-company-mission_vision.md`

### 2. Insight Generation

Use Cursor prompt: `_shared/prompts/10_generate_insight.mdc`

**Example inputs:**
```yaml
insight_id: be-ic-2025-08-004
type: opportunity
signal_ids:
  - buyer_experience-sig-nps-DACH-2025-07-17_2025-08-16
  - buyer_experience-sig-company-2025
  - buyer_experience-sig-company-2025_Q3
  - buyer_experience-sig-company-mission_vision
owner: federico.casabianca@eduki.com
```

**Output:** `Insights/be-ic-2025-08-004.md`

### 3. Strategy Generation

Use Cursor prompt: `_shared/prompts/20_generate_strategy_generic.mdc`

**Example inputs:**
```yaml
strategy_id_stub: 2025-08
insight_ids:
  - be-ic-2025-08-004
tags: ["buyer_experience", "dach"]
owner: federico.casabianca@eduki.com
```

**Output:** `strategy/generic/buyer_experience-str-generic-2025-08.md`

### 4. Signal Tagging (Enhanced Workflow)

Use the new tagging tool to add journey context and segments to existing signals:

```bash
# Tag NPS signals with inferred metadata + journey context
python buyer_experience_strategy/tools/tag_signal.py \
  --glob "signals/qualitative/buyer_experience-sig-nps-*.md" \
  --infer_nps \
  --market DACH \
  --phase explore_passive_looking \
  --layer search_relevance \
  --segments "active_*"

# Tag company signals for awareness phase (all segments)
python buyer_experience_strategy/tools/tag_signal.py \
  --glob "signals/qualitative/buyer_experience-sig-company-*.md" \
  --market DACH \
  --phase awareness_discovery \
  --layer landing_page_ux \
  --segments all
```

**Features:**
- **Auto-inference**: `--infer_nps` extracts market and date windows from NPS filenames
- **Validation**: Checks phase/layer combinations and segment IDs against catalogs
- **Bulk operations**: Process multiple signals with consistent metadata
- **Wildcard segments**: Use `active_*`, `lead_*`, `inactive_*`, `churned_*` patterns
- **All segments**: Use `--segments all` to include all 15 buyer segments

## File Reference

### Core Files
- **`tools/ingest_signals.py`** - CLI tool for converting raw data into structured signals
- **`tools/tag_signal.py`** - Bulk tagging tool for adding journey/market/segment context
- **`_shared/prompts/10_generate_insight.mdc`** - Cursor template for synthesizing signals into insights
- **`_shared/prompts/20_generate_strategy_generic.mdc`** - Cursor template for creating strategies from insights
- **`_shared/schemas/signal.schema.md`** - Enhanced signal schema with journey phases and segments
- **`_shared/schemas/insight.schema.md`** - Enhanced insight schema with behavioral analysis
- **`_shared/schemas/strategy.generic.schema.md`** - Schema definition for strategy artifacts
- **`_shared/rubrics/buyer_segments.yaml`** - Canonical catalog of 15 buyer segments (lead → active → inactive → churned)
- **`_shared/rubrics/*.rubric.md`** - Quality criteria for insights and strategies

### Available Buyer Segments
**Lead Segments** (0 purchases):
- `lead_freemium` - Has ≥1 free download, 0 purchases
- `lead_new_signup` - Signed up <30 days, no activity
- `lead_not_activated` - Signed up >30 days, no activity

**Active Segments** (recent purchase <30 days):
- `active_1_time_buyer` - First purchase <30 days (1 total)
- `active_slow_buyer` - Recent purchase (2-5 total)
- `active_normal_buyer` - Recent purchase (6-11 total)
- `active_heavy_buyer` - Recent purchase (12-23 total)
- `active_loyal_buyer` - Recent purchase (≥24 total)

**Inactive/Churned** (similar structure for 30-180 days and >180 days)

### Current Signals
- **NPS DACH**: `buyer_experience-sig-nps-DACH-2025-07-17_2025-08-16.md` (NPS: 47.8, 10,649 responses)
- **Company Goals 2025**: Annual targets including €40M GMV, +450k buyers
- **Company Goals Q3 2025**: AI tools strategy, quality assessment, referral program
- **Mission & Vision**: Core purpose and educational impact goals

---

# Development Roadmap (v2-v9)

## Phase 1: Journey & Market Foundation

### 1. Journey & Market Scoping ✅ **PARTIALLY COMPLETE**
**Built:**
- ✅ `_shared/rubrics/buyer_segments.yaml` - 15 canonical segments from lead to churned
- ✅ `_shared/schemas/signal.schema.md` - Enhanced with `market`, `buyer_journey_phase`, `structural_layer`, `segments`
- ✅ `_shared/schemas/insight.schema.md` - Enhanced with journey context and behavioral analysis
- ✅ `tools/tag_signal.py` - Bulk tagging script with validation

**Still needed:**
- ⏳ `_shared/rubrics/buyer_journey.yaml` - Journey phases and structural layers definition

**Deliverable:** Existing signals are taggable and filterable by journey phase and market.

**Example usage:**
```bash
# Tag NPS signals with wildcard segments (all active buyers)
python tools/tag_signal.py \
  --glob "signals/qualitative/buyer_experience-sig-nps-*.md" \
  --market DACH \
  --phase first_use \
  --layer satisfaction \
  --segments "active_*"

# Tag company signals for all segments
python tools/tag_signal.py \
  --glob "signals/qualitative/buyer_experience-sig-company-*.md" \
  --market DACH \
  --phase awareness_discovery \
  --layer landing_page_ux \
  --segments all

# Mix wildcards and specific segments
python tools/tag_signal.py \
  --glob "signals/qualitative/*.md" \
  --segments "lead_*,active_loyal_buyer,churned_*"
```

### 2. Insight Engine v2
**Build:**
- `_shared/prompts/10_generate_insight_v2.mdc` - Enhanced insight generation with rigor
- Enhanced rubric covering behavior analysis, assumptions, counter-evidence, metrics, experiments

**Deliverable:** Production-ready insights with comprehensive evidence and actionability.

**Enhanced output includes:**
- Behavioral patterns from signals
- Explicit assumptions and counter-evidence
- Experiment proposals and success metrics
- Journey phase and market context

### 3. Strategy Builder v2
**Build:**
- `_shared/prompts/20_generate_strategy_generic_v2.mdc` - Market-aware strategy generation
- Enhanced strategy schema with baselines, pillars, initiatives, and risk assessment

**Deliverable:** Coherent buyer-experience strategy documents with measurable goals.

**Example inputs:**
```yaml
strategy_id_stub: dach-2025-q4
insight_ids:
  - be-ic-2025-08-004
  - be-ic-2025-08-005
market: DACH
journey_scope: [awareness_discovery, explore_passive_looking]
owner: federico.casabianca@eduki.com
```

## Phase 2: Communication & Implementation

### 4. Narrative Generator
**Build:**
- `_shared/prompts/30_generate_narrative.mdc` - Convert strategies into persuasive narratives
- `_shared/rubrics/narrative.rubric.md` - Storytelling quality criteria

**Deliverable:** Compelling stories to socialize strategies across teams.

**Input:** Strategy documents + target audience definition
**Output:** Executive narratives, team briefs, stakeholder presentations

### 5. PRD Generator
**Build:**
- `_shared/prompts/40_generate_prd.mdc` - Convert strategy initiatives into PRDs
- `_shared/schemas/prd.schema.md` - Problem, goals, scope, non-goals, risks, experiment plan

**Deliverable:** Initiative-level PRDs that reference strategy and define success metrics.

**Example flow:**
```
Strategy Initiative → PRD Template → Product Requirements Document
"Improve search relevance" → Problem definition, success metrics, experiment plan
```

### 6. CPO Review Engine
**Build:**
- `_shared/prompts/50_cpo_review.mdc` - Strategic critique using proven frameworks
- `_shared/rubrics/cpo_review.rubric.md` - 7 Powers, Rummelt Good Strategy criteria

**Deliverable:** Structured critique + decision log for strategy refinement.

**Review dimensions:**
- Strategic coherence (Rummelt)
- Competitive advantage (7 Powers)
- Market timing and execution feasibility
- Resource allocation and prioritization

## Phase 3: Automation & Scale

### 7. Orchestration Pipeline
**Build:**
- `Makefile` or `pipeline.py` - Chain entire workflow with one command
- `project.yaml` - Project configuration (IDs, market scope, workflow preferences)

**Deliverable:** End-to-end DACH buyer experience strategy generation in one command.

**Example usage:**
```bash
# Full pipeline from signals to PRDs
make strategy-pipeline MARKET=DACH PROJECT=buyer_experience

# Individual steps remain editable
make insights SIGNALS="nps-dach,company-2025"
make strategy INSIGHTS="be-ic-2025-08-004"
```

### 8. Framework Extensibility
**Build:**
- `_shared/prompts/strategy/` - Framework-specific strategy templates
  - `21_generate_strategy_ost.mdc` (Objectives, Strategies, Tactics)
  - `22_generate_strategy_jtbd.mdc` (Jobs-to-be-Done)
  - `23_generate_strategy_rummelt.mdc` (Good Strategy Bad Strategy)
  - `24_generate_strategy_wardley.mdc` (Wardley Mapping)

**Deliverable:** Swap strategy frameworks without breaking the pipeline.

**Configuration:**
```yaml
# project.yaml
strategy_framework: generic  # or ost, jtbd, rummelt, wardley
market: DACH
default_owner: federico.casabianca@eduki.com
```

### 9. Governance & Versioning
**Build:**
- `strategy/CHANGELOG.md` - Version history and decision rationale
- Schema enforcement for `version`, `source_ids` in all artifacts
- `tools/lint_strategy.py` - Consistency and completeness validation

**Deliverable:** Auditable, consistent strategy documents with clear provenance.

**Quality gates:**
- All strategies reference source insights
- Version bumps require changelog entries
- Broken links or missing evidence trigger warnings
- PRDs must trace back to strategy initiatives

---

## Next Steps

**Immediate (Week 1-2):**
1. Create `buyer_journey.yaml` with DACH-specific phases and layers
2. Build `tools/tag_signal.py` for bulk signal enhancement
3. Enhance existing signals with journey/market context

**Short-term (Week 3-4):**
1. Upgrade insight generation with v2 rigor requirements
2. Build market-aware strategy generator
3. Test end-to-end workflow on current DACH signals

**Medium-term (Month 2):**
1. Add narrative and PRD generation capabilities
2. Implement CPO review framework
3. Create orchestration pipeline for repeatable execution

**Long-term (Month 3+):**
1. Add multiple strategy frameworks
2. Implement governance and quality gates
3. Scale to additional markets beyond DACH