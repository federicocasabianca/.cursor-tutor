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
    Updated component responsible for building user profiles based on behavior data.
    Weights adjusted based on correlation analysis of purchase predictors.
    """
    def __init__(self, data_loader):
        self.data_loader = data_loader
        self.user_profiles = {}
        
        # Define signal weights based on correlation analysis
        self.signal_weights = {
            # Purchases remain strongest signal
            "purchase": 1.0,
            
            # Interaction weights adjusted based on correlation data
            "view_material": 0.7,      # 46-52% correlation
            "view_preview": 0.5,       # 32-36% correlation
            "search": 0.4,             # 29% correlation 
            "add_to_cart": 0.3,        # 20-23% correlation
            "download": 0.2,           # 11-12% correlation
            "favorite": 0.15,          # 10-11% correlation - reduced from previous implementation
            "click": 0.1,              # Lower base interaction
            
            # Category vs grade weights - category is stronger predictor
            "category_multiplier": 1.2,  # Subject correlations consistently higher
            "grade_multiplier": 1.0
        }
    
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
            user_ids.add(purchase["user_id"])
        for favorite in self.data_loader.favorites:
            user_ids.add(favorite["user_id"])
        for interaction in self.data_loader.interactions:
            user_ids.add(interaction["user_id"])
        for search in self.data_loader.searches:
            user_ids.add(search["user_id"])
        
        # Initialize empty profiles
        for user_id in user_ids:
            self.user_profiles[user_id] = {
                "user_id": user_id,
                "behavior": {
                    "purchases": [],
                    "favorites": [],
                    "interactions": [],
                    "searches": [],
                    "viewed_materials": set(),  # Track viewed materials separately
                    "previewed_materials": set()  # Track previewed materials separately
                },
                "preferences": {
                    "categories": defaultdict(float),
                    "grade_levels": defaultdict(float),
                    "price_ranges": defaultdict(float),
                    "is_bundle": defaultdict(float)
                },
                "context": {
                    "device": None
                },
                "recent_activity": {
                    "last_active_date": None,
                    "last_purchased_material": None,
                    "last_search_query": None,
                    "last_viewed_material": None,
                    "last_previewed_material": None
                },
                "subject_affinity_score": defaultdict(float),  # New category affinity tracking
                "grade_affinity_score": defaultdict(float)     # New grade affinity tracking
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
                category_weight = self.signal_weights["purchase"] * self.signal_weights["category_multiplier"]
                grade_weight = self.signal_weights["purchase"] * self.signal_weights["grade_multiplier"]
                
                self.user_profiles[user_id]["preferences"]["categories"][purchase["material_category"]] += category_weight
                self.user_profiles[user_id]["preferences"]["grade_levels"][purchase["class_grade"]] += grade_weight
                
                # Update subject and grade affinity scores
                self.user_profiles[user_id]["subject_affinity_score"][purchase["material_category"]] += category_weight
                self.user_profiles[user_id]["grade_affinity_score"][purchase["class_grade"]] += grade_weight
                
                # Categorize price ranges
                price = float(purchase["purchase_price"])
                price_range = self._get_price_range(price)
                self.user_profiles[user_id]["preferences"]["price_ranges"][price_range] += self.signal_weights["purchase"]
                
                # Bundle preference
                is_bundle = "1" if purchase["is_bundle"] == "1" else "0"
                self.user_profiles[user_id]["preferences"]["is_bundle"][is_bundle] += self.signal_weights["purchase"]
                
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
        Process favorites data to enrich user profiles with reduced weight.
        """
        for favorite in self.data_loader.favorites:
            user_id = favorite["user_id"]
            if user_id in self.user_profiles:
                # Add to behavior
                self.user_profiles[user_id]["behavior"]["favorites"].append(favorite)
                
                # Update preferences counters - reduced weight based on correlation data
                category_weight = self.signal_weights["favorite"] * self.signal_weights["category_multiplier"]
                grade_weight = self.signal_weights["favorite"] * self.signal_weights["grade_multiplier"]
                
                self.user_profiles[user_id]["preferences"]["categories"][favorite["material_category"]] += category_weight
                self.user_profiles[user_id]["preferences"]["grade_levels"][favorite["class_grade"]] += grade_weight
                
                # Update subject and grade affinity scores
                self.user_profiles[user_id]["subject_affinity_score"][favorite["material_category"]] += category_weight
                self.user_profiles[user_id]["grade_affinity_score"][favorite["class_grade"]] += grade_weight
                
                # Categorize price ranges
                price = float(favorite["material_price"])
                price_range = self._get_price_range(price)
                self.user_profiles[user_id]["preferences"]["price_ranges"][price_range] += self.signal_weights["favorite"]
                
                # Bundle preference
                is_bundle = "1" if favorite["is_bundle"] == "1" else "0"
                self.user_profiles[user_id]["preferences"]["is_bundle"][is_bundle] += self.signal_weights["favorite"]
                
                # Update context
                self.user_profiles[user_id]["context"]["device"] = favorite["user_device"]
                
                # Update recent activity
                favorite_date = datetime.strptime(favorite["date"], "%Y-%m-%d")
                if (self.user_profiles[user_id]["recent_activity"]["last_active_date"] is None or
                    favorite_date > datetime.strptime(self.user_profiles[user_id]["recent_activity"]["last_active_date"], "%Y-%m-%d")):
                    self.user_profiles[user_id]["recent_activity"]["last_active_date"] = favorite["date"]
    
    def _process_interactions(self):
        """
        Process interaction data with updated weights based on correlation analysis.
        """
        for interaction in self.data_loader.interactions:
            user_id = interaction["user_id"]
            if user_id in self.user_profiles:
                # Add to behavior
                self.user_profiles[user_id]["behavior"]["interactions"].append(interaction)
                
                # Determine weight based on interaction type
                interaction_type = interaction["type"]
                if interaction_type == "view_material":
                    weight = self.signal_weights["view_material"]
                    # Track viewed materials
                    self.user_profiles[user_id]["behavior"]["viewed_materials"].add(interaction["material_id"])
                    # Update last viewed material
                    interaction_date = datetime.strptime(interaction["date"], "%Y-%m-%d")
                    if (self.user_profiles[user_id]["recent_activity"]["last_viewed_material"] is None or
                        interaction_date > datetime.strptime(self.user_profiles[user_id]["recent_activity"].get("last_viewed_date", "2000-01-01"), "%Y-%m-%d")):
                        self.user_profiles[user_id]["recent_activity"]["last_viewed_material"] = interaction["material_id"]
                        self.user_profiles[user_id]["recent_activity"]["last_viewed_date"] = interaction["date"]
                elif interaction_type == "view_preview":
                    weight = self.signal_weights["view_preview"]
                    # Track previewed materials
                    self.user_profiles[user_id]["behavior"]["previewed_materials"].add(interaction["material_id"])
                    # Update last previewed material
                    interaction_date = datetime.strptime(interaction["date"], "%Y-%m-%d")
                    if (self.user_profiles[user_id]["recent_activity"]["last_previewed_material"] is None or
                        interaction_date > datetime.strptime(self.user_profiles[user_id]["recent_activity"].get("last_previewed_date", "2000-01-01"), "%Y-%m-%d")):
                        self.user_profiles[user_id]["recent_activity"]["last_previewed_material"] = interaction["material_id"]
                        self.user_profiles[user_id]["recent_activity"]["last_previewed_date"] = interaction["date"]
                elif interaction_type == "add_to_cart":
                    weight = self.signal_weights["add_to_cart"]
                elif interaction_type == "download":
                    weight = self.signal_weights["download"]
                else:  # Default to click
                    weight = self.signal_weights["click"]
                
                # Apply category vs grade multipliers
                category_weight = weight * self.signal_weights["category_multiplier"]
                grade_weight = weight * self.signal_weights["grade_multiplier"]
                
                # Update preferences
                self.user_profiles[user_id]["preferences"]["categories"][interaction["material_category"]] += category_weight
                self.user_profiles[user_id]["preferences"]["grade_levels"][interaction["class_grade"]] += grade_weight
                
                # Update subject and grade affinity scores
                self.user_profiles[user_id]["subject_affinity_score"][interaction["material_category"]] += category_weight
                self.user_profiles[user_id]["grade_affinity_score"][interaction["class_grade"]] += grade_weight
                
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
        Process search data with increased weight based on correlation analysis.
        """
        for search in self.data_loader.searches:
            user_id = search["user_id"]
            if user_id in self.user_profiles:
                # Add to behavior
                self.user_profiles[user_id]["behavior"]["searches"].append(search)
                
                # Apply search weight to subject category (no grade data in searches)
                category_weight = self.signal_weights["search"] * self.signal_weights["category_multiplier"]
                
                # Update category preference from search result
                if "material_category" in search:
                    self.user_profiles[user_id]["preferences"]["categories"][search["material_category"]] += category_weight
                    self.user_profiles[user_id]["subject_affinity_score"][search["material_category"]] += category_weight
                
                # Update grade preference if available
                if "class_grade" in search:
                    grade_weight = self.signal_weights["search"] * self.signal_weights["grade_multiplier"]
                    self.user_profiles[user_id]["preferences"]["grade_levels"][search["class_grade"]] += grade_weight
                    self.user_profiles[user_id]["grade_affinity_score"][search["class_grade"]] += grade_weight
                
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
                # Sort by score rather than just counting occurrences
                sorted_categories = sorted(
                    profile["subject_affinity_score"].items(), 
                    key=lambda x: x[1], 
                    reverse=True
                )
                profile["preferred_category"] = sorted_categories[0][0] if sorted_categories else None
            else:
                profile["preferred_category"] = None
                
            if profile["preferences"]["grade_levels"]:
                # Sort by score rather than just counting occurrences
                sorted_grades = sorted(
                    profile["grade_affinity_score"].items(), 
                    key=lambda x: x[1], 
                    reverse=True
                )
                profile["preferred_grade"] = sorted_grades[0][0] if sorted_grades else None
            else:
                profile["preferred_grade"] = None
                
            if profile["preferences"]["price_ranges"]:
                # Get most common price range
                sorted_prices = sorted(
                    profile["preferences"]["price_ranges"].items(),
                    key=lambda x: x[1],
                    reverse=True
                )
                profile["preferred_price_range"] = sorted_prices[0][0] if sorted_prices else None
            else:
                profile["preferred_price_range"] = None
            
            if profile["preferences"]["is_bundle"]:
                # Get bundle preference
                sorted_bundles = sorted(
                    profile["preferences"]["is_bundle"].items(),
                    key=lambda x: x[1],
                    reverse=True
                )
                profile["preferred_bundle_status"] = sorted_bundles[0][0] if sorted_bundles else None
            else:
                profile["preferred_bundle_status"] = None
                
            # Generate ranked lists of preferences (not just the top one)
            profile["ranked_categories"] = sorted(
                profile["subject_affinity_score"].items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            profile["ranked_grades"] = sorted(
                profile["grade_affinity_score"].items(),
                key=lambda x: x[1],
                reverse=True
            )
    
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
    Updated component responsible for generating recommendations using the rule-based approach.
    Prioritizes view/preview behaviors based on correlation analysis.
    """
    def __init__(self, data_loader, user_profiles):
        self.data_loader = data_loader
        self.user_profiles = user_profiles
        self.material_pool = list(data_loader.materials.values())
        
        # Define rule priorities based on correlation analysis
        self.rule_priorities = {
            "view_based": 1,        # Highest priority - 46-52% correlation
            "preview_based": 2,     # Second priority - 32-36% correlation
            "recent_acquisition": 3, # Still strong signal
            "search_based": 4,      # Added as significant signal - 29% correlation
            "cart_based": 5,        # Added based on correlation - 20-23% correlation
            "favorites_based": 6,   # Lowered priority - only 10-11% correlation
            "category_grade_preference": 7,
            "price_preference": 8,
            "popular_by_grade": 9,
            "overall_popular": 10
        }
    
    def get_recommendations(self, user_id, limit=5):
        """
        Generate recommendations for a specific user with updated rule priorities.
        """
        # Check if user exists
        if user_id not in self.user_profiles:
            return self._get_fallback_recommendations(limit=limit)
        
        # Get user profile
        profile = self.user_profiles[user_id]
        
        # Initialize recommendations with scores for sorting
        all_recommendations = []
        
        # Apply each rule in priority order
        
        # 1. View-based rule (highest priority based on correlation)
        view_recs = self._apply_view_based_rules(profile, limit)
        all_recommendations.extend(view_recs)
        
        # 2. Preview-based rule
        preview_recs = self._apply_preview_based_rules(profile, limit)
        all_recommendations.extend([rec for rec in preview_recs if rec["material_id"] not in [r["material_id"] for r in all_recommendations]])
        
        # 3. Recent acquisition rule (previously highest priority)
        acquisition_recs = self._apply_acquisition_based_rules(profile, limit)
        all_recommendations.extend([rec for rec in acquisition_recs if rec["material_id"] not in [r["material_id"] for r in all_recommendations]])
        
        # 4. Search-based rule
        search_recs = self._apply_search_based_rules(profile, limit)
        all_recommendations.extend([rec for rec in search_recs if rec["material_id"] not in [r["material_id"] for r in all_recommendations]])
        
        # 5. Cart-based rule
        cart_recs = self._apply_cart_based_rules(profile, limit)
        all_recommendations.extend([rec for rec in cart_recs if rec["material_id"] not in [r["material_id"] for r in all_recommendations]])
        
        # 6. Favorites-based rule (downgraded priority)
        favorite_recs = self._apply_favorites_based_rules(profile, limit)
        all_recommendations.extend([rec for rec in favorite_recs if rec["material_id"] not in [r["material_id"] for r in all_recommendations]])
        
        # 7. Preference-based rules
        if len(all_recommendations) < limit:
            preference_recs = self._apply_preference_based_rules(profile, limit - len(all_recommendations))
            all_recommendations.extend([rec for rec in preference_recs if rec["material_id"] not in [r["material_id"] for r in all_recommendations]])
        
        # 8. Fallback rules
        if len(all_recommendations) < limit:
            fallback_recs = self._get_fallback_recommendations(profile, limit - len(all_recommendations))
            all_recommendations.extend([rec for rec in fallback_recs if rec["material_id"] not in [r["material_id"] for r in all_recommendations]])
        
        # Sort recommendations by rule priority and then by score
        all_recommendations.sort(key=lambda x: (self.rule_priorities.get(x["rule"], 99), -x.get("score", 0)))
        
        return all_recommendations[:limit]
    
    def _apply_view_based_rules(self, profile, limit=5):
        """
        NEW: Apply recommendations based on viewed materials (highest correlation signal).
        """
        recommendations = []
        
        # Check if user has viewed materials
        if profile["behavior"]["viewed_materials"]:
            # Get recently viewed material
            if profile["recent_activity"].get("last_viewed_material"):
                viewed_material_id = profile["recent_activity"]["last_viewed_material"]
                
                if viewed_material_id in self.data_loader.materials:
                    viewed_material = self.data_loader.materials[viewed_material_id]
                    
                    # Find materials with same category and grade level
                    similar_materials = []
                    for material in self.material_pool:
                        if (material["category"] == viewed_material["category"] and 
                            material["class_grade"] == viewed_material["class_grade"] and 
                            str(material["material_id"]) != viewed_material_id):
                            
                            # Check if not already purchased
                            purchased_ids = [p["material_id"] for p in profile["behavior"]["purchases"]]
                            if str(material["material_id"]) not in purchased_ids:
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
                            "rule": "view_based",
                            "score": 5.0  # High base score
                        })
        
        return recommendations
    
    def _apply_preview_based_rules(self, profile, limit=5):
        """
        NEW: Apply recommendations based on previewed materials (second highest correlation).
        """
        recommendations = []
        
        # Check if user has previewed materials
        if profile["behavior"]["previewed_materials"]:
            # Get recently previewed material
            if profile["recent_activity"].get("last_previewed_material"):
                previewed_material_id = profile["recent_activity"]["last_previewed_material"]
                
                if previewed_material_id in self.data_loader.materials:
                    previewed_material = self.data_loader.materials[previewed_material_id]
                    
                    # Find materials with same category and grade level
                    similar_materials = []
                    for material in self.material_pool:
                        if (material["category"] == previewed_material["category"] and 
                            material["class_grade"] == previewed_material["class_grade"] and 
                            str(material["material_id"]) != previewed_material_id):
                            
                            # Check if not already purchased
                            purchased_ids = [p["material_id"] for p in profile["behavior"]["purchases"]]
                            if str(material["material_id"]) not in purchased_ids:
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
                            "rule": "preview_based",
                            "score": 4.5  # High base score
                        })
        
        return recommendations
    
    def _apply_acquisition_based_rules(self, profile, limit=5):
        """
        Previously called _apply_behavior_based_rules, focusing on recent purchases.
        """
        recommendations = []
        
        # Rule: Recent Acquisitions - recommend materials with same grade/subject and similar price
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
                        "rule": "recent_acquisition",
                        "score": 4.0  # High but lower than view/preview
                    })
        
        return recommendations
    
    def _apply_search_based_rules(self, profile, limit=5):
        """
        NEW: Apply recommendations based on search queries (29% correlation).
        """
        recommendations = []
        
        # Check if user has search history
        if profile["behavior"]["searches"]:
            # Get recent searches (last 3)
            recent_searches = sorted(
                profile["behavior"]["searches"],
                key=lambda x: datetime.strptime(x["date"], "%Y-%m-%d"),
                reverse=True
            )[:3]
            
            # Extract categories and grades from recent searches
            search_categories = [s["material_category"] for s in recent_searches if "material_category" in s]
            search_grades = [s["class_grade"] for s in recent_searches if "class_grade" in s]
            
            # Count frequencies
            category_counts = Counter(search_categories)
            grade_counts = Counter(search_grades)
            
            # Get most common category and grade from searches
            most_common_category = category_counts.most_common(1)[0][0] if category_counts else None
            most_common_grade = grade_counts.most_common(1)[0][0] if grade_counts else None
            
            if most_common_category and most_common_grade:
                # Find materials matching search patterns
                matching_materials = []
                for material in self.material_pool:
                    if (material["category"] == most_common_category and 
                        material["class_grade"] == most_common_grade):
                        
                        # Check if not already purchased
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
                        "rule": "search_based",
                        "score": 3.5
                    })
        
        return recommendations
    
    def _apply_cart_based_rules(self, profile, limit=5):
        """
        NEW: Apply recommendations based on cart additions (20-23% correlation).
        """
        recommendations = []
        
        # Extract cart additions from interactions
        cart_interactions = [i for i in profile["behavior"]["interactions"] if i["type"] == "add_to_cart"]
        
        if cart_interactions:
            # Get most recent cart addition
            recent_cart = sorted(
                cart_interactions,
                key=lambda x: datetime.strptime(x["date"], "%Y-%m-%d"),
                reverse=True
            )[0]
            
            cart_material_id = recent_cart["material_id"]
            
            if cart_material_id in self.data_loader.materials:
                cart_material = self.data_loader.materials[cart_material_id]
                
                # Find materials with same category and grade level
                similar_materials = []
                for material in self.material_pool:
                    if (material["category"] == cart_material["category"] and 
                        material["class_grade"] == cart_material["class_grade"] and 
                        str(material["material_id"]) != cart_material_id):
                        
                        # Check if not already purchased
                        purchased_ids = [p["material_id"] for p in profile["behavior"]["purchases"]]
                        if str(material["material_id"]) not in purchased_ids:
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
                        "rule": "cart_based",
                        "score": 3.0
                    })
        
        return recommendations
    
    def _apply_favorites_based_rules(self, profile, limit=5):
        """
        Apply favorites-based rules with lower priority based on correlation data.
        """
        recommendations = []
        
        if profile["behavior"]["favorites"]:
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
                        
                        # Check if not already purchased
                        purchased_ids = [p["material_id"] for p in profile["behavior"]["purchases"]]
                        if str(material["material_id"]) not in purchased_ids:
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
                        "rule": "favorites_based",
                        "score": 2.5  # Lower score due to lower correlation
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
                    "rule": "category_grade_preference",
                    "score": 2.0
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
                        "rule": "price_preference",
                        "score": 1.5
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
                    "rule": "popular_by_grade",
                    "score": 1.0
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
                        "rule": "overall_popular",
                        "score": 0.5
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