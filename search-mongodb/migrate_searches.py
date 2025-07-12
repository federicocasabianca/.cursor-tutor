#!/usr/bin/env python3
"""
Migration script to move search queries from searches.json to MongoDB.
This script will:
1. Read the existing searches.json file
2. Transform the data to the new MongoDB schema
3. Insert the data into the search_queries collection
4. Provide a summary of the migration
"""

import json
import os
from datetime import datetime
from db import get_mongodb_connection
from query_tracking.service import classify_query_generic_specific, ensure_query_tracking_indexes

def migrate_searches_to_mongodb():
    """Migrate search queries from searches.json to MongoDB"""
    
    # Check if searches.json exists
    searches_file = 'searches/searches.json'
    if not os.path.exists(searches_file):
        print(f"File {searches_file} not found. Nothing to migrate.")
        return
    
    try:
        # Read existing searches
        print("Reading searches.json...")
        with open(searches_file, 'r', encoding='utf-8') as file:
            searches = json.load(file)
        
        print(f"Found {len(searches)} search entries to migrate")
        
        # Connect to MongoDB
        client = get_mongodb_connection()
        db = client[os.getenv('DATABASE_NAME', 'materials_db')]
        collection = db['search_queries']
        
        # Ensure indexes exist
        ensure_query_tracking_indexes(client)
        
        # Migration statistics
        migrated_count = 0
        skipped_count = 0
        error_count = 0
        
        # Process each search entry
        for search in searches:
            try:
                query = search.get('search_keyword', '').strip()
                if not query:
                    skipped_count += 1
                    continue
                
                # Classify the query
                query_type = classify_query_generic_specific(query)
                
                # Prepare the document for MongoDB
                query_doc = {
                    "query": query,
                    "query_type": query_type,
                    "user_id": search.get('user_id', 'system'),
                    "device": search.get('devices_used', 'web'),
                    "search_frequency": int(search.get('search_frequency', 1)),
                    "first_search_date": datetime.strptime(
                        search.get('first_search_date', datetime.now().strftime('%Y-%m-%d')), 
                        '%Y-%m-%d'
                    ),
                    "last_search_date": datetime.strptime(
                        search.get('last_search_date', datetime.now().strftime('%Y-%m-%d')), 
                        '%Y-%m-%d'
                    ),
                    "result_count": 0  # We don't have this data from the old format
                }
                
                # Insert into MongoDB (use upsert to avoid duplicates)
                result = collection.update_one(
                    {"query": query},
                    {"$set": query_doc},
                    upsert=True
                )
                
                if result.upserted_id:
                    migrated_count += 1
                    print(f"Migrated: '{query}' (type: {query_type})")
                else:
                    print(f"Updated existing: '{query}' (type: {query_type})")
                
            except Exception as e:
                error_count += 1
                print(f"Error migrating query '{search.get('search_keyword', 'unknown')}': {e}")
        
        # Print migration summary
        print("\n" + "="*50)
        print("MIGRATION SUMMARY")
        print("="*50)
        print(f"Total entries processed: {len(searches)}")
        print(f"Successfully migrated: {migrated_count}")
        print(f"Skipped (empty queries): {skipped_count}")
        print(f"Errors: {error_count}")
        
        # Get statistics from MongoDB
        total_queries = collection.count_documents({})
        generic_count = collection.count_documents({"query_type": "generic"})
        specific_count = collection.count_documents({"query_type": "specific"})
        
        print(f"\nMongoDB Statistics:")
        print(f"Total queries in database: {total_queries}")
        print(f"Generic queries: {generic_count}")
        print(f"Specific queries: {specific_count}")
        
        # Ask if user wants to backup the old file
        response = input("\nDo you want to backup the old searches.json file? (y/n): ")
        if response.lower() in ['y', 'yes']:
            backup_file = f"{searches_file}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(searches, f, indent=2, ensure_ascii=False)
            print(f"Backup created: {backup_file}")
        
        print("\nMigration completed successfully!")
        
    except Exception as e:
        print(f"Migration failed: {e}")
    finally:
        if 'client' in locals():
            client.close()

if __name__ == '__main__':
    print("Search Queries Migration Tool")
    print("="*30)
    print("This tool will migrate search queries from searches.json to MongoDB")
    print("The new schema includes query classification (generic/specific)")
    print()
    
    response = input("Do you want to proceed with the migration? (y/n): ")
    if response.lower() in ['y', 'yes']:
        migrate_searches_to_mongodb()
    else:
        print("Migration cancelled.") 