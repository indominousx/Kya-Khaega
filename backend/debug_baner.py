import pandas as pd

df = pd.read_csv('Zomato_Menu_Classified_with_Area.csv')

print(f'Original total items: {len(df)}')

# Apply the same cleaning as in the backend
df.dropna(subset=['Price'], inplace=True)
print(f'After dropping empty prices: {len(df)}')

df['Price'] = df['Price'].astype(str).str.replace(r'[^\d.]', '', regex=True)
df.loc[df['Price'] == '', 'Price'] = pd.NA
df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
df.dropna(subset=['Price'], inplace=True)
print(f'After numeric conversion: {len(df)}')

df.dropna(subset=['Item_Name', 'Restaurant_Name', 'Food Type', 'Cuisine'], inplace=True)
print(f'After dropping critical columns: {len(df)}')

# Filter for Baner
baner = df[df['Area'] == 'Baner']
print(f'Items in Baner: {len(baner)}')

if len(baner) > 0:
    print('Sample Baner items:')
    for i, (_, row) in enumerate(baner.head(10).iterrows()):
        print(f'{i+1}. {row["Item_Name"]} - ₹{row["Price"]} ({row["Restaurant_Name"]})')
        
    # Test sampling 5 items
    if len(baner) >= 5:
        sample = baner.sample(n=5, random_state=42)
        print(f'\nSample of 5 items:')
        for i, (_, row) in enumerate(sample.iterrows()):
            print(f'{i+1}. {row["Item_Name"]} - ₹{row["Price"]}')
    else:
        print(f'Only {len(baner)} items available, cannot sample 5')
else:
    print('No items found in Baner after filtering')