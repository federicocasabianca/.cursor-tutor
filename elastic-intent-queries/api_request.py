#!/usr/bin/env python3
"""
API Request Script for Eduki Search Service
Makes POST requests to search API and saves responses as JSON files.
"""

import requests
import json
import urllib.parse
import os
import re
from pathlib import Path

class EdukiSearchAPI:
    def __init__(self, bearer_token_file="bearer_token.txt"):
        """Initialize the API client with bearer token."""
        self.base_url = "https://api.eduki.com/api/v3/search/materials"
        self.bearer_token = self._load_bearer_token(bearer_token_file)
        self.headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
    def _load_bearer_token(self, token_file):
        """Load bearer token from file."""
        try:
            with open(token_file, 'r') as f:
                return f.read().strip()
        except FileNotFoundError:
            raise FileNotFoundError(f"Bearer token file '{token_file}' not found")
    
    def _decode_query(self, encoded_query):
        """Decode URL-encoded query string."""
        # Handle both + and %20 encodings
        decoded = urllib.parse.unquote_plus(encoded_query)
        return decoded
    
    def _create_filename(self, query):
        """Create filename from query string."""
        # Decode the query first
        decoded_query = self._decode_query(query)
        # Replace spaces with underscores and remove special characters
        filename = re.sub(r'[^\w\s-]', '', decoded_query)
        filename = re.sub(r'\s+', '_', filename)
        return f"{filename}.json"
    
    def make_request(self, query, save_response=True):
        """
        Make API request for given query.
        
        Args:
            query (str): Search query (can be URL encoded)
            save_response (bool): Whether to save response to JSON file
            
        Returns:
            dict: API response data
        """
        # Decode query for display purposes
        decoded_query = self._decode_query(query)
        print(f"Making request for query: '{decoded_query}'")
        
        # Prepare URL parameters
        params = {
            "limit": 36,
            "p": 0,
            "q": decoded_query,  # Use decoded query for the actual request
            "world": "de"
        }
        
        # Prepare payload
        payload = {
            "page_content": "value",
            "test_segment": 30,
            "auto_suggest": 1,
            "intent": 0
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
            
            print(f"✅ Request successful! Status: {response.status_code}")
            print(f"Response contains {len(response_data.get('data', {}).get('materials', []))} materials")
            
            # Save response if requested
            if save_response:
                filename = self._create_filename(query)
                self._save_response(response_data, filename)
                print(f"💾 Response saved to: {filename}")
            
            return response_data
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Status Code: {e.response.status_code}")
                print(f"Response: {e.response.text}")
            return None
    
    def _save_response(self, data, filename):
        """Save response data to JSON file."""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Failed to save response: {e}")

def main():
    """Main function to test API requests."""
    print("🚀 Starting Eduki Search API Tests")
    print("=" * 50)
    
    # Initialize API client
    try:
        api = EdukiSearchAPI()
        print("✅ API client initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize API client: {e}")
        return
    
    # Test queries
    test_queries = [
        "buchstabeneinführung"
    ]
    
    print(f"\n📝 Testing {len(test_queries)} queries:")
    print("-" * 30)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Test {i}/{len(test_queries)}")
        result = api.make_request(query)
        
        if result:
            # Display some basic info about the response
            materials = result.get('data', {}).get('materials', [])
            if materials:
                print(f"📚 First material title: {materials[0].get('title', 'N/A')}")
                print(f"👤 First material author: {materials[0].get('author', {}).get('details', {}).get('publicName', 'N/A')}")
        
        print("-" * 30)
    
    print("\n✨ API testing completed!")

if __name__ == "__main__":
    main()
