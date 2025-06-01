from flask import Flask, render_template, request, redirect, url_for
from user_profiling import PersonalizationService
from recommendation import RecommendationService
from functools import lru_cache
import time

app = Flask(__name__)
profiling_service = PersonalizationService()
recommendation_service = RecommendationService()

# Cache user IDs for 1 hour
@lru_cache(maxsize=1)
def get_user_ids():
    """Get list of available user IDs"""
    return profiling_service.repository.get_top_users_by_gmv(100)  # Get up to 100 users

# Cache user profiles for 5 minutes
@lru_cache(maxsize=1000)
def get_cached_user_profile(user_id: str):
    """Get cached user profile"""
    return profiling_service.get_user_profile(user_id)

# Cache user contributions for 5 minutes
@lru_cache(maxsize=1000)
def get_cached_contributions(user_id: str):
    """Get cached user contributions"""
    return profiling_service.analyze_profile_contribution(user_id)

# Cache recommendations for 5 minutes
@lru_cache(maxsize=1000)
def get_cached_recommendations(user_id: str, limit: int, diversity_factor: float):
    """Get cached recommendations"""
    return recommendation_service.get_recommendations_for_user(
        user_id=user_id,
        limit=limit,
        diversity_factor=diversity_factor
    )

@app.route('/')
def index():
    return redirect(url_for('user_profile', user_id='179045'))

@app.route('/user/<user_id>/profile')
def user_profile(user_id):
    # Get cached data
    user_profile = get_cached_user_profile(user_id)
    contributions = get_cached_contributions(user_id)
    
    return render_template('profile.html',
                         user_profile=user_profile,
                         contributions=contributions,
                         user_id=user_id,
                         user_ids=get_user_ids(),
                         active_page='profile')

@app.route('/user/<user_id>/recommendations')
def recommendations(user_id):
    # Get parameters from request
    limit = int(request.args.get('limit', 10))
    diversity_factor = float(request.args.get('diversity_factor', 0.3))
    
    # Get cached recommendations
    recommendations = get_cached_recommendations(user_id, limit, diversity_factor)
    
    # Separate regular and fallback recommendations
    regular_recs = [r for r in recommendations if not r.get("is_fallback")]
    fallback_recs = [r for r in recommendations if r.get("is_fallback")]
    
    # Get explanation of recommendations
    explanation = recommendation_service.explain_recommendations(recommendations)
    
    return render_template('recommendations.html',
                         regular_recs=regular_recs,
                         fallback_recs=fallback_recs,
                         explanation=explanation,
                         user_id=user_id,
                         user_ids=get_user_ids(),
                         active_page='recommendations')

if __name__ == '__main__':
    app.run(debug=True) 