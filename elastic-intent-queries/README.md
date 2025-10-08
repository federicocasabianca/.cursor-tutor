# Eduki Search API Client

This directory contains Python scripts to interact with the Eduki search API.

## Files

- `api_request.py` - Main API client class and test script
- `run_query.py` - Simple command-line tool for single queries
- `bearer_token.txt` - Authentication token (required)
- `*.json` - API response files saved automatically

## Setup

1. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install required dependencies:
```bash
pip install requests
```

## Usage

### Running the test script
```bash
python api_request.py
```
This runs predefined test queries and saves responses as JSON files.

### Running single queries
```bash
python run_query.py "your search query"
```

Example:
```bash
python run_query.py "klasse 5 mathematik"
```

## API Details

- **Endpoint**: `https://api.eduki.com/api/v3/search/materials`
- **Method**: POST
- **Authentication**: Bearer token (from `bearer_token.txt`)
- **Parameters**:
  - `limit=36`
  - `p=0` 
  - `q=<search_query>` (URL encoded)
  - `world=de`
- **Payload**:
  - `page_content=value`
  - `test_segment=30`
  - `auto_suggest=1`
  - `intent=1`

## File Naming Convention

Query responses are saved as JSON files with the following naming:
- URL-encoded queries are decoded
- Spaces are replaced with underscores
- Special characters are removed
- `.json` extension is added

Examples:
- `escape+room+klasse+4` → `escape_room_klasse_4.json`
- `mini-paket+biologie` → `mini-paket_biologie.json`
- `buchstabeneinführung` → `buchstabeneinführung.json`

## Response Format

The API returns JSON responses containing:
- `query` - The original search query used
- `data.materials[]` - Array of search results
- Each material includes: title, description, author, cover image, etc.
