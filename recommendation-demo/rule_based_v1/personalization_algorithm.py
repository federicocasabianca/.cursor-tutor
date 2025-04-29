import json
import os
from datetime import datetime
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Set, Any

class DataLoader:
    """
    Component responsible for loading and preprocessing the data.
    """
    def __init__(self, data_path="."):
        self.data_path = data_path
        self.materials = {}
        self.purchases = []
        self.favorites = []
        self.interactions = []
        self.searches = []
    
    def load_data(self):
        """
        Load all data files from the specified path.
        """
        # Load materials
        with open(os.path.join(self.data_path, "materials.json"), "r") as f:
            materials_data = json.load(f)
            # Index materials by ID for faster lookup
            self.materials = {str(item["material_id"]): item for item in materials_data}
        
        # Load user behavior data
        with open(os.path.join(self.data_path, "purchases.json"), "r") as f:
            self.purchases = json.load(f)
        
        with open(os.path.join(self.data_path, "favorites.json"), "r") as f:
            self.favorites = json.load(f)
        
        with open(os.path.join(self.data_path, "interactions.json"), "r") as f:
            self.interactions = json.load(f)
        
        with open(os.path.join(self.data_path, "searches.json"), "r") as f:
            self.searches = json.load(f)
        
        print(f"Loaded {len(self.materials)} materials")
        print(f"Loaded {len(self.purchases)} purchases")
        print(f"Loaded {len(self.favorites)} favorites")
        print(f"Loaded {len(self.interactions)} interactions")
        print(f"Loaded {len(self.searches)} searches")
        
        return self


class UserProfileBuilder:
    """
    Component responsible for building user profiles based on behavior data.
    """
    def __init__(self, data_loader):
        self.data_loader = data_loader
        self.user_profiles = {}
    
    def build_profiles(self):
        """
        Process all user data to build comprehensive profiles.
        """
        # Initialize user profiles
        self._initialize_user_profiles()
        
        # Process different types of signals
        self._process_purchases()
        self._process_favorites()
        self._process_interactions()
        self._process_searches()
        
        # Infer preferences based on behaviors
        self._infer_preferences()
        
        return self.user_profiles
    
    def _initialize_user_profiles(self):
        """
        Initialize user profiles with empty structures.
        """
        # Get all unique user IDs from all data sources
        user_ids = set()
        for purchase in self.data_loader.purchases:
            try:
                user_ids.add(purchase["user_id"])
            except KeyError:
                print(f"Warning: Found search record without user_id field: {search}")
                continue
        for favorite in self.data_loader.favorites:
            try:
                user_ids.add(favorite["user_id"])
            except KeyError:
                print(f"Warning: Found search record without user_id field: {search}")
                continue
        for interaction in self.data_loader.interactions:
            try:
                user_ids.add(interaction["user_id"])
            except KeyError:
                print(f"Warning: Found search record without user_id field: {search}")
                continue
        for search in self.data_loader.searches:
            try:
                user_ids.add(search["user_id"])
            except KeyError:
                print(f"Warning: Found search record without user_id field: {search}")
                continue
        
        # Initialize empty profiles
        for user_id in user_ids:
            self.user_profiles[user_id] = {
                "user_id": user_id,
                "behavior": {
                    "purchases": [],
                    "favorites": [],
                    "interactions": [],
                    "searches": []
                },
                "preferences": {
                    "categories": Counter(),
                    "grade_levels": Counter(),
                    "price_ranges": Counter(),
                    "is_bundle": Counter()
                },
                "context": {
                    "device": None
                },
                "recent_activity": {
                    "last_active_date": None,
                    "last_purchased_material": None,
                    "last_search_query": None
                }
            }
    
    def _process_purchases(self):
        """
        Process purchase data to enrich user profiles.
        """
        for purchase in self.data_loader.purchases:
            user_id = purchase["user_id"]
            if user_id in self.user_profiles:
                # Add to behavior
                self.user_profiles[user_id]["behavior"]["purchases"].append(purchase)
                
                # Update preferences counters
                self.user_profiles[user_id]["preferences"]["categories"][purchase["material_category"]] += 1
                self.user_profiles[user_id]["preferences"]["grade_levels"][purchase["class_grade"]] += 1
                
                # Categorize price ranges
                price = float(purchase["purchase_price"])
                price_range = self._get_price_range(price)
                self.user_profiles[user_id]["preferences"]["price_ranges"][price_range] += 1
                
                # Bundle preference
                is_bundle = "1" if purchase["is_bundle"] == "1" else "0"
                self.user_profiles[user_id]["preferences"]["is_bundle"][is_bundle] += 1
                
                # Update context
                self.user_profiles[user_id]["context"]["device"] = purchase["user_device"]
                
                # Update recent activity
                purchase_date = datetime.strptime(purchase["date"], "%Y-%m-%d")
                if (self.user_profiles[user_id]["recent_activity"]["last_active_date"] is None or
                    purchase_date > datetime.strptime(self.user_profiles[user_id]["recent_activity"]["last_active_date"], "%Y-%m-%d")):
                    self.user_profiles[user_id]["recent_activity"]["last_active_date"] = purchase["date"]
                    self.user_profiles[user_id]["recent_activity"]["last_purchased_material"] = purchase["material_id"]
    
    def _process_favorites(self):
        """
        Process favorites data to enrich user profiles.
        """
        for favorite in self.data_loader.favorites:
            user_id = favorite["user_id"]
            if user_id in self.user_profiles:
                # Add to behavior
                self.user_profiles[user_id]["behavior"]["favorites"].append(favorite)
                
                # Update preferences counters
                self.user_profiles[user_id]["preferences"]["categories"][favorite["material_category"]] += 0.5  # Lower weight than purchases
                self.user_profiles[user_id]["preferences"]["grade_levels"][favorite["class_grade"]] += 0.5
                
                # Categorize price ranges
                price = float(favorite["material_price"])
                price_range = self._get_price_range(price)
                self.user_profiles[user_id]["preferences"]["price_ranges"][price_range] += 0.5
                
                # Bundle preference
                is_bundle = "1" if favorite["is_bundle"] == "1" else "0"
                self.user_profiles[user_id]["preferences"]["is_bundle"][is_bundle] += 0.5
                
                # Update context
                self.user_profiles[user_id]["context"]["device"] = favorite["user_device"]
                
                # Update recent activity
                favorite_date = datetime.strptime(favorite["date"], "%Y-%m-%d")
                if (self.user_profiles[user_id]["recent_activity"]["last_active_date"] is None or
                    favorite_date > datetime.strptime(self.user_profiles[user_id]["recent_activity"]["last_active_date"], "%Y-%m-%d")):
                    self.user_profiles[user_id]["recent_activity"]["last_active_date"] = favorite["date"]
    
    def _process_interactions(self):
        """
        Process interaction data to enrich user profiles.
        """
        for interaction in self.data_loader.interactions:
            user_id = interaction["user_id"]
            if user_id in self.user_profiles:
                # Add to behavior
                self.user_profiles[user_id]["behavior"]["interactions"].append(interaction)
                
                # Update preferences counters with smaller weights
                weight = 0.3 if interaction["type"] == "click" else 0.4 if interaction["type"] == "view_preview" else 0.5 if interaction["type"] == "add_to_cart" else 0.2
                
                self.user_profiles[user_id]["preferences"]["categories"][interaction["material_category"]] += weight
                self.user_profiles[user_id]["preferences"]["grade_levels"][interaction["class_grade"]] += weight
                
                # Categorize price ranges
                price = float(interaction["material_price"])
                price_range = self._get_price_range(price)
                self.user_profiles[user_id]["preferences"]["price_ranges"][price_range] += weight
                
                # Bundle preference
                is_bundle = "1" if interaction["is_bundle"] == "1" else "0"
                self.user_profiles[user_id]["preferences"]["is_bundle"][is_bundle] += weight
                
                # Update context
                self.user_profiles[user_id]["context"]["device"] = interaction["user_device"]
                
                # Update recent activity
                interaction_date = datetime.strptime(interaction["date"], "%Y-%m-%d")
                if (self.user_profiles[user_id]["recent_activity"]["last_active_date"] is None or
                    interaction_date > datetime.strptime(self.user_profiles[user_id]["recent_activity"]["last_active_date"], "%Y-%m-%d")):
                    self.user_profiles[user_id]["recent_activity"]["last_active_date"] = interaction["date"]
    
    def _process_searches(self):
        """
        Process search data to enrich user profiles.
        """
        for search in self.data_loader.searches:
            user_id = search["user_id"]
            if user_id in self.user_profiles:
                # Add to behavior
                self.user_profiles[user_id]["behavior"]["searches"].append(search)
                
                # Update context
                self.user_profiles[user_id]["context"]["device"] = search["user_device"]
                
                # Update recent activity
                search_date = datetime.strptime(search["date"], "%Y-%m-%d")
                if (self.user_profiles[user_id]["recent_activity"]["last_active_date"] is None or
                    search_date > datetime.strptime(self.user_profiles[user_id]["recent_activity"]["last_active_date"], "%Y-%m-%d")):
                    self.user_profiles[user_id]["recent_activity"]["last_active_date"] = search["date"]
                    self.user_profiles[user_id]["recent_activity"]["last_search_query"] = search["query"]
    
    def _infer_preferences(self):
        """
        Infer user preferences based on their behavior patterns.
        """
        for user_id, profile in self.user_profiles.items():
            # Get the most common preferences
            if profile["preferences"]["categories"]:
                profile["preferred_category"] = profile["preferences"]["categories"].most_common(1)[0][0]
            else:
                profile["preferred_category"] = None
                
            if profile["preferences"]["grade_levels"]:
                profile["preferred_grade"] = profile["preferences"]["grade_levels"].most_common(1)[0][0]
            else:
                profile["preferred_grade"] = None
                
            if profile["preferences"]["price_ranges"]:
                profile["preferred_price_range"] = profile["preferences"]["price_ranges"].most_common(1)[0][0]
            else:
                profile["preferred_price_range"] = None
            
            if profile["preferences"]["is_bundle"]:
                profile["preferred_bundle_status"] = profile["preferences"]["is_bundle"].most_common(1)[0][0]
            else:
                profile["preferred_bundle_status"] = None
    
    def _get_price_range(self, price):
        """
        Categorize prices into ranges.
        """
        if price == 0:
            return "free"
        elif price <= 3:
            return "low"
        elif price <= 7:
            return "medium"
        else:
            return "high"


class RecommendationEngine:
    """
    Component responsible for generating recommendations using the rule-based approach.
    """
    def __init__(self, data_loader, user_profiles):
        self.data_loader = data_loader
        self.user_profiles = user_profiles
        self.material_pool = list(data_loader.materials.values())
    
    def get_recommendations(self, user_id, limit=5):
        """
        Generate recommendations for a specific user.
        """
        # Check if user exists
        if user_id not in self.user_profiles:
            return self._get_fallback_recommendations(limit=limit)
        
        # Get user profile
        profile = self.user_profiles[user_id]
        
        # Try behavior-based rules first
        recommendations = self._apply_behavior_based_rules(profile, limit)
        
        # If not enough recommendations, try preference-based rules
        if len(recommendations) < limit:
            preference_recs = self._apply_preference_based_rules(profile, limit - len(recommendations))
            recommendations.extend([rec for rec in preference_recs if rec["material_id"] not in [r["material_id"] for r in recommendations]])
        
        # If still not enough, use fallback rules
        if len(recommendations) < limit:
            fallback_recs = self._get_fallback_recommendations(profile, limit - len(recommendations))
            recommendations.extend([rec for rec in fallback_recs if rec["material_id"] not in [r["material_id"] for r in recommendations]])
        
        return recommendations[:limit]
    
    def _apply_behavior_based_rules(self, profile, limit=5):
        """
        Apply behavior-based recommendation rules.
        """
        recommendations = []
        
        # Rule 1: Recent Acquisitions - recommend materials with same grade/subject and similar price
        if profile["recent_activity"]["last_purchased_material"]:
            last_material_id = profile["recent_activity"]["last_purchased_material"]
            if last_material_id in self.data_loader.materials:
                last_material = self.data_loader.materials[last_material_id]
                
                # Find materials with same grade level and category
                similar_materials = []
                for material in self.material_pool:
                    if (material["class_grade"] == last_material["class_grade"] and 
                        material["category"] == last_material["category"] and 
                        str(material["material_id"]) != last_material_id):
                        
                        # Calculate price similarity (within 2€)
                        last_price = float(last_material["price"])
                        current_price = float(material["price"])
                        if abs(current_price - last_price) <= 2:
                            similar_materials.append(material)
                
                # Sort by bestseller rating
                similar_materials.sort(key=lambda x: float(x["bestseller_rating"]), reverse=True)
                
                # Add recommendations
                for material in similar_materials[:limit]:
                    recommendations.append({
                        "material_id": str(material["material_id"]),
                        "title": material["title"],
                        "category": material["category"],
                        "class_grade": material["class_grade"],
                        "price": material["price"],
                        "bestseller_rating": material["bestseller_rating"],
                        "is_bundle": material["is_bundle"],
                        "rule": "recent_acquisition"
                    })
        
        # Rule 2: Favorites - recommend materials similar to favorites
        if len(recommendations) < limit and profile["behavior"]["favorites"]:
            # Get all favorite material IDs
            favorite_ids = [fav["material_id"] for fav in profile["behavior"]["favorites"]]
            
            # Get favorite materials details
            favorite_materials = [self.data_loader.materials.get(fav_id) for fav_id in favorite_ids if fav_id in self.data_loader.materials]
            
            # Count favorite categories and grade levels
            fav_categories = Counter([m["category"] for m in favorite_materials if m])
            fav_grades = Counter([m["class_grade"] for m in favorite_materials if m])
            
            # Get most common category and grade
            most_common_category = fav_categories.most_common(1)[0][0] if fav_categories else None
            most_common_grade = fav_grades.most_common(1)[0][0] if fav_grades else None
            
            if most_common_category and most_common_grade:
                # Find materials with same category and grade
                similar_materials = []
                for material in self.material_pool:
                    if (material["category"] == most_common_category and
                        material["class_grade"] == most_common_grade and
                        str(material["material_id"]) not in favorite_ids):
                        similar_materials.append(material)
                
                # Sort by bestseller rating
                similar_materials.sort(key=lambda x: float(x["bestseller_rating"]), reverse=True)
                
                # Add recommendations
                for material in similar_materials[:limit - len(recommendations)]:
                    recommendations.append({
                        "material_id": str(material["material_id"]),
                        "title": material["title"],
                        "category": material["category"],
                        "class_grade": material["class_grade"],
                        "price": material["price"],
                        "bestseller_rating": material["bestseller_rating"],
                        "is_bundle": material["is_bundle"],
                        "rule": "favorites_based"
                    })
        
        return recommendations
    
    def _apply_preference_based_rules(self, profile, limit=5):
        """
        Apply preference-based recommendation rules.
        """
        recommendations = []
        
        # Rule 1: Category and Grade Preference
        if profile["preferred_category"] and profile["preferred_grade"]:
            matching_materials = []
            for material in self.material_pool:
                if (material["category"] == profile["preferred_category"] and
                    material["class_grade"] == profile["preferred_grade"]):
                    # Check if this material was already purchased
                    purchased_ids = [p["material_id"] for p in profile["behavior"]["purchases"]]
                    if str(material["material_id"]) not in purchased_ids:
                        matching_materials.append(material)
            
            # Sort by bestseller rating
            matching_materials.sort(key=lambda x: float(x["bestseller_rating"]), reverse=True)
            
            # Add recommendations
            for material in matching_materials[:limit]:
                recommendations.append({
                    "material_id": str(material["material_id"]),
                    "title": material["title"],
                    "category": material["category"],
                    "class_grade": material["class_grade"],
                    "price": material["price"],
                    "bestseller_rating": material["bestseller_rating"],
                    "is_bundle": material["is_bundle"],
                    "rule": "category_grade_preference"
                })
        
        # Rule 2: Price Range Preference
        if len(recommendations) < limit and profile["preferred_price_range"]:
            price_range = profile["preferred_price_range"]
            min_price, max_price = 0, 0
            
            if price_range == "free":
                min_price, max_price = 0, 0
            elif price_range == "low":
                min_price, max_price = 0.01, 3
            elif price_range == "medium":
                min_price, max_price = 3.01, 7
            elif price_range == "high":
                min_price, max_price = 7.01, float('inf')
            
            matching_materials = []
            for material in self.material_pool:
                price = float(material["price"]) if isinstance(material["price"], (int, float, str)) else 0
                if min_price <= price <= max_price:
                    # Prioritize materials matching the preferred grade if available
                    if profile["preferred_grade"] and material["class_grade"] == profile["preferred_grade"]:
                        matching_materials.append((material, 2))  # Higher priority
                    else:
                        matching_materials.append((material, 1))  # Lower priority
            
            # Sort by priority then bestseller rating
            matching_materials.sort(key=lambda x: (x[1], float(x[0]["bestseller_rating"])), reverse=True)
            
            # Add recommendations
            for material, _ in matching_materials[:limit - len(recommendations)]:
                # Check if already recommended
                if material["material_id"] not in [r["material_id"] for r in recommendations]:
                    recommendations.append({
                        "material_id": str(material["material_id"]),
                        "title": material["title"],
                        "category": material["category"],
                        "class_grade": material["class_grade"],
                        "price": material["price"],
                        "bestseller_rating": material["bestseller_rating"],
                        "is_bundle": material["is_bundle"],
                        "rule": "price_preference"
                    })
        
        return recommendations
    
    def _get_fallback_recommendations(self, profile=None, limit=5):
        """
        Get fallback recommendations for when behavior and preference rules don't yield enough results.
        """
        recommendations = []
        
        # If we have a profile, use its preferred grade level if available
        if profile and profile["preferred_grade"]:
            # Find popular materials for that grade level
            grade_materials = [m for m in self.material_pool if m["class_grade"] == profile["preferred_grade"]]
            # Sort by bestseller rating
            grade_materials.sort(key=lambda x: float(x["bestseller_rating"]), reverse=True)
            
            # Add recommendations
            for material in grade_materials[:limit]:
                recommendations.append({
                    "material_id": str(material["material_id"]),
                    "title": material["title"],
                    "category": material["category"],
                    "class_grade": material["class_grade"],
                    "price": material["price"],
                    "bestseller_rating": material["bestseller_rating"],
                    "is_bundle": material["is_bundle"],
                    "rule": "popular_by_grade"
                })
        
        # If still not enough or no profile provided, return overall most popular
        if len(recommendations) < limit:
            # Sort all materials by bestseller rating
            popular_materials = sorted(self.material_pool, 
                                      key=lambda x: float(x["bestseller_rating"]), 
                                      reverse=True)
            
            # Add recommendations
            for material in popular_materials[:limit - len(recommendations)]:
                # Check if already recommended
                if material["material_id"] not in [r["material_id"] for r in recommendations]:
                    recommendations.append({
                        "material_id": str(material["material_id"]),
                        "title": material["title"],
                        "category": material["category"],
                        "class_grade": material["class_grade"],
                        "price": material["price"],
                        "bestseller_rating": material["bestseller_rating"],
                        "is_bundle": material["is_bundle"],
                        "rule": "overall_popular"
                    })
        
        return recommendations


class PersonalizationService:
    """
    Main service class that orchestrates the personalization process.
    """
    def __init__(self, data_path="."):
        self.data_loader = None
        self.user_profiles = {}
        self.recommendation_engine = None
        self.data_path = data_path
    
    def initialize(self):
        """
        Initialize the personalization service.
        """
        print("Initializing Personalization Service...")
        
        # Load data
        self.data_loader = DataLoader(self.data_path).load_data()
        
        # Build user profiles
        profile_builder = UserProfileBuilder(self.data_loader)
        self.user_profiles = profile_builder.build_profiles()
        
        # Initialize recommendation engine
        self.recommendation_engine = RecommendationEngine(self.data_loader, self.user_profiles)
        
        print(f"Personalization Service initialized with {len(self.user_profiles)} user profiles.")
        return self
    
    def get_recommendations_for_user(self, user_id, limit=5):
        """
        Get personalized recommendations for a specific user.
        """
        if not self.recommendation_engine:
            raise Exception("Personalization Service not initialized. Call initialize() first.")
        
        return self.recommendation_engine.get_recommendations(user_id, limit)
    
    def get_user_profile(self, user_id):
        """
        Get a user's profile information.
        """
        if user_id in self.user_profiles:
            return self.user_profiles[user_id]
        return None


def main():
    """
    Main function to demonstrate the personalization service.
    """
    # Initialize the service
    service = PersonalizationService().initialize()
    
    # Get all user IDs
    user_ids = list(service.user_profiles.keys())
    
    # Print recommendations for each user
    for user_id in user_ids:
        print(f"\n=============== Recommendations for User {user_id} ===============")
        
        # Get user profile insights
        profile = service.get_user_profile(user_id)
        print(f"Preferred Grade: {profile.get('preferred_grade', 'Unknown')}")
        print(f"Preferred Category: {profile.get('preferred_category', 'Unknown')}")
        print(f"Preferred Price Range: {profile.get('preferred_price_range', 'Unknown')}")
        print(f"Recent Activity: {profile.get('recent_activity', {}).get('last_active_date', 'Unknown')}")
        
        # Get recommendations
        recommendations = service.get_recommendations_for_user(user_id, limit=5)
        
        # Print recommendations
        print("\nTop 5 Recommendations:")
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec['title']} - {rec['category']} - {rec['class_grade']} - €{rec['price']} - Rule: {rec['rule']}")
    
    print("\nPersonalization demo completed.")


if __name__ == "__main__":
    main()