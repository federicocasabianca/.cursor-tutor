#!/usr/bin/env python3
"""
Simple script to run individual API queries
Usage: python run_query.py "your search query here"
"""

import sys
from api_request import EdukiSearchAPI

def main():
    if len(sys.argv) != 2:
        print("Usage: python run_query.py 'your search query'")
        print("Example: python run_query.py 'klasse 5 mathematik'")
        return
    
    query = sys.argv[1]
    
    try:
        api = EdukiSearchAPI()
        result = api.make_request(query)
        
        if result:
            materials = result.get('data', {}).get('materials', [])
            print(f"\n📊 Summary:")
            print(f"   Total materials found: {len(materials)}")
            
            if materials:
                print(f"   First 3 results:")
                for i, material in enumerate(materials[:3], 1):
                    title = material.get('title', 'N/A')
                    author = material.get('author', {}).get('details', {}).get('publicName', 'N/A')
                    print(f"   {i}. {title} (by {author})")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
