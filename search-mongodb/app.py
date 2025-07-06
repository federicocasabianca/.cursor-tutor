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
        
        # Note: For Atlas Search, you need to create a search index in the MongoDB Atlas UI
        # The search index should include these fields:
        # - title (text)
        # - description (text)
        # - category (text)
        # - grade_level (text)
        # - material_type (text)
        # - author_slug (text)
        # - bestseller_rating (number)
        # - material_id (number)
        print("Note: Ensure you have created a 'search_index' in MongoDB Atlas with the required fields")
        
        print("Successfully created/updated all indexes")
    except Exception as e:
        print(f"Error creating indexes: {e}")
        raise

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

def call_intent_api(query: str):
    """Call the external intent detection API and return detected categories and grade levels with confidence."""
    url = "https://srch-main.api.eduki.info/api/v3/query-intent/predict"
    headers = {"Content-Type": "application/json"}
    payload = {"text": query}
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=3)
        response.raise_for_status()
        result = response.json()
        # result['tags'] should have 'category' and 'grade' as lists of (name, confidence)
        return result.get('tags', {})
    except Exception as e:
        print(f"Intent API error: {e}")
        return {}

@app.route('/search')
def search():
    query = request.args.get('q', '')
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 14))
    if not query:
        return jsonify([])

    try:
        client = get_mongodb_connection()
        db = client[os.getenv('DATABASE_NAME', 'materials_db')]
        collection = db[os.getenv('COLLECTION_NAME', 'materials')]

        # Call intent detection service
        category_intents = []
        grade_intents = []
        try:
            tags = call_intent_api(query)
            category_intents = tags.get('category', []) if isinstance(tags, dict) else []
            grade_intents = tags.get('grade', []) if isinstance(tags, dict) else []
        except Exception as e:
            category_intents = []
            grade_intents = []

        # Determine category boost and tooltip
        category_boost = 5
        boost_tooltip = "Category field uses default boost (5). "
        high_conf_category = None
        high_conf_category_raw = None
        for cat, conf in category_intents:
            if conf > 0.95:
                high_conf_category_raw = cat
                # Use only the top-level category if path-like
                top_level_cat = cat.split('->')[0].strip() if '->' in cat else cat
                high_conf_category = (top_level_cat, conf, cat)
                break
        if high_conf_category:
            category_boost = 7
            boost_tooltip = f"Category field uses high boost (7) because intent '{high_conf_category[2]}' (using top-level '{high_conf_category[0]}') was detected with confidence {high_conf_category[1]*100:.1f}%. "
        else:
            if category_intents:
                boost_tooltip += "Intent detected but confidence is 95% or lower. "
            else:
                boost_tooltip += "No category intent detected. "

        # Leave must_clauses empty for future use
        must_clauses = []
        should_clauses = [
            {
                "text": {
                    "query": query,
                    "path": "title",
                    "score": {"boost": {"value": 8}}
                }
            },
            {
                "text": {
                    "query": query,
                    "path": "description",
                    "score": {"boost": {"value": 2}}
                }
            },
            {
                "text": {
                    "query": high_conf_category[0] if high_conf_category else query,
                    "path": "category",
                    "score": {"boost": {"value": category_boost}}
                }
            },
            {
                "text": {
                    "query": query,
                    "path": "grade_level",
                    "score": {"boost": {"value": 2}}
                }
            },
            {
                "text": {
                    "query": query,
                    "path": "material_type",
                    "score": {"boost": {"value": 2}}
                }
            },
            {
                "text": {
                    "query": query,
                    "path": "author_slug",
                    "score": {"boost": {"value": 1}}
                }
            }
        ]
        minimum_should = 2

        search_stage = {
            "$search": {
                "index": "search_index",
                "compound": {
                    "must": must_clauses,
                    "should": should_clauses,
                    "minimumShouldMatch": minimum_should
                }
            }
        }
        pipeline = [
            search_stage,
            {"$addFields": {"score": {"$meta": "searchScore"}}},
            {"$sort": {"score": -1}},
            {"$skip": (page - 1) * limit},
            {"$limit": limit}
        ]
        results = list(collection.aggregate(pipeline))
        total_count_pipeline = [search_stage, {"$count": "count"}]
        count_result = list(collection.aggregate(total_count_pipeline))
        total_count = count_result[0]["count"] if count_result else 0
        for result in results:
            result['_id'] = str(result['_id'])
            result['score'] = round(result.get('score', 0), 2)
        # Store successful search if results were found
        if total_count > 0:
            store_search_query(query)
        
        return jsonify({
            "results": results,
            "total": total_count,
            "page": page,
            "limit": limit,
            "category_intents": category_intents,
            "grade_intents": grade_intents,
            "search_boost_tooltip": boost_tooltip
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

def detect_intents_spacy(query):
    doc = nlp(query)
    detected = set()
    for intent, matcher in PHRASE_MATCHERS.items():
        matches = matcher(doc)
        if matches:
            detected.add(intent)
    return list(detected)

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

@app.route('/typeahead')
def typeahead():
    query = request.args.get('q', '').strip()
    
    try:
        client = get_mongodb_connection()
        db = client[os.getenv('DATABASE_NAME', 'materials_db')]
        collection = db[os.getenv('COLLECTION_NAME', 'materials')]
        
        # Collect all suggestions by type
        materials = []
        authors = []
        queries = []
        
        # Handle empty query - show most frequent searches
        if not query:
            previous_searches = load_previous_searches()
            for search_query, frequency in previous_searches[:10]:  # Top 10 most frequent
                queries.append({
                    "text": search_query,
                    "type": "query",
                    "id": search_query,
                    "score": frequency,
                    "search_score": 0,
                    "highlight_start": 0,
                    "highlight_end": 0
                })
            
            # Return only frequent queries for empty input
            return jsonify(queries[:10])
        
        # For non-empty queries, proceed with normal search
        # 1. Search for materials (titles) - get more than needed for balancing
        material_pipeline = [
            {
                "$search": {
                    "index": "search_index",
                    "text": {
                        "query": query,
                        "path": "title",
                        "fuzzy": {"maxEdits": 1}
                    }
                }
            },
            {"$addFields": {"score": {"$meta": "searchScore"}}},
            {"$addFields": {"bestseller_rating": {"$ifNull": ["$bestseller_rating", 0]}}},
            {"$sort": {"bestseller_rating": -1, "title": 1}},
            {"$limit": 10},  # Get more for balancing
            {
                "$project": {
                    "title": 1,
                    "material_id": 1,
                    "bestseller_rating": 1,
                    "score": 1
                }
            }
        ]
        
        material_results = list(collection.aggregate(material_pipeline))
        for material in material_results:
            # Calculate highlight positions for material titles
            title = material['title']
            highlight_start, highlight_end = find_highlight_positions(title, query)
            
            materials.append({
                "text": title,
                "type": "material",
                "id": material['material_id'],
                "score": material.get('bestseller_rating', 0),
                "search_score": material.get('score', 0),
                "highlight_start": highlight_start,
                "highlight_end": highlight_end
            })
        
        # 2. Search for authors - get more than needed for balancing
        author_pipeline = [
            {
                "$search": {
                    "index": "search_index",
                    "text": {
                        "query": query,
                        "path": "author_slug",
                        "fuzzy": {"maxEdits": 1}
                    }
                }
            },
            {"$group": {"_id": "$author_slug"}},
            {"$sort": {"_id": 1}},
            {"$limit": 10}  # Get more for balancing
        ]
        
        author_results = list(collection.aggregate(author_pipeline))
        for author in author_results:
            # Calculate highlight positions for author names
            author_name = author['_id']
            highlight_start, highlight_end = find_highlight_positions(author_name, query)
            
            authors.append({
                "text": author_name,
                "type": "author",
                "id": author_name,
                "score": 0,  # Authors ranked alphabetically
                "search_score": 0,
                "highlight_start": highlight_start,
                "highlight_end": highlight_end
            })
        
        # 3. Search for previous queries - get more than needed for balancing
        previous_searches = load_previous_searches()
        for search_query, frequency in previous_searches:
            if query.lower() in search_query.lower():
                # Calculate highlight positions for search queries
                highlight_start, highlight_end = find_highlight_positions(search_query, query)
                
                queries.append({
                    "text": search_query,
                    "type": "query",
                    "id": search_query,
                    "score": frequency,
                    "search_score": 0,
                    "highlight_start": highlight_start,
                    "highlight_end": highlight_end
                })
                if len(queries) >= 10:  # Get more for balancing
                    break
        
        # 4. Add the typed query as a fallback if no matches found
        if not materials and not authors and not queries:
            return jsonify([{
                "text": query,
                "type": "query",
                "id": query,
                "score": 0,
                "search_score": 0,
                "highlight_start": 0,
                "highlight_end": len(query)
            }])
        
        # 5. Dynamic balancing algorithm (same as before)
        def balance_suggestions(materials, authors, queries, target_total=10):
            """Dynamically balance suggestions to reach target_total"""
            available_types = []
            if materials:
                available_types.append('material')
            if authors:
                available_types.append('author')
            if queries:
                available_types.append('query')
            
            if not available_types:
                return []
            
            # Calculate base distribution based on available types
            if len(available_types) == 1:
                # Only one type available - use all available slots
                if available_types[0] == 'material':
                    return materials[:target_total]
                elif available_types[0] == 'author':
                    return authors[:target_total]
                else:  # query
                    return queries[:target_total]
            
            elif len(available_types) == 2:
                # Two types available - adjust 70/20/10 ratio
                if 'query' in available_types and 'material' in available_types:
                    # Queries get 70%, materials get 30%
                    query_count = min(7, len(queries))
                    material_count = min(target_total - query_count, len(materials))
                    return queries[:query_count] + materials[:material_count]
                
                elif 'query' in available_types and 'author' in available_types:
                    # Queries get 80%, authors get 20%
                    query_count = min(8, len(queries))
                    author_count = min(target_total - query_count, len(authors))
                    return queries[:query_count] + authors[:author_count]
                
                elif 'material' in available_types and 'author' in available_types:
                    # Materials get 80%, authors get 20%
                    material_count = min(8, len(materials))
                    author_count = min(target_total - material_count, len(authors))
                    return materials[:material_count] + authors[:author_count]
            
            else:
                # All three types available - use standard 70/20/10 ratio
                query_count = min(7, len(queries))
                material_count = min(2, len(materials))
                author_count = min(1, len(authors))
                
                # If we have room, distribute remaining slots
                remaining = target_total - query_count - material_count - author_count
                if remaining > 0:
                    if len(materials) > material_count:
                        material_count += min(remaining // 2, len(materials) - material_count)
                        remaining -= min(remaining // 2, len(materials) - material_count)
                    if remaining > 0 and len(authors) > author_count:
                        author_count += min(remaining, len(authors) - author_count)
                
                return queries[:query_count] + materials[:material_count] + authors[:author_count]
        
        # 6. Apply dynamic balancing
        balanced_suggestions = balance_suggestions(materials, authors, queries, 10)
        
        # 7. Sort within each type and apply final ranking
        def calculate_priority(suggestion):
            base_score = 0
            
            # Type-based priority (adjusted for dynamic balancing)
            if suggestion['type'] == 'query':
                base_score = 70
            elif suggestion['type'] == 'material':
                base_score = 20
            elif suggestion['type'] == 'author':
                base_score = 10
            
            # Boost by individual scores
            if suggestion['type'] == 'material':
                # Normalize bestseller rating (0-5 scale) to 0-100
                base_score += (suggestion['score'] / 5) * 20
            elif suggestion['type'] == 'query':
                # Boost by frequency (normalize to reasonable range)
                base_score += min(suggestion['score'] * 2, 30)
            
            # Boost by search relevance score
            base_score += suggestion['search_score'] * 10
            
            return base_score
        
        # Sort by priority and ensure we have exactly 10 (or fewer if not enough available)
        balanced_suggestions.sort(key=calculate_priority, reverse=True)
        final_suggestions = balanced_suggestions[:10]
        
        return jsonify(final_suggestions)
        
    except Exception as e:
        print(f"Typeahead error: {e}")
        return jsonify([])
    finally:
        if 'client' in locals():
            client.close()

def find_highlight_positions(text, query):
    """Find the start and end positions for highlighting matching text"""
    if not query or not text:
        return 0, 0
    
    text_lower = text.lower()
    query_lower = query.lower()
    
    # Find the first occurrence of the query in the text
    start_pos = text_lower.find(query_lower)
    if start_pos == -1:
        # If exact match not found, try to find partial matches
        query_words = query_lower.split()
        for word in query_words:
            if len(word) >= 2:  # Only consider words with 2+ characters
                word_pos = text_lower.find(word)
                if word_pos != -1:
                    start_pos = word_pos
                    end_pos = word_pos + len(word)
                    return start_pos, end_pos
        
        # If no partial matches found, return 0, 0
        return 0, 0
    
    end_pos = start_pos + len(query)
    return start_pos, end_pos

@app.route('/search/material/<int:material_id>')
def search_material_by_id(material_id):
    """Search for a specific material by ID"""
    try:
        client = get_mongodb_connection()
        db = client[os.getenv('DATABASE_NAME', 'materials_db')]
        collection = db[os.getenv('COLLECTION_NAME', 'materials')]
        
        # Find the specific material
        material = collection.find_one({"material_id": material_id})
        
        if not material:
            return jsonify({"error": "Material not found"}), 404
        
        # Convert ObjectId to string for JSON serialization
        material['_id'] = str(material['_id'])
        material['score'] = 10.0  # High score for exact match
        
        # Store the search query (material title)
        store_search_query(material['title'])
        
        return jsonify({
            "results": [material],
            "total": 1,
            "page": 1,
            "limit": 1,
            "category_intents": [],
            "grade_intents": [],
            "search_boost_tooltip": "Exact material match"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if 'client' in locals():
            client.close()

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