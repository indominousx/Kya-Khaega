import pandas as pd
import numpy as np # We'll use NumPy for high-speed conditional logic
import time
import re # Regular Expressions for smarter searching
import os # Import the os module

# --- 1. SETUP AND DATA LOADING ---

# Construct an absolute path to the data file to ensure it's found
# regardless of the script's execution directory.
script_dir = os.path.dirname(os.path.abspath(__file__))
data_file_path = os.path.join(script_dir, 'Zomato_Menu_Scraped.xlsx')

print(f"Loading data from '{data_file_path}'...")
try:
    # Specifying the engine can sometimes be faster for .xlsx files
    df = pd.read_excel(data_file_path, engine='openpyxl')
    print(f"Dataset loaded successfully with {len(df)} rows.")
except FileNotFoundError:
    print("Error: 'Zomato_Menu_Scraped.xlsx' not found. Please ensure it's in the same directory.")
    exit()

# --- 2. EXPANDED AND MORE DETAILED KEYWORDS ---
# We're adding more categories and making existing ones more specific.
# The order of the 'cuisine_keywords' dictionary is now CRITICAL for correct classification.

non_veg_keywords = {
    'chicken', 'mutton', 'lamb', 'fish', 'prawn', 'shrimp', 'egg', 'keema', 
    'kheema', 'bacon', 'ham', 'sausage', 'pork', 'beef', 'salami', 'pepperoni'
}

# This dictionary is now ordered by precedence. More specific categories go first.
cuisine_keywords = {
    'Beverages': {'tea', 'coffee', 'lassi', 'juice', 'shake', 'soda', 'mocktail', 'cooler', 'sharbat', 'drink'},
    'Desserts': {'cake', 'pastry', 'ice cream', 'brownie', 'sundae', 'muffin', 'kulfi', 'gulab jamun', 'jalebi', 'rasgulla', 'falooda', 'dessert'},
    'South Indian': {'dosa', 'idli', 'vada', 'uttapam', 'sambhar', 'rasam', 'upma'},
    'Maharashtrian': {'misal', 'pav bhaji', 'vada pav', 'thalipeeth', 'pithla', 'sabudana'},
    'Mughlai': {'kebab', 'korma', 'mughlai', 'shahi', 'nawabi', 'haleem'},
    'Italian': {'pasta', 'pizza', 'risotto', 'lasagna', 'ravioli', 'spaghetti', 'penne', 'macaroni', 'bruschetta', 'pesto', 'alfredo', 'carbonara'},
    'Chinese': {'noodles', 'manchurian', 'schezwan', 'hakka', 'chow mein', 'dim sum', 'spring roll', 'szechuan', 'momos', 'wonton'},
    'North Indian': {'tandoori', 'masala', 'naan', 'roti', 'paratha', 'tikka', 'dal makhani', 'chole', 'bhature', 'kulcha', 'paneer'},
    'Continental': {'burger', 'sandwich', 'steak', 'fries', 'salad', 'soup', 'bread', 'grill', 'wrap', 'hot dog', 'tacos'},
    # Generic Indian is last to catch items that weren't classified above
    'Indian (General)': {'biryani', 'curry', 'thali', 'khichdi', 'pakora', 'samosa', 'bhaji'}
}

# --- 3. HIGH-SPEED VECTORIZED CLASSIFICATION ---

print("\nStarting optimized classification process...")
start_time = time.time()

# Create a lowercase version of the item names once to avoid repeating the operation
# Using .get('Item_Name') is safer in case the column doesn't exist
df['item_lower'] = df.get('Item_Name', pd.Series(dtype=str)).str.lower().fillna('')

# --- Part A: Food Type Classification (using np.where) ---
# This is much faster than .apply() for a simple if/else condition.
# We create a single regex pattern to find any of the non-veg keywords.
# \b ensures we match whole words only.
non_veg_regex = r'\b(' + '|'.join(re.escape(k) for k in non_veg_keywords) + r')\b'
df['Food Type'] = np.where(df['item_lower'].str.contains(non_veg_regex, regex=True, na=False), 
                           'Non-Veg', 
                           'Veg')


# --- Part B: Cuisine Classification (using np.select) ---
# This is the fastest way to handle multiple, ordered conditions (if/elif/elif/.../else).
conditions = []
choices = []

# Build lists of conditions and choices based on our ordered dictionary
for cuisine, keywords in cuisine_keywords.items():
    regex = r'\b(' + '|'.join(re.escape(k) for k in keywords) + r')\b'
    conditions.append(df['item_lower'].str.contains(regex, regex=True, na=False))
    choices.append(cuisine)

# np.select applies the conditions in order and assigns the corresponding choice.
# If no condition is met, it assigns the 'default' value.
df['Cuisine'] = np.select(conditions, choices, default='Other')


# --- 4. CLEANUP AND SAVE ---
# We can now drop the temporary lowercase column
df = df.drop(columns=['item_lower'])

end_time = time.time()
print(f"Classification completed in {end_time - start_time:.2f} seconds.")

# --- 5. DISPLAY RESULTS AND SAVE ---
print("\n--- Classification Summary ---")
print("\nValue Counts for 'Food Type':")
print(df['Food Type'].value_counts())

print("\nValue Counts for 'Cuisine':")
print(df['Cuisine'].value_counts())

output_filename = 'Zomato_Menu_Classified.xlsx'
print(f"\nSaving enriched data to '{output_filename}'...")
try:
    df.to_excel(output_filename, index=False)
    print("File saved successfully.")
except Exception as e:
    print(f"Error saving file: {e}")