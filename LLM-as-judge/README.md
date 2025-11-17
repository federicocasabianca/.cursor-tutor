# LLM-as-Judge

Judge search results from hybrid search using LLM evaluation.

## Project Structure

```
LLM-as-judge/
├── llm_as_judge_prompt.md      # LLM evaluation instructions
├── judge_search_results.py      # Main script to judge search results
├── setup_folders.py             # Script to create query folder structure
├── fetch_all_queries.py         # Script to fetch search results for all queries
├── queries/                     # Query folders (one per query)
│   ├── kostenlos/
│   │   ├── query_metadata.txt   # Query metadata
│   │   ├── results.json         # Search results (fetched via API)
│   │   └── judgment.json        # Generated judgment (output)
│   └── ...
└── context/                     # Context files for LLM
    └── taxonomy_categories.csv  # Taxonomy reference data
```

## Setup

1. **Install dependencies:**
   ```bash
   pip install openai requests
   ```

2. **Set up environment:**
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```
   
   **Note:** The bearer token for the Eduki Search API should be in:
   `../elastic-intent-queries/bearer_token.txt`

3. **Create query folders:**
   ```bash
   python setup_folders.py
   ```
   This creates folders for all queries from the intent markdown files.

4. **Fetch search results for all queries:**
   ```bash
   python fetch_all_queries.py
   ```
   This will:
   - Read all query folders
   - Extract the original query from each folder's metadata
   - Make API requests using the Eduki Search API
   - Save results as `results.json` in each query folder
   
   Options:
   - `--overwrite`: Overwrite existing results.json files
   - `--query-folder <name>`: Process only a specific query folder
   
   Example:
   ```bash
   # Fetch all queries
   python fetch_all_queries.py
   
   # Fetch a specific query
   python fetch_all_queries.py --query-folder kostenlos
   
   # Overwrite existing results
   python fetch_all_queries.py --overwrite
   ```

5. **Add your evaluation prompt:**
   Edit `llm_as_judge_prompt.md` with your LLM evaluation instructions.

## Usage

Judge search results for a specific query:

```bash
python judge_search_results.py <query_folder_name>
```

### Examples

```bash
# Judge results for "kostenlos" query
python judge_search_results.py kostenlos

# Judge results for "weihnachten klasse 1" query
python judge_search_results.py weihnachten_klasse_1
```

The script will:
1. Load the prompt from `llm_as_judge_prompt.md`
2. Load the query metadata from the query folder
3. Load the search results JSON from the query folder
4. Load context files (taxonomy CSV)
5. Call the LLM to generate a judgment
6. Save the judgment to `judgment.json` in the query folder

## Query Folder Names

Query folder names are sanitized versions of the original queries:
- Spaces and special characters are replaced with underscores
- Converted to lowercase
- Example: "weihnachten klasse 1" → "weihnachten_klasse_1"

To see all available query folders:
```bash
ls queries/
```

## Output

The judgment is saved as `judgment.json` in each query folder, containing:
- The original query
- The judgment text from the LLM
- Model information
- Query metadata

## Customization

- **Model**: Edit `judge_search_results.py` to change the LLM model (default: `gpt-4o`)
- **Temperature**: Adjust temperature in the script for more/less deterministic judgments
- **Context**: Add more context files to the `context/` directory and update the `load_context()` method

