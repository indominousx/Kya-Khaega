import pandas as pd

# Load and clean data exactly like the backend
df = pd.read_csv('Zomato_Menu_Classified_with_Area.csv')
df.dropna(subset=['Price'], inplace=True)
df['Price'] = df['Price'].astype(str).str.replace(r'[^\d.]', '', regex=True)
df.loc[df['Price'] == '', 'Price'] = pd.NA
df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
df.dropna(subset=['Price'], inplace=True)
df.dropna(subset=['Item_Name', 'Restaurant_Name', 'Food Type', 'Cuisine'], inplace=True)

# Test specifically with Baner area and check for duplicates
user_area = "Baner"
filtered_df = df.copy()

print(f"Total data: {len(filtered_df)}")

exact_area = filtered_df[filtered_df['Area'].str.lower() == user_area.lower()]
print(f"Exact area matches: {len(exact_area)}")

# Check for duplicates that might cause issues
print(f"Unique items in Baner: {exact_area['Item_Name'].nunique()}")
print(f"Total rows in Baner: {len(exact_area)}")

# Check if sampling 4 works
sample_4 = exact_area.sample(n=4, random_state=42)
print(f"Sample 4 shape: {sample_4.shape}")

# Convert to list of dicts like in the API
records_4 = sample_4.to_dict('records')
print(f"Records 4 length: {len(records_4)}")

# Check if there are any None/NaN values that might cause issues
print("Checking for problematic values:")
for col in sample_4.columns:
    null_count = sample_4[col].isnull().sum()
    if null_count > 0:
        print(f"Column {col} has {null_count} null values")

# Test the exact conditions when userArea is specified
recommendations_list = []
if not exact_area.empty:
    from_user_area = min(len(exact_area), 4)
    sampled = exact_area.sample(n=from_user_area, random_state=42)
    recommendations_list.extend(sampled.to_dict('records'))
    print(f"Added {from_user_area} from user area")

print(f"Recommendations list length: {len(recommendations_list)}")

# Check if converting back to DataFrame causes issues
recommendations_df = pd.DataFrame(recommendations_list)
print(f"DataFrame from list shape: {recommendations_df.shape}")

# Final conversion
final_dict = recommendations_df.to_dict(orient='records')
print(f"Final dict length: {len(final_dict)}")

print("Items:")
for i, item in enumerate(final_dict):
    print(f"{i+1}. {item.get('Item_Name', 'No name')} from {item.get('Area', 'No area')}")