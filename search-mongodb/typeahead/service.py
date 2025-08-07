import os
import requests
from urllib.parse import quote
from utils.highlight import find_highlight_positions

def get_typeahead_suggestions(query):
    try:
        if not query:
            # Return empty list for empty query - let the frontend handle this
            return []
        
        # Prepare the API call
        base_url = "https://suggestion.api.eduki.info/api/v3/suggest/prefix"
        encoded_query = quote(query)
        world = os.getenv('SUGGEST_WORLD', 'de')  # Default to 'de' if not specified
        
        url = f"{base_url}?term={encoded_query}&world={world}"
        
        # Make the API request
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        
        suggestions_data = response.json()
        
        # Transform the API response to match our expected format
        suggestions = []
        for item in suggestions_data:
            suggestion = {
                "text": item["query"],
                "type": item["type"],
                "id": item["metadata"].get("id", item["query"]),
                "score": 0,  # API doesn't provide scores, so we default to 0
                "search_score": 0,
                "highlight_start": 0,
                "highlight_end": 0,
                "metadata": item["metadata"]  # Keep the original metadata
            }
            
            # Calculate highlight positions if the query matches
            if query.lower() in item["query"].lower():
                highlight_start, highlight_end = find_highlight_positions(item["query"], query)
                suggestion["highlight_start"] = highlight_start
                suggestion["highlight_end"] = highlight_end
            
            suggestions.append(suggestion)
        
        # If no suggestions from API, return the user's query as a search suggestion
        if not suggestions:
            return [{
                "text": query,
                "type": "query",
                "id": query,
                "score": 0,
                "search_score": 0,
                "highlight_start": 0,
                "highlight_end": len(query),
                "metadata": {}
            }]
        
        # Limit to 10 suggestions
        return suggestions[:10]
        
    except requests.RequestException as e:
        print(f"API request error: {e}")
        # Fallback: return the user's query as a search suggestion
        return [{
            "text": query,
            "type": "query",
            "id": query,
            "score": 0,
            "search_score": 0,
            "highlight_start": 0,
            "highlight_end": len(query),
            "metadata": {}
        }]
    except Exception as e:
        print(f"Typeahead error: {e}")
        return []
