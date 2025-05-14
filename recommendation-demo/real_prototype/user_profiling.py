import json
import datetime
from collections import defaultdict, Counter
import math
from typing import Dict, List, Tuple, Any, Optional

##############################################
# Data Access Layer
##############################################

class DataLoader:
    """Responsible for loading data from various sources"""
    
    @staticmethod
    def load_json_file(file_path: str) -> List[Dict]:
        """Load data from a JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except Exception as e:
            print(f"Error loading file {file_path}: {e}")
            return []
    
    def load_event_data(self, event_type: str, file_path: str) -> List[Dict]:
        """Load specific event type data"""
        return self.load_json_file(file_path)
    
    def load_material_data(self, file_path: str) -> List[Dict]:
        """Load material inventory data"""
        return self.load_json_file(file_path)


class DataRepository:
    """Manages access to all data sources"""
    
    def __init__(self, base_path: str = "./data/"):
        self.base_path = base_path
        self.loader = DataLoader()
        self._event_data = None
        self._materials = None
    
    def get_event_data(self) -> Dict[str, List[Dict]]:
        """Get all event data (lazy loading)"""
        if self._event_data is None:
            self._event_data = self._load_all_event_data()
        return self._event_data
    
    def get_materials(self) -> Dict[str, Dict]:
        """Get materials inventory (lazy loading)"""
        if self._materials is None:
            materials_list = self.loader.load_material_data(f"{self.base_path}materials.json")
            self._materials = {item["material_id"]: item for item in materials_list}
        return self._materials
    
    def _load_all_event_data(self) -> Dict[str, List[Dict]]:
        """Load all user event data"""
        event_files = {
            "purchases": "purchase.json",
            "viewMaterial": "viewMaterial.json",
            "showMaterialPreview": "showMaterialPreview.json",
            "addToCart": "addToCart.json",
            "freeDownload": "freeDownload.json",
            "addToFavorites": "addToFavorites.json",
            "searches": "searches.json"
        }
        
        data = {}
        for event_type, file_name in event_files.items():
            data[event_type] = self.loader.load_event_data(
                event_type, 
                f"{self.base_path}{file_name}"
            )
        
        return data
    
    def get_user_events(self, user_id: str) -> Dict[str, List[Dict]]:
        """Get all events for a specific user"""
        all_events = self.get_event_data()
        user_events = {}
        
        for event_type, events in all_events.items():
            user_events[event_type] = [
                event for event in events 
                if event.get("user_id") == user_id
            ]
        
        return user_events
    
    def get_top_users_by_gmv(self, limit: int = 10) -> List[str]:
        """Get top users by GMV"""
        purchases = self.get_event_data().get("purchases", [])
        
        user_gmv = defaultdict(float)
        for purchase in purchases:
            user_id = purchase.get("user_id")
            if user_id:
                user_gmv[user_id] += float(purchase.get("price_euro", 0))
        
        return [user_id for user_id, _ in sorted(
            user_gmv.items(), key=lambda x: x[1], reverse=True
        )[:limit]]


##############################################
# Domain Layer
##############################################

class EventProcessor:
    """Processes user events and extracts insights with explicit priority handling"""
    
    def __init__(self):
        # Define weights based on the correlation analysis
        # Purchases have maximum priority (1.0)
        self.grade_weights = {
            "purchases": 1.0,  # Maximum weight for actual purchases
            "viewMaterial": 0.46,
            "showMaterialPreview": 0.32,
            "searches": 0.0,  # No data to match with grade
            "addToCart": 0.20,
            "freeDownload": 0.11,
            "addToFavorites": 0.10
        }
        
        self.subject_weights = {
            "purchases": 1.0,  # Maximum weight for actual purchases
            "viewMaterial": 0.52,
            "showMaterialPreview": 0.36,
            "searches": 0.29,
            "addToCart": 0.23,
            "freeDownload": 0.12,
            "addToFavorites": 0.11
        }
        
        # Explicit ordering of event types by importance
        # This can be used to prioritize processing if needed
        self.event_priority_order = [
            "purchases",  # Highest priority
            "viewMaterial",
            "showMaterialPreview",
            "addToCart",
            "searches",
            "freeDownload",
            "addToFavorites"  # Lowest priority
        ]
    
    def get_event_weight(self, event_type: str, for_grade: bool = True) -> float:
        """Get the appropriate weight for an event type"""
        if for_grade:
            return self.grade_weights.get(event_type, 0.0)
        else:
            return self.subject_weights.get(event_type, 0.0)
    
    def parse_datetime(self, time_str: str) -> datetime.datetime:
        """Parse datetime string to datetime object"""
        try:
            return datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S.%f %Z")
        except:
            try:
                # Fallback if format is different
                return datetime.datetime.strptime(time_str, "%Y-%m-%d")
            except:
                # If all parsing fails, return current time
                return datetime.datetime.now()
    
    def calculate_time_decay(self, event_time: str, reference_time: Optional[datetime.datetime] = None) -> float:
        """
        Calculate time decay factor - more recent events get higher weight
        Using exponential decay with half-life of 30 days
        """
        if reference_time is None:
            reference_time = datetime.datetime.now()
            
        event_datetime = self.parse_datetime(event_time)
        
        # Calculate days difference
        days_diff = (reference_time - event_datetime).days
        
        # Ensure days_diff is not negative
        days_diff = max(0, days_diff)
        
        # Half-life of 30 days (adjust as needed)
        half_life = 30
        
        # Exponential decay formula: weight = 2^(-days/half_life)
        decay_factor = math.pow(2, -days_diff / half_life)
        
        return decay_factor
    
    def extract_categories(self, categories_str: str) -> List[str]:
        """Extract individual categories from comma-separated string"""
        if not categories_str or categories_str == "Unknown":
            return []
        return [cat.strip() for cat in categories_str.split(",")]
    
    def extract_grades(self, grades_str: str) -> List[str]:
        """Extract individual grade levels from comma-separated string"""
        if not grades_str or grades_str == "Unknown":
            return []
        return [grade.strip() for grade in grades_str.split(",")]
    
    def get_event_time(self, event: Dict) -> str:
        """Extract time from an event with fallbacks"""
        if "time" in event:
            return event["time"]
        elif "date" in event:
            return event["date"]
        elif "last_search_date" in event:
            return event["last_search_date"]
        else:
            return datetime.datetime.now().strftime("%Y-%m-%d")


class PriceAnalyzer:
    """Analyzes price preferences and categorizes prices"""
    
    def __init__(self):
        # Price range buckets
        self.price_ranges = {
            "free": (0, 0),
            "low": (0, 2),
            "medium": (2, 7),
            "high": (7, float('inf'))
        }
    
    def get_price_range(self, price: float) -> str:
        """Determine the price range category for a given price"""
        if price == 0:
            return "free"
        elif 0 < price <= 2:
            return "low"
        elif 2 < price <= 7:
            return "medium"
        else:
            return "high"
    
    def analyze_price_preferences(self, purchases: List[Dict]) -> Dict[str, float]:
        """Analyze price preferences based on purchase history"""
        price_ranges_counter = Counter()
        
        for purchase in purchases:
            price = float(purchase.get("price_euro", 0))
            price_range = self.get_price_range(price)
            
            # Apply time decay to give more weight to recent purchases
            time_str = purchase.get("time", purchase.get("date", ""))
            if time_str:
                time_decay = EventProcessor().calculate_time_decay(time_str)
                price_ranges_counter[price_range] += time_decay
            else:
                # If no time information, just count as 1
                price_ranges_counter[price_range] += 1
        
        # Convert to relative weights
        total = sum(price_ranges_counter.values()) or 1
        return {k: v/total for k, v in price_ranges_counter.items()}


class SearchAnalyzer:
    """Analyzes search behavior to extract preferences"""
    
    def __init__(self, materials: Dict[str, Dict], event_processor: EventProcessor):
        self.materials = materials
        self.event_processor = event_processor
    
    def extract_search_insights(self, searches: List[Dict], weight: float) -> Tuple[Counter, Counter]:
        """Extract category and grade insights from search queries"""
        categories_counter = Counter()
        grades_counter = Counter()
        
        for search in searches:
            query = search.get("search_keyword", "").lower()
            frequency = int(search.get("search_frequency", 1))
            time_decay = self.event_processor.calculate_time_decay(
                search.get("last_search_date", "")
            )
            
            # Apply subject weight for searches
            weighted_score = weight * time_decay * frequency
            
            # Try to extract subject information from the search query
            # This is a simple approach - in a real system you'd want more sophisticated NLP
            for material in self.materials.values():
                categories = self.event_processor.extract_categories(material.get("categories", ""))
                for category in categories:
                    if category.lower() in query:
                        categories_counter[category] += weighted_score
                
                # Try to match grade levels in search query
                for grade in self.event_processor.extract_grades(material.get("class_grades", "")):
                    if grade.lower() in query:
                        grades_counter[grade] += weighted_score * 0.5  # Lower weight since no direct correlation
        
        return categories_counter, grades_counter


class UserProfiler:
    """Creates user profiles based on their behavior with explicit event prioritization"""
    
    def __init__(self, repository: DataRepository):
        self.repository = repository
        self.event_processor = EventProcessor()
        self.price_analyzer = PriceAnalyzer()
        self.search_analyzer = SearchAnalyzer(
            repository.get_materials(), 
            self.event_processor
        )
    
    def get_reference_time(self, user_events: Dict[str, List[Dict]]) -> datetime.datetime:
        """Get the most recent event time as reference"""
        all_times = []
        
        for events in user_events.values():
            for event in events:
                time_str = self.event_processor.get_event_time(event)
                if time_str:
                    all_times.append(self.event_processor.parse_datetime(time_str))
        
        return max(all_times) if all_times else datetime.datetime.now()
    
    def process_material_based_events(
        self, 
        events: List[Dict], 
        event_type: str, 
        reference_time: datetime.datetime,
        materials: Dict[str, Dict]
    ) -> Tuple[Counter, Counter]:
        """Process events that are related to materials"""
        categories_counter = Counter()
        grades_counter = Counter()
        
        for event in events:
            material_id = event.get("material_id")
            if not material_id:
                continue
            
            # Get material details if available
            material = materials.get(material_id)
            if not material:
                # If material is not in our inventory but we have category info in the event
                material = event
            
            # Calculate time decay
            time_str = self.event_processor.get_event_time(event)
            time_decay = self.event_processor.calculate_time_decay(time_str, reference_time)
            
            # Process categories
            categories = self.event_processor.extract_categories(material.get("categories", ""))
            cat_weight = self.event_processor.get_event_weight(event_type, False) * time_decay
            for category in categories:
                categories_counter[category] += cat_weight
            
            # Process grade levels
            grades = self.event_processor.extract_grades(material.get("class_grades", ""))
            grade_weight = self.event_processor.get_event_weight(event_type, True) * time_decay
            for grade in grades:
                grades_counter[grade] += grade_weight
        
        return categories_counter, grades_counter
    
    def create_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Create a comprehensive profile for a user considering all events with appropriate weighting"""
        # Get all user events
        user_events = self.repository.get_user_events(user_id)
        materials = self.repository.get_materials()
        
        # Get reference time for time decay calculation
        reference_time = self.get_reference_time(user_events)
        
        # Initialize counters for aggregation
        all_categories = Counter()
        all_grades = Counter()
        
        # Log event counts for transparency
        event_counts = {k: len(v) for k, v in user_events.items()}
        
        # Ensure we process all events, in order of priority
        for event_type in self.event_processor.event_priority_order:
            events = user_events.get(event_type, [])
            
            if event_type == "searches":
                # Special handling for searches
                cat_counter, grade_counter = self.search_analyzer.extract_search_insights(
                    events, 
                    self.event_processor.get_event_weight(event_type, False)
                )
            else:
                # Material-based events
                cat_counter, grade_counter = self.process_material_based_events(
                    events, 
                    event_type, 
                    reference_time,
                    materials
                )
            
            # Aggregate counters
            all_categories.update(cat_counter)
            all_grades.update(grade_counter)
        
        # Analyze price preferences - focus on purchases for price analysis
        price_preferences = self.price_analyzer.analyze_price_preferences(
            user_events.get("purchases", [])
        )
        
        # Determine top price preference
        top_price = max(price_preferences.items(), key=lambda x: x[1])[0] if price_preferences else "medium"
        
        # Create the profile
        profile = {
            "user_id": user_id,
            "preferred_categories": [cat for cat, _ in all_categories.most_common(3)],
            "preferred_grades": [grade for grade, _ in all_grades.most_common(3)],
            "price_preference": top_price,
            "category_weights": dict(all_categories),
            "grade_weights": dict(all_grades),
            "price_range_weights": price_preferences,
            "event_counts": event_counts,
            "profile_generation_time": datetime.datetime.now().isoformat()
        }
        
        return profile


##############################################
# Service Layer 
##############################################

class PersonalizationService:
    """Public interface for personalization services"""
    
    def __init__(self, data_path: str = "./data/"):
        self.repository = DataRepository(data_path)
        self.profiler = UserProfiler(self.repository)
    
    def get_top_user_profiles(self, top_n: int = 10) -> Dict[str, Dict[str, Any]]:
        """Get profiles for top N users by GMV"""
        top_users = self.repository.get_top_users_by_gmv(top_n)
        profiles = {}
        
        for user_id in top_users:
            profiles[user_id] = self.profiler.create_user_profile(user_id)
        
        return profiles
    
    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Get profile for a specific user"""
        return self.profiler.create_user_profile(user_id)
    
    def get_user_behavior(self, user_id: str) -> Dict[str, List[Dict]]:
        """Get all recorded behaviors for a specific user"""
        return self.repository.get_user_events(user_id)
    
    def analyze_profile_contribution(self, user_id: str) -> Dict[str, Any]:
        """Analyze how different event types contribute to a user's profile"""
        user_events = self.repository.get_user_events(user_id)
        materials = self.repository.get_materials()
        reference_time = self.profiler.get_reference_time(user_events)
        
        event_contributions = {}
        
        # Analyze each event type separately
        for event_type in self.profiler.event_processor.event_priority_order:
            events = user_events.get(event_type, [])
            
            if event_type == "searches":
                cat_counter, grade_counter = self.profiler.search_analyzer.extract_search_insights(
                    events, 
                    self.profiler.event_processor.get_event_weight(event_type, False)
                )
            else:
                cat_counter, grade_counter = self.profiler.process_material_based_events(
                    events, 
                    event_type, 
                    reference_time,
                    materials
                )
            
            # Record top contributions from this event type
            event_contributions[event_type] = {
                "count": len(events),
                "top_categories": [cat for cat, _ in cat_counter.most_common(3)],
                "top_grades": [grade for grade, _ in grade_counter.most_common(3)],
                "grade_weight": self.profiler.event_processor.get_event_weight(event_type, True),
                "subject_weight": self.profiler.event_processor.get_event_weight(event_type, False)
            }
        
        return event_contributions


# Example usage when run directly
if __name__ == "__main__":
    service = PersonalizationService()
    
    # Get profiles for top 10 users
    top_profiles = service.get_top_user_profiles(10)
    print(f"Generated profiles for {len(top_profiles)} users")
    
    # Example: Get profile for a specific user
    user_profile = service.get_user_profile("23759")
    print(f"\nProfile for user 23759:")
    print(f"Preferred categories: {user_profile['preferred_categories']}")
    print(f"Preferred grades: {user_profile['preferred_grades']}")
    print(f"Price preference: {user_profile['price_preference']}")
    
    # Example: Get behavior data for a user
    user_behavior = service.get_user_behavior("23759")
    print(f"\nBehavior counts for user 23759:")
    for event_type, events in user_behavior.items():
        print(f"{event_type}: {len(events)} events")
    
    # Analyze how different events contribute to the profile
    contributions = service.analyze_profile_contribution("23759")
    print("\nEvent contribution analysis:")
    for event_type, data in contributions.items():
        print(f"\n{event_type.upper()} (count: {data['count']}):")
        print(f"  Grade weight: {data['grade_weight']}")
        print(f"  Subject weight: {data['subject_weight']}")
        print(f"  Top categories: {data['top_categories']}")
        print(f"  Top grades: {data['top_grades']}")