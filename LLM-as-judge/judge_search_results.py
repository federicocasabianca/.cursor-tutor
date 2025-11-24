#!/usr/bin/env python3
"""
LLM-as-Judge: Script to judge search results using LLM evaluation.

Usage:
    python judge_search_results.py <query_folder_name>
    
Example:
    python judge_search_results.py kostenlos
    python judge_search_results.py weihnachten_klasse_1
"""
import json
import argparse
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
import csv

try:
    from openai import OpenAI
except ImportError:
    print("Error: openai package not installed. Install with: pip install openai")
    sys.exit(1)


class SearchResultJudge:
    """Judge search results using LLM evaluation."""
    
    def __init__(self, base_dir: Optional[Path] = None):
        """Initialize the judge with base directory."""
        if base_dir is None:
            base_dir = Path(__file__).parent
        self.base_dir = base_dir
        self.prompt_file = base_dir / 'llm_as_judge_prompt.md'
        self.queries_dir = base_dir / 'queries'
        self.context_dir = base_dir / 'context'
        self.taxonomy_file = self.context_dir / 'taxonomy_categories.csv'
        
        # Initialize OpenAI client (will use OPENAI_API_KEY from environment)
        self.client = OpenAI()

    def _discover_query_folders(self) -> List[Path]:
        """Return all query folders regardless of grouping."""
        metadata_files = list(self.queries_dir.rglob('query_metadata.txt'))
        folders = [path.parent for path in metadata_files]
        return sorted(folders, key=lambda p: p.relative_to(self.queries_dir).as_posix())

    def list_available_queries(self) -> List[str]:
        """Return relative paths for all available queries."""
        return [folder.relative_to(self.queries_dir).as_posix() for folder in self._discover_query_folders()]

    def resolve_query_folder(self, query_folder_name: str) -> Path:
        """
        Resolve query folder names.
        Supports both grouped paths (e.g., categories/kostenlos) and legacy short names (e.g., kostenlos).
        """
        candidate = self.queries_dir / query_folder_name
        if (candidate / 'query_metadata.txt').exists():
            return candidate

        matches = [folder for folder in self._discover_query_folders() if folder.name == query_folder_name]
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            options = ", ".join(str(folder.relative_to(self.queries_dir)) for folder in matches)
            raise ValueError(
                f"Multiple query folders share the name '{query_folder_name}'. "
                f"Please specify one of: {options}"
            )

        available = ", ".join(self.list_available_queries())
        raise FileNotFoundError(
            f"Query folder '{query_folder_name}' not found under {self.queries_dir}.\n"
            f"Available folders: {available}"
        )
    
    def load_prompt(self) -> str:
        """Load the LLM prompt/instructions."""
        if not self.prompt_file.exists():
            raise FileNotFoundError(
                f"Prompt file not found: {self.prompt_file}\n"
                "Please create llm_as_judge_prompt.md with your evaluation instructions."
            )
        return self.prompt_file.read_text(encoding='utf-8')
    
    def load_query_metadata(self, query_folder: Path) -> Dict[str, str]:
        """Load query metadata from the query folder."""
        metadata_file = query_folder / 'query_metadata.txt'
        if not metadata_file.exists():
            raise FileNotFoundError(
                f"Query metadata not found: {metadata_file}\n"
                "Run setup_folders.py first to create the folder structure."
            )
        
        metadata = {}
        with open(metadata_file, 'r', encoding='utf-8') as f:
            for line in f:
                if ':' in line:
                    key, value = line.split(':', 1)
                    metadata[key.strip()] = value.strip()
        return metadata
    
    def load_search_results(self, query_folder: Path) -> Dict[str, Any]:
        """Load search results JSON from the query folder."""
        # Prefer the standardized results.json produced by fetch_all_queries
        results_file = query_folder / 'results.json'
        
        if not results_file.exists():
            # Fall back to any JSON file (legacy behavior) to avoid breaking older folders
            json_files = sorted(query_folder.glob('*.json'))
            if not json_files:
                raise FileNotFoundError(
                    f"No JSON file found in query folder: {query_folder}\n"
                    "Please add a search results JSON file to this folder."
                )
            results_file = json_files[0]
            if len(json_files) > 1:
                print(f"Warning: Multiple JSON files found. Using: {results_file.name}")
        
        with open(results_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_context(self) -> str:
        """Load context files (taxonomy CSV)."""
        if not self.taxonomy_file.exists():
            print(f"Warning: Taxonomy file not found: {self.taxonomy_file}")
            return ""
        
        # Read CSV and format as text for context
        context_lines = []
        with open(self.taxonomy_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            # Include header
            if reader.fieldnames:
                context_lines.append("Taxonomy Categories:")
                context_lines.append("Columns: " + ", ".join(reader.fieldnames))
                context_lines.append("")
                # Include first 100 rows as sample (adjust as needed)
                for i, row in enumerate(reader):
                    if i >= 100:
                        context_lines.append(f"... (showing first 100 rows, total rows may be more)")
                        break
                    context_lines.append(f"Row {i+1}: {json.dumps(row, ensure_ascii=False)}")
        
        return "\n".join(context_lines)
    
    def create_judgment_prompt(
        self,
        base_prompt: str,
        query: str,
        search_results: Dict[str, Any],
        context: str
    ) -> str:
        """Create the full prompt for LLM judgment."""
        # Format search results as JSON string
        results_str = json.dumps(search_results, indent=2, ensure_ascii=False)
        
        prompt = f"""{base_prompt}

## Query to Evaluate
{query}

## Search Results
{results_str}

## Context
{context}

## Task
Please provide your judgment on the search results for the query above based on the instructions provided.
"""
        return prompt
    
    def get_queries_by_group(self, group_name: str) -> List[str]:
        """Get all query folder names in a specific group."""
        group_dir = self.queries_dir / group_name
        if not group_dir.exists() or not group_dir.is_dir():
            available_groups = [d.name for d in self.queries_dir.iterdir() if d.is_dir()]
            raise FileNotFoundError(
                f"Group '{group_name}' not found in {self.queries_dir}.\n"
                f"Available groups: {', '.join(available_groups)}"
            )
        
        query_folders = [
            folder.relative_to(self.queries_dir).as_posix()
            for folder in group_dir.iterdir()
            if folder.is_dir() and (folder / 'query_metadata.txt').exists()
        ]
        return sorted(query_folders)
    
    def judge(self, query_folder_name: str, verbose: bool = True) -> Dict[str, Any]:
        """Judge search results for a specific query folder."""
        query_folder = self.resolve_query_folder(query_folder_name)
        relative_folder = query_folder.relative_to(self.queries_dir).as_posix()
        
        if verbose:
            print(f"Judging query: {relative_folder}")
            print(f"Folder: {query_folder}")
        
        # Load all required data
        if verbose:
            print("Loading prompt...")
        base_prompt = self.load_prompt()
        
        if verbose:
            print("Loading query metadata...")
        metadata = self.load_query_metadata(query_folder)
        query = metadata.get('Original Query', query_folder_name)
        
        if verbose:
            print("Loading search results...")
        search_results = self.load_search_results(query_folder)
        
        if verbose:
            print("Loading context...")
        context = self.load_context()
        
        # Create full prompt
        if verbose:
            print("Creating judgment prompt...")
        full_prompt = self.create_judgment_prompt(
            base_prompt, query, search_results, context
        )
        
        # Call LLM
        if verbose:
            print("Calling LLM for judgment...")
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",  # Adjust model as needed
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert evaluator of search results quality. Follow the instructions carefully and provide detailed, structured judgments."
                    },
                    {
                        "role": "user",
                        "content": full_prompt
                    }
                ],
                temperature=0.3  # Lower temperature for more consistent judgments
            )
            
            judgment_text = response.choices[0].message.content
            
            # Save judgment
            judgment_file = query_folder / 'judgment.json'
            judgment_data = {
                "query": query,
                "query_folder": query_folder_name,
                "judgment": judgment_text,
                "model": "gpt-4o",
                "metadata": metadata
            }
            
            with open(judgment_file, 'w', encoding='utf-8') as f:
                json.dump(judgment_data, f, indent=2, ensure_ascii=False)
            
            if verbose:
                print(f"\n✓ Judgment saved to: {judgment_file}")
                print("\n" + "="*80)
                print("JUDGMENT:")
                print("="*80)
                print(judgment_text)
                print("="*80)
            
            return judgment_data
            
        except Exception as e:
            print(f"Error calling LLM: {e}")
            raise
    
    def judge_group(self, group_name: str, skip_existing: bool = False) -> Dict[str, Any]:
        """Judge all queries in a specific group."""
        query_folders = self.get_queries_by_group(group_name)
        total = len(query_folders)
        
        print(f"\n{'='*80}")
        print(f"Processing group: {group_name}")
        print(f"Total queries: {total}")
        print(f"{'='*80}\n")
        
        results = {
            'group': group_name,
            'total': total,
            'successful': 0,
            'failed': 0,
            'skipped': 0,
            'errors': []
        }
        
        for i, query_folder in enumerate(query_folders, 1):
            judgment_file = self.queries_dir / query_folder / 'judgment.json'
            
            if skip_existing and judgment_file.exists():
                print(f"[{i}/{total}] ⏭️  Skipping {query_folder} (judgment.json already exists)")
                results['skipped'] += 1
                continue
            
            print(f"\n[{i}/{total}] Processing: {query_folder}")
            print("-" * 80)
            
            try:
                self.judge(query_folder, verbose=False)
                results['successful'] += 1
                print(f"✅ Successfully judged: {query_folder}")
            except Exception as e:
                results['failed'] += 1
                error_msg = f"{query_folder}: {str(e)}"
                results['errors'].append(error_msg)
                print(f"❌ Failed to judge {query_folder}: {e}")
                import traceback
                traceback.print_exc()
        
        print(f"\n{'='*80}")
        print(f"GROUP SUMMARY: {group_name}")
        print(f"{'='*80}")
        print(f"Total queries: {total}")
        print(f"✅ Successful: {results['successful']}")
        print(f"⏭️  Skipped: {results['skipped']}")
        print(f"❌ Failed: {results['failed']}")
        if results['errors']:
            print(f"\nErrors:")
            for error in results['errors']:
                print(f"  - {error}")
        print(f"{'='*80}\n")
        
        return results
    
    def judge_all(self, skip_existing: bool = False) -> Dict[str, Any]:
        """Judge all queries in all groups."""
        groups = [d.name for d in self.queries_dir.iterdir() if d.is_dir()]
        groups.sort()
        
        print(f"\n{'='*80}")
        print(f"Processing ALL groups")
        print(f"Groups: {', '.join(groups)}")
        print(f"{'='*80}\n")
        
        all_results = {
            'groups': {},
            'total_queries': 0,
            'total_successful': 0,
            'total_failed': 0,
            'total_skipped': 0
        }
        
        for group_name in groups:
            group_results = self.judge_group(group_name, skip_existing=skip_existing)
            all_results['groups'][group_name] = group_results
            all_results['total_queries'] += group_results['total']
            all_results['total_successful'] += group_results['successful']
            all_results['total_failed'] += group_results['failed']
            all_results['total_skipped'] += group_results['skipped']
        
        print(f"\n{'='*80}")
        print("OVERALL SUMMARY")
        print(f"{'='*80}")
        print(f"Total queries: {all_results['total_queries']}")
        print(f"✅ Successful: {all_results['total_successful']}")
        print(f"⏭️  Skipped: {all_results['total_skipped']}")
        print(f"❌ Failed: {all_results['total_failed']}")
        print(f"{'='*80}\n")
        
        return all_results


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Judge search results using LLM evaluation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Judge a single query
  python judge_search_results.py kostenlos
  python judge_search_results.py categories/kunst
  
  # Judge all queries in a specific group
  python judge_search_results.py --group categories
  python judge_search_results.py --group grade-level
  
  # Judge all queries in all groups
  python judge_search_results.py --all
  
  # Skip queries that already have judgments
  python judge_search_results.py --group categories --skip-existing
  
The query folder name can be specified as:
  - Short name (e.g., "kostenlos") - will be resolved automatically
  - Full path (e.g., "categories/kunst") - explicit group/folder path
        """
    )
    parser.add_argument(
        'query_folder',
        nargs='?',
        help='Name of the query folder to judge (optional if --group or --all is used)'
    )
    parser.add_argument(
        '--group',
        help='Judge all queries in a specific group (e.g., "categories", "grade-level")'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Judge all queries in all groups'
    )
    parser.add_argument(
        '--skip-existing',
        action='store_true',
        help='Skip queries that already have judgment.json files'
    )
    parser.add_argument(
        '--base-dir',
        type=Path,
        help='Base directory of the project (default: script directory)'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.all and args.group:
        print("Error: Cannot use --all and --group together", file=sys.stderr)
        sys.exit(1)
    
    if args.all and args.query_folder:
        print("Error: Cannot specify query_folder when using --all", file=sys.stderr)
        sys.exit(1)
    
    if args.group and args.query_folder:
        print("Error: Cannot specify query_folder when using --group", file=sys.stderr)
        sys.exit(1)
    
    if not args.all and not args.group and not args.query_folder:
        print("Error: Must specify either query_folder, --group, or --all", file=sys.stderr)
        parser.print_help()
        sys.exit(1)
    
    try:
        judge = SearchResultJudge(base_dir=args.base_dir)
        
        if args.all:
            judge.judge_all(skip_existing=args.skip_existing)
        elif args.group:
            judge.judge_group(args.group, skip_existing=args.skip_existing)
        else:
            judge.judge(args.query_folder)
            
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

