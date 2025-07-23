# File: backend/app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import os

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}}) 

data_file_name = 'Zomato_Menu_Classified.csv'

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
        df['Price'] = df['Price'].astype(str).str.replace(r'[^\d.]', '', regex=True)
        df.loc[df['Price'] == '', 'Price'] = pd.NA
        df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
        # We only drop rows where the PRICE is invalid, as it's used for comparison.
        df.dropna(subset=['Price'], inplace=True)
        print(f"--- LOG: Rows after cleaning Price column: {len(df)}")
    else:
        print("--- LOG: WARNING - 'Price' column not found.")

    # --- FIX: REMOVED THE AGGRESSIVE dropna CALL ---
    # The filtering logic below handles missing values in these columns gracefully.
    # We only need to ensure the columns themselves exist.
    required_cols = ['Item_Name', 'Restaurant_Name', 'Food Type', 'Cuisine']
    for col in required_cols:
        if col not in df.columns:
            raise Exception(f"CRITICAL ERROR: Required column '{col}' not found in the data.")
    
    # Fill any potential empty text fields in these specific columns with 'Unknown'
    df[required_cols] = df[required_cols].fillna('Unknown')

    print(f"--- LOG: FINAL DATA READY with {len(df)} rows.")
        
except Exception as e:
    print(f"--- LOG: FATAL ERROR - An exception occurred during data loading: {e}")
    df = pd.DataFrame()

# --- API Endpoint (no changes needed) ---
@app.route('/api/recommend', methods=['POST'])
def get_recommendations():
    if df.empty:
        return jsonify({"error": "Server data is empty or not loaded correctly."}), 500
    
    data = request.get_json()
    food_types = data.get('foodTypes', [])
    cuisines = data.get('cuisines', [])
    min_price = data.get('minPrice')
    max_price = data.get('maxPrice')
    filtered_df = df.copy()

    if food_types: filtered_df = filtered_df[filtered_df['Food Type'].isin(food_types)]
    if cuisines: filtered_df = filtered_df[filtered_df['Cuisine'].isin(cuisines)]
    if 'Price' in filtered_df.columns:
        # Check that min_price and max_price are valid numbers before converting to float
        if min_price is not None and str(min_price).isnumeric():
            filtered_df = filtered_df[filtered_df['Price'] >= float(min_price)]
        if max_price is not None and str(max_price).isnumeric():
            filtered_df = filtered_df[filtered_df['Price'] <= float(max_price)]

    if filtered_df.empty: return jsonify([])
    
    num_samples = min(len(filtered_df), 5)
    recommendations = filtered_df.sample(n=num_samples)
    return jsonify(recommendations.to_dict(orient='records'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)