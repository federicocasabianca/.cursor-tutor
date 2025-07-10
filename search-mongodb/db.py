import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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
        try:
            collection.drop_index("title_text_description_text_material_type_text_author_slug_text")
        except Exception:
            pass
        collection.create_index([
            ("title", "text"),
            ("description", "text"),
            ("material_type", "text"),
            ("author_slug", "text")
        ], name="title_text_description_text_material_type_text_author_slug_text")
        print("Note: Ensure you have created a 'search_index' in MongoDB Atlas with the required fields")
        print("Successfully created/updated all indexes")
    except Exception as e:
        print(f"Error creating indexes: {e}")
        raise
