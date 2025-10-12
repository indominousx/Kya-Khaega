import pandas as pd

# Load the dataset
df = pd.read_csv('Zomato_Menu_Classified_with_Area.csv')

# Test the improved location filtering for Kondhwa
user_area = "Kondhwa"
print(f"Testing location filtering for: {user_area}")
print("=" * 50)

# Exact area match
exact_match = df[df['Area'].str.lower() == user_area.lower()]
print(f"Exact matches for '{user_area}': {len(exact_match)}")
if not exact_match.empty:
    print("Restaurant names in exact area:")
    restaurants = exact_match['Restaurant_Name'].unique()
    for i, restaurant in enumerate(restaurants[:10], 1):  # Show first 10
        print(f"  {i}. {restaurant}")
    print(f"Total unique restaurants: {len(restaurants)}")
else:
    print("No exact matches found.")

print("\n" + "=" * 50)

# Partial match
partial_match = df[
    (df['Area'].str.contains(user_area, case=False, na=False)) & 
    (df['Area'].str.lower() != user_area.lower())
]
print(f"Partial matches for '{user_area}': {len(partial_match)}")
if not partial_match.empty:
    areas = partial_match['Area'].unique()
    print("Areas with partial matches:")
    for area in areas[:5]:  # Show first 5 areas
        print(f"  - {area}")

print("\n" + "=" * 50)

# Test with different areas
test_areas = ["Baner", "Hinjawadi", "Shivajinagar"]
for area in test_areas:
    exact = len(df[df['Area'].str.lower() == area.lower()])
    partial = len(df[df['Area'].str.contains(area, case=False, na=False)])
    print(f"{area}: Exact={exact}, Partial={partial}")