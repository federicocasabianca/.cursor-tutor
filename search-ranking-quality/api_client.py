#!/usr/bin/env python3
"""
API Client for Eduki Search Service
Handles live API requests for the Compare functionality.
"""

import requests
import json
import urllib.parse
import os
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
    
    def search_materials(self, query, limit=12):
        """
        Search for materials using the live API.
        
        Args:
            query (str): Search query
            limit (int): Number of results to return (default: 12)
            
        Returns:
            dict: API response data in the same format as JSON files
        """
        print(f"Making API request for query: '{query}'")
        
        # Prepare URL parameters (these go in the query string)
        url_params = {
            "limit": limit,
            "p": 0,
            "q": query,
            "world": "de"
        }
        
        # Prepare POST body payload (match QA's working config exactly)
        form_data = {
            "page_context": "main",  # Note: "page_context" not "page_content"
            "test_segment": 30,
            "auto_suggest": 1,
            "intent": 1
        }
        
        print(f"🔧 URL params: {url_params}")
        print(f"🔧 Form data being sent: {form_data}")
        
        # Update headers for JSON payload (match production)
        headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        try:
            # Make POST request with URL params and JSON payload (match production)
            response = requests.post(
                self.base_url,
                params=url_params,  # URL parameters  
                json=form_data,     # JSON payload (not form data)
                headers=headers,
                timeout=30
            )
            
            # Debug: Print the actual URL that was called
            print(f"🌐 Actual URL called: {response.url}")
            
            # Check if request was successful
            response.raise_for_status()
            
            # Parse JSON response
            response_data = response.json()
            
            print(f"✅ API request successful! Status: {response.status_code}")
            print(f"🔍 Response keys: {list(response_data.keys())}")
            
            # Check both possible response structures
            materials = []
            if 'data' in response_data and response_data['data'] and 'materials' in response_data['data']:
                materials = response_data['data']['materials']
                print(f"📊 Found materials in 'data.materials' structure")
            elif 'items' in response_data and response_data['items'] and 'materials' in response_data['items']:
                materials = response_data['items']['materials'] 
                print(f"📊 Found materials in 'items.materials' structure")
            else:
                print(f"⚠️  No materials found in expected structures")
                print(f"🔍 Full response structure: {json.dumps(response_data, indent=2)[:500]}...")
            
            # Transform the response to match our expected format
            transformed_data = {
                "items": {
                    "materials": materials
                },
                "auto_suggest": response_data.get('auto_suggest', {}),
                "meta": response_data.get('meta', {})
            }
            
            materials_count = len(materials)
            print(f"Retrieved {materials_count} materials")
            
            return transformed_data
            
        except requests.exceptions.RequestException as e:
            print(f"❌ API request failed: {e}")
            error_details = {
                'error_type': 'RequestException',
                'message': str(e)
            }
            
            if hasattr(e, 'response') and e.response is not None:
                error_details['status_code'] = e.response.status_code
                try:
                    error_details['response_text'] = e.response.text
                except:
                    error_details['response_text'] = 'Unable to read response'
                    
            raise Exception(f"API request failed: {error_details}")
        
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            raise Exception(f"Unexpected error during API request: {str(e)}")
    


def test_api_client():
    """Test function for the API client."""
    try:
        api = EdukiSearchAPI()
        result = api.search_materials("test query", limit=5)
        print("✅ API client test successful")
        return True
    except Exception as e:
        print(f"❌ API client test failed: {e}")
        return False

if __name__ == "__main__":
    test_api_client()
