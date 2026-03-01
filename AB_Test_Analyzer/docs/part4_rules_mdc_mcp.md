# Part 4: Cursor rules, MDC, MCP, and one integration

Article Part 4 covers scaling the co-pilot setup with **rules**, **rule files (MDC)**, **MCP**, and **one live integration** (Notion or Statsig). Below: what we can show from the AB Test Analyzer state, short section descriptions, and how it extends the scaling story.

---

## 1. What we can show readers (from AB_Test_Analyzer)

| Topic | Current state in AB_Test_Analyzer | What to show |
|-------|-----------------------------------|--------------|
| **Cursor rules** | Single `.cursorrules` (Project + Response style). Evolved: phase, templates, decisions, experiment_log. | How we use and evolve `.cursorrules`; when to add project-level rules in `.cursor/rules/` (e.g. file-specific for `drafts/*.md`, `decisions/*.md`). |
| **MDC files** | No `.mdc` in this project. Repo has `query-assistant/rules/*.mdc` as reference. | Cursor’s rule format (`.mdc` in `.cursor/rules/`), when to use vs `.cursorrules`, how they fit together (globs, alwaysApply, reuse). Optional: add one example `.mdc` in AB_Test_Analyzer. |
| **MCP** | No MCP in analyzer codebase; workspace has Notion + Statsig MCPs. | What MCP is (tools + resources), why it matters for live context (data, docs), and that the co-pilot can pull/push without re-explaining. |
| **One integration** | README mentions Notion/JIRA; no implementation. MCP tools exist for Notion (fetch, update-page) and Statsig (get experiment, update experiment). | **One** integration only: pattern “pull company context → use in chat → push updates.” Notion: fetch page/DB, update page. Statsig: get experiment list/details, update experiment. Reader learns the pattern; we don’t implement both. |

---

## 2. Super short section descriptions (for questions)

- **Cursor rules — going deeper**  
  How we use and evolve `.cursorrules` (and optionally project-level rules in `.cursor/rules/`): one file vs many, what goes in Project vs Response style, when to add rules as the workflow grows (templates, decisions, experiment log).

- **MDC files**  
  Cursor’s rule format (e.g. `.mdc` in `.cursor/rules/`): when to use them, how they fit with `.cursorrules` (scope, globs, alwaysApply), and how they help with reuse and file-specific behavior.

- **MCP (Model Context Protocol)**  
  What MCP is, why it matters for the co-pilot: live context (data, docs) via tools and resources so the model can pull and push without the user re-explaining everything each time.

- **Connecting to one tool**  
  One integration (Notion **or** Statsig): pull company context (e.g. fetch page, list experiments), use it in the conversation, push updates (e.g. update page, update experiment). One concrete flow so the reader can replicate the pattern elsewhere.

---

## 3. Scaling evolution (from Part 3 → Part 4)

- **Part 3:** Local workflow at scale — commands (save-context, clear/compact), CONTEXT_LOG, experiment log, decisions per test. No external systems.
- **Part 4:** Same workflow + **persistent rules** (cursor rules, MDC) so behavior stays consistent across sessions and files, and **live context** (MCP + one integration) so the co-pilot can read/write company data and docs without re-explaining.

Result: the reader goes from "I run the analyzer and keep a log" to "I have stable rules and one connected tool (Notion or Statsig) following a clear pull → use → push pattern."

---

## Suggested next steps (for the article / project)

- **Rules:** Document how `.cursorrules` was evolved (phase, templates, decisions, experiment_log); optionally add one file-specific rule in `.cursor/rules/` (e.g. for `drafts/*.md` or `decisions/*.md`) to show the split.
- **MDC:** Add one example `.mdc` in AB_Test_Analyzer (e.g. decision-memo or ab-test-draft) and/or point to `query-assistant/rules/*.mdc` for format reference.
- **MCP + one integration:** Choose Notion **or** Statsig for the article; describe the flow (pull → use → push) with that tool only, so the pattern is clear and replicable.
