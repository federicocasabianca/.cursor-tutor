# Eduki — Copy/Paste Prompt for Dual Search Evaluation

Use this markdown block directly in ChatGPT (or any GPT-4 class model) after pasting the supporting data files.

---

## System Message

You are an expert evaluator of Eduki search results. Follow the rubric exactly, score every result independently (no re-ranking), and provide thorough, audit-ready calculations. Work in two phases (Hybrid results and Lexical results) and then compare them head-to-head.

---

## Reference Rubric (from `llm_as_judge_prompt.md`)

**Relevance Scores (0–3)**  
- **0 – Irrelevant:** No lexical overlap in title/categories *and* no semantic relationship to the query.  
- **1 – Weak:** Partial lexical match in title *or* category, and only loose semantic relationship.  
- **2 – Good:** Some combination of full/partial lexical alignment across title/categories with clear semantic relevance. A bit of noise acceptable, but the core must align.  
- **3 – Excellent:** Strong lexical match in both title and category, clean/precise categories, and clear semantic alignment.

**General Rules**  
- Use **only** the provided `title` and `material_categories`. Ignore descriptions, prices, grades, etc.  
- Prefer specific categories; noisy or off-topic categories decrease relevance.  
- Score each material independently. Do **not** reorder or filter the list.  
- Output must include Query, Title, Score, and Explanation (1–2 sentences referencing title/categories).

### Few-Shot Diagnoses (copy verbatim)

- **Example 1**  
  - Query: `kinderrechte`  
  - Title: `Kinderrechte (Visualisierung für die Tafel)`  
  - Category: `Sachunterricht→Demokratie & Gesellschaft→Zusammenleben→Regeln, Rechte & Pflichten`  
  - Score: **3**  
  - Reason: Exact lexical match plus precise civic-education category.

- **Example 2**  
  - Query: `herbstferien`  
  - Title: `Feriengrüsse Einhornklasse`  
  - Categories: `Fachübergreifendes→Classroom Management→Persönlichkeitsentwicklung`; `Fachübergreifendes→Ferien`  
  - Score: **1**  
  - Reason: Only generic “Ferien” overlap; no “herbst” signal.

- **Example 3**  
  - Query: `halloween`  
  - Title: `Streichholzschachtelwörter "Halloween"`  
  - Categories: `Deutsch→Anfangsunterricht→Lesen lernen→Silben & Wörter`; `Fachübergreifendes→Jahreszeiten & Feste→Halloween`; `DaZ/DaF→Schreiben→Schriftspracherwerb`  
  - Score: **2**  
  - Reason: Strong title + one precise category, but extra noisy categories reduce clarity.

- **Example 4**  
  - Query: `lesen`  
  - Title: `Silvester Lese- und Arbeitsheft`  
  - Categories: `Deutsch→Anfangsunterricht→Lesen lernen→Sätze & erste Texte`; `Deutsch→Lesen→Lesetraining→Lesetagebuch & Portfolio`; `Fachübergreifendes→Jahreszeiten & Feste→Neujahr`; `Deutsch→Vertretungsstunden`  
  - Score: **1**  
  - Reason: Some reading categories, but title centers on “Silvester”; off-topic festive categories add noise.

- **Example 5**  
  - Query: `zahlenstrahl 100`  
  - Title: `Zahlenmauern bis 100`  
  - Category: `Mathematik→Grundrechenarten→Zahlenraum 100`  
  - Score: **3**  
  - Reason: Near-exact lexical match and perfectly aligned numeric category.

- **Example 6**  
  - Query: `spielzeug kostenlos`  
  - Title: `Freiarbeit: Silbenkasten - Spielzeug (Kl. 1)`  
  - Category: `Deutsch→Anfangsunterricht`  
  - Score: **1**  
  - Reason: “Spielzeug” present, but no “kostenlos” signal; category generic.

---

## Inputs to Paste (exact order)

1. `taxonomy_categories.csv` (you may truncate after ~100 rows if needed, but keep headers)  
2. `results_hybrid.json` (raw JSON)  
3. `results_lexical.json` (raw JSON)

Clearly label each JSON block so the model knows which mode it belongs to.

---

## Workflow Instructions

### Phase A — Per-Mode Judgments

Perform the following twice: once for **Hybrid (vector=true)** results, once for **Lexical (no vector)** results.

For each mode:
1. Iterate over the materials in the order they appear (rank order).  
2. Assign a relevance score (0–3) per rubric and give a brief justification citing only title/categories.  
3. After scoring all 36 materials:
   - Produce a table showing counts **and percentages** per score (0/1/2/3).  
   - List the **Top 3 strongest** (score 3, clean categories) with reasons.  
   - List the **Top 3 weakest** (lowest scores) with reasons.

### Phase B — Comparative Analytics

Using the judgments from Phase A:
1. **Score Distribution Comparison**  
   - Create a head-to-head table showing % of materials at each score for Hybrid vs Lexical.  
   - Highlight the largest deltas (e.g., “Lexical has +40% more score-3 results”).

2. **NDCG@12**  
   - Treat the list order as the ranking.  
   - Use graded relevance = assigned score (0–3).  
   - Compute DCG@12 and IDCG@12 explicitly for each mode (show intermediate sums).  
   - Report the final **NDCG@12** for Hybrid and Lexical, and state which is higher.

3. **Recall@12**  
   - Define “relevant” as score ≥ 2.  
   - Recall@12 = (# of relevant items in top 12) / (total # of relevant items in the entire list).  
   - Compute for both modes and identify the winner.

### Phase C — Final Conclusion

Write a concise narrative (≤2 paragraphs) answering:
- Which mode delivers better overall quality?  
- Reference the score distribution percentages, NDCG@12, and Recall@12 in the explanation.  
- Call out any meaningful trade-offs (e.g., “Hybrid surfaces more creative variety but with lower precision”).

---

## Output Template

Follow this exact structure in your response:

1. **Hybrid Judgments**  
   - Material-by-material scores + explanations  
   - Score distribution table  
   - Top 3 strongest / Top 3 weakest

2. **Lexical Judgments**  
   - Same subsections as Hybrid

3. **Comparative Metrics**  
   - Score distribution comparison table  
   - NDCG@12 calculations & results  
   - Recall@12 calculations & results

4. **Conclusion**  
   - Narrative summary referencing all key metrics

---

After pasting this prompt, provide the three input files in the order listed above and instruct the model to begin the evaluation.

