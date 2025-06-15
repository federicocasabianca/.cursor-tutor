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

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    return app

app = create_app()

def get_mongodb_connection():
    """Establish connection to MongoDB Atlas"""
    try:
        connection_string = os.getenv('MONGODB_URI')
        if not connection_string:
            raise ValueError("MongoDB connection string not found in environment variables")
        
        client = MongoClient(connection_string)
        client.admin.command('ping')
        print("Successfully connected to MongoDB!")
        return client
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        raise

def ensure_indexes(client):
    """Ensure all necessary indexes are created"""
    try:
        db = client[os.getenv('DATABASE_NAME', 'materials_db')]
        collection = db[os.getenv('COLLECTION_NAME', 'materials')]
        
        # Create all necessary indexes
        collection.create_index("material_id", unique=True)
        collection.create_index("author_slug")
        collection.create_index("category")
        collection.create_index("grade_level")
        collection.create_index("material_type")
        
        # Create text index for search
        # First, drop existing text index if it exists
        try:
            collection.drop_index("title_text_description_text_material_type_text_author_slug_text")
        except Exception:
            pass  # Index might not exist, which is fine
        
        # Create new text index
        collection.create_index([
            ("title", "text"),
            ("description", "text"),
            ("material_type", "text"),
            ("author_slug", "text")
        ], name="title_text_description_text_material_type_text_author_slug_text")
        
        print("Successfully created/updated all indexes")
    except Exception as e:
        print(f"Error creating indexes: {e}")
        raise

def load_materials_from_json(file_path: str) -> List[Dict[str, Any]]:
    """Load and transform materials from JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            raw_data = json.load(file)
            
        materials = []
        for item in raw_data:
            # Convert categories and grade_levels to arrays if they're strings
            categories = item.get("categories", "")
            if isinstance(categories, str):
                categories = [cat.strip() for cat in categories.split(",")] if categories else []
            
            grade_levels = item.get("class_grades", "")
            if isinstance(grade_levels, str):
                grade_levels = [grade.strip() for grade in grade_levels.split(",")] if grade_levels else []
            
            material = {
                "material_id": int(item.get("material_id", 0)),
                "title": str(item.get("material_title", "")),
                "description": str(item.get("description", "")),
                "category": categories,
                "grade_level": grade_levels,
                "price": float(item.get("price", 0.0)),
                "is_free": bool(item.get("is_free", False)),
                "material_type": str(item.get("material_types", "")),
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

@app.route('/search')
def search():
    query = request.args.get('q', '')
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 12))
    if not query:
        return jsonify([])
    
    try:
        client = get_mongodb_connection()
        db = client[os.getenv('DATABASE_NAME', 'materials_db')]
        collection = db[os.getenv('COLLECTION_NAME', 'materials')]
        
        # Create text search query
        search_query = {
            "$text": {
                "$search": query
            }
        }
        
        # Pagination
        skip = (page - 1) * limit
        cursor = collection.find(
            search_query,
            {"score": {"$meta": "textScore"}}
        ).sort([("score", {"$meta": "textScore"})]).skip(skip).limit(limit)
        results = list(cursor)
        
        # Get total count for this query
        total_count = collection.count_documents(search_query)
        
        # Convert ObjectId to string for JSON serialization
        for result in results:
            result['_id'] = str(result['_id'])
            result['score'] = round(result['score'], 2)
        
        return jsonify({
            "results": results,
            "total": total_count,
            "page": page,
            "limit": limit
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if 'client' in locals():
            client.close()

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
    'category': 'search-mongodb/taxonomy/taxonomy_categories.csv',
    'grade_level': 'search-mongodb/taxonomy/taxonomy_grade_levels.csv',
    'material_type': 'search-mongodb/taxonomy/taxonomy_material_type.csv',
    'school_type': 'search-mongodb/taxonomy/taxonomy_school_types.csv',
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

def detect_intents_spacy(query):
    doc = nlp(query)
    detected = set()
    for intent, matcher in PHRASE_MATCHERS.items():
        matches = matcher(doc)
        if matches:
            detected.add(intent)
    return list(detected)

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