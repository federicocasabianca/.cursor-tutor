from flask import Flask, render_template, request, redirect, url_for
from user_profiling import PersonalizationService
from recommendation import RecommendationService

app = Flask(__name__)
profiling_service = PersonalizationService()
recommendation_service = RecommendationService()

@app.route('/')
def index():
    return redirect(url_for('user_profile', user_id='179045'))

@app.route('/user/<user_id>/profile')
def user_profile(user_id):
    user_profile = profiling_service.get_user_profile(user_id)
    contributions = profiling_service.analyze_profile_contribution(user_id)
    
    return render_template('profile.html',
                         user_profile=user_profile,
                         contributions=contributions,
                         user_id=user_id,
                         active_page='profile')

@app.route('/user/<user_id>/recommendations')
def recommendations(user_id):
    recommendations = recommendation_service.get_recommendations_for_user(
        user_id=user_id,
        limit=10,
        diversity_factor=0.3
    )
    
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
                         active_page='recommendations')

if __name__ == '__main__':
    app.run(debug=True) 