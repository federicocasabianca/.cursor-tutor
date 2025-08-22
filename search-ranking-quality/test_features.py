#!/usr/bin/env python3

from app import load_materials_data, calculate_metrics, prepare_table_data, analyze_query_title_match

def test_query_matching():
    """Test the query-title matching functionality"""
    print("=== Testing Query-Title Matching ===")
    
    # Test cases
    test_cases = [
        ("math worksheet", "Math Worksheet for Grade 3", "full_match"),
        ("math", "Science and Math Activities", "partial_match"), 
        ("english", "Math Worksheet for Grade 3", "no_match"),
        ("reading comprehension", "Reading Comprehension Exercises", "full_match"),
        ("reading", "Reading Comprehension Exercises", "partial_match"),
    ]
    
    for query, title, expected in test_cases:
        result = analyze_query_title_match(query, title)
        print(f"Query: '{query}' | Title: '{title}'")
        print(f"  Expected: {expected} | Got: {result['type']} | Score: {result['score']}")
        print(f"  Matched tokens: {result['matched_tokens']}")
        print()

def test_with_real_data():
    """Test with the actual materials.json data"""
    print("=== Testing with Real Data ===")
    
    data = load_materials_data()
    if not data:
        print("Could not load materials.json")
        return
    
    materials = data.get('items', {}).get('materials', [])
    auto_suggest = data.get('auto_suggest', {})
    original_query = auto_suggest.get('original_query', 'No query found')
    
    print(f"Original query: '{original_query}'")
    print(f"Total materials: {len(materials)}")
    
    # Calculate metrics for top 5
    metrics = calculate_metrics(materials, top_k=5, original_query=original_query)
    world_info = metrics['query_info']['world_info']
    match_summary = metrics['query_info']['match_summary']
    
    print(f"\nWorld: {world_info['world']} {world_info['flag']}")
    print(f"Match Summary:")
    print(f"  Full matches: {match_summary['full_match']}")
    print(f"  Partial matches: {match_summary['partial_match']}")
    print(f"  No matches: {match_summary['no_match']}")
    
    # Show first few titles with their matches
    table_data = prepare_table_data(materials, top_k=5, original_query=original_query)
    print(f"\nTop 5 title matches:")
    for i, row in enumerate(table_data):
        match = row['title_match']
        print(f"{i+1}. [{match['type'].upper()}] {row['title'][:60]}...")
        if match['matched_tokens']:
            print(f"   Matched tokens: {', '.join(match['matched_tokens'])}")

if __name__ == "__main__":
    test_query_matching()
    test_with_real_data()
