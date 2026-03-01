# Part 4 — Cursor rules (tentative section content)

Tentative article content for the first part of Part 4: Cursor rules. Use this to take screenshots and follow along. Each subsection explains **why it matters**, **when to do it**, and **what you get**. No project changes required for now.

---

## 1. What Cursor rules are and where they live

**Screenshot opportunity:** Project root with `.cursorrules` visible (e.g. in Cursor file tree or as the open file).

**Content:**

In the AB Test Analyzer project, the file `.cursorrules` at the project root tells Cursor how to behave in this codebase. It’s a single Markdown file that Cursor reads when you’re in this project. No extra setup: if the file exists, Cursor uses it.

**3.1 — Why this step is important and how it’s different from before**  
Before using rules, the assistant had no stable project context: you had to repeat scope, templates, and conventions in every chat. With `.cursorrules`, that context is **persistent and project-scoped**. The main difference is: once the file is in place, every conversation in this project gets the same baseline (scope, templates, decision format) without you re-explaining it.

**3.2 — When you need this step**  
As soon as you want the AI to consistently follow project structure, naming, or workflows (e.g. “always use this template for AB tests” or “decisions go in `decisions/<test_name>.md`”). If you’re starting a new project or formalizing how you work, add a `.cursorrules` file early.

**3.3 — What you get**  
A single place that defines “how we work in this project.” The model will use it automatically in every chat in this folder, so you get consistent behavior (templates, paths, response style) without pasting instructions each time.

---

## 2. How we structure the file: Project vs Response style

**Screenshot opportunity:** `.cursorrules` open in the editor, with the two sections visible: `## Project` and `## Response style`.

**Content:**

We split rules into two parts:

- **Project:** What the project is, what’s in scope, where things go (drafts, results, decisions, experiment log), and how to use templates. This is the “what to do and where” layer.
- **Response style:** How the assistant should answer (length, tone, when to say “I’m not sure,” when to correct wrong premises). This is the “how to communicate” layer.

In the AB Test Analyzer, the Project section points to `README.md` as the source of truth, defines Phase 1 scope, and specifies: use `templates/ab_test_template.md` when drafting a test; write decision memos to `decisions/<test_name>.md`; suggest adding a row to `experiment_log.md` when a decision is finalized. The Response style section asks for concise, direct answers and explicit uncertainty.

**3.1 — Why this step is important and how it’s different from before**  
A single blob of instructions is hard to maintain and to reason about. Separating **project behavior** (structure, scope, templates) from **response behavior** (tone, clarity, honesty) makes it clear what to update when the workflow or the communication style changes. Before, everything lived in one mental (or pasted) block; now you can evolve “what we do” and “how we talk” independently.

**3.2 — When you need this step**  
When your `.cursorrules` grows beyond a few bullets, or when you notice the model is good at structure but inconsistent in tone (or the opposite). Splitting Project vs Response helps as soon as you have both “do X in this project” and “answer like this” rules.

**3.3 — What you get**  
A clearer, maintainable rules file: you can edit project rules without touching style, and vice versa. Screenshots can show the two sections so readers see the split at a glance.

---

## 3. Evolving rules as the workflow grows (phase, templates, decisions, experiment log)

**Screenshot opportunity:** Same `.cursorrules` with the relevant bullets visible (e.g. the lines about template, decision memo, experiment_log).

**Content:**

The AB Test Analyzer `.cursorrules` didn’t start with everything at once. It evolved:

1. **Phase and scope** — “Phase 1 – foundation” and what’s in/out of scope (e.g. no Notion/JIRA yet). This sets expectations and avoids scope creep.
2. **Templates** — “When drafting an AB test, use the structure from `templates/ab_test_template.md`.” So every new test draft follows the same structure.
3. **Decisions** — “When drafting a decision memo, create or update `decisions/<test_name>.md` with: test name, area, decision, primary metric + outcome, why, learnings, next steps.” Same name as in `drafts/` and `results/` so one test stays linked across folders.
4. **Experiment log** — “When the user has finalized a decision, suggest adding a row to `experiment_log.md` (test name, area, decision, primary metric, outcome) or offer to add it.” So the log stays a single place to look back.

Each of these was added when the workflow needed it (Part 2 → Part 3 of the series). The file is a living doc: you add a rule when you want the assistant to do something consistently.

**3.1 — Why this step is important and how it’s different from before**  
Before evolving the file, the assistant had to be told each time: “use the template,” “put the memo here,” “update the log.” Now those behaviors are encoded once. The difference is: **from “tell the model every time” to “the model knows the workflow.”** That’s what makes the setup scale across sessions and teammates.

**3.2 — When you need this step**  
Whenever you introduce a new artifact or convention (a new template, a new folder, a new “when you do X, also do Y”). Add one or a few bullets to `.cursorrules` so the next conversation already follows the new workflow.

**3.3 — What you get**  
A rules file that matches your current process. New chats automatically use the right template, write to the right paths, and suggest the right follow-ups (e.g. experiment log). Readers can replicate this by adding similar bullets as their own workflow grows.

---

## 4. When to add project-level rules (e.g. `.cursor/rules/`)

**Screenshot opportunity:** (Optional for later.) File tree showing `.cursor/rules/` with one or more `.mdc` files, or a short note: “We’ll cover this in the MDC section.”

**Content:**

So far we’ve used a **single** `.cursorrules` file. For many projects that’s enough. Sometimes you’ll want **more than one rule file**, or rules that apply only when certain files are open (e.g. only when editing `drafts/*.md` or `decisions/*.md`). That’s where **project-level rules** in `.cursor/rules/` come in: they’re the same idea as `.cursorrules`, but with:

- Multiple files (e.g. one per concern: “drafts,” “decisions,” “code”).
- Optional **scope** (e.g. “only when this file pattern is open”).

We’re not changing anything in the project for this section. The takeaway: **start with one `.cursorrules`; when it gets long or you want file-specific behavior, consider splitting into `.cursor/rules/` and using the MDC format** (covered in the next section).

**3.1 — Why this step is important and how it’s different from before**  
One file can become long and mixed. Splitting lets you keep “draft an AB test” rules in one place and “write a decision memo” in another, and (with MDC) apply them only when the relevant files are open. The difference: **from “one big rule file” to “organized, optionally scoped rules.”**

**3.2 — When you need this step**  
When `.cursorrules` is hard to scan or when you want different behavior for different file types (e.g. stricter rules for `decisions/*.md` than for general chat). Not required for the AB Test Analyzer at its current size; we mention it so readers know the option exists.

**3.3 — What you get**  
A path to scale: one file for now, with a clear next step (multiple rule files, possibly file-scoped) when the project or team grows. The article can defer the concrete “how” to the MDC section.

---

## Screenshot checklist (for following along)

- [ ] **1.1** — Project root with `.cursorrules` in the file tree or as the active tab.
- [ ] **2.1** — `.cursorrules` open with `## Project` and `## Response style` visible.
- [ ] **3.1** — The bullets in `.cursorrules` that reference template, `decisions/<test_name>.md`, and `experiment_log.md`.
- [ ] **4.1** — (Optional) A placeholder or short note about `.cursor/rules/` for the MDC section.

---

## Summary for the article

- **What:** `.cursorrules` at project root = persistent, project-scoped instructions for Cursor.
- **Why it matters:** Stops you from re-explaining scope, templates, and conventions every time; the main difference is “tell once, apply every chat.”
- **When:** As soon as you want consistent behavior (structure, paths, response style); evolve the file when you add new workflow steps (templates, decisions, experiment log).
- **What you get:** Consistent use of templates, decision memos in the right place, experiment log suggestions, and a clear path to splitting into `.cursor/rules/` and MDC when needed.
