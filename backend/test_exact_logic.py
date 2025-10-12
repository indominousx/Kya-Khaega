import pandas as pd
import json

# Simulate the exact same conditions as the API
df = pd.read_csv('Zomato_Menu_Classified_with_Area.csv')

# Clean data exactly like in the backend
df.dropna(subset=['Price'], inplace=True)
df['Price'] = df['Price'].astype(str).str.replace(r'[^\d.]', '', regex=True)
df.loc[df['Price'] == '', 'Price'] = pd.NA
df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
df.dropna(subset=['Price'], inplace=True)
df.dropna(subset=['Item_Name', 'Restaurant_Name', 'Food Type', 'Cuisine'], inplace=True)

print(f"Total cleaned data: {len(df)}")

# Filter just like the API (no food types, cuisines, or price filters - just area)
filtered_df = df.copy()
user_area = "Baner"

print(f"Filtered data: {len(filtered_df)}")

# Test the exact same logic
num_samples = 5
total_available = len(filtered_df)

print(f"Total items available after filtering: {total_available}")

if total_available >= num_samples:
    exact_area = filtered_df[filtered_df['Area'].str.lower() == user_area.lower()]
    other_areas = filtered_df[filtered_df['Area'].str.lower() != user_area.lower()]
    
    print(f"Items in {user_area}: {len(exact_area)}")
    print(f"Items in other areas: {len(other_areas)}")
    
    recommendations_list = []
    
    # Get up to 4 from user's area
    if not exact_area.empty:
        from_user_area = min(len(exact_area), 4)
        sampled_from_user = exact_area.sample(n=from_user_area, random_state=42)
        recommendations_list.extend(sampled_from_user.to_dict('records'))
        print(f"Added {from_user_area} from {user_area}")
    
    # Fill remaining slots from other areas
    remaining_needed = num_samples - len(recommendations_list)
    print(f"Remaining needed: {remaining_needed}")
    
    if remaining_needed > 0 and not other_areas.empty:
        from_other_areas = min(len(other_areas), remaining_needed)
        sampled_from_others = other_areas.sample(n=from_other_areas, random_state=42)
        recommendations_list.extend(sampled_from_others.to_dict('records'))
        print(f"Added {from_other_areas} from other areas")
    
    print(f"Final recommendations list length: {len(recommendations_list)}")
    
    # Convert back to DataFrame like in the API
    recommendations = pd.DataFrame(recommendations_list)
    print(f"Final DataFrame shape: {recommendations.shape}")
    
    # Convert to dict like in the API
    result_dict = recommendations.to_dict(orient='records')
    print(f"Final dict length: {len(result_dict)}")
    
    # Show items
    print("Final items:")
    for i, item in enumerate(result_dict):
        print(f"{i+1}. {item['Item_Name']} from {item['Area']}")
        
else:
    print(f"Not enough items: {total_available}")