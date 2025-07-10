import os
from db import get_mongodb_connection
from search.service import load_previous_searches
from utils.highlight import find_highlight_positions

def get_typeahead_suggestions(query):
    try:
        client = get_mongodb_connection()
        db = client[os.getenv('DATABASE_NAME', 'materials_db')]
        collection = db[os.getenv('COLLECTION_NAME', 'materials')]
        materials = []
        authors = []
        queries = []
        if not query:
            previous_searches = load_previous_searches()
            for search_query, frequency in previous_searches[:10]:
                queries.append({
                    "text": search_query,
                    "type": "query",
                    "id": search_query,
                    "score": frequency,
                    "search_score": 0,
                    "highlight_start": 0,
                    "highlight_end": 0
                })
            return queries[:10]
        material_pipeline = [
            {"$search": {"index": "search_index", "text": {"query": query, "path": "title", "fuzzy": {"maxEdits": 1}}}},
            {"$addFields": {"score": {"$meta": "searchScore"}}},
            {"$addFields": {"bestseller_rating": {"$ifNull": ["$bestseller_rating", 0]}}},
            {"$sort": {"bestseller_rating": -1, "title": 1}},
            {"$limit": 10},
            {"$project": {"title": 1, "material_id": 1, "bestseller_rating": 1, "score": 1}}
        ]
        material_results = list(collection.aggregate(material_pipeline))
        for material in material_results:
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
        author_pipeline = [
            {"$search": {"index": "search_index", "text": {"query": query, "path": "author_slug", "fuzzy": {"maxEdits": 1}}}},
            {"$group": {"_id": "$author_slug"}},
            {"$sort": {"_id": 1}},
            {"$limit": 10}
        ]
        author_results = list(collection.aggregate(author_pipeline))
        for author in author_results:
            author_name = author['_id']
            highlight_start, highlight_end = find_highlight_positions(author_name, query)
            authors.append({
                "text": author_name,
                "type": "author",
                "id": author_name,
                "score": 0,
                "search_score": 0,
                "highlight_start": highlight_start,
                "highlight_end": highlight_end
            })
        previous_searches = load_previous_searches()
        for search_query, frequency in previous_searches:
            if query.lower() in search_query.lower():
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
                if len(queries) >= 10:
                    break
        if not materials and not authors and not queries:
            return [{
                "text": query,
                "type": "query",
                "id": query,
                "score": 0,
                "search_score": 0,
                "highlight_start": 0,
                "highlight_end": len(query)
            }]
        def balance_suggestions(materials, authors, queries, target_total=10):
            available_types = []
            if materials:
                available_types.append('material')
            if authors:
                available_types.append('author')
            if queries:
                available_types.append('query')
            if not available_types:
                return []
            if len(available_types) == 1:
                if available_types[0] == 'material':
                    return materials[:target_total]
                elif available_types[0] == 'author':
                    return authors[:target_total]
                else:
                    return queries[:target_total]
            elif len(available_types) == 2:
                if 'query' in available_types and 'material' in available_types:
                    query_count = min(7, len(queries))
                    material_count = min(target_total - query_count, len(materials))
                    return queries[:query_count] + materials[:material_count]
                elif 'query' in available_types and 'author' in available_types:
                    query_count = min(8, len(queries))
                    author_count = min(target_total - query_count, len(authors))
                    return queries[:query_count] + authors[:author_count]
                elif 'material' in available_types and 'author' in available_types:
                    material_count = min(8, len(materials))
                    author_count = min(target_total - material_count, len(authors))
                    return materials[:material_count] + authors[:author_count]
            else:
                query_count = min(7, len(queries))
                material_count = min(2, len(materials))
                author_count = min(1, len(authors))
                remaining = target_total - query_count - material_count - author_count
                if remaining > 0:
                    if len(materials) > material_count:
                        material_count += min(remaining // 2, len(materials) - material_count)
                        remaining -= min(remaining // 2, len(materials) - material_count)
                    if remaining > 0 and len(authors) > author_count:
                        author_count += min(remaining, len(authors) - author_count)
                return queries[:query_count] + materials[:material_count] + authors[:author_count]
        balanced_suggestions = balance_suggestions(materials, authors, queries, 10)
        def calculate_priority(suggestion):
            base_score = 0
            if suggestion['type'] == 'query':
                base_score = 70
            elif suggestion['type'] == 'material':
                base_score = 20
            elif suggestion['type'] == 'author':
                base_score = 10
            if suggestion['type'] == 'material':
                base_score += (suggestion['score'] / 5) * 20
            elif suggestion['type'] == 'query':
                base_score += min(suggestion['score'] * 2, 30)
            base_score += suggestion['search_score'] * 10
            return base_score
        balanced_suggestions.sort(key=calculate_priority, reverse=True)
        final_suggestions = balanced_suggestions[:10]
        return final_suggestions
    except Exception as e:
        print(f"Typeahead error: {e}")
        return []
    finally:
        if 'client' in locals():
            client.close()
