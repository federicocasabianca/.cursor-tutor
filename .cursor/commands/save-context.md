# Save Context Command

When the user invokes `/save-context` (or references this command), perform the following:

## Step 1: Identify the Current Initiative and Topic

- **Initiative:** Determine which initiative folder the user is working in (e.g. `rebalance_free_paid`, `LTR_v1.1`) from the current path or open files.
- **Topic:** Infer the **conversation topic** for this session so entries can be grouped in `CONTEXT_LOG.md`:
  - From the user's words (e.g. "we're working on thank you page", "mp_upsell", "name a fair price"), or
  - From open files (e.g. `phase1_1c_mp_upsell_module.md` → topic "mp_upsell"), or
  - From the conversation focus (e.g. phase name, feature name).
- Use a **short, consistent topic label** (e.g. `mp_upsell`, `thank_you_page`, `name_a_fair_price`).

## Step 2: Summarize the Current Conversation

Create a concise, structured summary that captures:
- **Current goals and objectives** for this topic/initiative
- **Key decisions made** (with brief rationale)
- **Important assumptions or constraints**
- **Open questions or next steps**
- **Key files** referenced (PRDs, specs, etc.)

Keep the summary structured (headings, bullets) and concise (1–2 pages max when written).

## Step 3: Append to CONTEXT_LOG.md with Topic and Date Heading

- Target file: `CONTEXT_LOG.md` in the initiative root (e.g. `initiatives/explore_discover/<initiative>/CONTEXT_LOG.md`).
- **Always add a new section** with this heading format:
  - `## YYYY-MM-DD · <topic>`
  - Example: `## 2026-02-06 · mp_upsell`
- **Append** (do not overwrite). Under that heading add:
  - **Summary** (from Step 2)
  - **Decisions** (if any)
  - **Next steps** (if any)
  - **Key files referenced** (optional list)
- If `CONTEXT_LOG.md` does not exist, create it with a brief intro line (e.g. "Context log for this initiative. Each section is one conversation session.") then add the first `## YYYY-MM-DD · <topic>` section.

## Step 4: Confirm and Suggest Next Steps

- Confirm: "I've saved the conversation to `CONTEXT_LOG.md` under **YYYY-MM-DD · <topic>**."
- Proactively suggest: "Run `/compact` or `/clear` to avoid context rot when you continue."
