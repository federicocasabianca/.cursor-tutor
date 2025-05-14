import json
import os
import numpy as np
from datetime import datetime
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Set, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class DataLoader:
    """
    Component responsible for loading and preprocessing the enhanced data.
    """
    def __init__(self, data_path="."):
        self.data_path = data_path
        self.materials = {}
        self.user_profiles = {}
    
    def load_data(self):
        """
        Load all data files from the specified path.
        """
        # Load enhanced materials
        with open(os.path.join(self.data_path, "materials_enhanced.json"), "r") as f:
            materials_data = json.load(f)
            # Index materials by ID for faster lookup
            self.materials = {str(item["material_id"]): item for item in materials_data}
        
        # Load enhanced user profiles
        with open(os.path.join(self.data_path, "user_profile_enhanced.json"), "r") as f:
            user_profiles_data = json.load(f)
            # Index user profiles by ID
            self.user_profiles = {item["user_id"]: item for item in user_profiles_data}
        
        print(f"Loaded {len(self.materials)} materials")
        print(f"Loaded {len(self.user_profiles)} user profiles")
        
        return self
    
    def prepare_content_features(self):
        """
        Prepare content-based features for all materials.
        """
        # Create content feature text for TF-IDF
        for material_id, material in self.materials.items():
            # Combine descriptive text fields for better text analysis
            content_text = [
                material.get("title", ""),
                material.get("description", ""),
                material.get("category", ""),
                material.get("subcategory", ""),
                material.get("class_grade", ""),
            ]
            
            # Add topics as individual terms for better matching
            if "topics" in material and isinstance(material["topics"], list):
                content_text.extend(material["topics"])
            
            # Add competencies as terms for skill-based matching
            if "competencies" in material and isinstance(material["competencies"], list):
                content_text.extend(material["competencies"])
            
            # Add teaching approach for pedagogical style matching
            if "teaching_approach" in material:
                content_text.append(material["teaching_approach"])
            
            # Store as combined text
            self.materials[material_id]["content_text"] = " ".join(content_text)
        
        return self


class ContentFeatureExtractor:
    """
    Component responsible for extracting and vectorizing content features.
    """
    def __init__(self, data_loader):
        self.data_loader = data_loader
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',  # For German content, consider a custom stopwords list
            ngram_range=(1, 2)     # Include both unigrams and bigrams
        )
        self.material_feature_vectors = {}
        self.categorical_features = {}
    
    def build_feature_vectors(self):
        """
        Build content-based feature vectors for all materials.
        """
        # Get all content text for TF-IDF training
        material_ids = []
        content_texts = []
        
        for material_id, material in self.data_loader.materials.items():
            if "content_text" in material:
                material_ids.append(material_id)
                content_texts.append(material["content_text"])
        
        # Create TF-IDF vectors for text content
        tfidf_matrix = self.tfidf_vectorizer.fit_transform(content_texts)
        
        # Store TF-IDF vectors by material ID
        for i, material_id in enumerate(material_ids):
            self.material_feature_vectors[material_id] = tfidf_matrix[i]
        
        # Extract categorical features
        self._extract_categorical_features()
        
        return self
    
    def _extract_categorical_features(self):
        """
        Extract categorical features from materials for non-text matching.
        """
        # Initialize categorical feature dictionaries
        self.categorical_features = {
            "grade_level": {},
            "category": {},
            "subcategory": {},
            "teaching_approach": {},
            "complexity_level": {},
            "format": {},
            "seasonal_relevance": {},
            "is_bundle": {}
        }
        
        # Extract features from each material
        for material_id, material in self.data_loader.materials.items():
            # Grade level
            if "class_grade" in material:
                self.categorical_features["grade_level"][material_id] = material["class_grade"]
            
            # Category
            if "category" in material:
                self.categorical_features["category"][material_id] = material["category"]
            
            # Subcategory
            if "subcategory" in material:
                self.categorical_features["subcategory"][material_id] = material["subcategory"]
            
            # Teaching approach
            if "teaching_approach" in material:
                self.categorical_features["teaching_approach"][material_id] = material["teaching_approach"]
            
            # Complexity level
            if "complexity_level" in material:
                self.categorical_features["complexity_level"][material_id] = material["complexity_level"]
            
            # Format
            if "format" in material:
                self.categorical_features["format"][material_id] = material["format"]
            
            # Seasonal relevance
            if "seasonal_relevance" in material and isinstance(material["seasonal_relevance"], list):
                self.categorical_features["seasonal_relevance"][material_id] = material["seasonal_relevance"]
            
            # Is bundle
            if "is_bundle" in material:
                self.categorical_features["is_bundle"][material_id] = material["is_bundle"]
    
    def get_tfidf_similarity(self, material_id1, material_id2):
        """
        Calculate cosine similarity between two materials based on TF-IDF vectors.
        """
        if material_id1 not in self.material_feature_vectors or material_id2 not in self.material_feature_vectors:
            return 0.0
        
        vec1 = self.material_feature_vectors[material_id1]
        vec2 = self.material_feature_vectors[material_id2]
        
        similarity = cosine_similarity(vec1, vec2)[0][0]
        return float(similarity)
    
    def get_categorical_similarity(self, material_id1, material_id2):
        """
        Calculate similarity between two materials based on categorical features.
        """
        if material_id1 not in self.data_loader.materials or material_id2 not in self.data_loader.materials:
            return 0.0
        
        # Initialize similarity score and feature count
        similarity_score = 0.0
        feature_count = 0
        
        # Check each categorical feature
        for feature_name, feature_dict in self.categorical_features.items():
            if material_id1 in feature_dict and material_id2 in feature_dict:
                feature_count += 1
                
                # For list features (e.g., seasonal_relevance)
                if isinstance(feature_dict[material_id1], list) and isinstance(feature_dict[material_id2], list):
                    # Calculate Jaccard similarity for lists
                    set1 = set(feature_dict[material_id1])
                    set2 = set(feature_dict[material_id2])
                    if set1 or set2:  # Avoid division by zero
                        intersection = len(set1.intersection(set2))
                        union = len(set1.union(set2))
                        similarity_score += intersection / union
                
                # For scalar features
                else:
                    if feature_dict[material_id1] == feature_dict[material_id2]:
                        similarity_score += 1.0
        
        # Calculate average similarity across all features
        if feature_count > 0:
            return similarity_score / feature_count
        else:
            return 0.0
    
    def get_combined_similarity(self, material_id1, material_id2, text_weight=0.6):
        """
        Calculate combined similarity using both TF-IDF and categorical features.
        """
        text_similarity = self.get_tfidf_similarity(material_id1, material_id2)
        categorical_similarity = self.get_categorical_similarity(material_id1, material_id2)
        
        # Weighted combination
        combined_similarity = (text_weight * text_similarity) + ((1 - text_weight) * categorical_similarity)
        return combined_similarity


class UserProfileAnalyzer:
    """
    Component responsible for analyzing user profiles and generating content preferences.
    """
    def __init__(self, data_loader, feature_extractor):
        self.data_loader = data_loader
        self.feature_extractor = feature_extractor
        self.user_content_preferences = {}
        self.user_preferred_materials = {}
        self.seasonal_context = self._get_current_season()
    
    def _get_current_season(self):
        """
        Determine current season based on date.
        """
        current_month = datetime.now().month
        
        if 3 <= current_month <= 5:
            return "Frühling"
        elif 6 <= current_month <= 8:
            return "Sommer"
        elif 9 <= current_month <= 11:
            return "Herbst"
        else:
            return "Winter"
    
    def analyze_user_profiles(self):
        """
        Analyze user profiles to extract content preferences.
        """
        for user_id, profile in self.data_loader.user_profiles.items():
            # Initialize user preference data
            self.user_content_preferences[user_id] = {
                "text_preferences": "",
                "categorical_preferences": {},
                "liked_material_ids": [],
                "disliked_material_ids": []
            }
            
            # Extract explicit preferences
            self._extract_explicit_preferences(user_id, profile)
            
            # Extract implicit preferences from interactions
            self._extract_implicit_preferences(user_id, profile)
            
            # Extract liked and disliked materials
            self._extract_material_preferences(user_id, profile)
            
            # Build user preference vector
            self._build_user_preference_vector(user_id)
        
        return self
    
    def _extract_explicit_preferences(self, user_id, profile):
        """
        Extract explicit preferences from user profile.
        """
        if "explicit_preferences" in profile:
            explicit_prefs = profile["explicit_preferences"]
            
            # Extract categorical preferences
            cat_prefs = self.user_content_preferences[user_id]["categorical_preferences"]
            
            # Preferred subjects (categories)
            if "preferred_subjects" in explicit_prefs and explicit_prefs["preferred_subjects"]:
                cat_prefs["category"] = explicit_prefs["preferred_subjects"]
            
            # Preferred grades
            if "preferred_grades" in explicit_prefs and explicit_prefs["preferred_grades"]:
                cat_prefs["grade_level"] = explicit_prefs["preferred_grades"]
            
            # Preferred formats
            if "preferred_formats" in explicit_prefs and explicit_prefs["preferred_formats"]:
                cat_prefs["format"] = explicit_prefs["preferred_formats"]
            
            # Preferred complexity
            if "preferred_complexity" in explicit_prefs and explicit_prefs["preferred_complexity"]:
                cat_prefs["complexity_level"] = explicit_prefs["preferred_complexity"]
            
            # Preferred teaching approaches
            if "preferred_teaching_approaches" in explicit_prefs and explicit_prefs["preferred_teaching_approaches"]:
                cat_prefs["teaching_approach"] = explicit_prefs["preferred_teaching_approaches"]
            
            # Build text representation of preferences for TF-IDF matching
            text_parts = []
            
            # Add preferred subjects to text
            if "preferred_subjects" in explicit_prefs and explicit_prefs["preferred_subjects"]:
                text_parts.extend(explicit_prefs["preferred_subjects"])
            
            # Add preferred content types to text
            if "preferred_content_types" in explicit_prefs and explicit_prefs["preferred_content_types"]:
                text_parts.extend(explicit_prefs["preferred_content_types"])
            
            # Store text preferences
            self.user_content_preferences[user_id]["text_preferences"] += " ".join(text_parts)
    
    def _extract_implicit_preferences(self, user_id, profile):
        """
        Extract implicit preferences from user profile.
        """
        if "implicit_preferences" in profile:
            implicit_prefs = profile["implicit_preferences"]
            cat_prefs = self.user_content_preferences[user_id]["categorical_preferences"]
            text_parts = []
            
            # Extract viewed subjects (categories)
            if "viewed_subjects" in implicit_prefs:
                # Get top 2 most viewed subjects
                top_subjects = sorted(
                    implicit_prefs["viewed_subjects"].items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:2]
                
                # Add to categorical preferences if not already set
                if "category" not in cat_prefs:
                    cat_prefs["category"] = [subject for subject, _ in top_subjects]
                
                # Add to text preferences
                text_parts.extend([subject for subject, _ in top_subjects])
            
            # Extract viewed grades
            if "viewed_grades" in implicit_prefs:
                # Get top grade
                top_grade = sorted(
                    implicit_prefs["viewed_grades"].items(),
                    key=lambda x: x[1],
                    reverse=True
                )[0][0]
                
                # Add to categorical preferences if not already set
                if "grade_level" not in cat_prefs:
                    cat_prefs["grade_level"] = [top_grade]
                
                # Add to text preferences
                text_parts.append(top_grade)
            
            # Extract viewed topics
            if "viewed_topics" in implicit_prefs and implicit_prefs["viewed_topics"]:
                # Add top 5 topics to text preferences
                topics = implicit_prefs["viewed_topics"][:5] if len(implicit_prefs["viewed_topics"]) > 5 else implicit_prefs["viewed_topics"]
                text_parts.extend(topics)
            
            # Extract competency focus
            if "competency_focus" in implicit_prefs and implicit_prefs["competency_focus"]:
                # Add competencies to text preferences
                text_parts.extend(implicit_prefs["competency_focus"])
            
            # Add teaching context to preferences
            if "teaching_context" in profile:
                context = profile["teaching_context"]
                
                # Add current curriculum topics
                if "current_curriculum_topics" in context and context["current_curriculum_topics"]:
                    text_parts.extend(context["current_curriculum_topics"])
                
                # Consider school type
                if "school_type" in context and context["school_type"]:
                    text_parts.append(context["school_type"])
            
            # Add to text preferences
            self.user_content_preferences[user_id]["text_preferences"] += " " + " ".join(text_parts)
    
    def _extract_material_preferences(self, user_id, profile):
        """
        Extract liked and disliked materials from user interactions.
        """
        if "interaction_history" in profile:
            history = profile["interaction_history"]
            
            # Add purchased and favorited materials as liked
            liked_materials = set()
            if "purchases" in history:
                liked_materials.update([str(material_id) for material_id in history["purchases"]])
            
            if "favorites" in history:
                liked_materials.update([str(material_id) for material_id in history["favorites"]])
            
            self.user_content_preferences[user_id]["liked_material_ids"] = list(liked_materials)
            
            # Add negative signals as disliked
            disliked_materials = set()
            if "negative_signals" in history:
                neg_signals = history["negative_signals"]
                
                if "bounced_from" in neg_signals:
                    disliked_materials.update([str(material_id) for material_id in neg_signals["bounced_from"]])
                
                if "removed_from_cart" in neg_signals:
                    disliked_materials.update([str(material_id) for material_id in neg_signals["removed_from_cart"]])
            
            self.user_content_preferences[user_id]["disliked_material_ids"] = list(disliked_materials)
    
    def _build_user_preference_vector(self, user_id):
        """
        Build a TF-IDF preference vector for the user.
        """
        user_prefs = self.user_content_preferences[user_id]
        preference_text = user_prefs["text_preferences"]
        
        # Add content from liked materials to preference text
        for material_id in user_prefs["liked_material_ids"]:
            if material_id in self.data_loader.materials and "content_text" in self.data_loader.materials[material_id]:
                # Add material content with less weight (avoid overwhelming explicit preferences)
                preference_text += " " + self.data_loader.materials[material_id]["content_text"]
        
        # Transform preference text to TF-IDF vector
        if preference_text.strip():
            user_preference_vector = self.feature_extractor.tfidf_vectorizer.transform([preference_text])
            
            # Store vector
            user_prefs["preference_vector"] = user_preference_vector


class ContentBasedRecommender:
    """
    Component responsible for generating content-based recommendations.
    """
    def __init__(self, data_loader, feature_extractor, profile_analyzer):
        self.data_loader = data_loader
        self.feature_extractor = feature_extractor
        self.profile_analyzer = profile_analyzer
        self.similarity_cache = {}
    
    def get_recommendations(self, user_id, limit=5, include_explanation=True):
        """
        Generate content-based recommendations for a user.
        """
        # Check if user exists
        if user_id not in self.profile_analyzer.user_content_preferences:
            return self._get_popularity_based_recommendations(limit)
        
        # Get user preferences
        user_prefs = self.profile_analyzer.user_content_preferences[user_id]
        
        # Get current season for seasonal relevance
        current_season = self.profile_analyzer.seasonal_context
        
        # Initialize scores for all materials
        material_scores = {}
        
        # Method 1: Content similarity to liked materials
        self._score_by_liked_materials(user_id, material_scores)
        
        # Method 2: Direct preference vector similarity
        self._score_by_preference_vector(user_id, material_scores)
        
        # Method 3: Categorical preference matching
        self._score_by_categorical_preferences(user_id, material_scores)
        
        # Method 4: Seasonal relevance boost
        self._boost_seasonal_materials(material_scores, current_season)
        
        # Filter out materials the user has already interacted with or disliked
        filtered_scores = self._filter_known_materials(user_id, material_scores)
        
        # Sort materials by score
        sorted_materials = sorted(
            filtered_scores.items(),
            key=lambda x: x[1]["total_score"],
            reverse=True
        )
        
        # Build recommendation list
        recommendations = []
        for material_id, score_data in sorted_materials[:limit]:
            material = self.data_loader.materials[material_id]
            
            rec = {
                "material_id": material_id,
                "title": material["title"],
                "category": material["category"],
                "class_grade": material["class_grade"],
                "price": material["price"],
                "bestseller_rating": material["bestseller_rating"],
                "score": score_data["total_score"]
            }
            
            # Add explanation if requested
            if include_explanation:
                rec["explanation"] = self._generate_explanation(material_id, score_data)
            
            recommendations.append(rec)
        
        return recommendations
    
    def _score_by_liked_materials(self, user_id, material_scores):
        """
        Score materials based on similarity to user's liked materials.
        """
        user_prefs = self.profile_analyzer.user_content_preferences[user_id]
        liked_materials = user_prefs["liked_material_ids"]
        
        # Skip if no liked materials
        if not liked_materials:
            return
        
        # Calculate similarity to each liked material
        for material_id in self.data_loader.materials:
            # Skip if it's a liked material itself
            if material_id in liked_materials:
                continue
            
            # Initialize if not exists
            if material_id not in material_scores:
                material_scores[material_id] = {
                    "liked_material_score": 0,
                    "preference_vector_score": 0,
                    "categorical_score": 0,
                    "seasonal_score": 0,
                    "total_score": 0,
                    "contribution_factors": []
                }
            
            # Calculate average similarity to liked materials
            similarities = []
            similar_materials = []
            
            for liked_id in liked_materials:
                # Skip if liked material doesn't exist in our data
                if liked_id not in self.data_loader.materials:
                    continue
                
                # Get similarity
                similarity = self.feature_extractor.get_combined_similarity(material_id, liked_id)
                
                if similarity > 0.5:  # Only consider significant similarities
                    similarities.append(similarity)
                    similar_materials.append(liked_id)
            
            # Calculate score based on similarities
            if similarities:
                score = sum(similarities) / len(similarities)
                material_scores[material_id]["liked_material_score"] = score
                material_scores[material_id]["total_score"] += score
                
                # Record top similar material
                if similar_materials:
                    most_similar = similar_materials[similarities.index(max(similarities))]
                    material_scores[material_id]["contribution_factors"].append({
                        "type": "similar_to_liked",
                        "related_id": most_similar,
                        "score": max(similarities)
                    })
    
    def _score_by_preference_vector(self, user_id, material_scores):
        """
        Score materials based on similarity to user's preference vector.
        """
        user_prefs = self.profile_analyzer.user_content_preferences[user_id]
        
        # Skip if no preference vector
        if "preference_vector" not in user_prefs:
            return
        
        user_vector = user_prefs["preference_vector"]
        
        # Calculate similarity to each material
        for material_id, material in self.data_loader.materials.items():
            # Skip if no content text
            if "content_text" not in material:
                continue
            
            # Initialize if not exists
            if material_id not in material_scores:
                material_scores[material_id] = {
                    "liked_material_score": 0,
                    "preference_vector_score": 0,
                    "categorical_score": 0,
                    "seasonal_score": 0,
                    "total_score": 0,
                    "contribution_factors": []
                }
            
            # Get material vector
            if material_id in self.feature_extractor.material_feature_vectors:
                material_vector = self.feature_extractor.material_feature_vectors[material_id]
                
                # Calculate cosine similarity
                similarity = float(cosine_similarity(user_vector, material_vector)[0][0])
                
                # Update score
                material_scores[material_id]["preference_vector_score"] = similarity
                material_scores[material_id]["total_score"] += similarity
                
                # Record contribution if significant
                if similarity > 0.4:
                    material_scores[material_id]["contribution_factors"].append({
                        "type": "matches_preferences",
                        "score": similarity
                    })
    
    def _score_by_categorical_preferences(self, user_id, material_scores):
        """
        Score materials based on matching categorical preferences.
        """
        user_prefs = self.profile_analyzer.user_content_preferences[user_id]
        categorical_prefs = user_prefs["categorical_preferences"]
        
        # Skip if no categorical preferences
        if not categorical_prefs:
            return
        
        # Calculate match for each material
        for material_id, material in self.data_loader.materials.items():
            # Initialize if not exists
            if material_id not in material_scores:
                material_scores[material_id] = {
                    "liked_material_score": 0,
                    "preference_vector_score": 0,
                    "categorical_score": 0,
                    "seasonal_score": 0,
                    "total_score": 0,
                    "contribution_factors": []
                }
            
            # Calculate category matches
            matches = 0
            total_categories = 0
            matching_categories = []
            
            for category_name, preferred_values in categorical_prefs.items():
                # Skip if not a valid feature
                if category_name not in self.feature_extractor.categorical_features:
                    continue
                
                # Get material's value for this category
                if material_id in self.feature_extractor.categorical_features[category_name]:
                    material_value = self.feature_extractor.categorical_features[category_name][material_id]
                    total_categories += 1
                    
                    # Check for match
                    if isinstance(preferred_values, list):
                        # For list preferences
                        if isinstance(material_value, list):
                            # Both are lists - check for intersection
                            if any(pref in material_value for pref in preferred_values):
                                matches += 1
                                matching_categories.append(category_name)
                        else:
                            # Material value is scalar - check if in preferences
                            if material_value in preferred_values:
                                matches += 1
                                matching_categories.append(category_name)
                    else:
                        # For scalar preference
                        if material_value == preferred_values:
                            matches += 1
                            matching_categories.append(category_name)
            
            # Calculate categorical score
            if total_categories > 0:
                score = matches / total_categories
                material_scores[material_id]["categorical_score"] = score
                material_scores[material_id]["total_score"] += score
                
                # Record contribution if matches found
                if matching_categories:
                    material_scores[material_id]["contribution_factors"].append({
                        "type": "category_match",
                        "matched_categories": matching_categories,
                        "score": score
                    })
    
    def _boost_seasonal_materials(self, material_scores, current_season):
        """
        Apply seasonal boost to relevant materials.
        """
        seasonal_feature = self.feature_extractor.categorical_features.get("seasonal_relevance", {})
        
        # Skip if no seasonal data
        if not seasonal_feature:
            return
        
        # Check each material for seasonal relevance
        for material_id, seasons in seasonal_feature.items():
            # Skip if material not in scores
            if material_id not in material_scores:
                continue
            
            # Skip if not a list of seasons
            if not isinstance(seasons, list):
                continue
            
            # Check if current season matches
            if current_season in seasons or "ganzjährig" in seasons:
                # Apply seasonal boost
                seasonal_boost = 0.2 if current_season in seasons else 0.1
                material_scores[material_id]["seasonal_score"] = seasonal_boost
                material_scores[material_id]["total_score"] += seasonal_boost
                
                # Record contribution
                material_scores[material_id]["contribution_factors"].append({
                    "type": "seasonal_relevance",
                    "season": current_season,
                    "score": seasonal_boost
                })
    
    def _filter_known_materials(self, user_id, material_scores):
        """
        Filter out materials the user has already interacted with or disliked.
        """
        user_prefs = self.profile_analyzer.user_content_preferences[user_id]
        liked_materials = set(user_prefs["liked_material_ids"])
        disliked_materials = set(user_prefs["disliked_material_ids"])
        
        # Filter out materials
        filtered_scores = {}
        for material_id, scores in material_scores.items():
            if material_id not in liked_materials and material_id not in disliked_materials:
                filtered_scores[material_id] = scores
        
        return filtered_scores
    
    def _generate_explanation(self, material_id, score_data):
        """
        Generate human-readable explanation for recommendation.
        """
        material = self.data_loader.materials[material_id]
        explanation_parts = []
        
        # Add explanation based on contribution factors
        for factor in score_data["contribution_factors"]:
            factor_type = factor["type"]
            
            if factor_type == "similar_to_liked":
                related_id = factor["related_id"]
                if related_id in self.data_loader.materials:
                    related_title = self.data_loader.materials[related_id]["title"]
                    similarity = factor["score"]
                    explanation_parts.append(
                        f"Ähnlich zu Material '{related_title}', das Ihnen gefallen hat (Ähnlichkeit: {similarity:.0%})"
                    )
            
            elif factor_type == "matches_preferences":
                similarity = factor["score"]
                explanation_parts.append(
                    f"Entspricht Ihren inhaltlichen Präferenzen (Übereinstimmung: {similarity:.0%})"
                )
            
            elif factor_type == "category_match":
                matched = factor["matched_categories"]
                if "category" in matched:
                    explanation_parts.append(f"Passt zu Ihrem bevorzugten Fach: {material['category']}")
                if "grade_level" in matched:
                    explanation_parts.append(f"Passt zu Ihrer bevorzugten Klassenstufe: {material['class_grade']}")
                if "teaching_approach" in matched and "teaching_approach" in material:
                    explanation_parts.append(f"Entspricht Ihrem bevorzugten Lehransatz: {material['teaching_approach']}")
            
            elif factor_type == "seasonal_relevance":
                season = factor["season"]
                explanation_parts.append(f"Relevant für die aktuelle Jahreszeit: {season}")
        
        # Add topic information if available
        if "topics" in material and isinstance(material["topics"], list) and material["topics"]:
            topics_str = ", ".join(material["topics"][:3])  # Limit to top 3 topics
            explanation_parts.append(f"Behandelt relevante Themen: {topics_str}")
        
        return explanation_parts
    
    def _get_popularity_based_recommendations(self, limit=5):
        """
        Fallback recommendations for new users based on popularity.
        """
        # Sort materials by bestseller rating
        sorted_materials = sorted(
            self.data_loader.materials.items(),
            key=lambda x: float(x[1].get("bestseller_rating", 0)),
            reverse=True
        )
        
        # Build recommendation list
        recommendations = []
        for material_id, material in sorted_materials[:limit]:
            recommendations.append({
                "material_id": material_id,
                "title": material["title"],
                "category": material["category"],
                "class_grade": material["class_grade"],
                "price": material["price"],
                "bestseller_rating": material["bestseller_rating"],
                "explanation": ["Beliebtes Material in dieser Kategorie"],
                "score": 0.0
            })
        
        return recommendations


class PersonalizationService:
    """
    Main service class that orchestrates the content-based personalization process.
    """
    def __init__(self, data_path="."):
        self.data_loader = None
        self.feature_extractor = None
        self.profile_analyzer = None
        self.recommender = None
        self.data_path = data_path
    
    def initialize(self):
        """
        Initialize the personalization service.
        """
        print("Initializing Content-Based Personalization Service...")
        
        # Load and prepare data
        self.data_loader = DataLoader(self.data_path).load_data().prepare_content_features()
        
        # Extract features
        self.feature_extractor = ContentFeatureExtractor(self.data_loader).build_feature_vectors()
        
        # Analyze user profiles
        self.profile_analyzer = UserProfileAnalyzer(self.data_loader, self.feature_extractor).analyze_user_profiles()
        
        # Initialize recommender
        self.recommender = ContentBasedRecommender(self.data_loader, self.feature_extractor, self.profile_analyzer)
        
        print(f"Content-Based Personalization Service initialized with {len(self.data_loader.user_profiles)} user profiles.")
        return self
    
    def get_recommendations_for_user(self, user_id, limit=5, include_explanation=True):
        """
        Get personalized recommendations for a specific user.
        """
        if not self.recommender:
            raise Exception("Personalization Service not initialized. Call initialize() first.")
        
        return self.recommender.get_recommendations(user_id, limit, include_explanation)
    
    def get_user_profile(self, user_id):
        """
        Get a user's profile information.
        """
        if user_id in self.data_loader.user_profiles:
            return self.data_loader.user_profiles[user_id]
        return None


def main():
    """
    Main function to demonstrate the content-based personalization service.
    """
    # Initialize the service
    service = PersonalizationService().initialize()
    
    # Get all user IDs
    user_ids = list(service.data_loader.user_profiles.keys())
    
    # Print recommendations for each user
    for user_id in user_ids:
        print(f"\n=============== Content-Based Recommendations for User {user_id} ===============")
        
        # Get user profile insights
        profile = service.data_loader.user_profiles[user_id]
        if "explicit_preferences" in profile and "preferred_subjects" in profile["explicit_preferences"]:
            print(f"Preferred Subjects: {profile['explicit_preferences']['preferred_subjects']}")
        
        if "explicit_preferences" in profile and "preferred_grades" in profile["explicit_preferences"]:
            print(f"Preferred Grades: {profile['explicit_preferences']['preferred_grades']}")
        
        if "teaching_context" in profile and "current_curriculum_topics" in profile["teaching_context"]:
            print(f"Current Topics: {profile['teaching_context']['current_curriculum_topics']}")
        
        # Get recommendations
        recommendations = service.get_recommendations_for_user(user_id, limit=5)
        
        # Print recommendations
        print("\nTop 5 Recommendations:")
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec['title']} - {rec['category']} - {rec['class_grade']} - €{rec['price']} - Score: {rec['score']:.2f}")
            
            # Print explanation
            if "explanation" in rec:
                print("   Why? " + " | ".join(rec["explanation"]))
    
    print("\nContent-based personalization demo completed.")


if __name__ == "__main__":
    main()