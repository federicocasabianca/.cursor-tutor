# JIRA: Prioritize Sparse Vector Implementation Over Dense Vectors for Search Enhancement

## Summary
Based on comprehensive analysis of 330K+ real user queries, we should prioritize **sparse vector** implementation over dense vectors for our Elasticsearch search enhancement. The data shows users primarily search with exact terms and simple phrases, not complex natural language that would benefit from dense vector semantic understanding.

## Background
We're evaluating whether to implement sparse_vector or dense_vector in Elasticsearch 7.20 CE to complement our existing lexical search. Dense vectors in ES 7.20 CE have performance limitations (mostly brute force), so we need to validate which approach will provide the best ROI.

## Data Sources Analyzed
- **6 ZIP files** containing real user queries from the past year:
  - Winter 2024 Query.zip
  - Summer 2024 Query.zip  
  - Summer 25 Query July 16 2025.zip
  - Fall 2024 Query.zip
  - Summer 2025 Query.zip
  - Spring 2025 Query.zip
- **Taxonomy files** for intent classification:
  - taxonomy_categories.csv (1,344 terms)
  - taxonomy_grade_levels.csv (22 terms)
  - taxonomy_material_type.csv (26 terms)

## Query Analysis Results

### Scale of Analysis
- **330,413 unique queries** analyzed
- **258,496,023 total query frequency** (sum of all occurrences)
- **Frequency threshold**: Only queries with >100 occurrences included

### Query Complexity Metrics

#### Linguistic Complexity Scoring (0-10 scale)
**Criteria for complexity scoring:**
- Word count >1, >2, >4 words (+1 each)
- Contains conjunctions (und, oder, aber) (+1)
- Contains prepositions (für, mit, von, zu) (+1) 
- Contains articles (der, die, das, ein) (+1)
- Contains adjectives (gut, neu, wichtig) (+1)
- Contains descriptive words (bunt, kreativ, interaktiv) (+1)
- Contains educational terms (lernen, üben, verstehen) (+1)
- Contains qualifiers (kostenlos, einfach, praktisch) (+1)

#### Natural Language Scoring (0-10 scale)
**Criteria for natural language scoring:**
- Multi-word phrases (≥3 words: +2)
- Contains conjunctions (+2)
- Contains prepositions (+1)
- Contains articles (+1)
- Contains adjectives (+1)
- Contains descriptive words (+1)
- Contains educational terms (+1)
- Contains qualifiers (+1)

### Key Findings

#### Query Length Distribution
- **38.3%** are single-word queries (98.9M frequency)
- **30.0%** are two-word queries (77.5M frequency)
- **20.0%** are three-word queries (51.7M frequency)
- **Only 11.7%** are 4+ word queries

#### Complexity Distribution
- **Average linguistic complexity: 1.95/10** (very low)
- **Average natural language score: 1.59/10** (very low)
- **78.9%** of queries score 0-2 on complexity scale
- **Only 0.1%** of queries score 7+ on complexity scale

#### Intent Classification
- **60.0%** are "no-intent" queries (don't match taxonomy)
- **28.3%** are "combination" queries (multiple taxonomy terms)
- **11.6%** are "category" queries (single category)
- **0.1%** are "material_type" queries

## Examples Illustrating Query Patterns

### Single-Word Queries (38.3% of all queries)
**Top examples by frequency:**
1. `weihnachten` (2.1M searches)
2. `kostenlos` (1.2M searches)
3. `adventskalender` (928K searches)
4. `herbst` (727K searches)
5. `halloween` (602K searches)

### Two-Word Queries (30.0% of all queries)
**Examples:**
- `klasse 1` (exact grade level)
- `sankt martin` (exact topic)
- `weihnachten basteln` (topic + action)

### Complex Queries (0.1% of queries scoring 7+ complexity)
**Rare examples of natural language:**
- `märchen neu entdecken: die bremer stadtmusikanten - märchentexte und kreative materialien - für genaues lesen und verstehen` (complexity: 9)
- `wassergewöhnung: bewegen im wasser - schwimmen - einfach sport: kreativ, kompetenzorientiert und sicher` (complexity: 9)

## Engineering Implications

### Why Sparse Vectors Are Better Suited

1. **Exact Term Matching**: 38.3% of queries are single words - sparse vectors excel at exact/semi-exact matching
2. **Low Semantic Complexity**: Average complexity of 1.95/10 means users aren't using complex language that requires semantic understanding
3. **Taxonomy-Heavy Queries**: 28.3% are "combination" queries mixing multiple taxonomy terms - perfect for sparse vector synonym expansion
4. **Performance**: Sparse vectors are faster and more efficient for the query patterns we see

### Why Dense Vectors Are Overkill

1. **Minimal Natural Language**: Only 0.1% of queries show complex natural language patterns
2. **Performance Cost**: Dense vectors in ES 7.20 CE have significant performance limitations
3. **Low ROI**: The semantic understanding capabilities would be wasted on exact-term queries

## Current Search Quality Issues (from serve_metrics)

Based on our existing search quality data:
- **Grade Level Intent**: 90% GOOD_RESULTS (exact matching works well)
- **Category Intent**: 25% GOOD_RESULTS (exact matching struggles)
- **Combined Intent**: 62.5% GOOD_RESULTS (mixed results)
- **Common failure**: "margin < 0.35" affects 100% of failed queries

## Recommendation

**Phase 1**: Implement sparse vectors to address:
- Category concentration issues (affects 100% of failed category queries)
- Margin scoring problems
- Synonym expansion for taxonomy terms

**Phase 2**: Monitor for natural language query growth
**Phase 3**: Consider dense vectors only if complex natural language queries become significant (>5% of total)

## Success Metrics
- Improve category intent GOOD_RESULTS from 25% to 60%+
- Reduce "margin < 0.35" failures by 50%+
- Maintain current grade level performance (90% GOOD_RESULTS)

## Technical Notes
- ES 7.20 CE sparse vector implementation is more mature and performant
- Sparse vectors can be implemented incrementally without disrupting current search
- Lower computational overhead aligns with our query volume (258M+ queries analyzed)

---
**Priority**: High
**Effort**: Medium (sparse vectors) vs High (dense vectors)
**Risk**: Low (sparse vectors) vs Medium (dense vectors with ES 7.20 CE limitations)
