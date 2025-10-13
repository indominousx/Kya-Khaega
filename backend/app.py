# File: backend/app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import os
import json
from supabase import create_client, Client

app = Flask(__name__)
# Allow all origins for both API routes and health check
CORS(app, resources={
    r"/*": {"origins": "*"},
    r"/api/*": {"origins": "*"}
}) 

# Initialize Supabase client
SUPABASE_URL = "https://bxbiafbvprdmcayumxnx.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJ4YmlhZmJ2cHJkbWNheXVteG54Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjAxNjQ1MzcsImV4cCI6MjA3NTc0MDUzN30.02_mypsf-AbNXMH0hUUylDTziMyVyUKQbORy1ZXC1KE"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

data_file_name = 'The_file.csv'

try:
    script_dir = os.path.dirname(__file__) 
    file_path = os.path.join(script_dir, data_file_name)
    
    print(f"--- LOG: Attempting to load data from: {file_path}")
    df = pd.read_csv(file_path)
    print(f"--- LOG: CSV file loaded. Initial row count: {len(df)}")
    print(f"--- LOG: Columns found: {df.columns.tolist()}")

    # --- ADVANCED PRICE CLEANING ---
    if 'Price' in df.columns:
        print("--- LOG: Starting 'Price' column cleaning...")
        # First, drop rows where 'Price' is already empty
        df.dropna(subset=['Price'], inplace=True)
        print(f"--- LOG: Rows after dropping empty prices: {len(df)}")
        
        # Convert to string and use regex to remove everything that isn't a digit or decimal
        df['Price'] = df['Price'].astype(str).str.replace(r'[^\d.]', '', regex=True)
        
        # After cleaning, some might be empty strings. Replace them with NaN.
        df.loc[df['Price'] == '', 'Price'] = pd.NA
        print(f"--- LOG: Rows after replacing empty strings in Price: {len(df)}")

        # Now convert to numeric. Coerce will handle any remaining bad formats.
        df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
        
        # Finally, drop any rows that could not be converted.
        df.dropna(subset=['Price'], inplace=True)
        print(f"--- LOG: Rows after final numeric conversion of Price: {len(df)}")
    else:
        print("--- LOG: WARNING - 'Price' column not found.")

    # --- CLEAN DINING_RATING COLUMN ---
    if 'Dining_Rating' in df.columns:
        print("--- LOG: Starting 'Dining_Rating' column cleaning...")
        # Convert to numeric, coerce errors to NaN
        df['Dining_Rating'] = pd.to_numeric(df['Dining_Rating'], errors='coerce')
        print(f"--- LOG: Dining_Rating conversion complete")
    else:
        print("--- LOG: WARNING - 'Dining_Rating' column not found.")

    # --- CLEAN VOTES COLUMN ---
    if 'Votes' in df.columns:
        print("--- LOG: Starting 'Votes' column cleaning...")
        # Convert to numeric, coerce errors to NaN
        df['Votes'] = pd.to_numeric(df['Votes'], errors='coerce')
        print(f"--- LOG: Votes conversion complete")
    else:
        print("--- LOG: WARNING - 'Votes' column not found.")

    # --- CLEAN OTHER CRITICAL COLUMNS ---
    # This is another potential point of failure. We will check it too.
    initial_rows_before_final_clean = len(df)
    df.dropna(subset=['Item_Name', 'Restaurant_Name', 'Food Type', 'Cuisine'], inplace=True)
    print(f"--- LOG: Rows after cleaning other critical columns: {len(df)}")
    print(f"--- LOG: Dropped {initial_rows_before_final_clean - len(df)} rows due to missing critical data.")
    
    print(f"--- LOG: FINAL DATA READY with {len(df)} rows.")
        
except Exception as e:
    print(f"--- LOG: FATAL ERROR - An exception occurred during data loading: {e}")
    df = pd.DataFrame() # Ensure df is empty on error

# Health check endpoint
@app.route('/')
def health_check():
    available_areas = []
    if not df.empty and 'Area' in df.columns:
        available_areas = sorted(df['Area'].unique().tolist())
    
    return jsonify({
        "status": "Backend is running!",
        "service": "Kya Khaega API",
        "data_loaded": not df.empty,
        "total_items": len(df) if not df.empty else 0,
        "available_areas": available_areas[:20] if available_areas else [],  # Show first 20 areas
        "total_areas": len(available_areas) if available_areas else 0
    })

# API Endpoint
@app.route('/api/recommend', methods=['POST'])
def get_recommendations():
    if df.empty:
        return jsonify({"error": "Server data is empty or not loaded correctly."}), 500
    
    # Get data from frontend
    data = request.get_json()
    food_types = data.get('foodTypes', [])
    cuisines = data.get('cuisines', [])
    min_price = data.get('minPrice')
    max_price = data.get('maxPrice')
    user_area = data.get('userArea')
    user_location = data.get('userLocation')
    userId = data.get('userId', '')
    userPreferences = data.get('userPreferences', {})
    
    print(f"--- LOG: User area detected: {user_area}")
    print(f"--- LOG: User location: {user_location}")
    print(f"--- LOG: User ID: {userId}")
    print(f"--- LOG: User preferences: {userPreferences}")
    
    # Fetch user preferences from Supabase if userId is provided
    db_preferences = {}
    if userId:
        try:
            response = supabase.table('user_preferences').select('*').eq('user_id', userId).execute()
            if response.data and len(response.data) > 0:
                db_preferences = response.data[0]
                print(f"--- LOG: Retrieved DB preferences: {db_preferences}")
            else:
                print(f"--- LOG: No preferences found in DB for user: {userId}")
        except Exception as e:
            print(f"--- LOG: Error fetching user preferences: {str(e)}")
    
    filtered_df = df.copy()
    
    # Apply user preferences from database (if available) - these override manual selections
    if db_preferences:
        print("--- LOG: Applying user preferences from database")
        
        # Apply cuisine preferences from DB
        if 'cuisine_preferences' in db_preferences and db_preferences['cuisine_preferences']:
            try:
                # Parse cuisine preferences if it's a JSON string
                if isinstance(db_preferences['cuisine_preferences'], str):
                    db_cuisines = json.loads(db_preferences['cuisine_preferences'])
                else:
                    db_cuisines = db_preferences['cuisine_preferences']
                
                if isinstance(db_cuisines, list) and len(db_cuisines) > 0:
                    filtered_df = filtered_df[filtered_df['Cuisine'].isin(db_cuisines)]
                    print(f"--- LOG: Applied DB cuisine filter: {db_cuisines}, {len(filtered_df)} items remain")
            except Exception as e:
                print(f"--- LOG: Error applying DB cuisine preferences: {str(e)}")
        
        # Apply food type preference from DB
        if 'food_type' in db_preferences and db_preferences['food_type']:
            filtered_df = filtered_df[filtered_df['Food Type'].str.contains(db_preferences['food_type'], case=False, na=False)]
            print(f"--- LOG: Applied DB food type filter: {db_preferences['food_type']}, {len(filtered_df)} items remain")
        
        # Apply daily budget from DB
        if 'daily_budget' in db_preferences and db_preferences['daily_budget'] and 'Price' in filtered_df.columns:
            try:
                db_budget = float(db_preferences['daily_budget'])
                filtered_df = filtered_df[filtered_df['Price'] <= db_budget]
                print(f"--- LOG: Applied DB budget filter: ≤{db_budget}, {len(filtered_df)} items remain")
            except (ValueError, TypeError) as e:
                print(f"--- LOG: Error applying DB budget preference: {str(e)}")
    else:
        print("--- LOG: No DB preferences found, applying manual filters")
    
    # Apply manual filters only if no DB preferences were applied
    if not db_preferences:
        if food_types: 
            filtered_df = filtered_df[filtered_df['Food Type'].isin(food_types)]
            print(f"--- LOG: Applied manual food type filter: {food_types}, {len(filtered_df)} items remain")
        if cuisines: 
            filtered_df = filtered_df[filtered_df['Cuisine'].isin(cuisines)]
            print(f"--- LOG: Applied manual cuisine filter: {cuisines}, {len(filtered_df)} items remain")
        if 'Price' in filtered_df.columns:
            if min_price is not None: 
                filtered_df = filtered_df[filtered_df['Price'] >= float(min_price)]
                print(f"--- LOG: Applied manual min price filter: ≥{min_price}, {len(filtered_df)} items remain")
            if max_price is not None: 
                filtered_df = filtered_df[filtered_df['Price'] <= float(max_price)]
                print(f"--- LOG: Applied manual max price filter: ≤{max_price}, {len(filtered_df)} items remain")
    
    # Apply location-based filtering with strict prioritization
    if user_area and 'Area' in filtered_df.columns:
        print(f"--- LOG: Filtering by user area: {user_area}")
        
        # First, try exact area match (highest priority)
        exact_area_filtered = filtered_df[filtered_df['Area'].str.lower() == user_area.lower()]
        
        if not exact_area_filtered.empty:
            print(f"--- LOG: Found {len(exact_area_filtered)} restaurants in exact area: {user_area}")
            filtered_df = exact_area_filtered
        else:
            # Second, try partial match (e.g., "Kondhwa Budruk" matches "Kondhwa")
            partial_match = filtered_df[filtered_df['Area'].str.contains(user_area, case=False, na=False)]
            
            if not partial_match.empty:
                print(f"--- LOG: Found {len(partial_match)} restaurants with partial area match for: {user_area}")
                filtered_df = partial_match
            else:
                # Last resort: look for very close nearby areas only
                print(f"--- LOG: No direct matches found in {user_area}, checking immediate nearby areas")
                nearby_areas = get_immediate_nearby_areas(user_area)  # More restrictive function
                if nearby_areas:
                    # Use exact matching for nearby areas to avoid distant matches
                    nearby_pattern = '^(' + '|'.join([area.replace('(', r'\(').replace(')', r'\)') for area in nearby_areas]) + ')$'
                    nearby_filtered = filtered_df[filtered_df['Area'].str.match(nearby_pattern, case=False, na=False)]
                    if not nearby_filtered.empty:
                        print(f"--- LOG: Found {len(nearby_filtered)} restaurants in immediate nearby areas: {nearby_areas}")
                        filtered_df = nearby_filtered
                    else:
                        print(f"--- LOG: No restaurants found even in nearby areas. Showing limited results from all areas.")
                        # If still nothing, return a very small sample from all areas with distance warning
                        filtered_df = filtered_df.head(3)  # Only 3 results to indicate limited options
    
    if filtered_df.empty: 
        print("--- LOG: No restaurants found after filtering")
        return jsonify([])
    
    # Completely rewritten logic: GUARANTEE exactly 5 results
    target_count = 5
    
    if len(filtered_df) < target_count:
        # If less than 5 available total, return all
        recommendations = filtered_df
        print(f"--- LOG: Only {len(filtered_df)} items available, returning all")
    else:
        # We have enough data, now prioritize by area
        if user_area and 'Area' in filtered_df.columns:
            user_area_items = filtered_df[filtered_df['Area'].str.lower() == user_area.lower()]
            non_user_area_items = filtered_df[filtered_df['Area'].str.lower() != user_area.lower()]
            
            result_items = []
            
            # Step 1: Add up to 4 from user's area (or all if less than 4)
            if len(user_area_items) > 0:
                user_count = min(len(user_area_items), 4)
                user_sample = user_area_items.sample(n=user_count, random_state=None)
                result_items.append(user_sample)
                print(f"--- LOG: Added {user_count} items from {user_area}")
            
            # Step 2: Fill remaining slots from other areas
            current_count = sum(len(df) for df in result_items)
            remaining = target_count - current_count
            
            if remaining > 0 and len(non_user_area_items) > 0:
                other_sample = non_user_area_items.sample(n=remaining, random_state=None)
                result_items.append(other_sample)
                print(f"--- LOG: Added {remaining} items from other areas")
            
            # Combine all results
            if result_items:
                recommendations = pd.concat(result_items, ignore_index=True)
            else:
                # Fallback: just sample 5 from anywhere
                recommendations = filtered_df.sample(n=target_count, random_state=None)
        else:
            # No area specified, just sample 5
            recommendations = filtered_df.sample(n=target_count, random_state=None)
            print(f"--- LOG: No area specified, sampled {target_count} items")
    
    print(f"--- LOG: Final recommendations shape: {recommendations.shape}")
    print(f"--- LOG: Final recommendations length: {len(recommendations)}")
    
    # Convert to dict and check length
    result_dict = recommendations.to_dict(orient='records')
    print(f"--- LOG: Dict conversion result length: {len(result_dict)}")
    
    # Log first few items for debugging
    for i, item in enumerate(result_dict[:3]):
        print(f"--- LOG: Item {i+1}: {item.get('Item_Name', 'Unknown')} from {item.get('Area', 'Unknown')}")
    
    # Add preference source information to response
    preference_source = "database" if db_preferences else "manual"
    
    response_data = {
        'recommendations': result_dict,
        'preference_source': preference_source,
        'applied_preferences': db_preferences if db_preferences else {
            'cuisines': cuisines,
            'food_types': food_types,
            'min_price': min_price,
            'max_price': max_price
        },
        'total_found': len(result_dict)
    }
    
    print(f"--- LOG: Response includes preference source: {preference_source}")
    
    return jsonify(response_data)

def get_immediate_nearby_areas(user_area):
    """Get only the most immediate nearby areas (within 2-3 km radius)"""
    # More restrictive mapping - only immediate neighbors
    immediate_area_mapping = {
        'Hinjawadi': ['Wakad', 'Baner'],
        'Baner': ['Hinjawadi', 'Wakad', 'Balewadi'],
        'Wakad': ['Hinjawadi', 'Baner'],
        'Aundh': ['Baner', 'Shivajinagar'],
        'Shivajinagar': ['Aundh', 'Deccan'],
        'Koregaon Park': ['Viman Nagar'],
        'Viman Nagar': ['Koregaon Park', 'Kalyani Nagar'],
        'Kalyani Nagar': ['Viman Nagar'],
        'Hadapsar': ['Kondhwa'],
        'Kondhwa': ['Hadapsar', 'Bibvewadi'],
        'Bibvewadi': ['Kondhwa'],
        'Kothrud': ['Karve Nagar', 'Deccan'],
        'Deccan': ['Shivajinagar', 'Kothrud'],
        'FC Road': ['Deccan'],
        'Camp': ['FC Road']
    }
    
    return immediate_area_mapping.get(user_area, [])

def get_nearby_areas(user_area):
    """Get nearby areas for a given area in Pune (legacy function - more permissive)"""
    area_mapping = {
        'Hinjawadi': ['Wakad', 'Baner', 'Aundh'],
        'Baner': ['Hinjawadi', 'Wakad', 'Aundh', 'Balewadi'],
        'Wakad': ['Hinjawadi', 'Baner', 'Aundh'],
        'Aundh': ['Baner', 'Wakad', 'Shivajinagar'],
        'Shivajinagar': ['Aundh', 'Deccan', 'FC Road', 'Koregaon Park'],
        'Koregaon Park': ['Shivajinagar', 'Viman Nagar', 'Kalyani Nagar'],
        'Viman Nagar': ['Koregaon Park', 'Kalyani Nagar', 'Hadapsar'],
        'Kalyani Nagar': ['Koregaon Park', 'Viman Nagar', 'Hadapsar'],
        'Hadapsar': ['Viman Nagar', 'Kalyani Nagar', 'Kondhwa'],
        'Kondhwa': ['Hadapsar', 'Bibvewadi'],
        'Kothrud': ['Karve Nagar', 'Warje', 'Deccan'],
        'Deccan': ['Shivajinagar', 'FC Road', 'Kothrud'],
        'FC Road': ['Shivajinagar', 'Deccan', 'Camp'],
        'Camp': ['FC Road', 'Kothrud']
    }
    
    return area_mapping.get(user_area, [])

# Get available areas endpoint
@app.route('/api/areas', methods=['GET'])
def get_areas():
    if df.empty:
        return jsonify({"error": "Server data is empty or not loaded correctly."}), 500
    
    if 'Area' in df.columns:
        areas = sorted(df['Area'].unique().tolist())
        return jsonify({
            "areas": areas,
            "total_areas": len(areas)
        })
    else:
        return jsonify({
            "areas": [],
            "total_areas": 0,
            "error": "Area column not found in data"
        })

# Debug endpoint to test the logic
@app.route('/api/debug', methods=['POST'])
def debug_recommendations():
    data = request.get_json()
    user_area = data.get('userArea', '')
    
    # Test the exact same logic with debug output
    result = {
        'total_data': len(df),
        'user_area': user_area,
        'message': 'Debug test'
    }
    
    if user_area and 'Area' in df.columns:
        user_items = df[df['Area'].str.lower() == user_area.lower()]
        other_items = df[df['Area'].str.lower() != user_area.lower()]
        result['user_area_count'] = len(user_items)
        result['other_areas_count'] = len(other_items)
        
        # Simple test: try to get 5 items
        if len(user_items) >= 4:
            sample_4 = user_items.sample(n=4)
            sample_1 = other_items.sample(n=1) if len(other_items) > 0 else pd.DataFrame()
            
            if not sample_1.empty:
                combined = pd.concat([sample_4, sample_1], ignore_index=True)
                result['final_count'] = len(combined)
                result['items'] = combined[['Item_Name', 'Area']].to_dict('records')
            else:
                result['final_count'] = len(sample_4)
                result['items'] = sample_4[['Item_Name', 'Area']].to_dict('records')
        
    return jsonify(result)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)