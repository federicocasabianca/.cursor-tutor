#!/usr/bin/env python3
"""
Fetch search results for all queries using the Eduki Search API.

This script:
1. Reads all query folders from queries/
2. Extracts the original query from query_metadata.txt
3. Makes API requests using the same logic as api_request.py
4. Transforms the response to match results.json format
5. Saves results.json in each query folder
"""
import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from urllib.parse import urlencode
import requests

class EdukiSearchAPI:
    """API client for Eduki Search Service - copied from api_request.py"""
    
    def __init__(self, bearer_token_file=None, mock_response_file=None):
        """Initialize the API client with bearer token."""
        if bearer_token_file is None:
            # Look for bearer token in the same directory as this script (LLM-as-judge project)
            script_dir = Path(__file__).parent
            bearer_token_file = script_dir / 'bearer_token.txt'
            if not bearer_token_file.exists():
                # Fallback: try parent directory's elastic-intent-queries
                parent_dir = script_dir.parent / 'elastic-intent-queries'
                bearer_token_file = parent_dir / 'bearer_token.txt'
                if not bearer_token_file.exists():
                    # Last fallback: current working directory
                    bearer_token_file = Path('bearer_token.txt')
        
        self.base_url = "https://vector.api.eduki.info/api/v3/search/materials"
        context_dir = Path(__file__).parent / 'context'
        default_mock_path = context_dir / 'example.json'
        self.mock_response_path = Path(mock_response_file) if mock_response_file else default_mock_path
        self.bearer_token = self._load_bearer_token(bearer_token_file)
        self.headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
    def _load_bearer_token(self, token_file):
        """Load bearer token from file."""
        token_path = Path(token_file)
        if not token_path.exists():
            raise FileNotFoundError(
                f"Bearer token file '{token_file}' not found. "
                f"Please ensure bearer_token.txt exists in the LLM-as-judge/ directory."
            )
        with open(token_path, 'r') as f:
            return f.read().strip()
    
    def make_request(self, query, use_vector=True):
        """
        Make API request for given query.
        
        Args:
            query (str): Search query
            use_vector (bool): If True, include vector=true parameter (hybrid mode).
                              If False, exclude vector parameter (lexical mode).
            
        Returns:
            dict: Transformed response data in results.json format
        """
        mode = "Hybrid" if use_vector else "Lexical"
        print(f"Making {mode.lower()} request for query: '{query}'")
        
        # Prepare URL parameters
        params = {
            "limit": 36,
            "q": query,
            "world": "de",
            "metrics": "true"
        }
        
        # Add vector parameter only for hybrid mode
        if use_vector:
            params["vector"] = "true"

        # Include the previously required payload
        payload = {
            "page_context": "main",
            "auto_suggest": True  
        }
        
        # Build and print the full request URL as plain string
        query_string = urlencode(params)
        full_url = f"{self.base_url}?{query_string}"
        print(f"📋 Full Request URL: {full_url}")
        print(f"📋 Request Payload: {json.dumps(payload, indent=2)}")
        print(f"📋 Request Headers: {json.dumps({k: v for k, v in self.headers.items() if k != 'Authorization'}, indent=2)}")
        
        try:
            response_status = None
            if self.mock_response_path.exists():
                print(f"📄 Reading mock response from {self.mock_response_path}")
                with open(self.mock_response_path, 'r', encoding='utf-8') as f:
                    response_data = json.load(f)
                response_status = "mock-file"
            else:
                # Make POST request (vector endpoint still accepts POST with this payload)
                response = requests.post(
                    self.base_url,
                    params=params,
                    json=payload,
                    headers=self.headers,
                    timeout=30
                )
                
                # Check if request was successful
                response.raise_for_status()
                
                # Parse JSON response
                response_data = response.json()
                response_status = response.status_code
            
            # Save raw API response as-is (for debugging and comparison with Postman)
            # Add the query and mode to the response for reference
            raw_response = response_data.copy()
            raw_response["_query"] = query
            raw_response["_request_status"] = response_status
            raw_response["_mode"] = "hybrid" if use_vector else "lexical"
            
            # Extract materials count for logging
            materials = response_data.get('items', {}).get('materials', [])
            materials_count = len(materials) if materials else 0
            
            mode = "Hybrid" if use_vector else "Lexical"
            print(f"✅ {mode} request successful! Status: {response_status}")
            print(f"📊 Materials returned: {materials_count}")
            
            return raw_response
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Status Code: {e.response.status_code}")
                print(f"Response: {e.response.text[:500]}...")
            return None


def load_query_metadata(query_folder: Path) -> Dict[str, str]:
    """Load query metadata from the query folder."""
    metadata_file = query_folder / 'query_metadata.txt'
    if not metadata_file.exists():
        raise FileNotFoundError(f"Query metadata not found: {metadata_file}")
    
    metadata = {}
    with open(metadata_file, 'r', encoding='utf-8') as f:
        for line in f:
            if ':' in line:
                key, value = line.split(':', 1)
                metadata[key.strip()] = value.strip()
    return metadata


def discover_query_folders(queries_dir: Path) -> List[Path]:
    """Return all query folders (handles nested grouped directories)."""
    if not queries_dir.exists():
        return []
    metadata_files = list(queries_dir.rglob('query_metadata.txt'))
    folders = [path.parent for path in metadata_files]
    return sorted(folders, key=lambda p: p.relative_to(queries_dir).as_posix())


def resolve_query_folder(queries_dir: Path, folder_arg: str) -> Path:
    """Resolve a user-provided folder argument to an actual query folder path."""
    candidate = queries_dir / folder_arg
    if (candidate / 'query_metadata.txt').exists():
        return candidate
    
    matches = [folder for folder in discover_query_folders(queries_dir) if folder.name == folder_arg]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        options = ", ".join(str(folder.relative_to(queries_dir)) for folder in matches)
        raise ValueError(
            f"Multiple query folders share the name '{folder_arg}'. "
            f"Please specify one of: {options}"
        )
    
    available = ", ".join(
        str(folder.relative_to(queries_dir))
        for folder in discover_query_folders(queries_dir)
    )
    raise FileNotFoundError(
        f"Query folder '{folder_arg}' not found under {queries_dir}.\n"
        f"Available folders: {available}"
    )


def fetch_all_queries(base_dir: Optional[Path] = None, overwrite: bool = False):
    """
    Fetch search results for all queries.
    
    Args:
        base_dir: Base directory of the project (default: script directory)
        overwrite: Whether to overwrite existing results.json files
    """
    if base_dir is None:
        base_dir = Path(__file__).parent
    
    queries_dir = base_dir / 'queries'
    
    if not queries_dir.exists():
        raise FileNotFoundError(f"Queries directory not found: {queries_dir}")
    
    # Initialize API client
    try:
        api = EdukiSearchAPI()
        print("✅ API client initialized successfully\n")
    except Exception as e:
        print(f"❌ Failed to initialize API client: {e}")
        return
    
    # Get all query folders (supports grouped directories)
    query_folders = discover_query_folders(queries_dir)
    total_queries = len(query_folders)
    
    print(f"Found {total_queries} query folders\n")
    print("=" * 80)
    
    # Statistics
    success_count = 0
    error_count = 0
    skipped_count = 0
    
    # Process each query folder
    for i, query_folder in enumerate(query_folders, 1):
        query_name = query_folder.relative_to(queries_dir).as_posix()
        
        print(f"\n[{i}/{total_queries}] Processing: {query_name}")
        print("-" * 80)
        
        try:
            # Load query metadata
            metadata = load_query_metadata(query_folder)
            original_query = metadata.get('Original Query', query_name)
            
            print(f"Original Query: {original_query}")
            
            # Make both hybrid and lexical API requests
            hybrid_results_file = query_folder / 'results_hybrid.json'
            lexical_results_file = query_folder / 'results_lexical.json'
            
            # Check if results already exist (for both modes)
            if not overwrite and hybrid_results_file.exists() and lexical_results_file.exists():
                print(f"⏭️  Skipping {query_name} (both results files already exist)")
                skipped_count += 1
                continue
            
            hybrid_success = False
            lexical_success = False
            
            # Make hybrid request (with vector=true)
            print(f"\n🔍 Making Hybrid request (vector=true)...")
            hybrid_results = api.make_request(original_query, use_vector=True)
            
            if hybrid_results:
                with open(hybrid_results_file, 'w', encoding='utf-8') as f:
                    json.dump(hybrid_results, f, indent=2, ensure_ascii=False)
                print(f"💾 Hybrid results saved to: {hybrid_results_file}")
                hybrid_success = True
            else:
                print(f"❌ Failed to fetch hybrid results for {query_name}")
            
            # Make lexical request (without vector parameter)
            print(f"\n🔍 Making Lexical request (no vector parameter)...")
            lexical_results = api.make_request(original_query, use_vector=False)
            
            if lexical_results:
                with open(lexical_results_file, 'w', encoding='utf-8') as f:
                    json.dump(lexical_results, f, indent=2, ensure_ascii=False)
                print(f"💾 Lexical results saved to: {lexical_results_file}")
                lexical_success = True
            else:
                print(f"❌ Failed to fetch lexical results for {query_name}")
            
            if hybrid_success and lexical_success:
                success_count += 1
            elif hybrid_success or lexical_success:
                # Partial success
                success_count += 1
            else:
                error_count += 1
                
        except Exception as e:
            print(f"❌ Error processing {query_name}: {e}")
            import traceback
            traceback.print_exc()
            error_count += 1
    
    # Print summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total queries: {total_queries}")
    print(f"✅ Successful: {success_count}")
    print(f"⏭️  Skipped: {skipped_count}")
    print(f"❌ Errors: {error_count}")
    print("=" * 80)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Fetch search results for all queries using the Eduki Search API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python fetch_all_queries.py
  python fetch_all_queries.py --overwrite
  python fetch_all_queries.py --query-folder kostenlos
  python fetch_all_queries.py --query-folder categories/kostenlos
        """
    )
    parser.add_argument(
        '--query-folder',
        help='Process only a specific query folder (e.g., "kostenlos" or "categories/kostenlos")'
    )
    parser.add_argument(
        '--overwrite',
        action='store_true',
        help='Overwrite existing results.json files'
    )
    parser.add_argument(
        '--base-dir',
        type=Path,
        help='Base directory of the project (default: script directory)'
    )
    
    args = parser.parse_args()
    
    if args.query_folder:
        # Process single query folder
        base_dir = args.base_dir or Path(__file__).parent
        queries_dir = base_dir / 'queries'
        try:
            query_folder = resolve_query_folder(queries_dir, args.query_folder)
        except Exception as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)
        
        try:
            api = EdukiSearchAPI()
            metadata = load_query_metadata(query_folder)
            original_query = metadata.get(
                'Original Query',
                query_folder.relative_to(queries_dir).as_posix()
            )
            
            hybrid_results_file = query_folder / 'results_hybrid.json'
            lexical_results_file = query_folder / 'results_lexical.json'
            
            # Make hybrid request (with vector=true)
            print(f"\n🔍 Making Hybrid request (vector=true)...")
            hybrid_results = api.make_request(original_query, use_vector=True)
            
            if hybrid_results:
                with open(hybrid_results_file, 'w', encoding='utf-8') as f:
                    json.dump(hybrid_results, f, indent=2, ensure_ascii=False)
                print(f"💾 Hybrid results saved to: {hybrid_results_file}")
            else:
                print("❌ Failed to fetch hybrid results", file=sys.stderr)
                sys.exit(1)
            
            # Make lexical request (without vector parameter)
            print(f"\n🔍 Making Lexical request (no vector parameter)...")
            lexical_results = api.make_request(original_query, use_vector=False)
            
            if lexical_results:
                with open(lexical_results_file, 'w', encoding='utf-8') as f:
                    json.dump(lexical_results, f, indent=2, ensure_ascii=False)
                print(f"💾 Lexical results saved to: {lexical_results_file}")
            else:
                print("❌ Failed to fetch lexical results", file=sys.stderr)
                sys.exit(1)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            sys.exit(1)
    else:
        # Process all query folders
        fetch_all_queries(base_dir=args.base_dir, overwrite=args.overwrite)


if __name__ == '__main__':
    main()

