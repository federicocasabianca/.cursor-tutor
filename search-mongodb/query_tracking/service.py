import os
from datetime import datetime
from typing import List, Dict, Any, Tuple
from db import get_mongodb_connection

def classify_query_generic_specific(query: str) -> str:
    """
    Classify a query as generic or specific.
    This is a placeholder implementation - you can enhance this later with more sophisticated logic.
    
    For now, we'll use simple heuristics:
    - Generic: 1-2 words, common terms
    - Specific: 3+ words or contains specific identifiers
    """
    query = query.strip().lower()
    words = query.split()
    
    # Simple heuristics for now
    if len(words) <= 2:
        return "generic"
    else:
        return "specific"

def store_search_query_mongodb(query: str, result_count: int = 0, user_id: str = "system", device: str = "web"):
    """
    Store a search query in MongoDB with generic/specific classification.
    Uses upsert to update existing queries or create new ones.
    """
    try:
        client = get_mongodb_connection()
        db = client[os.getenv('DATABASE_NAME', 'materials_db')]
        collection = db['search_queries']
        
        # Classify the query
        query_type = classify_query_generic_specific(query)
        
        # Prepare the document
        query_doc = {
            "query": query.strip(),
            "query_type": query_type,  # "generic" or "specific"
            "user_id": user_id,
            "device": device,
            "last_search_date": datetime.utcnow(),
            "result_count": result_count
        }
        
        # Use upsert to update existing or create new
        result = collection.update_one(
            {"query": query.strip()},
            {
                "$inc": {"search_frequency": 1},
                "$set": {
                    "query_type": query_type,
                    "last_search_date": datetime.utcnow(),
                    "result_count": result_count
                },
                "$setOnInsert": {
                    "first_search_date": datetime.utcnow(),
                    "user_id": user_id,
                    "device": device
                }
            },
            upsert=True
        )
        
        print(f"Query tracking: {'Updated' if result.modified_count > 0 else 'Inserted'} query '{query}' (type: {query_type})")
        
    except Exception as e:
        print(f"Error storing search query in MongoDB: {e}")
    finally:
        if 'client' in locals():
            client.close()

def load_previous_searches_mongodb(limit: int = 100) -> List[Tuple[str, int]]:
    """
    Load previous search queries from MongoDB, sorted by frequency.
    Returns list of (query, frequency) tuples.
    """
    try:
        client = get_mongodb_connection()
        db = client[os.getenv('DATABASE_NAME', 'materials_db')]
        collection = db['search_queries']
        
        # Get queries sorted by frequency (descending)
        pipeline = [
            {"$sort": {"search_frequency": -1}},
            {"$limit": limit},
            {"$project": {"query": 1, "search_frequency": 1}}
        ]
        
        results = list(collection.aggregate(pipeline))
        search_list = [(doc['query'], doc['search_frequency']) for doc in results]
        
        return search_list
        
    except Exception as e:
        print(f"Error loading previous searches from MongoDB: {e}")
        return []
    finally:
        if 'client' in locals():
            client.close()

def get_query_statistics() -> Dict[str, Any]:
    """
    Get statistics about stored queries.
    """
    try:
        client = get_mongodb_connection()
        db = client[os.getenv('DATABASE_NAME', 'materials_db')]
        collection = db['search_queries']
        
        # Get total queries
        total_queries = collection.count_documents({})
        
        # Get generic vs specific breakdown
        generic_count = collection.count_documents({"query_type": "generic"})
        specific_count = collection.count_documents({"query_type": "specific"})
        
        # Get most frequent queries
        most_frequent = list(collection.find().sort("search_frequency", -1).limit(10))
        
        # Get recent queries
        recent_queries = list(collection.find().sort("last_search_date", -1).limit(10))
        
        return {
            "total_queries": total_queries,
            "generic_queries": generic_count,
            "specific_queries": specific_count,
            "most_frequent": most_frequent,
            "recent_queries": recent_queries
        }
        
    except Exception as e:
        print(f"Error getting query statistics: {e}")
        return {}
    finally:
        if 'client' in locals():
            client.close()

def ensure_query_tracking_indexes(client):
    """
    Ensure necessary indexes exist for query tracking collection.
    """
    try:
        db = client[os.getenv('DATABASE_NAME', 'materials_db')]
        collection = db['search_queries']
        
        # Create indexes for efficient querying
        collection.create_index("query", unique=True)
        collection.create_index("query_type")
        collection.create_index("search_frequency")
        collection.create_index("last_search_date")
        collection.create_index("user_id")
        
        print("Successfully created/updated query tracking indexes")
        
    except Exception as e:
        print(f"Error creating query tracking indexes: {e}")
        raise 