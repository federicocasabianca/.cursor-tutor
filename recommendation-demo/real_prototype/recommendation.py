import random
import datetime
from collections import defaultdict, Counter
from typing import Dict, List, Any, Set, Tuple

# Import from user_profiling.py
from user_profiling import DataRepository, UserProfiler, PersonalizationService

class MaterialRecommender:
    """Recommends teaching materials based on user profiles"""
    
    def __init__(self, repository: DataRepository):
        self.repository = repository
        
        # Configuration parameters for recommendation
        self.config = {
            # Distribution of recommendations across different categories
            "category_distribution": {
                "top_categories": 0.7,  # 70% from top categories
                "related_categories": 0.2,  # 20% from related categories
                "discovery": 0.1  # 10% discovery (different categories)
            },
            
            # Price range distribution
            "price_distribution": {
                "preferred": 0.7,  # 70% from preferred price range
                "adjacent": 0.2,  # 20% from adjacent price ranges
                "other": 0.1  # 10% from any price range
            },
            
            # Freshness factors (weight multipliers)
            "freshness": {
                "recent": 1.5,  # Materials less than 3 months old
                "standard": 1.0,  # Materials 3-12 months old
                "older": 0.7  # Materials older than 12 months
            },
            
            # Maximum number of materials from the same author (increased from 2 to 4)
            "max_per_author": 4
        }
        
        # Define category relationships (for related categories)
        # This would ideally come from a taxonomy service or be learned from data
        self.related_categories = self._build_category_relationships()
    
    def _build_category_relationships(self) -> Dict[str, List[str]]:
        """
        Build relationships between categories
        In a production system, this would be more sophisticated,
        possibly using semantic similarity or co-occurrence data
        """
        # Simple mapping of categories to related ones
        # This is a placeholder - in production, this would be data-driven
        relationships = defaultdict(list)
        
        # Extract all categories from materials
        all_categories = set()
        for material in self.repository.get_materials().values():
            categories = material.get("categories", "")
            for category in self._extract_categories(categories):
                all_categories.add(category)
        
        # For demonstration, create some simple relationships
        # Based on keyword matching (in a real system this would be more sophisticated)
        for category in all_categories:
            for other_category in all_categories:
                if category != other_category:
                    # If categories share words, consider them related
                    category_words = set(category.lower().split())
                    other_words = set(other_category.lower().split())
                    if category_words.intersection(other_words):
                        relationships[category].append(other_category)
        
        return dict(relationships)
    
    def _extract_categories(self, categories_str: str) -> List[str]:
        """Extract individual categories from comma-separated string"""
        if not categories_str or categories_str == "Unknown":
            return []
        return [cat.strip() for cat in categories_str.split(",")]
    
    def _extract_grades(self, grades_str: str) -> List[str]:
        """Extract individual grade levels from comma-separated string"""
        if not grades_str or grades_str == "Unknown":
            return []
        return [grade.strip() for grade in grades_str.split(",")]
    
    def _get_user_interactions(self, user_id: str) -> Set[str]:
        """Get all material IDs the user has interacted with (purchased or downloaded)"""
        user_events = self.repository.get_user_events(user_id)
        
        # Collect material IDs the user has already purchased or downloaded
        interacted_materials = set()
        
        for event_type in ["purchases", "freeDownload"]:
            for event in user_events.get(event_type, []):
                material_id = event.get("material_id")
                if material_id:
                    interacted_materials.add(material_id)
        
        return interacted_materials
    
    def _get_freshness_score(self, material: Dict) -> float:
        """Calculate a freshness score for a material based on its age"""
        # Get current time and material creation/update times
        now = datetime.datetime.now()
        
        try:
            created_at = datetime.datetime.strptime(
                material.get("created_at", "").split()[0], "%Y-%m-%d"
            )
        except:
            created_at = now - datetime.timedelta(days=365)  # Default to 1 year old
        
        try:
            updated_at = datetime.datetime.strptime(
                material.get("updated_at", "").split()[0], "%Y-%m-%d"
            )
        except:
            updated_at = created_at
        
        # Use the most recent date between creation and update
        latest_date = max(created_at, updated_at)
        
        # Calculate age in days
        age_days = (now - latest_date).days
        
        # Assign freshness multiplier based on age
        if age_days < 90:  # Less than 3 months
            return self.config["freshness"]["recent"]
        elif age_days < 365:  # 3-12 months
            return self.config["freshness"]["standard"]
        else:  # Older than 12 months
            return self.config["freshness"]["older"]
    
    def _is_price_adjacent(self, price_range: str, preferred_range: str) -> bool:
        """Check if a price range is adjacent to the preferred range"""
        # Define the order of price ranges
        range_order = ["free", "low", "medium", "high"]
        
        if price_range == preferred_range:
            return False
        
        try:
            price_idx = range_order.index(price_range)
            preferred_idx = range_order.index(preferred_range)
            return abs(price_idx - preferred_idx) == 1
        except ValueError:
            return False
    
    def _get_price_range(self, price: float) -> str:
        """Determine the price range category for a given price"""
        if price == 0:
            return "free"
        elif 0 < price <= 2:
            return "low"
        elif 2 < price <= 7:
            return "medium"
        else:
            return "high"
    
    def _score_material_for_user(
        self, 
        material: Dict, 
        user_profile: Dict, 
        score_type: str
    ) -> float:
        """
        Score a material based on user profile and scoring type
        
        Args:
            material: Material to score
            user_profile: User profile from UserProfiler
            score_type: Type of score to calculate ("category", "grade", "price")
            
        Returns:
            Normalized score between 0 and 1
        """
        if score_type == "category":
            # Score based on category match with user preferences
            material_categories = self._extract_categories(material.get("categories", ""))
            preferred_categories = user_profile.get("preferred_categories", [])
            category_weights = user_profile.get("category_weights", {})
            
            # Calculate score based on overlap with preferred categories
            score = 0
            for category in material_categories:
                if category in preferred_categories:
                    # Higher score for higher-ranked categories
                    rank = preferred_categories.index(category)
                    rank_weight = 1.0 / (rank + 1)  # 1.0, 0.5, 0.33 for ranks 0, 1, 2
                    score += rank_weight
                    
                    # Add weight from profile
                    score += category_weights.get(category, 0) / 100
                
                # Add smaller score for related categories
                elif any(category in self.related_categories.get(pref, []) for pref in preferred_categories):
                    score += 0.3
            
            # Normalize score
            return min(1.0, score)
        
        elif score_type == "grade":
            # Score based on grade level match
            material_grades = self._extract_grades(material.get("class_grades", ""))
            preferred_grades = user_profile.get("preferred_grades", [])
            grade_weights = user_profile.get("grade_weights", {})
            
            # Calculate score based on overlap with preferred grades
            score = 0
            for grade in material_grades:
                if grade in preferred_grades:
                    # Higher score for higher-ranked grades
                    rank = preferred_grades.index(grade)
                    rank_weight = 1.0 / (rank + 1)
                    score += rank_weight
                    
                    # Add weight from profile
                    score += grade_weights.get(grade, 0) / 100
            
            # Normalize score
            return min(1.0, score)
        
        elif score_type == "price":
            # Score based on price preference
            price = float(material.get("price", 0))
            price_range = self._get_price_range(price)
            preferred_range = user_profile.get("price_preference", "medium")
            
            if price_range == preferred_range:
                return 1.0
            elif self._is_price_adjacent(price_range, preferred_range):
                return 0.5
            else:
                return 0.2
        
        else:
            return 0.0
    
    def _filter_by_author_diversity(
        self, 
        materials: List[Dict], 
        max_per_author: int = 2
    ) -> List[Dict]:
        """
        Filter list to ensure author diversity
        
        Args:
            materials: List of materials to filter
            max_per_author: Maximum number of materials allowed per author
            
        Returns:
            Filtered list with author diversity
        """
        filtered_materials = []
        author_counts = defaultdict(int)
        
        for material in materials:
            author_id = material.get("material", {}).get("author_id", "unknown")
            
            if author_counts[author_id] < max_per_author:
                filtered_materials.append(material)
                author_counts[author_id] += 1
        
        return filtered_materials
    
    def recommend_materials(
        self, 
        user_profile: Dict, 
        limit: int = 10,
        diversity_factor: float = 0.3
    ) -> List[Dict]:
        """
        Generate material recommendations for a user based on their profile
        Always returns the requested number of recommendations if possible
        
        Args:
            user_profile: User profile from UserProfiler
            limit: Target number of recommendations to return
            diversity_factor: Weight given to diversity (0-1)
            
        Returns:
            List of recommended materials
        """
        user_id = user_profile.get("user_id")
        if not user_id:
            return []
        
        # Get materials the user has already interacted with
        interacted_materials = self._get_user_interactions(user_id)
        
        # Get all available materials
        all_materials = self.repository.get_materials()
        
        # Filter out materials the user has already purchased or downloaded
        candidate_materials = {
            mid: material for mid, material in all_materials.items()
            if mid not in interacted_materials
        }
        
        if not candidate_materials:
            return []
        
        # Score each material based on user profile
        scored_materials = []
        
        for material_id, material in candidate_materials.items():
            # Skip materials with missing key data
            if not material.get("categories") or not material.get("class_grades"):
                continue
            
            # Calculate individual scores
            category_score = self._score_material_for_user(material, user_profile, "category")
            grade_score = self._score_material_for_user(material, user_profile, "grade")
            price_score = self._score_material_for_user(material, user_profile, "price")
            
            # Get freshness factor
            freshness_factor = self._get_freshness_score(material)
            
            # Bestseller rating as a quality factor (normalized)
            try:
                bestseller_score = min(1.0, float(material.get("bestseller_rating", 0)) / 1000)
            except:
                bestseller_score = 0.0
            
            # Calculate combined score
            # Weights can be adjusted based on what's most important
            combined_score = (
                (category_score * 0.35) +  # Category match
                (grade_score * 0.25) +     # Grade match
                (price_score * 0.15) +     # Price match
                (bestseller_score * 0.15)  # Quality indicator
            ) * freshness_factor           # Freshness multiplier
            
            # Add randomness for diversity
            randomness = random.random() * diversity_factor
            final_score = (combined_score * (1 - diversity_factor)) + randomness
            
            scored_materials.append({
                "material_id": material_id,
                "material": material,
                "score": final_score,
                "category_score": category_score,
                "grade_score": grade_score,
                "price_score": price_score,
                "freshness_factor": freshness_factor,
                "bestseller_score": bestseller_score,
                "is_fallback": False  # Mark as regular recommendation
            })
        
        # Sort by score
        sorted_materials = sorted(scored_materials, key=lambda x: x["score"], reverse=True)
        
        # IMPROVED: If we need more recommendations, add bestseller fallback items
        if len(sorted_materials) < limit:
            # Create a list of unused materials (not in scored_materials)
            used_material_ids = {item["material_id"] for item in sorted_materials}
            
            bestseller_materials = []
            for material_id, material in candidate_materials.items():
                # Skip if already scored or missing bestseller rating
                if material_id in used_material_ids or not material.get("bestseller_rating"):
                    continue
                
                # Get freshness factor
                freshness_factor = self._get_freshness_score(material)
                
                # Use only bestseller rating for scoring
                try:
                    bestseller_score = min(1.0, float(material.get("bestseller_rating", 0)) / 1000)
                except:
                    bestseller_score = 0
                
                # Apply freshness to the bestseller score
                final_score = bestseller_score * freshness_factor
                
                bestseller_materials.append({
                    "material_id": material_id,
                    "material": material,
                    "score": final_score,
                    "category_score": 0.0,  # No category match for fallback
                    "grade_score": 0.0,     # No grade match for fallback
                    "price_score": 0.0,     # No price match for fallback
                    "freshness_factor": freshness_factor,
                    "bestseller_score": bestseller_score,
                    "is_fallback": True     # Mark as fallback recommendation
                })
            
            # Sort bestseller fallback items by score
            bestseller_materials.sort(key=lambda x: x["score"], reverse=True)
            
            # Add top bestseller materials to the candidate pool
            sorted_materials.extend(bestseller_materials[:limit * 2])
        
        # Select top materials up to the limit
        top_materials = sorted_materials[:min(limit, len(sorted_materials))]
        
        # Format the recommendations
        recommendations = []
        for item in top_materials:
            material = item["material"]
            is_fallback = item.get("is_fallback", False)
            
            recommendations.append({
                "material_id": item["material_id"],
                "title": material.get("material_title", ""),
                "price": material.get("price", ""),
                "categories": material.get("categories", ""),
                "class_grades": material.get("class_grades", ""),
                "author_id": material.get("author_id", "unknown"),
                "score": item["score"],
                "is_fallback": is_fallback,
                "recommendation_factors": {
                    "category_match": item["category_score"],
                    "grade_match": item["grade_score"],
                    "price_match": item["price_score"],
                    "freshness": item["freshness_factor"],
                    "popularity": item["bestseller_score"]
                }
            })
        
        return recommendations


class RecommendationService:
    """Service to provide recommendations based on user profiles"""
    
    def __init__(self, data_path: str = "./data/"):
        # Create connections to the user profiling components
        self.repository = DataRepository(data_path)
        self.profiler = UserProfiler(self.repository)
        self.recommender = MaterialRecommender(self.repository)
    
    def get_recommendations_for_user(
        self, 
        user_id: str, 
        limit: int = 10,
        diversity_factor: float = 0.3
    ) -> List[Dict]:
        """Get recommendations for a specific user"""
        # Get user profile using the profiler from user_profiling.py
        user_profile = self.profiler.create_user_profile(user_id)
        
        # Generate recommendations based on the profile
        return self.recommender.recommend_materials(
            user_profile,
            limit=limit,
            diversity_factor=diversity_factor
        )
    
    def explain_recommendations(self, recommendations: List[Dict]) -> Dict[str, Any]:
        """Generate explanation for a set of recommendations"""
        
        if not recommendations:
            return {"explanation": "No recommendations available"}
        
        # Analyze composition of recommendations
        categories = []
        grades = []
        price_ranges = []
        freshness = {"recent": 0, "standard": 0, "older": 0}
        
        for rec in recommendations:
            # Extract categories
            for cat in self._extract_categories(rec.get("categories", "")):
                categories.append(cat)
            
            # Extract grades
            for grade in self._extract_grades(rec.get("class_grades", "")):
                grades.append(grade)
            
            # Get price range
            price = float(rec.get("price", 0))
            price_range = self._get_price_range(price)
            price_ranges.append(price_range)
            
            # Classify freshness
            freshness_factor = rec.get("recommendation_factors", {}).get("freshness", 0)
            if freshness_factor >= 1.5:
                freshness["recent"] += 1
            elif freshness_factor >= 1.0:
                freshness["standard"] += 1
            else:
                freshness["older"] += 1
        
        # Count occurrences
        from collections import Counter
        category_counts = Counter(categories)
        grade_counts = Counter(grades)
        price_counts = Counter(price_ranges)
        
        # Create explanation
        explanation = {
            "summary": f"Generated {len(recommendations)} recommendations",
            "categories": dict(category_counts.most_common(5)),
            "grades": dict(grade_counts.most_common(5)),
            "price_distribution": dict(price_counts),
            "freshness_distribution": freshness,
            "recommendation_factors": {
                "avg_category_match": sum(r.get("recommendation_factors", {}).get("category_match", 0) for r in recommendations) / len(recommendations),
                "avg_grade_match": sum(r.get("recommendation_factors", {}).get("grade_match", 0) for r in recommendations) / len(recommendations),
                "avg_price_match": sum(r.get("recommendation_factors", {}).get("price_match", 0) for r in recommendations) / len(recommendations),
                "avg_freshness": sum(r.get("recommendation_factors", {}).get("freshness", 0) for r in recommendations) / len(recommendations),
                "avg_popularity": sum(r.get("recommendation_factors", {}).get("popularity", 0) for r in recommendations) / len(recommendations)
            }
        }
        
        return explanation
    
    def _extract_categories(self, categories_str: str) -> List[str]:
        """Extract individual categories from comma-separated string"""
        if not categories_str or categories_str == "Unknown":
            return []
        return [cat.strip() for cat in categories_str.split(",")]
    
    def _extract_grades(self, grades_str: str) -> List[str]:
        """Extract individual grade levels from comma-separated string"""
        if not grades_str or grades_str == "Unknown":
            return []
        return [grade.strip() for grade in grades_str.split(",")]
    
    def _get_price_range(self, price: float) -> str:
        """Determine the price range category for a given price"""
        if price == 0:
            return "free"
        elif 0 < price <= 2:
            return "low"
        elif 2 < price <= 7:
            return "medium"
        else:
            return "high"


# Example usage when run directly
if __name__ == "__main__":
    service = RecommendationService()
    
    # Get recommendations for a user
    user_id = "23759"
    recommendations = service.get_recommendations_for_user(
        user_id=user_id,
        limit=10,
        diversity_factor=0.3
    )
    
    print(f"\nTop recommendations for user {user_id}:")
    for i, rec in enumerate(recommendations[:5], 1):
        print(f"{i}. {rec['title']} - €{rec['price']} - Score: {rec['score']:.2f}")
        print(f"   Categories: {rec['categories']}")
        print(f"   Grades: {rec['class_grades']}")
        print(f"   Factors: Category:{rec['recommendation_factors']['category_match']:.2f}, "
              f"Grade:{rec['recommendation_factors']['grade_match']:.2f}, "
              f"Price:{rec['recommendation_factors']['price_match']:.2f}, "
              f"Freshness:{rec['recommendation_factors']['freshness']:.2f}")
        print()
    
    # Get explanation of recommendations
    explanation = service.explain_recommendations(recommendations)
    print("\nRecommendation Explanation:")
    print(f"Summary: {explanation['summary']}")
    print(f"Category Distribution: {explanation['categories']}")
    print(f"Grade Distribution: {explanation['grades']}")
    print(f"Price Distribution: {explanation['price_distribution']}")
    print(f"Freshness: Recent: {explanation['freshness_distribution']['recent']}, "
          f"Standard: {explanation['freshness_distribution']['standard']}, "
          f"Older: {explanation['freshness_distribution']['older']}")
    print("\nAverage Factors:")
    for factor, value in explanation['recommendation_factors'].items():
        print(f"  {factor}: {value:.2f}")