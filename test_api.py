import requests
import json

try:
    response = requests.get('http://127.0.0.1:5000/api/dataset-analysis')
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("API Response Preview:")
        print(f"Total Items: {data['overview']['total_items']}")
        print(f"Total Restaurants: {data['overview']['total_restaurants']}")
        print(f"Average Price: ₹{data['overview']['avg_price']}")
        print(f"Most Popular Cuisine: {data['insights']['most_popular_cuisine']}")
        print("✅ API is working correctly!")
    else:
        print(f"❌ API Error: {response.text}")
        
except Exception as e:
    print(f"❌ Connection Error: {e}")