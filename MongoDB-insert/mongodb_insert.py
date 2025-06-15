from pymongo import MongoClient
from dotenv import load_dotenv
import os
import json
from datetime import datetime
from typing import List, Dict, Any

# Load environment variables
load_dotenv()

def get_mongodb_connection():
    """Establish connection to MongoDB Atlas"""
    try:
        # Get connection string from environment variable
        connection_string = os.getenv('MONGODB_URI')
        if not connection_string:
            raise ValueError("MongoDB connection string not found in environment variables")
        
        # Create MongoDB client
        client = MongoClient(connection_string)
        
        # Test the connection
        client.admin.command('ping')
        print("Successfully connected to MongoDB!")
        return client
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        raise

def load_materials_from_json(file_path: str) -> List[Dict[str, Any]]:
    """Load and transform materials from JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            raw_data = json.load(file)
            
        # Transform the data to match our schema
        materials = []
        for item in raw_data:
            material = {
                "material_id": int(item.get("material_id", 0)),
                "title": str(item.get("material_title", "")),
                "description": str(item.get("description", "")),
                "category": item.get("categories", ""),
                "grade_level": item.get("class_grades", ""),
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
        # Get database and collection
        db = client[database_name]
        collection = db[collection_name]
        
        # Create indexes for better query performance
        collection.create_index("material_id", unique=True)
        collection.create_index("author_slug")
        collection.create_index("category")
        collection.create_index("grade_level")
        collection.create_index("material_type")
        
        # Insert documents
        if isinstance(documents, list):
            # Use ordered=False to continue insertion even if some documents fail
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

def main():
    try:
        # Connect to MongoDB
        client = get_mongodb_connection()
        
        # Load materials from JSON file
        json_file_path = "dataset.json"
        materials = load_materials_from_json(json_file_path)
        
        # Insert materials into MongoDB
        database_name = os.getenv('DATABASE_NAME', 'materials_db')
        collection_name = os.getenv('COLLECTION_NAME', 'materials')
        
        inserted_ids = insert_documents(client, database_name, collection_name, materials)
        
        # Close the connection
        client.close()
        print("MongoDB connection closed")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main() 