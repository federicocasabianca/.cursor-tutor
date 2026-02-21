# Part 3: Commands and context rot (article section)

This doc is the **commands section** for the article series — how to avoid context rot when analyzing AB test results over multiple chats.

---

## What are Cursor commands?

Commands are custom instructions you can run from the chat (e.g. `/save-context`, `/clear`). In Cursor they live as **Markdown files** in `.cursor/commands/`. The name of the file (without `.md`) becomes the command name. When you type `/save-context`, Cursor loads the contents of `save-context.md` and the model follows those instructions.

They are not code: they’re short specs that tell the AI what to do when you invoke them. That makes them easy to edit and version in your repo.

---

## Why use commands for context rot?

Long or multi-session conversations make the model “forget” earlier decisions and drift. **Context rot** is when the chat no longer reflects the real state of the project. The fix is to:

1. **Persist state in files** (e.g. a context log, README, or experiment log).
2. **Start a new chat (or compact/clear)** so the next session starts from a clean slate.
3. **Recover** by opening or @-mentioning the saved file so the model reads the canonical state.

Commands automate step 1 and guide you through 2 and 3.

---

## How to create a command

1. Create or open the folder `.cursor/commands/` (at repo root or in your project).
2. Add a `.md` file, e.g. `save-context.md`. The filename (without `.md`) is the command name.
3. Write clear, step-by-step instructions: what to infer, what to write, where to append it, what to tell the user.
4. Invoke the command from chat with `/save-context` (or whatever you named the file).

No API or config is required. The model is instructed to follow the file when you reference the command.

---

## Example: save-context

**Goal:** Append a short, structured summary of the current conversation to a log file so the next session can resume from it.

**Typical flow:**

1. **Identify context:** Which project or initiative (e.g. from path or open files) and a short topic label (e.g. `checkout_button_test`).
2. **Summarize:** Current goals, decisions, assumptions, open questions, key files.
3. **Append:** Add a new section to `CONTEXT_LOG.md` with a date + topic heading (e.g. `## 2026-02-02 · checkout_button_test`) and the summary, decisions, next steps, key files.
4. **Confirm:** Tell the user where it was saved and suggest running `/compact` or `/clear` next.

If `CONTEXT_LOG.md` doesn’t exist, the command instructs the model to create it with a one-line intro, then add the first section.

**Recovery:** In a new chat, open or @ `CONTEXT_LOG.md` (or the specific initiative’s context log). The model then uses that section as the canonical state.

---

## Example: clear (or compact)

**Goal:** After saving context, tell the user to clear the chat (or start a new one) so the next session doesn’t carry stale context.

**Typical flow:**

1. **Check:** If something important isn’t yet in files (e.g. `CONTEXT_LOG.md`), run save-context first.
2. **Guide:** “Context is saved. Run `/clear` in Cursor (or start a new chat). After that, I’ll reload from your files.”
3. **After clear:** Re-read `CONTEXT_LOG.md` (focusing on the section for the current topic), README or PRD, and any active specs. Treat those as canonical; don’t rely on the old chat.

So: **save-context** = write state to a log; **clear** = discard chat and reload from that log (and other key files). Together they implement the “desk analogy”: write the important stuff down, then clear the desk and resume from the notes.

---

## Summary

| Item | Purpose |
|------|--------|
| **Commands** | `.cursor/commands/*.md`; filename = command name. |
| **save-context** | Append a dated, topic-labeled summary to `CONTEXT_LOG.md`. |
| **clear / compact** | Ensure context is saved, then tell user to clear chat; next session reloads from files. |
| **Recovery** | Open or @ the context log (and key files) in a new chat. |

This keeps analysis work (e.g. AB test results, decision memos, experiment log) aligned across sessions without relying on long chat history.
