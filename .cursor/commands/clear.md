# Clear Command

When the user invokes `/clear` (or references this command), perform the following:

## Step 1: Ensure Context is Saved First

Before suggesting clearing, verify that important conversation state is in files (especially `CONTEXT_LOG.md`). If not, run the save-context workflow first, then proceed.

## Step 2: Guide the User

Tell the user that context is saved and they can run `/clear` in Cursor (or start a new chat). After clearing, you will reload the key initiative files and focus on the current conversation topic.

## Step 3: Post-Clear Reload (Topic-Aware)

After the user runs `/clear` (or starts a new chat):
- **Re-read** the initiative's key files:
  - `CONTEXT_LOG.md`: **prioritize the section matching the current conversation topic** (e.g. the `## YYYY-MM-DD · <topic>` block for this chat). Use other sections only as optional background.
  - `README.md` or `PRD/PRD.md` for goals and context.
  - Any active spec files relevant to the current topic.
- Treat these as the **canonical state** for this topic; the previous chat is gone.
- Confirm: "I've reloaded context from files, focusing on the [topic] section. What would you like to work on next?"
