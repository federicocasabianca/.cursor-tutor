# Part 4 — MDC example + recap for readers

## 1. What the MDC file would do (in detail)

An MDC file is an extra rules file that Cursor loads **only when you have certain files open**. The `.cursorrules` at the project root is always on. The MDC is added on top when the file you're editing matches the rule's glob.

**Example: `decision-memo.mdc` with `globs: decisions/*.md`**

- You open `decisions/checkout_button_color_test.md` (or create a new file in `decisions/`).
- Cursor sees the path matches `decisions/*.md`, so it loads `decision-memo.mdc` into context for that chat.
- You already have `.cursorrules` (project scope, response style, and the decision-memo bullets that are there today). Now you also have the MDC content, which repeats and sharpens the decision-memo part **only for this kind of file**.

**What changes in practice**

- When you ask Cursor to "draft the decision from the results" or "add the learnings section," the model has the MDC in context. So it's more likely to: use the same test name as in `drafts/` and `results/`, keep the sections (test name, area, decision, primary metric + outcome, why, what we learned, next steps), and at the end suggest adding a row to `experiment_log.md` or offer to add it.
- When you're in a different file (e.g. `drafts/some_test.md` or the README), that MDC is **not** loaded. Only `.cursorrules` applies. So the extra decision-memo rules are only in play when you're actually in a decision file.

**Why use it here**

- Same behavior could stay in `.cursorrules` only. The MDC gives you: (1) a clearer place to edit decision-memo rules without touching the rest of `.cursorrules`, and (2) file-scoped context — the model gets a stronger reminder exactly when you're in `decisions/*.md`. If you add more rule files later (e.g. one for `drafts/*.md` about the AB test template), each applies only when you're in that kind of file.

**Example content for `AB_Test_Analyzer/.cursor/rules/decision-memo.mdc`:**

```markdown
---
description: When writing or editing a decision memo, keep structure and naming consistent with the rest of the project.
globs: decisions/*.md
alwaysApply: false
---

# Decision memo rules

- Use the same test name as in `drafts/` and `results/` (e.g. `checkout_button_color_test`).
- Include: test name, area, decision (go/no-go), primary metric + outcome, why, what we learned, next steps.
- When the decision is finalized, suggest adding a row to `experiment_log.md` or offer to add it.
```

**The file is created at:** `AB_Test_Analyzer/.cursor/rules/decision-memo.mdc`

---

### How to see the MDC in action

**Setup:** Open a file that matches the glob (e.g. `decisions/checkout_button_color_test.md` or create a new file like `decisions/my_new_test.md`). Keep that file open or in the chat context. Start a new chat (or continue in one where that file is referenced) so Cursor loads the MDC.

**Things to ask the AI:**

1. **Draft a decision from results**  
   e.g. *"Using the results in `results/checkout_button_color_test.csv` (or the draft in `drafts/checkout_button_color_test.md`), draft the decision memo for this test."*  
   You should get a memo with: same test name as in drafts/results, sections (test name, area, decision, primary metric + outcome, why, what we learned, next steps), and at the end a suggestion to add a row to `experiment_log.md` or an offer to add it.

2. **Fill in or add a section**  
   e.g. *"Add the 'What we learned' section"* or *"Add the 'Next steps' section based on the decision."*  
   The model should keep the existing structure and naming and, when the memo looks final, suggest or offer to update `experiment_log.md`.

3. **Check structure**  
   e.g. *"Does this decision memo follow the project structure? What's missing?"*  
   The model should check against the MDC: test name, area, decision, primary metric + outcome, why, what we learned, next steps, and whether a row should be added to the experiment log.

4. **Finalize and log**  
   e.g. *"This decision is final. Add a row to experiment_log.md."* or *"Consider this decision done — update the experiment log."*  
   The model should add the row (test name, area, decision, primary metric, outcome) to `experiment_log.md`.

**To confirm the MDC is loaded:** Ask with a decision file open; then ask the same kind of question with only `drafts/` or README open. With the decision file open you should get the structure and the experiment-log suggestion; without it, behavior may rely only on `.cursorrules`.

---

## 2. Recap — written structure (as if you wrote it)

Use this as the article structure for the Cursor rules recap. You can change it later.

---

**Cursor rules at project level — quick recap**

In this project we have one file at the root that Cursor reads automatically: `.cursorrules`. No extra setup. If the file is there, every chat in this folder uses it.

**What's in it**

Two parts:

- **Project** — What the project is, what's in scope, where things go. README is the source of truth. We define the phase (e.g. Phase 1 – foundation) and what's in and out of scope. When you draft an AB test, use the template. When you write a decision memo, put it in `decisions/<test_name>.md` and keep the same name as in drafts and results. When a decision is done, suggest adding a row to `experiment_log.md`. Code stays minimal and aligned to the README.
- **Response style** — How the assistant should answer. Medium-length by default. No fluff; go straight to the answer. If something is unclear or off-track, say so. If we're not sure, say so; don't overstate confidence.

**How we got here**

We didn't write it all at once. We added bits as the workflow grew: first phase and scope, then the template for drafting tests, then where decision memos go, then the experiment log step. So the file is a living doc — you add a line when you want the assistant to do something the same way every time.

**Why it matters**

Before, we had to repeat scope, templates, and conventions in every chat. With `.cursorrules`, that's in one place. Every conversation in this project gets the same baseline. That sets you up for the next step: when one file isn't enough, or you want rules that apply only when certain files are open, you add `.cursor/rules/` and use the `.mdc` format (see the MDC section).

---

*End of recap*
