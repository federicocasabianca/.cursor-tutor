# Context log

Context log for the AB Test Analyzer project. Each section is one conversation session.

## 2026-02-02 · save_context_init

### Summary

- **Project state:** AB_Test_Analyzer has README.md, .cursorrules, `templates/ab_test_template.md`, and `drafts/` (e.g. checkout_button_color_test.md). Cursor uses the template when drafting AB tests per .cursorrules.
- **Article series:** Part 2 published (draft AB test with template, step-by-step, what's in template and why, what we're not doing yet). Part 3 planned: analyze results without integrations (lightweight results input, decision memo, experiment log, context rot). Part 4: MCP + one tool (Notion or Statsig).
- **Context rot (for article):** Desk analogy in place. Commands = .md in `.cursor/commands/`; two commands for readers: save context (append summary to a log file), clear/compact (then start fresh). Recovery = open or @ the saved file in a new chat.

### Decisions

- None this session (invoked save-context for AB_Test_Analyzer only).

### Next steps

- When continuing work on AB_Test_Analyzer: open or @ this file in a new chat for context.
- For article Part 3: add commands section (what they are, how to create, save-context + clear example) and experiment log.

### Key files referenced

- `README.md`, `.cursorrules`, `templates/ab_test_template.md`, `drafts/checkout_button_color_test.md`

---

## 2026-02-21 · part3_commands_and_experiment_log

### Summary

- **Picked up from context log:** Next steps were to add (1) commands section for article Part 3 and (2) experiment log.
- **Done:**  
  - **Commands section:** Added `docs/part3_commands.md` — what Cursor commands are (`.cursor/commands/*.md`), how to create them, save-context and clear examples, recovery via CONTEXT_LOG, and a short summary table.  
  - **Experiment log:** Added `templates/experiment_log_template.md` — one block per experiment: results table (primary/secondary/guardrails), sample size, significance, caveats; decision memo (decision, rationale, follow-up). Designed for a single running `EXPERIMENT_LOG.md` or one file per test.
- **Docs:** Added `docs/README.md` pointing to the Part 3 commands doc.

### Decisions

- None.

### Next steps

- Integrate `docs/part3_commands.md` into the actual article (Part 3) when publishing.
- Optionally add a "Results & log" step to README "How to use" (e.g. use experiment log template after running the analyzer).
- Part 4: MCP + one tool (Notion or Statsig) when ready.

### Key files referenced

- `CONTEXT_LOG.md`, `docs/part3_commands.md`, `templates/experiment_log_template.md`, `.cursor/commands/save-context.md`, `.cursor/commands/clear.md`, `.cursor/commands/compact.md`
