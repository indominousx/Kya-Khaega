# File: backend/app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import os
import json
import random
from supabase import create_client, Client
from ai_service import FoodAIService

app = Flask(__name__)
CORS(app, resources={
    r"/*": {"origins": "*"},
    r"/api/*": {"origins": "*"}
}) 

# Initialize Supabase client
SUPABASE_URL = "https://bxbiafbvprdmcayumxnx.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJ4YmlhZmJ2cHJkbWNheXVteG54Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjAxNjQ1MzcsImV4cCI6MjA3NTc0MDUzN30.02_mypsf-AbNXMH0hUUylDTziMyVyUKQbORy1ZXC1KE"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Initialize AI Service
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyAjE2GUy5_saZHT7N_RUzOkK8jfG67lGiA")
ai_service = FoodAIService(GEMINI_API_KEY)

# Load and clean dataset
def load_dataset():
    try:
        script_dir = os.path.dirname(__file__)
        file_path = os.path.join(script_dir, 'The_file.csv')
        
        df = pd.read_csv(file_path)
        
        # Clean Price column
        if 'Price' in df.columns:
            df.dropna(subset=['Price'], inplace=True)
            df['Price'] = df['Price'].astype(str).str.replace(r'[^\d.]', '', regex=True)
            df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
            df.dropna(subset=['Price'], inplace=True)
        
        # Clean numeric columns
        if 'Dining_Rating' in df.columns:
            df['Dining_Rating'] = pd.to_numeric(df['Dining_Rating'], errors='coerce')
        
        if 'Votes' in df.columns:
            df['Votes'] = pd.to_numeric(df['Votes'], errors='coerce')
        
        # Clean essential columns
        df.dropna(subset=['Item_Name', 'Restaurant_Name', 'Food Type', 'Cuisine'], inplace=True)
        
        return df
        
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return pd.DataFrame()

df = load_dataset()

# Health check endpoint
@app.route('/')
def health_check():
    return jsonify({
        "status": "Kya Khaega API is running!",
        "service": "Food Recommendation Engine",
        "data_loaded": not df.empty,
        "total_restaurants": len(df) if not df.empty else 0
    })

# Areas endpoint for dropdown population
@app.route('/api/areas', methods=['GET'])
def get_areas():
    """Get list of all available areas from the dataset"""
    if df.empty:
        return jsonify({"error": "Restaurant data not available"}), 500
    
    try:
        # Get unique areas from the dataset
        if 'Area' in df.columns:
            areas = sorted(df['Area'].dropna().unique().tolist())
            return jsonify({
                "areas": areas,
                "total_areas": len(areas),
                "status": "success"
            })
        else:
            return jsonify({
                "areas": [],
                "total_areas": 0,
                "status": "no_area_column"
            })
            
    except Exception as e:
        return jsonify({"error": f"Failed to fetch areas: {str(e)}"}), 500

# Cuisines endpoint for dropdown population
@app.route('/api/cuisines', methods=['GET'])
def get_cuisines():
    """Get list of all available cuisines from the dataset"""
    if df.empty:
        return jsonify({"error": "Restaurant data not available"}), 500
    
    try:
        # Get unique cuisines from the dataset
        if 'Cuisine' in df.columns:
            cuisines = sorted(df['Cuisine'].dropna().unique().tolist())
            return jsonify({
                "cuisines": cuisines,
                "total_cuisines": len(cuisines),
                "status": "success"
            })
        else:
            return jsonify({
                "cuisines": [],
                "total_cuisines": 0,
                "status": "no_cuisine_column"
            })
            
    except Exception as e:
        return jsonify({"error": f"Failed to fetch cuisines: {str(e)}"}), 500

# Food types endpoint
@app.route('/api/food-types', methods=['GET'])
def get_food_types():
    """Get list of all available food types from the dataset"""
    if df.empty:
        return jsonify({"error": "Restaurant data not available"}), 500
    
    try:
        # Get unique food types from the dataset
        if 'Food Type' in df.columns:
            food_types = sorted(df['Food Type'].dropna().unique().tolist())
            return jsonify({
                "food_types": food_types,
                "total_food_types": len(food_types),
                "status": "success"
            })
        else:
            return jsonify({
                "food_types": [],
                "total_food_types": 0,
                "status": "no_food_type_column"
            })
            
    except Exception as e:
        return jsonify({"error": f"Failed to fetch food types: {str(e)}"}), 500

# Demographics-based Recommendation Engine
def get_user_demographics(userId):
    """Fetch user preferences and demographics from Supabase"""
    try:
        if not userId:
            return {}
        
        response = supabase.table('user_preferences').select('*').eq('user_id', userId).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return {}
    except Exception as e:
        print(f"Error fetching user demographics: {e}")
        return {}

def apply_demographic_filters(df, demographics, user_area=None):
    """Apply flexible demographic-based filters with variety preservation"""
    base_df = df.copy()
    
    print(f"DEBUG: apply_demographic_filters called with user_area: '{user_area}'")
    
    # Always apply location filter first (most important)
    if user_area and 'Area' in base_df.columns:
        print(f"DEBUG: Filtering by area '{user_area}'")
        area_match = base_df[base_df['Area'].str.lower() == user_area.lower()]
        print(f"DEBUG: Exact area matches: {len(area_match)}")
        if not area_match.empty:
            base_df = area_match
            print(f"DEBUG: Using exact area match, filtered to {len(base_df)} restaurants")
        else:
            partial_match = base_df[base_df['Area'].str.contains(user_area, case=False, na=False)]
            print(f"DEBUG: Partial area matches: {len(partial_match)}")
            if not partial_match.empty:
                base_df = partial_match
                print(f"DEBUG: Using partial area match, filtered to {len(base_df)} restaurants")
            else:
                print(f"DEBUG: No area matches found for '{user_area}', keeping all areas")
    else:
        print(f"DEBUG: No area filtering applied (user_area: '{user_area}', has Area column: {'Area' in base_df.columns})")
    
    # Always apply budget constraint (hard limit)
    if 'daily_budget' in demographics and demographics['daily_budget']:
        try:
            budget = float(demographics['daily_budget'])
            base_df = base_df[base_df['Price'] <= budget]
        except (ValueError, TypeError):
            pass
    
    print(f"After location and budget filters: {len(base_df)} restaurants")
    
    # Now create multiple pools for variety
    pools = []
    
    # Pool 1: Preferred cuisine + food type (most relevant)
    preferred_pool = base_df.copy()
    if 'cuisine_preferences' in demographics and demographics['cuisine_preferences']:
        try:
            cuisine_prefs = demographics['cuisine_preferences']
            if isinstance(cuisine_prefs, str):
                cuisine_prefs = json.loads(cuisine_prefs)
            if isinstance(cuisine_prefs, list) and len(cuisine_prefs) > 0:
                cuisine_match = preferred_pool[preferred_pool['Cuisine'].isin(cuisine_prefs)]
                if not cuisine_match.empty:
                    preferred_pool = cuisine_match
        except Exception:
            pass
    
    if 'food_type' in demographics and demographics['food_type']:
        food_type_match = preferred_pool[
            preferred_pool['Food Type'].str.contains(demographics['food_type'], case=False, na=False)
        ]
        if not food_type_match.empty:
            preferred_pool = food_type_match
    
    if not preferred_pool.empty:
        pools.append(('preferred', preferred_pool))
    
    # Pool 2: Only cuisine preferences (medium relevance)
    if 'cuisine_preferences' in demographics and demographics['cuisine_preferences']:
        try:
            cuisine_prefs = demographics['cuisine_preferences']
            if isinstance(cuisine_prefs, str):
                cuisine_prefs = json.loads(cuisine_prefs)
            if isinstance(cuisine_prefs, list) and len(cuisine_prefs) > 0:
                cuisine_only_pool = base_df[base_df['Cuisine'].isin(cuisine_prefs)]
                if not cuisine_only_pool.empty:
                    pools.append(('cuisine_only', cuisine_only_pool))
        except Exception:
            pass
    
    # Pool 3: Only food type (basic relevance)
    if 'food_type' in demographics and demographics['food_type']:
        food_type_only_pool = base_df[
            base_df['Food Type'].str.contains(demographics['food_type'], case=False, na=False)
        ]
        if not food_type_only_pool.empty:
            pools.append(('food_type_only', food_type_only_pool))
    
    # Pool 4: All restaurants in area (variety/exploration)
    if not base_df.empty:
        pools.append(('variety', base_df))
    
    print(f"Created {len(pools)} recommendation pools")
    
    # Combine pools with weights
    if pools:
        # Return the most relevant pool that has enough variety
        return pools[0][1]  # Start with most preferred pool
    
    return df  # Fallback to all restaurants

def get_five_different_restaurants(filtered_df, count=5):
    """Get exactly 5 dishes from 5 different restaurants based on user preferences"""
    if filtered_df.empty:
        return []
    
    # Create a scoring system
    scored_df = filtered_df.copy()
    scored_df['rating_score'] = scored_df['Dining_Rating'].fillna(3.0)
    scored_df['votes_score'] = scored_df['Votes'].fillna(1)
    
    # Normalize votes
    max_votes = scored_df['votes_score'].max()
    if max_votes > 0:
        scored_df['votes_normalized'] = (scored_df['votes_score'] / max_votes) * 2
    else:
        scored_df['votes_normalized'] = 1
    
    # Base recommendation score: Rating + Votes + randomness
    scored_df['recommendation_score'] = (
        scored_df['rating_score'] + 
        scored_df['votes_normalized'] + 
        scored_df.apply(lambda x: random.uniform(0, 0.5), axis=1)
    )
    
    recommendations = []
    used_restaurants = set()
    
    # Group by restaurant and get the best item from each restaurant
    restaurant_groups = scored_df.groupby('Restaurant_Name')
    
    # Create a list of best item from each restaurant
    restaurant_candidates = []
    for restaurant_name, group in restaurant_groups:
        best_item_in_restaurant = group.loc[group['recommendation_score'].idxmax()]
        restaurant_candidates.append(best_item_in_restaurant)
    
    # Convert to DataFrame for easier handling
    candidates_df = pd.DataFrame(restaurant_candidates)
    
    # Sort by recommendation score and take top 5 restaurants
    top_restaurants = candidates_df.nlargest(count, 'recommendation_score')
    
    # If we don't have 5 restaurants, fill remaining with best items from any restaurant
    if len(top_restaurants) < count:
        remaining_needed = count - len(top_restaurants)
        used_restaurant_names = set(top_restaurants['Restaurant_Name'].values)
        
        # Get remaining items not from already selected restaurants
        remaining_items = scored_df[~scored_df['Restaurant_Name'].isin(used_restaurant_names)]
        additional_items = remaining_items.nlargest(remaining_needed, 'recommendation_score')
        
        # Combine
        if not additional_items.empty:
            top_restaurants = pd.concat([top_restaurants, additional_items])
    
    # Convert to recommendation format
    for _, item in top_restaurants.iterrows():
        recommendations.append({
            'name': str(item.get('Item_Name', 'Unknown')),
            'restaurant': str(item.get('Restaurant_Name', 'Unknown')),
            'cuisine': str(item.get('Cuisine', 'Not specified')),
            'food_type': str(item.get('Food Type', 'Not specified')),
            'area': str(item.get('Area', 'Not specified')),
            'price': float(item.get('Price', 0)) if pd.notna(item.get('Price')) else 0.0,
            'rating': float(item.get('Dining_Rating', 0)) if pd.notna(item.get('Dining_Rating')) else 0.0,
            'votes': int(item.get('Votes', 0)) if pd.notna(item.get('Votes')) else 0,
            'score': round(float(item.get('recommendation_score', 0)), 2)
        })
        
        print(f"Selected: {item['Item_Name']} from {item['Restaurant_Name']} ({item['Cuisine']})")
    
    print(f"Final: {len(recommendations)} dishes from {len(set(r['restaurant'] for r in recommendations))} different restaurants")
    return recommendations

@app.route('/api/recommend', methods=['POST'])
def get_recommendations():
    """Main recommendation endpoint - prioritizes current selections over stored preferences"""
    if df.empty:
        return jsonify({"error": "Restaurant data not available"}), 500
    
    try:
        data = request.get_json()
        userId = data.get('userId', '')
        user_area = data.get('userArea', '')
        
        # Get current user selections from request
        current_cuisines = data.get('cuisines', [])
        current_food_types = data.get('foodTypes', [])
        current_min_price = data.get('minPrice')
        current_max_price = data.get('maxPrice')
        
        print(f"Current selections - Cuisines: {current_cuisines}, Food Types: {current_food_types}")
        
        # Get stored preferences as fallback
        stored_demographics = get_user_demographics(userId)
        print(f"Stored demographics: {stored_demographics}")
        
        # Create effective preferences (current selections override stored ones)
        effective_preferences = {}
        
        # Use current selections if provided, otherwise fall back to stored preferences
        if current_cuisines:
            effective_preferences['cuisine_preferences'] = current_cuisines
        elif stored_demographics.get('cuisine_preferences'):
            effective_preferences['cuisine_preferences'] = stored_demographics['cuisine_preferences']
        
        if current_food_types:
            effective_preferences['food_type'] = current_food_types[0] if current_food_types else None
        elif stored_demographics.get('food_type'):
            effective_preferences['food_type'] = stored_demographics['food_type']
        
        # For budget, use current selection or stored daily budget
        if current_max_price is not None:
            effective_preferences['daily_budget'] = current_max_price
        elif stored_demographics.get('daily_budget'):
            effective_preferences['daily_budget'] = stored_demographics['daily_budget']
        
        print(f"Effective preferences: {effective_preferences}")
        
        # Apply filtering with effective preferences
        filtered_restaurants = apply_demographic_filters(df, effective_preferences, user_area)
        print(f"Filtered to {len(filtered_restaurants)} restaurants")
        
        # Get exactly 5 recommendations from 5 different restaurants
        recommendations = get_five_different_restaurants(filtered_restaurants, 5)
        print(f"Generated {len(recommendations)} recommendations from {len(set(r['restaurant'] for r in recommendations))} different restaurants")
        
        # Response with analytics
        response_data = {
            'recommendations': recommendations,
            'total_found': len(recommendations),
            'user_demographics': {
                'has_preferences': bool(stored_demographics),
                'current_selections': {
                    'cuisines': current_cuisines,
                    'food_types': current_food_types,
                    'max_price': current_max_price
                },
                'stored_preferences': {
                    'cuisine_preferences': stored_demographics.get('cuisine_preferences', []) if stored_demographics else [],
                    'food_type': stored_demographics.get('food_type', '') if stored_demographics else '',
                    'daily_budget': stored_demographics.get('daily_budget', 0) if stored_demographics else 0
                },
                'effective_preferences': effective_preferences,
                'location': user_area
            },
            'filtering_stats': {
                'total_restaurants': len(df),
                'after_filtering': len(filtered_restaurants),
                'recommendation_method': 'current_selection_priority'
            }
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({"error": f"Recommendation engine error: {str(e)}"}), 500

@app.route('/api/ai-recommend', methods=['POST'])
def get_ai_recommendations():
    """AI-powered natural language food recommendation endpoint"""
    if df.empty:
        return jsonify({"error": "Restaurant data not available"}), 500
    
    try:
        data = request.get_json()
        user_query = data.get('query', '').strip()
        userId = data.get('userId', '')
        user_area = data.get('userArea', '')
        
        if not user_query:
            return jsonify({"error": "Please provide a food query"}), 400
        
        print(f"AI Query: '{user_query}' from user: {userId} in area: {user_area}")
        
        # Get available options from dataset
        available_cuisines = sorted(df['Cuisine'].dropna().unique().tolist()) if 'Cuisine' in df.columns else []
        available_areas = sorted(df['Area'].dropna().unique().tolist()) if 'Area' in df.columns else []
        
        # Get user demographics for enhanced AI understanding
        stored_demographics = get_user_demographics(userId)
        print(f"User Demographics: {stored_demographics}")
        
        # Use AI to understand the query with demographics context
        ai_understanding = ai_service.understand_food_query(
            user_query, 
            available_cuisines, 
            available_areas,
            stored_demographics
        )
        
        print(f"Enhanced AI Understanding: {ai_understanding}")
        
        # If user provided area, prioritize it over AI detected areas
        if user_area:
            ai_understanding['areas'] = [user_area]
        
        # Apply AI-powered intelligent filtering with demographics
        filtered_restaurants = ai_service.generate_smart_filters(
            ai_understanding, 
            df, 
            stored_demographics
        )
        
        print(f"AI + Demographics Filtered to {len(filtered_restaurants)} restaurants")
        
        # Rank recommendations using AI context and demographics
        ranked_restaurants = ai_service.rank_recommendations_with_context(
            filtered_restaurants, 
            ai_understanding,
            stored_demographics
        )
        
        # Get AI-based recommendations (3 dishes)
        ai_recommendations = get_five_different_restaurants(ranked_restaurants, 3)
        
        # Get demographic-based recommendations (2 dishes as requested)
        demographic_recommendations = ai_service.get_demographic_recommendations(
            df, 
            stored_demographics, 
            ai_understanding, 
            count=2
        )
        
        # Combine recommendations (3 AI + 2 demographic)
        recommendations = ai_recommendations + demographic_recommendations
        
        print(f"Generated {len(ai_recommendations)} AI + {len(demographic_recommendations)} demographic recommendations")
        
        # Generate explanation with demographics context
        explanation = ai_service.generate_explanation(ai_understanding, recommendations, stored_demographics)
        
        print(f"Generated {len(recommendations)} AI-powered recommendations")
        
        # Enhanced response with AI insights and demographics
        response_data = {
            'recommendations': recommendations,
            'ai_recommendations': ai_recommendations,
            'demographic_recommendations': demographic_recommendations,
            'total_found': len(recommendations),
            'ai_understanding': ai_understanding,
            'explanation': explanation,
            'query': user_query,
            'confidence': ai_understanding.get('confidence', 0.5),
            'filtering_stats': {
                'total_restaurants': len(df),
                'after_ai_filtering': len(filtered_restaurants),
                'ai_recommendation_count': len(ai_recommendations),
                'demographic_recommendation_count': len(demographic_recommendations),
                'recommendation_method': 'ai_powered_with_demographics'
            },
            'user_demographics': {
                'has_preferences': bool(stored_demographics),
                'preferences_data': stored_demographics,
                'used_fallback': ai_understanding.get('used_fallback', False),
                'location': user_area
            }
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"AI recommendation error: {str(e)}")
        return jsonify({
            "error": f"AI recommendation engine error: {str(e)}",
            "fallback_message": "Please try rephrasing your request or use the regular search."
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)