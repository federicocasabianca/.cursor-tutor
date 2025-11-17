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
import requests
from pathlib import Path
from typing import Dict, Any, Optional

class EdukiSearchAPI:
    """API client for Eduki Search Service - copied from api_request.py"""
    
    def __init__(self, bearer_token_file=None):
        """Initialize the API client with bearer token."""
        if bearer_token_file is None:
            # Try to find bearer token in parent directory
            parent_dir = Path(__file__).parent.parent / 'elastic-intent-queries'
            bearer_token_file = parent_dir / 'bearer_token.txt'
            if not bearer_token_file.exists():
                # Try current directory
                bearer_token_file = Path('bearer_token.txt')
        
        self.base_url = "https://metrics.api.eduki.info/api/v3/search/materials"
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
                f"Please ensure bearer_token.txt exists in elastic-intent-queries/ directory."
            )
        with open(token_path, 'r') as f:
            return f.read().strip()
    
    def make_request(self, query):
        """
        Make API request for given query.
        
        Args:
            query (str): Search query
            
        Returns:
            dict: Transformed response data in results.json format
        """
        print(f"Making request for query: '{query}'")
        
        # Prepare URL parameters
        params = {
            "access_check": 1,
            "limit": 36,
            "p": 0,
            "q": query.replace(' ', '%20'),  # Use %20 for spaces
            "world": "de",
            "intent": 1,
            "metrics": 1
        }
        
        # Prepare payload
        payload = {
            "page_context": "main",
            "auto_suggest": True
        }
        
        try:
            # Make POST request
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
            
            # Transform response to match results.json format
            # The API returns materials in response_data['items']['materials']
            materials = response_data.get('items', {}).get('materials', [])
            
            # Transform each material to include only the fields we need
            # Match the exact structure from results.json
            transformed_materials = []
            for material in materials:
                # Extract material_categories and ensure they have the right structure
                material_categories = material.get("material_categories", [])
                
                transformed_material = {
                    "id": material.get("id"),
                    "title": material.get("title"),
                    "_score": material.get("_score"),
                    "material_categories": material_categories
                }
                transformed_materials.append(transformed_material)
            
            # Create the final response in results.json format
            # This matches the structure: { "query": "...", "materials": [...] }
            transformed_response = {
                "query": query,
                "materials": transformed_materials
            }
            
            print(f"✅ Request successful! Status: {response.status_code}")
            print(f"📊 Materials returned: {len(transformed_materials)}")
            
            return transformed_response
            
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
    
    # Get all query folders
    query_folders = [d for d in queries_dir.iterdir() if d.is_dir()]
    total_queries = len(query_folders)
    
    print(f"Found {total_queries} query folders\n")
    print("=" * 80)
    
    # Statistics
    success_count = 0
    error_count = 0
    skipped_count = 0
    
    # Process each query folder
    for i, query_folder in enumerate(sorted(query_folders), 1):
        query_name = query_folder.name
        results_file = query_folder / 'results.json'
        
        # Check if results already exist
        if results_file.exists() and not overwrite:
            print(f"[{i}/{total_queries}] ⏭️  Skipping {query_name} (results.json already exists)")
            skipped_count += 1
            continue
        
        print(f"\n[{i}/{total_queries}] Processing: {query_name}")
        print("-" * 80)
        
        try:
            # Load query metadata
            metadata = load_query_metadata(query_folder)
            original_query = metadata.get('Original Query', query_name)
            
            print(f"Original Query: {original_query}")
            
            # Make API request
            results = api.make_request(original_query)
            
            if results:
                # Save results to results.json
                with open(results_file, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2, ensure_ascii=False)
                
                print(f"💾 Results saved to: {results_file}")
                success_count += 1
            else:
                print(f"❌ Failed to fetch results for {query_name}")
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
        """
    )
    parser.add_argument(
        '--query-folder',
        help='Process only a specific query folder (e.g., "kostenlos")'
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
        query_folder = queries_dir / args.query_folder
        
        if not query_folder.exists():
            print(f"Error: Query folder not found: {query_folder}", file=sys.stderr)
            sys.exit(1)
        
        try:
            api = EdukiSearchAPI()
            metadata = load_query_metadata(query_folder)
            original_query = metadata.get('Original Query', args.query_folder)
            
            results = api.make_request(original_query)
            
            if results:
                results_file = query_folder / 'results.json'
                with open(results_file, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2, ensure_ascii=False)
                print(f"💾 Results saved to: {results_file}")
            else:
                print("❌ Failed to fetch results", file=sys.stderr)
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

