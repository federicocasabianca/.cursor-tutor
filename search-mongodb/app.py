from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import json
from datetime import datetime
from typing import List, Dict, Any
from bson import json_util
import re
import spacy
from spacy.matcher import PhraseMatcher
import csv
import requests
from db import get_mongodb_connection, ensure_indexes
from search.routes import search_bp
from typeahead.routes import typeahead_bp
from intents.service import call_intent_api, detect_intents_spacy

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    return app

app = create_app()
app.register_blueprint(search_bp)
app.register_blueprint(typeahead_bp)

def load_materials_from_json(file_path: str) -> List[Dict[str, Any]]:
    """Load and transform materials from JSON file with proper field mapping and array conversion."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            raw_data = json.load(file)
        materials = []
        for item in raw_data:
            # Always convert to arrays
            categories = item.get("categories", "")
            if isinstance(categories, str):
                categories = [cat.strip() for cat in categories.split(",") if cat.strip()]
            elif not isinstance(categories, list):
                categories = []

            grade_levels = item.get("class_grades", "")
            if isinstance(grade_levels, str):
                grade_levels = [grade.strip() for grade in grade_levels.split(",") if grade.strip()]
            elif not isinstance(grade_levels, list):
                grade_levels = []

            material_types = item.get("material_types", "")
            if isinstance(material_types, str):
                material_types = [typ.strip() for typ in material_types.split(",") if typ.strip()]
            elif not isinstance(material_types, list):
                material_types = []

            material = {
                "material_id": int(item.get("material_id", 0)),
                "title": str(item.get("material_title", "")),
                "description": str(item.get("description", "")),
                "category": categories,
                "grade_level": grade_levels,
                "price": float(item.get("price", 0.0)),
                "is_free": bool(item.get("is_free", False)),
                "material_type": material_types,
                "bestseller_rating": float(item.get("bestseller_rating", 0.0)),
                "is_bundle": bool(item.get("is_bundle", False)),
                "author_slug": str(item.get("author_slug", "")),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            materials.append(material)
        print(f"Successfully loaded {len(materials)} materials from JSON")
        return materials
    except Exception as e:
        print(f"Error loading materials from JSON: {e}")
        raise

def insert_documents(client, database_name: str, collection_name: str, documents: List[Dict[str, Any]]) -> List[str]:
    """Insert documents into specified collection"""
    try:
        db = client[database_name]
        collection = db[collection_name]
        
        if isinstance(documents, list):
            result = collection.insert_many(documents, ordered=False)
            print(f"Successfully inserted {len(result.inserted_ids)} documents")
            return result.inserted_ids
        else:
            result = collection.insert_one(documents)
            print(f"Successfully inserted document with id: {result.inserted_id}")
            return [result.inserted_id]
    except Exception as e:
        print(f"Error inserting documents: {e}")
        raise

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/insert', methods=['POST'])
def insert_materials():
    try:
        client = get_mongodb_connection()
        materials = load_materials_from_json('dataset.json')
        inserted_ids = insert_documents(
            client,
            os.getenv('DATABASE_NAME', 'materials_db'),
            os.getenv('COLLECTION_NAME', 'materials'),
            materials
        )
        return jsonify({"message": f"Successfully inserted {len(inserted_ids)} materials"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if 'client' in locals():
            client.close()

# Load spaCy German model
nlp = spacy.load('de_core_news_sm')

# Taxonomy file paths
TAXONOMY_PATHS = {
    'category': './taxonomy/taxonomy_categories.csv',
    'grade_level': './taxonomy/taxonomy_grade_levels.csv',
    'material_type': './taxonomy/taxonomy_material_type.csv',
    'school_type': './taxonomy/taxonomy_school_types.csv',
}

def load_taxonomy_terms():
    taxonomy_terms = {}
    for intent, path in TAXONOMY_PATHS.items():
        terms = set()
        try:
            with open(path, encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if row:
                        terms.add(row[0].strip())
        except Exception as e:
            print(f"Error loading taxonomy for {intent}: {e}")
        taxonomy_terms[intent] = list(terms)
    return taxonomy_terms

TAXONOMY_TERMS = load_taxonomy_terms()

# Setup PhraseMatchers for each intent
PHRASE_MATCHERS = {}
for intent, terms in TAXONOMY_TERMS.items():
    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    patterns = [nlp.make_doc(term) for term in terms if term]
    if patterns:
        matcher.add(intent, patterns)
    PHRASE_MATCHERS[intent] = matcher

def load_previous_searches():
    """Load previous search queries from searches.json"""
    try:
        with open('searches/searches.json', 'r', encoding='utf-8') as file:
            searches = json.load(file)
        
        # Aggregate search queries by frequency
        search_freq = {}
        for search in searches:
            keyword = search.get('search_keyword', '').strip()
            if keyword:
                freq = int(search.get('search_frequency', 1))
                if keyword in search_freq:
                    search_freq[keyword] += freq
                else:
                    search_freq[keyword] = freq
        
        # Convert to list of (query, frequency) tuples, sorted by frequency
        search_list = [(query, freq) for query, freq in search_freq.items()]
        search_list.sort(key=lambda x: x[1], reverse=True)
        return search_list
    except Exception as e:
        print(f"Error loading previous searches: {e}")
        return []

def store_search_query(query):
    """Store a successful search query to searches.json"""
    try:
        # Load existing searches
        searches = []
        try:
            with open('searches/searches.json', 'r', encoding='utf-8') as file:
                searches = json.load(file)
        except FileNotFoundError:
            searches = []
        
        # Check if query already exists
        query_exists = False
        for search in searches:
            if search.get('search_keyword', '').strip() == query.strip():
                # Update frequency and last search date
                current_freq = int(search.get('search_frequency', 1))
                search['search_frequency'] = str(current_freq + 1)
                search['last_search_date'] = datetime.now().strftime('%Y-%m-%d')
                query_exists = True
                break
        
        # If query doesn't exist, add new entry
        if not query_exists:
            new_search = {
                "user_id": "system",
                "search_keyword": query.strip(),
                "search_frequency": "1",
                "first_search_date": datetime.now().strftime('%Y-%m-%d'),
                "last_search_date": datetime.now().strftime('%Y-%m-%d'),
                "devices_used": "web"
            }
            searches.append(new_search)
        
        # Save back to file
        with open('searches/searches.json', 'w', encoding='utf-8') as file:
            json.dump(searches, file, indent=2, ensure_ascii=False)
            
    except Exception as e:
        print(f"Error storing search query: {e}")

if __name__ == '__main__':
    # Create indexes immediately when starting the application
    try:
        client = get_mongodb_connection()
        ensure_indexes(client)
    except Exception as e:
        print(f"Error creating initial indexes: {e}")
    finally:
        if 'client' in locals():
            client.close()
    
    app.run(debug=True) 