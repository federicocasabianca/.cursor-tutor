#!/usr/bin/env python3
"""
Script to create folder structure for all queries from the intent markdown files.
"""
import os
import re
from pathlib import Path

INTENT_GROUPS = {
    'no_intent': 'no-intent',
    'category_intent': 'categories',
    'grade_intent': 'grade-level',
    'combined_intent': 'combined',
}

def extract_queries_from_markdown(md_file_path):
    """Extract query names from markdown table."""
    queries = []
    with open(md_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        # Match table rows with query names (skip header row)
        pattern = r'^\|\s*([^|]+?)\s*\|\s*(GOOD_RESULTS|NOT_GOOD_RESULTS)\s*\|'
        for line in content.split('\n'):
            match = re.match(pattern, line)
            if match:
                query = match.group(1).strip()
                if query and query.lower() != 'query':
                    queries.append(query)
    return queries

def sanitize_folder_name(query):
    """Convert query to a valid folder name."""
    # Replace spaces and special characters with underscores
    folder_name = re.sub(r'[^\w\s-]', '', query)
    folder_name = re.sub(r'[-\s]+', '_', folder_name)
    return folder_name.lower()

def create_folders():
    """Create folder structure for all queries."""
    base_dir = Path(__file__).parent
    queries_dir = base_dir / 'queries'
    queries_dir.mkdir(exist_ok=True)
    for group in INTENT_GROUPS.values():
        (queries_dir / group).mkdir(exist_ok=True)
    
    # Intent files to process
    intent_files = [
        ('no_intent.md', 'no_intent'),
        ('category_intent.md', 'category_intent'),
        ('grade_intent.md', 'grade_intent'),
        ('combined_intent.md', 'combined_intent'),
    ]
    
    # Path to the markdown files (assuming they're in elastic-intent-queries/)
    md_base = base_dir.parent / 'elastic-intent-queries'
    
    all_queries = {}
    
    for md_file, intent_type in intent_files:
        md_path = md_base / md_file
        if not md_path.exists():
            print(f"Warning: {md_path} not found, skipping...")
            continue
        
        queries = extract_queries_from_markdown(md_path)
        all_queries[intent_type] = queries
        
        print(f"\nProcessing {intent_type}: {len(queries)} queries")
        
        for query in queries:
            folder_name = sanitize_folder_name(query)
            group_dir_name = INTENT_GROUPS.get(intent_type, intent_type)
            group_dir = queries_dir / group_dir_name
            group_dir.mkdir(exist_ok=True)
            query_dir = group_dir / folder_name
            query_dir.mkdir(exist_ok=True)
            
            # Create a metadata file with the original query name
            metadata_file = query_dir / 'query_metadata.txt'
            with open(metadata_file, 'w', encoding='utf-8') as f:
                f.write(f"Original Query: {query}\n")
                f.write(f"Intent Type: {intent_type}\n")
                f.write(f"Folder Name: {folder_name}\n")
    
    print(f"\n✓ Created folders for {sum(len(q) for q in all_queries.values())} queries")
    return all_queries

if __name__ == '__main__':
    create_folders()

