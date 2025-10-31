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
        self.base_url = "https://metrics.api.eduki.info/api/v3/search/materials"
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
        
        # Prepare URL parameters with manual space encoding
        params = {
            "access_check": 1,
            "limit": 36,
            "p": 0,
            "q": decoded_query.replace(' ', '%20'),  # Use %20 instead of + for spaces
            "world": "de",
            "intent": 1,
            "metrics": 1
        }
        
        # Debug: Print the actual URL being constructed
        print(f"Debug - Query parameter: '{decoded_query}'")
        print(f"Debug - URL will be: {self.base_url}?q={decoded_query.replace(' ', '%20')}&...")
        
        # Prepare payload
        payload = {
            "page_context": "main",
            "auto_suggest": True
        }
        
        try:
            # Make POST request with proper URL encoding
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
            print(f"Response contains {len(response_data.get('items', {}).get('materials', []))} materials")
            
            # Save response if requested
            if save_response:
                filename = self._create_filename(query)
                self._save_response(response_data, filename, decoded_query)
                print(f"💾 Response saved to: {filename}")
            
            return response_data
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Status Code: {e.response.status_code}")
                print(f"Response: {e.response.text}")
            return None
    
    def _save_response(self, data, filename, query=None):
        """Save response data to JSON file with query parameter."""
        try:
            # Add query parameter to the data if provided
            if query:
                data['query'] = query
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Failed to save response: {e}")
    
    def get_results_quality(self, response_data):
        """Extract results quality label from API response."""
        if not response_data:
            return None
        
        return response_data.get('serve_metrics', {}).get('results_quality', {}).get('results_quality_label', 'N/A')

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
        "vorschule",
        "klasse 1",
        "1. Klasse",
        "erwachsenenbildung",
        "klasse 2",
        "2. klasse",
        "klasse 4",
        "4. klasse",
        "klasse 3",
        "3.klasse",
        "klasse 5"
    ]
    
    print(f"\n📝 Testing {len(test_queries)} queries:")
    print("-" * 30)
    
    # Store results for summary
    results_summary = []
    quality_counts = {}
    reasons_counter = {}
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Test {i}/{len(test_queries)}")
        result = api.make_request(query, save_response=False)  # Don't save individual files
        
        if result:
            # Extract quality metrics
            serve_metrics = result.get('serve_metrics', {})
            results_quality = serve_metrics.get('results_quality', {})
            quality_label = results_quality.get('results_quality_label', 'N/A')
            reasons = results_quality.get('reasons', []) or []  # Ensure it's a list
            
            # Store for summary
            results_summary.append({
                'query': query,
                'quality': quality_label,
                'reasons': reasons
            })
            
            # Count quality labels
            quality_counts[quality_label] = quality_counts.get(quality_label, 0) + 1
            
            # Count reasons for non-good results
            if quality_label != 'GOOD_RESULTS' and reasons:
                for reason in reasons:
                    reasons_counter[reason] = reasons_counter.get(reason, 0) + 1
            
            # Display some basic info about the response
            materials = result.get('items', {}).get('materials', [])
            print(f"📊 Results Quality: {quality_label}")
            if materials:
                print(f"📚 Materials returned: {len(materials)}")
        else:
            results_summary.append({
                'query': query,
                'quality': 'ERROR',
                'reasons': []
            })
            quality_counts['ERROR'] = quality_counts.get('ERROR', 0) + 1
        
        print("-" * 30)
    
    # Generate summary report
    _generate_summary_report(results_summary, quality_counts, reasons_counter)
    
    print("\n✨ API testing completed!")


def _generate_summary_report(results_summary, quality_counts, reasons_counter):
    """Generate a summary report file with query results analysis."""
    
    total_queries = len(results_summary)
    
    # Build report content
    report_lines = []
    report_lines.append("# Search Quality Assessment Report")
    report_lines.append("")
    report_lines.append("## Overall Results")
    report_lines.append("")
    report_lines.append("| Query | Quality |")
    report_lines.append("|-------|---------|")
    
    for item in results_summary:
        report_lines.append(f"| {item['query']} | {item['quality']} |")
    
    report_lines.append("")
    report_lines.append("## Quality Distribution")
    report_lines.append("")
    report_lines.append(f"**Total Queries:** {total_queries}")
    report_lines.append("")
    
    for quality_label, count in sorted(quality_counts.items()):
        percentage = (count / total_queries * 100) if total_queries > 0 else 0
        report_lines.append(f"- **{quality_label}:** {count} ({percentage:.1f}%)")
    
    report_lines.append("")
    report_lines.append("## Reasons for Non-Good Results")
    report_lines.append("")
    
    if reasons_counter:
        # Sort reasons by frequency
        sorted_reasons = sorted(reasons_counter.items(), key=lambda x: x[1], reverse=True)
        
        report_lines.append("| Reason | Count | Percentage |")
        report_lines.append("|--------|-------|------------|")
        
        # Count total non-good results
        non_good_total = sum(1 for item in results_summary if item['quality'] != 'GOOD_RESULTS')
        
        for reason, count in sorted_reasons:
            percentage = (count / non_good_total * 100) if non_good_total > 0 else 0
            report_lines.append(f"| {reason} | {count} | {percentage:.1f}% |")
        
        report_lines.append("")
        report_lines.append("### Queries by Reason")
        report_lines.append("")
        
        # Group queries by reasons
        for reason, _ in sorted_reasons:
            report_lines.append(f"#### {reason}")
            report_lines.append("")
            queries_with_reason = [item['query'] for item in results_summary 
                                  if item['reasons'] and reason in item['reasons']]
            for query in queries_with_reason:
                report_lines.append(f"- {query}")
            report_lines.append("")
    else:
        report_lines.append("*All queries returned good results!*")
        report_lines.append("")
    
    # Write report to file
    report_content = "\n".join(report_lines)
    report_filename = "search_quality_report.md"
    
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"\n📄 Summary report saved to: {report_filename}")
    
    # Also print summary to console
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print(f"Total Queries: {total_queries}")
    for quality_label, count in sorted(quality_counts.items()):
        percentage = (count / total_queries * 100) if total_queries > 0 else 0
        print(f"  {quality_label}: {count} ({percentage:.1f}%)")
    
    if reasons_counter:
        print("\nTop Reasons for Non-Good Results:")
        for reason, count in sorted(reasons_counter.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  - {reason}: {count}")
    print("=" * 50)

if __name__ == "__main__":
    main()
