#!/usr/bin/env python3
"""
Vector API Request Script for Eduki Search Service
Replicates the logic from api_request.py but targets the vector search endpoint.
"""

import json
import re
import urllib.parse
from pathlib import Path

import requests


class EdukiVectorSearchAPI:
    def __init__(self, bearer_token_file="bearer_token.txt"):
        """Initialize the API client with bearer token."""
        self.base_url = "https://vector.api.eduki.info/api/v3/search/materials"
        self.bearer_token = self._load_bearer_token(bearer_token_file)
        self.headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _load_bearer_token(self, token_file):
        """Load bearer token from file."""
        try:
            with open(token_file, "r", encoding="utf-8") as f:
                return f.read().strip()
        except FileNotFoundError as exc:
            raise FileNotFoundError(f"Bearer token file '{token_file}' not found") from exc

    def _decode_query(self, encoded_query):
        """Decode URL-encoded query string."""
        return urllib.parse.unquote_plus(encoded_query)

    def make_request(
        self,
        query,
        limit=36,
        world="de",
        metrics=True,
        vector=True,
        save_response=True,
    ):
        """
        Make API request for given query using the vector endpoint.

        Args:
            query (str): Search query (can be URL encoded)
            limit (int): Number of materials to request
            world (str): Region/world parameter
            metrics (bool): Whether to request metrics data
            vector (bool): Whether to request vector data
            save_response (bool): Whether to save trimmed response to JSON file

        Returns:
            dict: Trimmed API response data
        """
        decoded_query = self._decode_query(query)
        print(f"Making vector request for query: '{decoded_query}'")

        params = {
            "limit": limit,
            "q": decoded_query.replace(" ", "%20"),
            "world": world,
            "metrics": str(metrics).lower(),
            "vector": str(vector).lower(),
        }

        print("Debug - Vector request parameters:")
        for key, value in params.items():
            print(f"  {key}: {value}")

        payload = {
            "page_context": "main",
            "auto_suggest": True,
        }

        try:
            response = requests.post(
                self.base_url,
                params=params,
                json=payload,
                headers=self.headers,
                timeout=30,
            )
            response.raise_for_status()

            response_data = response.json()
            trimmed_response = self._build_trimmed_response(decoded_query, response_data)

            materials_count = len(trimmed_response.get("materials", []))
            print(f"✅ Vector request successful! Materials returned: {materials_count}")

            if save_response:
                filename = "results.json"
                self._save_response(trimmed_response, filename)
                print(f"💾 Trimmed vector response saved to: {filename}")

            print(json.dumps(trimmed_response, indent=2, ensure_ascii=False))
            return trimmed_response

        except requests.exceptions.RequestException as exc:
            print(f"❌ Vector request failed: {exc}")
            if getattr(exc, "response", None) is not None:
                print(f"Status Code: {exc.response.status_code}")
                print(f"Response: {exc.response.text}")
            return None

    def _build_trimmed_response(self, query, response_data):
        """Build a response limited to the requested material fields."""
        materials = response_data.get("items", {}).get("materials", [])

        trimmed_materials = []
        for material in materials:
            trimmed_materials.append(
                {
                    "id": material.get("id"),
                    "title": material.get("title"),
                    "_score": material.get("_score"),
                    "material_categories": material.get("material_categories", []),
                }
            )

        return {
            "query": query,
            "materials": trimmed_materials,
        }

    def _save_response(self, data, filename):
        """Save trimmed response data to JSON file."""
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except OSError as exc:
            print(f"❌ Failed to save response: {exc}")


def main():
    """Main function to test vector API requests."""
    print("🚀 Starting Eduki Vector Search API Tests")
    print("=" * 50)

    token_path = Path(__file__).with_name("bearer_token.txt")
    try:
        api = EdukiVectorSearchAPI(bearer_token_file=str(token_path))
        print("✅ Vector API client initialized successfully")
    except Exception as exc:
        print(f"❌ Failed to initialize vector API client: {exc}")
        return

    test_queries = [
        "spielzeug kostenlos",
    ]

    for query in test_queries:
        api.make_request(query, save_response=True)
        print("-" * 30)

    print("\n✨ Vector API testing completed!")


if __name__ == "__main__":
    main()


