import os
from db import get_mongodb_connection
from intents.service import call_intent_api
from query_tracking.service import store_search_query_mongodb, load_previous_searches_mongodb
from ltr.ranking_service import re_rank_search_results

def load_previous_searches():
    """Load previous search queries from MongoDB"""
    return load_previous_searches_mongodb(limit=100)

def store_search_query(query, result_count=0):
    """Store a successful search query to MongoDB"""
    store_search_query_mongodb(query, result_count)

def search_materials(query, page, limit):
    if not query:
        return {
            "results": [],
            "total": 0,
            "page": page,
            "limit": limit,
            "category_intents": [],
            "grade_intents": [],
            "search_boost_tooltip": ""
        }
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
        must_clauses = []
        should_clauses = [
            {"text": {"query": query, "path": "title", "score": {"boost": {"value": 8}}}},
            {"text": {"query": query, "path": "description", "score": {"boost": {"value": 2}}}},
            {"text": {"query": high_conf_category[0] if high_conf_category else query, "path": "category", "score": {"boost": {"value": category_boost}}}},
            {"text": {"query": query, "path": "grade_level", "score": {"boost": {"value": 2}}}},
            {"text": {"query": query, "path": "material_type", "score": {"boost": {"value": 2}}}},
            {"text": {"query": query, "path": "author_slug", "score": {"boost": {"value": 1}}}}
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
        
        # Store search query for tracking
        if total_count > 0:
            store_search_query(query, total_count)
        
        # Create search results dictionary
        search_results = {
            "results": results,
            "total": total_count,
            "page": page,
            "limit": limit,
            "category_intents": category_intents,
            "grade_intents": grade_intents,
            "search_boost_tooltip": boost_tooltip
        }
        
        # Apply LTR re-ranking
        try:
            re_ranked_results = re_rank_search_results(query, search_results)
            return re_ranked_results
        except Exception as e:
            print(f"Error in LTR re-ranking, using original results: {e}")
            return search_results
    finally:
        if 'client' in locals():
            client.close()

def get_material_by_id(material_id):
    try:
        client = get_mongodb_connection()
        db = client[os.getenv('DATABASE_NAME', 'materials_db')]
        collection = db[os.getenv('COLLECTION_NAME', 'materials')]
        material = collection.find_one({"material_id": material_id})
        if not material:
            return None
        material['_id'] = str(material['_id'])
        material['score'] = 10.0
        store_search_query(material['title'])
        return {
            "results": [material],
            "total": 1,
            "page": 1,
            "limit": 1,
            "category_intents": [],
            "grade_intents": [],
            "search_boost_tooltip": "Exact material match"
        }
    finally:
        if 'client' in locals():
            client.close()
