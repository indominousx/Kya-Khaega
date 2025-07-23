# File: backend/app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import os

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}}) # Allow all origins for Vercel

data_file_name = 'Zomato_Menu_Classified.csv'

try:
    script_dir = os.path.dirname(__file__) 
    file_path = os.path.join(script_dir, data_file_name)
    
    print(f"--- BACKEND LOG: Attempting to load data from: {file_path}")
    df = pd.read_csv(file_path)
    print("--- BACKEND LOG: CSV file loaded successfully into pandas.")
    print(f"--- BACKEND LOG: Columns found in CSV: {df.columns.tolist()}")

    if 'Price' in df.columns:
        print("--- BACKEND LOG: Cleaning 'Price' column...")
        df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
        original_rows = len(df)
        df.dropna(subset=['Price'], inplace=True)
        print(f"--- BACKEND LOG: Removed {original_rows - len(df)} rows with invalid prices.")
    else:
        print("--- BACKEND LOG: WARNING - 'Price' column not found.")

    df.dropna(subset=['Item_Name', 'Restaurant_Name', 'Food Type', 'Cuisine'], inplace=True)
    print(f"--- BACKEND LOG: Data ready with {len(df)} rows.")
    
except FileNotFoundError:
    print(f"--- BACKEND LOG: FATAL ERROR - FileNotFoundError. Could not find {file_path}")
    df = pd.DataFrame()
except Exception as e:
    print(f"--- BACKEND LOG: FATAL ERROR - An exception occurred: {e}")
    df = pd.DataFrame()

@app.route('/api/recommend', methods=['POST'])
def get_recommendations():
    print("--- BACKEND LOG: /api/recommend endpoint hit!")
    if df.empty:
        print("--- BACKEND LOG: ERROR - DataFrame is empty. Cannot give recommendations.")
        return jsonify({"error": "Server data is not loaded correctly."}), 500

    data = request.get_json()
    print(f"--- BACKEND LOG: Received request data: {data}")
    food_types = data.get('foodTypes', [])
    cuisines = data.get('cuisines', [])
    min_price = data.get('minPrice')
    max_price = data.get('maxPrice')

    filtered_df = df.copy()

    if food_types:
        filtered_df = filtered_df[filtered_df['Food Type'].isin(food_types)]
    if cuisines:
        filtered_df = filtered_df[filtered_df['Cuisine'].isin(cuisines)]
    if 'Price' in filtered_df.columns:
        if min_price is not None:
            filtered_df = filtered_df[filtered_df['Price'] >= float(min_price)]
        if max_price is not None:
            filtered_df = filtered_df[filtered_df['Price'] <= float(max_price)]
    
    print(f"--- BACKEND LOG: Found {len(filtered_df)} items after filtering.")
    
    if filtered_df.empty:
        return jsonify([])

    num_samples = min(len(filtered_df), 5)
    recommendations = filtered_df.sample(n=num_samples)
    result = recommendations.to_dict(orient='records')
    return jsonify(result)

# This is only for local testing, Vercel runs the app differently.
if __name__ == '__main__':
    app.run(debug=True, port=5000)