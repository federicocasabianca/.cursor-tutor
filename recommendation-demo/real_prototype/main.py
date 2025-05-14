"""
Main script to demonstrate the complete personalization and recommendation system.
This script shows how the user profiling and recommendation systems work together.
"""

import json
from user_profiling import PersonalizationService
from recommendation import RecommendationService

def print_user_profile(user_profile):
    """Print key information from a user profile"""
    print(f"\n=== User Profile for {user_profile['user_id']} ===")
    print(f"Preferred categories: {', '.join(user_profile['preferred_categories'])}")
    print(f"Preferred grades: {', '.join(user_profile['preferred_grades'])}")
    print(f"Price preference: {user_profile['price_preference']}")
    print(f"Event counts: {user_profile['event_counts']}")
    print("===================================\n")

def print_recommendations(recommendations):
    """Print recommendations in a readable format"""
    print("\n=== Top Recommendations ===")
    
    # Separate regular and fallback recommendations
    regular_recs = [r for r in recommendations if not r.get("is_fallback")]
    fallback_recs = [r for r in recommendations if r.get("is_fallback")]
    
    # Print regular recommendations
    if regular_recs:
        print("\nPersonalized Recommendations:")
        for i, rec in enumerate(regular_recs, 1):
            print(f"{i}. {rec['title']} - €{rec['price']} - Score: {rec['score']:.2f}")
            print(f"   Author ID: {rec['author_id']}")
            print(f"   Categories: {rec['categories']}")
            print(f"   Grades: {rec['class_grades']}")
            print(f"   Match factors:")
            factors = rec['recommendation_factors']
            print(f"     - Category match: {factors['category_match']:.2f}")
            print(f"     - Grade match: {factors['grade_match']:.2f}")
            print(f"     - Price match: {factors['price_match']:.2f}")
            print(f"     - Freshness: {factors['freshness']:.2f}")
            print(f"     - Popularity: {factors['popularity']:.2f}")
            print()
    
    # Print fallback recommendations
    if fallback_recs:
        print("\nPopular Recommendations (Fallback):")
        for i, rec in enumerate(fallback_recs, 1):
            print(f"{i}. {rec['title']} - €{rec['price']} - Score: {rec['score']:.2f}")
            print(f"   Author ID: {rec['author_id']}")
            print(f"   Categories: {rec['categories']}")
            print(f"   Grades: {rec['class_grades']}")
            print(f"   Popularity score: {rec['recommendation_factors']['popularity']:.2f}")
            print()
    
    print("===========================\n")

def print_recommendation_explanation(explanation):
    """Print explanation of recommendations"""
    print("\n=== Recommendation Explanation ===")
    print(f"Summary: {explanation['summary']}")
    
    print("\nCategory Distribution:")
    for category, count in explanation['categories'].items():
        print(f"  - {category}: {count}")
    
    print("\nGrade Distribution:")
    for grade, count in explanation['grades'].items():
        print(f"  - {grade}: {count}")
    
    print("\nPrice Distribution:")
    for price_range, count in explanation['price_distribution'].items():
        print(f"  - {price_range}: {count}")
    
    fresh = explanation['freshness_distribution']
    print(f"\nFreshness: Recent: {fresh['recent']}, Standard: {fresh['standard']}, Older: {fresh['older']}")
    print(f"Fallback recommendations: {explanation.get('fallback_count', 0)} of {sum(explanation['price_distribution'].values())}")
    
    print("\nAverage Match Factors:")
    for factor, value in explanation['recommendation_factors'].items():
        print(f"  - {factor}: {value:.2f}")
    print("==================================\n")

def run_demo(user_id="23759"):
    """Run a complete demonstration of the personalization system"""
    print("\n*** PERSONALIZATION AND RECOMMENDATION SYSTEM DEMO ***\n")
    
    # Initialize services
    profiling_service = PersonalizationService()
    recommendation_service = RecommendationService()
    
    print("1. Generating user profile...")
    user_profile = profiling_service.get_user_profile(user_id)
    print_user_profile(user_profile)
    
    print("2. Analyzing user profile contribution by event type...")
    contributions = profiling_service.analyze_profile_contribution(user_id)
    print("\nEvent contribution analysis:")
    for event_type, data in contributions.items():
        print(f"\n{event_type.upper()} (count: {data['count']}):")
        print(f"  Grade weight: {data['grade_weight']}")
        print(f"  Subject weight: {data['subject_weight']}")
        print(f"  Top categories: {data['top_categories']}")
        print(f"  Top grades: {data['top_grades']}")
    
    print("\n3. Generating personalized recommendations...")
    recommendations = recommendation_service.get_recommendations_for_user(
        user_id=user_id,
        limit=10,  # Always get exactly 10 recommendations
        diversity_factor=0.3
    )
    print_recommendations(recommendations)
    
    print("4. Generating recommendation explanation...")
    explanation = recommendation_service.explain_recommendations(recommendations)
    print_recommendation_explanation(explanation)
    
    print("*** DEMO COMPLETE ***\n")
    
    return {
        "user_profile": user_profile,
        "recommendations": recommendations,
        "explanation": explanation
    }

if __name__ == "__main__":
    # Run the demo with a specific user ID
    results = run_demo(user_id="179045")
    
    # Optionally, save results to files for further analysis
    with open("demo_results.json", "w") as f:
        json.dump(results, f, indent=2)