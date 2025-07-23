from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import os

# --- Initialization ---
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}}) 

# --- Load Data on Start-up ---
data_file_name = 'Zomato_Menu_Classified.csv' # Use the .csv file 

try:
    script_dir = os.path.dirname(__file__) 
    file_path = os.path.join(script_dir, data_file_name)
    
    print(f"Loading data from: {file_path}")
    df = pd.read_csv(file_path) # Use pd.read_csv
    df.columns = df.columns.str.strip() # FIX: Remove whitespace from column names
    print("Data loaded successfully.")

    # --- FIX: Smarter Price Cleaning ---
    if 'Price' in df.columns:
        print("Starting advanced cleaning of 'Price' column...")
        
        # Step 1: Convert the column to string type to use string operations.
        df['Price'] = df['Price'].astype(str)
        
        # Step 2: Use regex to remove ALL characters that are NOT digits or a decimal point.
        # This will remove '₹', ',', 'Rs.', spaces, etc.
        df['Price'] = df['Price'].str.replace(r'[^\d.]', '', regex=True)
        
        # Step 3: Now, convert the cleaned strings to numbers. 'coerce' will handle any empty strings.
        df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
        
        # Step 4: Drop any rows that are still invalid after all our cleaning.
        original_rows = len(df)
        df.dropna(subset=['Price'], inplace=True)
        
        print(f"Removed {original_rows - len(df)} rows with invalid prices.")
        print(f"Found {len(df)} rows with valid, numeric prices remaining.") # NEW, helpful log message
    else:
        print("Warning: 'Price' column not found. Price filtering will be disabled.")

    # Clean other essential columns
    df.dropna(subset=['Item_Name', 'Restaurant_Name', 'Food Type', 'Cuisine'], inplace=True)
    
except FileNotFoundError:
    print(f"--- FATAL ERROR ---")
    print(f"The file '{data_file_name}' was not found in the 'backend' directory.")
    df = pd.DataFrame()


# --- API Endpoint (No changes needed here) ---
@app.route('/api/recommend', methods=['POST'])
def get_recommendations():
    if df.empty:
        return jsonify({"error": "Server data not loaded. Check backend console."}), 500

    data = request.get_json()
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
        try:
            if min_price is not None:
                filtered_df = filtered_df[filtered_df['Price'] >= float(min_price)]
            if max_price is not None:
                filtered_df = filtered_df[filtered_df['Price'] <= float(max_price)]
        except (ValueError, TypeError):
            print("Warning: Invalid price data received. Skipping price filter.")
            pass

    if filtered_df.empty:
        return jsonify([])

    num_samples = min(len(filtered_df), 5)
    recommendations = filtered_df.sample(n=num_samples)
    
    result = recommendations.to_dict(orient='records')
    return jsonify(result)

# --- Run the Server ---
if __name__ == '__main__':
    app.run(debug=True, port=5000)