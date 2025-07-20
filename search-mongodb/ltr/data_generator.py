import os
import json
import random
from typing import List, Dict, Any, Tuple
from db import get_mongodb_connection
from query_tracking.service import load_previous_searches_mongodb
from feature_engineering import generate_synthetic_labels
from search.service import search_materials

# Label mapping
ACTION_LABELS = {
    "appearedInSearch": 1,
    "viewMaterial": 2,
    "showMaterialPreview": 3,
    "addToFavorites": 4,
    "freeDownload": 4,
    "addToCart": 5,
    "purchased": 6
}

# Synthetic funnel rates (cumulative, not exclusive)
FUNNEL_RATES = [
    ("purchased", 0.071),
    ("addToCart", 0.10),
    ("freeDownload", 0.50),
    ("addToFavorites", 0.15),
    ("showMaterialPreview", 0.20),
    ("viewMaterial", 0.80),
    ("appearedInSearch", 1.0)
]

def pick_action(is_free):
    r = random.random()
    cumulative = 0.0
    for action, rate in FUNNEL_RATES:
        if action == "freeDownload" and not is_free:
            continue
        cumulative += rate
        if r < cumulative:
            return action
    return "appearedInSearch"

class TrainingDataGenerator:
    """Generate training data for Learning-to-Rank model"""
    
    def __init__(self, max_documents_per_query: int = 100):
        self.max_documents_per_query = max_documents_per_query
        
    def load_search_queries(self) -> List[Tuple[str, int]]:
        try:
            queries = load_previous_searches_mongodb(limit=1000)
            print(f"Loaded {len(queries)} search queries")
            return queries
        except Exception as e:
            print(f"Error loading search queries: {e}")
            return []
    
    def simulate_search_results(self, query: str) -> List[Tuple[Dict[str, Any], float]]:
        try:
            result = search_materials(query, page=1, limit=self.max_documents_per_query)
            documents = result.get('results', [])
            doc_score_pairs = []
            for doc in documents:
                score = doc.get('score', 0.0)
                doc_score_pairs.append((doc, score))
            return doc_score_pairs
        except Exception as e:
            print(f"Error simulating search for query '{query}': {e}")
            return []

    def generate_training_data(self, min_queries: int = 100) -> List[Dict]:
        print("Generating synthetic, balanced training data...")
        queries = self.load_search_queries()
        if len(queries) < min_queries:
            print(f"Warning: Only {len(queries)} queries available, minimum requested: {min_queries}")
        training_data = []
        processed_queries = 0
        for query, _ in queries[:min_queries]:
            doc_score_pairs = self.simulate_search_results(query)
            if not doc_score_pairs:
                continue
            for document, mongodb_score in doc_score_pairs:
                user_id = f"user_{random.randint(1, 1000)}"
                # Synthetic user preferences: match if any overlap
                user_cat_pref = int(any(cat in document.get("category", []) for cat in ["Mathematik", "Deutsch"]))
                user_grade_pref = int(any(grade in document.get("grade_level", []) for grade in ["3. Klasse", "4. Klasse"]))
                is_free = document.get("is_free", False)
                action = pick_action(is_free)
                label = ACTION_LABELS[action]
                training_data.append({
                    "query": query,
                    "user_id": user_id,
                    "document": document,
                    "mongodb_score": mongodb_score,
                    "label": label,
                    "user_cat_pref": user_cat_pref,
                    "user_grade_pref": user_grade_pref
                })
            processed_queries += 1
        print(f"Generated {len(training_data)} training examples from {processed_queries} queries")
        return training_data

    def save_training_data(self, training_data: List[Dict], filename: str = 'training_data.json'):
        os.makedirs('data', exist_ok=True)
        with open(f'data/{filename}', 'w', encoding='utf-8') as f:
            json.dump(training_data, f, indent=2, ensure_ascii=False)
        print(f"Training data saved to data/{filename}")

    def load_training_data(self, filename: str = 'training_data.json') -> List[Dict]:
        filepath = f'data/{filename}'
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Training data file not found: {filepath}")
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"Loaded {len(data)} training examples from {filepath}")
        return data

def main():
    generator = TrainingDataGenerator(max_documents_per_query=100)
    training_data = generator.generate_training_data(min_queries=50)
    generator.save_training_data(training_data)
    print(f"Training data generation completed. Generated {len(training_data)} examples.")

if __name__ == "__main__":
    main() 