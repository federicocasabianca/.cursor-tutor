# LLM-as-Judge

Judge search results from hybrid search using LLM evaluation.

## Project Structure

```
LLM-as-judge/
├── llm_as_judge_prompt.md      # LLM evaluation instructions
├── judge_search_results.py      # Main script to judge search results
├── setup_folders.py             # Script to create query folder structure
├── fetch_all_queries.py         # Script to fetch search results for all queries
├── queries/                     # Query folders grouped by intent
│   ├── no-intent/
│   │   └── wetter/
│   │       ├── query_metadata.txt
│   │       ├── results.json
│   │       └── judgment.json
│   ├── categories/
│   │   └── kunst/
│   ├── grade-level/
│   │   └── klasse_1/
│   └── combined/
│       └── sankt_martin_klasse_1/
└── context/                     # Context files for LLM
    └── taxonomy_categories.csv  # Taxonomy reference data
```

## Setup

1. **Create and activate a virtual environment:**
   ```bash
   # Create virtual environment
   python3 -m venv .venv
   
   # Activate virtual environment
   # On macOS/Linux:
   source .venv/bin/activate
   # On Windows:
   # .venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install openai requests
   ```
   
   **Note:** Make sure your virtual environment is activated before installing packages.

3. **Set up environment:**
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```
   
   **Note:** The bearer token for the Eduki Search API should be in:
   `../elastic-intent-queries/bearer_token.txt`

4. **Create query folders:**
   ```bash
   python setup_folders.py
   ```
   This creates folders for all queries from the intent markdown files.

5. **Fetch search results for all queries:**
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
   - `--query-folder <name>`: Process only a specific query folder (e.g., `kostenlos` or `categories/kostenlos`)
   
   Example:
   ```bash
   # Fetch all queries
   python fetch_all_queries.py
   
   # Fetch a specific query
   python fetch_all_queries.py --query-folder kostenlos
   python fetch_all_queries.py --query-folder categories/kostenlos
   
   # Overwrite existing results
   python fetch_all_queries.py --overwrite
   ```

6. **Add your evaluation prompt:**
   Edit `llm_as_judge_prompt.md` with your LLM evaluation instructions.

**Note:** Remember to activate your virtual environment (`.venv`) before running any scripts:
   ```bash
   source .venv/bin/activate  # On macOS/Linux
   # .venv\Scripts\activate   # On Windows
   ```

## Usage

**Important:** Make sure your virtual environment is activated before running any scripts:
```bash
source .venv/bin/activate  # On macOS/Linux
# .venv\Scripts\activate   # On Windows
```

The `judge_search_results.py` script supports three modes of operation:

### 1. Judge a Single Query

Judge search results for a specific query folder:

```bash
python judge_search_results.py <query_folder_name>
```

**Examples:**
```bash
# Judge results using short name (resolved automatically)
python judge_search_results.py kostenlos

# Judge results for "weihnachten klasse 1" query
python judge_search_results.py weihnachten_klasse_1

# Judge results using explicit grouped path
python judge_search_results.py categories/kunst
python judge_search_results.py grade-level/klasse_1
python judge_search_results.py combined/sankt_martin_klasse_1
```

### 2. Judge All Queries in a Specific Group

Judge all queries within a specific intent group (e.g., `categories`, `grade-level`, `combined`, `no-intent`):

```bash
python judge_search_results.py --group <group_name>
```

**Examples:**
```bash
# Judge all queries in the categories group
python judge_search_results.py --group categories

# Judge all queries in the grade-level group
python judge_search_results.py --group grade-level

# Judge all queries in the combined group
python judge_search_results.py --group combined

# Judge all queries in the no-intent group
python judge_search_results.py --group no-intent

# Skip queries that already have judgments
python judge_search_results.py --group categories --skip-existing
```

### 3. Judge All Queries in All Groups

Judge all queries across all intent groups:

```bash
python judge_search_results.py --all
```

**Examples:**
```bash
# Judge all queries in all groups
python judge_search_results.py --all

# Skip queries that already have judgments
python judge_search_results.py --all --skip-existing
```

### Options

- `--group <name>`: Process all queries in a specific group (`categories`, `grade-level`, `combined`, `no-intent`)
- `--all`: Process all queries in all groups
- `--skip-existing`: Skip queries that already have `judgment.json` files
- `--base-dir <path>`: Specify a different base directory (default: script directory)

### What the Script Does

For each query, the script will:
1. Load the prompt from `llm_as_judge_prompt.md`
2. Load the query metadata from the query folder
3. Load the search results JSON from the query folder
4. Load context files (taxonomy CSV)
5. Call the LLM to generate a judgment
6. Save the judgment to `judgment.json` in the query folder

### Batch Processing Output

When processing multiple queries (using `--group` or `--all`), the script provides:
- Progress indicators showing which query is being processed (`[i/total]`)
- Summary statistics after each group
- Overall summary after processing all groups
- Error reporting for any failed queries

## Query Folder Names

Query folder names are sanitized versions of the original queries:
- Spaces and special characters are replaced with underscores
- Converted to lowercase
- Example: "weihnachten klasse 1" → "weihnachten_klasse_1"

Query folders are grouped by intent (`queries/no-intent`, `queries/categories`, `queries/grade-level`, `queries/combined`).  
To see all available query folders:
```bash
find queries -mindepth 2 -maxdepth 2 -type d
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

