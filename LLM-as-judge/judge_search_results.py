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
from typing import Dict, Any, Optional
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
        # Look for JSON files in the query folder
        json_files = list(query_folder.glob('*.json'))
        
        if not json_files:
            raise FileNotFoundError(
                f"No JSON file found in query folder: {query_folder}\n"
                "Please add a search results JSON file to this folder."
            )
        
        # Use the first JSON file found (or could be more specific)
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
    
    def judge(self, query_folder_name: str) -> Dict[str, Any]:
        """Judge search results for a specific query folder."""
        query_folder = self.queries_dir / query_folder_name
        
        if not query_folder.exists():
            raise FileNotFoundError(
                f"Query folder not found: {query_folder}\n"
                f"Available folders: {', '.join([d.name for d in self.queries_dir.iterdir() if d.is_dir()])}"
            )
        
        print(f"Judging query: {query_folder_name}")
        print(f"Folder: {query_folder}")
        
        # Load all required data
        print("Loading prompt...")
        base_prompt = self.load_prompt()
        
        print("Loading query metadata...")
        metadata = self.load_query_metadata(query_folder)
        query = metadata.get('Original Query', query_folder_name)
        
        print("Loading search results...")
        search_results = self.load_search_results(query_folder)
        
        print("Loading context...")
        context = self.load_context()
        
        # Create full prompt
        print("Creating judgment prompt...")
        full_prompt = self.create_judgment_prompt(
            base_prompt, query, search_results, context
        )
        
        # Call LLM
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


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Judge search results using LLM evaluation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python judge_search_results.py kostenlos
  python judge_search_results.py weihnachten_klasse_1
  
The query folder name should match the folder name in the queries/ directory.
        """
    )
    parser.add_argument(
        'query_folder',
        help='Name of the query folder to judge (e.g., "kostenlos" or "weihnachten_klasse_1")'
    )
    parser.add_argument(
        '--base-dir',
        type=Path,
        help='Base directory of the project (default: script directory)'
    )
    
    args = parser.parse_args()
    
    try:
        judge = SearchResultJudge(base_dir=args.base_dir)
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

