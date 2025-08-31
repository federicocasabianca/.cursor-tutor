---
artifact: strategy
framework: generic
project: buyer_experience
id: DACH-2025Q3
version: 1
date: 2025-08-24
owner: federico.casabianca@eduki.com
market: DACH
timeframe:
  start: 2025-09-01
  end: 2025-12-31
okrs: 
  - "Reach €40M GMV"
  - "Sustain 30% growth in DE world"
  - "Improve conversions in search and recommendations through quality"
scope:
  in: 
    - "Search relevance and quality signals"
    - "Material page conversion optimization"
    - "Personalized recommendations"
  out: 
    - "New market expansion"
    - "Author acquisition"
    - "Pricing strategy changes"
constraints: 
  - "No major infrastructure changes Q3/Q4"
  - "Maintain current author royalty structure"
  - "Preserve existing user experience patterns"
tags: 
  - "quality_optimization"
  - "personalization"
  - "conversion_improvement"
confidence: medium

# Focus constraints (for rubric Focus Gate)
focus_constraints:
  max_core_problems: 3
  max_pillars: 3
  max_now_initiatives: 4
  prioritization_rule: "Advance network effects power and maximize GMV delta"

# --- RUMMELT: Problem & governing rules ---
diagnosis:
  challenge: "DACH market shows moderate satisfaction (NPS 47.8) but conversion potential is limited by generic quality presentation and lack of career-stage personalization"
  root_causes:
    - "Quality assessment happens post-purchase rather than pre-purchase"
    - "Career stage differences in quality perception not captured in UX"
    - "Generic recommendations don't align with teacher-specific needs"
  obstacles:
    - "Limited real-time quality assessment capabilities"
    - "Lack of career stage data for personalization"
    - "Generic one-size-fits-all material presentation"
  core_problems:
    - "Quality signals are invisible during material discovery and evaluation"
    - "Recommendations ignore teacher career stage and context preferences"
    - "Material pages lack teacher-specific quality indicators"

guiding_policy:
  approach: "Make quality visible pre-purchase and personalize recommendations based on teacher career stages to increase conversion confidence"
  strategic_logic: "If we make quality assessment transparent and personalize for career stages, then teachers will convert more confidently because they can evaluate fit before purchase"
  trade_offs:
    - "Won't pursue generic marketplace improvements that don't target teacher-specific needs"
    - "Won't invest in post-purchase satisfaction improvements until pre-purchase experience is optimized"
    - "Won't expand to new subjects until current quality framework proves effective"
coherent_actions_summary: "Build visible quality framework, implement career-stage personalization, and optimize material pages for teacher evaluation workflow"

# --- PLAY-TO-WIN: Choices ---
where_to_play:
  market_segments: ["Primary education teachers", "Secondary education teachers", "Special needs educators"]
  customer_segments: ["Active buyers (1+ purchases)", "Lead freemium users", "New teacher signups"]
  geographies: ["DACH"]
how_to_win:
  advantage_hypothesis: "Win through teacher-specific quality transparency and career-stage personalization that competitors can't replicate without deep educational domain expertise"

# Enablement
enablers:
  critical_capabilities:
    - "Educational content quality assessment"
    - "Teacher behavior analytics"
    - "Real-time recommendation algorithms"
  capability_gaps:
    - "Career stage detection and classification"
    - "Quality signal extraction from materials"
    - "Teacher-specific personalization engine"

# --- 7 POWERS: Durability ---
seven_powers:
  chosen: ["network effects", "process power"]
  status: "emerging"
  path_to_power:
    - "Build teacher feedback loops that improve quality signals for all users"
    - "Develop proprietary teacher career stage classification algorithms"
    - "Create quality assessment processes that scale with material volume"
    - "Establish teacher-specific recommendation optimization that improves with usage"

# --- REFORGE: Metrics & Loops ---
north_star_metric:
  name: "GMV"
  baseline: 30000000
  target: 35000000
  unit: "EUR"
  by: 2025-12-31
input_metrics:
  - name: "NPS"
    baseline: 47.8
    target: 55.0
    unit: "index"
    by: 2025-12-31
  - name: "Search to Purchase Conversion Rate"
    baseline: 0.12
    target: 0.16
    unit: "percentage"
    by: 2025-12-31
  - name: "Material Page Conversion Rate"
    baseline: 0.08
    target: 0.11
    unit: "percentage"
    by: 2025-12-31
loops_impact:
  acquisition: "Better quality signals increase organic discovery through improved search ranking and word-of-mouth"
  retention: "Career-stage personalization increases repeat purchases by showing more relevant materials"
  monetization: "Quality transparency increases willingness to pay and reduces price sensitivity"

# --- Portfolio: Focused execution ---
pillars:
  - id: "quality_transparency"
    label: "Pre-Purchase Quality Transparency"
    rationale: "Make quality assessment visible during discovery to increase conversion confidence"
  - id: "career_personalization"
    label: "Career-Stage Personalization"
    rationale: "Tailor recommendations and quality indicators to teacher career stages"
  - id: "conversion_optimization"
    label: "Material Page Conversion Optimization"
    rationale: "Optimize teacher evaluation workflow on material pages"

initiatives_ranked:
  - pillar_id: "quality_transparency"
    name: "Quality Signal Display System"
    owner: "product.team@eduki.com"
    expected_impact: "Search to Purchase Conversion Rate -> +0.02 by 2025-11-30"
    evidence_insights:
      - "be-ic-2025-08-001"
    resources: "2 developers, 1 UX designer, 4 weeks"
    dependencies: ["Quality assessment algorithm", "A/B testing framework"]
    milestones:
      now:
        - "Audit current quality signals on material pages"
        - "Design quality indicator display mockups"
        - "A/B test enhanced quality displays"
      next:
        - "Implement quality indicators in search results"
        - "Add quality-based filtering options"
      later:
        - "Integrate user-generated quality signals"
        - "Build quality trend tracking"
    priority:
      impact: high
      confidence: high
      effort: medium
  - pillar_id: "career_personalization"
    name: "Teacher Career Stage Detection"
    owner: "data.team@eduki.com"
    expected_impact: "Material Page Conversion Rate -> +0.015 by 2025-12-15"
    evidence_insights:
      - "be-ic-2025-08-001"
    resources: "1 data scientist, 1 ML engineer, 6 weeks"
    dependencies: ["User behavior data pipeline", "Career stage taxonomy"]
    milestones:
      now:
        - "Analyze NPS feedback for career stage quality themes"
        - "Define teacher career stage taxonomy"
        - "Build career stage classification model"
      next:
        - "A/B test career-stage personalized recommendations"
        - "Implement dynamic quality emphasis by career stage"
      later:
        - "Expand personalization to entire user journey"
        - "Add career-specific quality metrics"
    priority:
      impact: high
      confidence: medium
      effort: high
  - pillar_id: "conversion_optimization"
    name: "Material Page Teacher Workflow"
    owner: "ux.team@eduki.com"
    expected_impact: "Material Page Conversion Rate -> +0.02 by 2025-11-15"
    evidence_insights:
      - "be-ic-2025-08-001"
    resources: "1 UX researcher, 2 developers, 1 designer, 5 weeks"
    dependencies: ["Teacher workflow research", "Material page analytics"]
    milestones:
      now:
        - "Research teacher material evaluation workflow"
        - "Redesign material page for teacher needs"
        - "Add teacher-specific quality indicators"
      next:
        - "Implement preview functionality improvements"
        - "Add curriculum alignment indicators"
      later:
        - "Build lesson planning integration features"
        - "Add collaborative evaluation features"
    priority:
      impact: medium
      confidence: high
      effort: medium
  - pillar_id: "quality_transparency"
    name: "AI Quality Assessment Pilot"
    owner: "ai.team@eduki.com"
    expected_impact: "NPS -> +2.0 by 2025-12-31"
    evidence_insights:
      - "be-ic-2025-08-001"
    resources: "2 ML engineers, 1 domain expert, 8 weeks"
    dependencies: ["Quality framework definition", "Material content analysis"]
    milestones:
      now:
        - "Build AI-powered quality assessment system"
        - "Pilot quality scoring on subset of materials"
        - "Validate quality scores against teacher feedback"
      next:
        - "Scale quality assessment to full catalog"
        - "Integrate scores into search ranking"
      later:
        - "Build predictive quality models"
        - "Automate quality improvement suggestions"
    priority:
      impact: high
      confidence: medium
      effort: high

# --- Governance, Risk, Tests, Counter-moves ---
review_cadence:
  frequency: "bi-weekly"
  owner: "federico.casabianca@eduki.com"
  dashboard: "GMV & conversion metrics dashboard"
risk_assessment:
  key_risks:
    - "Career stage detection accuracy may be too low for effective personalization"
    - "Quality signals might not correlate with actual teacher satisfaction"
    - "Technical implementation complexity could delay launch"
  mitigation_strategies:
    - "Start with simple career stage indicators (experience level, subject) before complex classification"
    - "Validate quality signals through teacher feedback loops and A/B testing"
    - "Implement MVP versions first, iterate based on user response"
  assumptions:
    - "Teachers value quality transparency over other material page improvements"
    - "Career stage is a valid dimension for personalization in education"
    - "Current NPS feedback accurately represents broader teacher sentiment"
test_plan:
  experiments:
    - "A/B test quality indicator display on material pages — metric: conversion rate — expected: +15%"
    - "Test career-stage personalized recommendations — metric: click-through rate — expected: +20%"
    - "Pilot AI quality scoring vs teacher ratings — metric: correlation coefficient — expected: >0.7"
  kill_criteria:
    - "If conversion rate doesn't improve by +5% after 4 weeks, pause quality signals"
    - "If career stage classification accuracy <70%, revert to simpler segmentation"
    - "If implementation costs exceed €200k budget, reduce scope"
counter_moves:
  anticipated_competitor_responses:
    - "Competitors may copy visible quality indicators"
    - "Larger platforms might acquire educational AI companies"
    - "Alternative platforms could emphasize teacher community features"
  our_responses:
    - "Deepen educational domain expertise and teacher-specific features"
    - "Build stronger teacher feedback loops and data collection"
    - "Focus on quality assessment accuracy and personalization sophistication"

# Evidence
links:
  from:
    - "be-ic-2025-08-001"
  to: []
---

### Focus Gate validation
- Core problems listed: 3 / 3
- Pillars: 3 / 3  
- NOW initiatives included: 4 / 4
- Each NOW initiative → ties to: GMV (via conversion rate improvements) and NPS

### Strategic Logic (one paragraph)
If we do **make quality visible pre-purchase and personalize for teacher career stages** (coherent actions under pillars), then **GMV will increase from €30M to €35M and NPS will improve from 47.8 to 55** (target NSM & inputs) will happen, because **teachers will convert more confidently when they can evaluate material fit before purchase, and career-stage personalization will show more relevant quality indicators** (advantage hypothesis + path to power).

### Path to Power (why it lasts)
Our chosen powers (network effects + process power) strengthen as more teachers provide feedback that improves quality signals for all users, while our proprietary career stage classification and quality assessment processes become harder to replicate. Each teacher interaction improves the personalization accuracy, creating a flywheel where better quality signals → more confident purchases → more feedback → even better signals.

### Measurement Plan (if any baselines/targets missing)
Current baselines established from existing NPS data and estimated conversion rates. Will instrument detailed conversion funnel tracking from search → material page → purchase, and implement teacher feedback collection system to validate quality signal effectiveness within first 4 weeks of implementation.
