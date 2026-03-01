# Save Article Command

When the user invokes `/save_article` (or "save article" with a URL), save a web article into the inspiration library using the standard template.

## Input

- **URL** (required): The article URL to save. The user may paste it or provide it after invoking the command.
- **Area** (optional): One of `category_pages`, `home_page`, `search`, `navigation`. If omitted, use `uncategorized`.

## Steps

### 1. Resolve URL and area

- If the user only invoked the command, ask: "Paste the article URL (and optionally the area: category_pages, home_page, search, navigation)."
- Normalize the URL (e.g. strip tracking params, use canonical form if obvious).
- Set `area` from the user's message or default to `uncategorized`.

### 2. Check for duplicate

- Search existing inspiration files under `initiatives/explore_discover/future_search/inspiration/` for this URL in frontmatter (e.g. grep for the url value).
- If the URL is already saved, tell the user: "This URL is already saved as [filename]." Do not create a new file.

### 3. Fetch and parse the page

- Fetch the URL (e.g. with the web fetch / MCP tool) to get the page content.
- From the response, derive:
  - **Title** — from the page title or main heading.
  - **Summary** — a **structured summary** (see below) that you use to fill the Summary section. Prefer the article’s own summary or intro when present; otherwise build it from headings and main paragraphs.
  - **Summary structure** — the Summary section should include, when applicable:
    - **What it’s about** — main topic, thesis, or claim (1–3 sentences).
    - **Key points or structure** — main sections, arguments, or takeaways (bullets or short paragraphs).
    - **Evidence or examples** — any data, case studies, or concrete examples mentioned (brief).
    - **Relevance** — 1–2 sentences on how this relates to the chosen `area` (e.g. home_page, search, category_pages, navigation) or to Explore & Discovery / defensibility / personalization, if obvious from the content.

### 4. Read the template

- Read `initiatives/explore_discover/future_search/inspiration/_template.md` to use the same frontmatter keys and body sections (Summary, Key quotes, Concepts/terms, My notes).

### 5. Create the new article file

- **Path:** `initiatives/explore_discover/future_search/inspiration/<area>/YYYY-MM-DD_slug.md`
  - `YYYY-MM-DD` = today's date.
  - `slug` = URL-safe slug from the title (lowercase, spaces to underscores, strip special chars).
- **Frontmatter:** Fill from template. Set:
  - `url`: the normalized URL
  - `title`: from the page
  - `source`: leave empty or set from domain/publication if obvious
  - `date_saved`: today (YYYY-MM-DD)
  - `date_published`: leave empty unless present in the page
  - `area`: the chosen area
  - `tags`: empty array or from context
  - `takeaway`: empty or one line if you can infer it
- **Body:**
  - **Summary:** The derived **structured summary** from step 3 (what it’s about, key points/structure, evidence/examples, relevance). Aim for a concise but complete overview (e.g. 2–4 short paragraphs or equivalent bullets), not only one sentence.
  - **Key quotes:** Leave placeholder or a single `<!-- ... -->` so the user can fill later.
  - **Concepts / terms:** *(Optional)* If the article introduces important concepts, terms, or frameworks, list them in one line or a short bullet list; otherwise leave empty or `<!-- ... -->`.
  - **My notes:** Leave placeholder so the user can add strategy/roadmap notes.

Write the file to the path above.

### 6. Confirm

- Tell the user: "Saved to `inspiration/<area>/YYYY-MM-DD_slug.md`. Summary includes [what it's about / key points / relevance to area]. You can add Key quotes, Concepts/terms, and My notes when you review it."

## Notes

- If the URL cannot be fetched (4xx, 5xx, or blocked), report the error and do not create a file.
- If `initiatives/` is not available in the workspace, use the path the user expects for the future_search initiative (or ask).
- When writing the Summary, prefer the article's own words for the thesis or conclusion; avoid generic filler. If the page is mostly lists or short blocks, turn them into a short structured overview (bullets or 2–3 sentences) rather than a single vague sentence.
