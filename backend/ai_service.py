import google.generativeai as genai
import pandas as pd
import json
import re
from typing import Dict, List, Optional, Tuple

class FoodAIService:
    def __init__(self, api_key: str):
        """Initialize the AI service with Gemini API key"""
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
    def understand_food_query(self, user_query: str, available_cuisines: List[str], 
                            available_areas: List[str], user_demographics: Dict = None) -> Dict:
        """
        Use Gemini AI to understand user's natural language food request
        and extract relevant preferences, considering user demographics
        """
        
        # Build context from user demographics
        demographics_context = ""
        if user_demographics:
            demographics_context = f"""
        
        User Demographics & Preferences:
        - Daily Budget: ₹{user_demographics.get('daily_budget', 'Not specified')}
        - Preferred Cuisines: {user_demographics.get('cuisine_preferences', 'Not specified')}
        - Food Type: {user_demographics.get('food_type', 'Not specified')}
        - User Name: {user_demographics.get('name', 'Not specified')}
        
        Consider these demographics when analyzing the query, especially for price and cuisine preferences.
        """
        
        prompt = f"""
        You are an intelligent food recommendation assistant for a restaurant app in Pune, India.
        Analyze this user query and extract relevant food preferences in JSON format.
        
        User Query: "{user_query}"{demographics_context}
        
        Available Cuisines: {', '.join(available_cuisines)}
        Available Areas: {', '.join(available_areas)}
        
        Extract and return ONLY a JSON object with these fields:
        {{
            "cuisines": [list of matching cuisines from available list],
            "food_types": [list from: "Veg", "Non-Veg", "Vegan", "Jain"],
            "dietary_preferences": [list from: "Spicy", "Mild", "Sweet", "Healthy", "Fast Food", "Rich", "Light", "Low-Oil", "Grilled", "Fried"],
            "meal_type": "string from: Breakfast, Lunch, Dinner, Snack, Dessert, Brunch",
            "price_preference": "string from: Budget, Mid-range, Premium, Ultra-Budget",
            "price_range": {{"min": number, "max": number}},
            "areas": [list of matching areas from available list],
            "delivery_time": "string from: Express, Standard, Flexible",
            "restaurant_type": [list from: "Fine-Dining", "Casual", "Quick-Bites", "Cafe", "Street-Food", "Cloud-Kitchen"],
            "cuisine_intensity": "string from: Authentic, Fusion, Mild-Fusion"
            "specific_dishes": [list of specific food items mentioned],
            "mood_context": "string describing the eating context/mood",
            "urgency": "string from: Immediate, Normal, Flexible",
            "group_size": "string from: Solo, Couple, Small Group, Large Group",
            "confidence": number between 0-1 indicating how well you understood the query
        }}
        
        Enhanced Rules for Advanced Filtering:
        
        FOOD TYPE DETECTION (Very Important):
        - "Veg"/"Vegetarian": vegetarian, veg, pure veg, no meat, no chicken, no fish
        - "Non-Veg": non-veg, meat, chicken, mutton, fish, seafood, egg
        - "Vegan": vegan, no dairy, plant-based, no milk products
        - "Jain": jain food, no onion, no garlic, jain-friendly
        - If user says "only veg" or "strictly vegetarian" → ["Veg"]
        - If user says "non-veg" or mentions meat → ["Non-Veg"] 
        - If unclear or no preference → ["Veg", "Non-Veg"]
        
        PRICE ANALYSIS:
        - Ultra-Budget: Under ₹100 per person ("very cheap", "under 100", "street food price")
        - Budget: ₹100-200 per person ("cheap", "budget", "affordable", "student budget")
        - Mid-range: ₹200-500 per person ("reasonable", "moderate", "decent price")  
        - Premium: Above ₹500 per person ("expensive", "fine dining", "premium", "splurge")
        - Extract specific amounts: "under 300", "around 400", "less than 250"
        
        RESTAURANT TYPE DETECTION:
        - "Fine-Dining": fine dining, fancy, upscale, formal, date night, anniversary
        - "Casual": casual, family restaurant, regular dining
        - "Quick-Bites": quick, fast, takeaway, grab and go, quick bite
        - "Cafe": cafe, coffee shop, bakery, dessert place
        - "Street-Food": street food, roadside, local vendors, chaat
        - "Cloud-Kitchen": delivery only, cloud kitchen, online only
        
        DELIVERY TIME:
        - "Express": urgent, quick delivery, fast, ASAP, hungry now
        - "Standard": normal delivery, regular time
        - "Flexible": no rush, can wait, planning ahead
        
        Additional Rules:
        - Prioritize explicit price mentions in query over demographics
        - For cuisines, combine query preferences with user's demographic preferences
        - Consider urgency: "quick", "fast" = Immediate; "later", "planning" = Flexible
        - Detect group context: "for two", "date", "family", "friends", "alone"
        - Be very precise with price range extraction - look for rupee amounts, budget words
        - If no price mentioned but demographics available, use 80% of daily budget as max
        - Return valid JSON only, no additional text or explanations
        """
        
        try:
            response = self.model.generate_content(prompt)
            
            # Clean the response to extract JSON
            response_text = response.text.strip()
            
            # Remove any markdown formatting
            response_text = re.sub(r'```json\s*', '', response_text)
            response_text = re.sub(r'```\s*$', '', response_text)
            
            # Parse JSON
            parsed_result = json.loads(response_text)
            
            # Validate and clean the result
            return self._validate_ai_response(parsed_result, available_cuisines, available_areas)
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            return self._create_fallback_response()
        except Exception as e:
            print(f"AI service error: {e}")
            return self._create_fallback_response()
    
    def _validate_ai_response(self, response: Dict, available_cuisines: List[str], 
                            available_areas: List[str]) -> Dict:
        """Validate and clean the AI response"""
        
        # Ensure all required fields exist with defaults
        validated_response = {
            "cuisines": [],
            "food_types": ["Veg", "Non-Veg"],  # Default to both unless specifically mentioned
            "dietary_preferences": [],
            "meal_type": "",
            "price_preference": "Mid-range",
            "price_range": {"min": 0, "max": 1000},
            "areas": [],
            "specific_dishes": [],
            "mood_context": "",
            "urgency": "Normal",
            "group_size": "Solo",
            "confidence": 0.5,
            "delivery_time": "Standard",
            "restaurant_type": [],
            "cuisine_intensity": "Authentic"
        }
        
        # Update with AI response, validating each field
        if isinstance(response, dict):
            # Validate cuisines
            if "cuisines" in response and isinstance(response["cuisines"], list):
                validated_cuisines = []
                for cuisine in response["cuisines"]:
                    # Case-insensitive matching
                    for available in available_cuisines:
                        if cuisine.lower() == available.lower():
                            validated_cuisines.append(available)
                            break
                validated_response["cuisines"] = validated_cuisines
            
            # Validate areas
            if "areas" in response and isinstance(response["areas"], list):
                validated_areas = []
                for area in response["areas"]:
                    # Case-insensitive and partial matching
                    for available in available_areas:
                        if area.lower() in available.lower() or available.lower() in area.lower():
                            validated_areas.append(available)
                            break
                validated_response["areas"] = validated_areas
            
            # Validate food types with enhanced options
            if "food_types" in response and isinstance(response["food_types"], list):
                valid_food_types = []
                allowed_food_types = ["Veg", "Non-Veg", "Vegan", "Jain"]
                for ft in response["food_types"]:
                    if ft in allowed_food_types:
                        valid_food_types.append(ft)
                if valid_food_types:
                    validated_response["food_types"] = valid_food_types
            
            # Validate restaurant types
            if "restaurant_type" in response and isinstance(response["restaurant_type"], list):
                valid_restaurant_types = []
                allowed_types = ["Fine-Dining", "Casual", "Quick-Bites", "Cafe", "Street-Food", "Cloud-Kitchen"]
                for rt in response["restaurant_type"]:
                    if rt in allowed_types:
                        valid_restaurant_types.append(rt)
                validated_response["restaurant_type"] = valid_restaurant_types
            
            # Validate price_range
            if "price_range" in response and isinstance(response["price_range"], dict):
                price_range = response["price_range"]
                if "min" in price_range and "max" in price_range:
                    try:
                        validated_response["price_range"] = {
                            "min": float(price_range["min"]),
                            "max": float(price_range["max"])
                        }
                    except (ValueError, TypeError):
                        pass
            
            # Copy other fields if they exist and are not None
            for field in ["dietary_preferences", "meal_type", "price_preference", 
                         "specific_dishes", "mood_context", "urgency", "group_size", "confidence",
                         "delivery_time", "cuisine_intensity"]:
                if field in response and response[field] is not None:
                    validated_response[field] = response[field]
        
        return validated_response
    
    def _create_fallback_response(self) -> Dict:
        """Create a fallback response when AI parsing fails"""
        return {
            "cuisines": [],
            "food_types": ["Veg", "Non-Veg"],
            "dietary_preferences": [],
            "meal_type": "",
            "price_preference": "Mid-range",
            "price_range": {"min": 0, "max": 1000},
            "areas": [],
            "specific_dishes": [],
            "mood_context": "general food search",
            "urgency": "Normal",
            "group_size": "Solo",
            "confidence": 0.1,
            "delivery_time": "Standard",
            "restaurant_type": [],
            "cuisine_intensity": "Authentic"
        }
    
    def generate_smart_filters(self, ai_understanding: Dict, df: pd.DataFrame, 
                             user_demographics: Dict = None) -> pd.DataFrame:
        """
        Apply intelligent filtering based on AI understanding of the user query and demographics
        """
        filtered_df = df.copy()
        
        # Apply cuisine filters (prioritize AI understanding, supplement with demographics)
        cuisines_to_filter = []
        if ai_understanding.get("cuisines"):
            cuisines_to_filter.extend(ai_understanding["cuisines"])
        elif user_demographics and user_demographics.get("cuisine_preferences"):
            # Use demographics as fallback if no cuisines in query
            demo_cuisines = user_demographics["cuisine_preferences"]
            if isinstance(demo_cuisines, str):
                try:
                    demo_cuisines = json.loads(demo_cuisines)
                except:
                    demo_cuisines = [demo_cuisines]
            if isinstance(demo_cuisines, list):
                cuisines_to_filter.extend(demo_cuisines)
        
        if cuisines_to_filter:
            cuisine_filter = filtered_df['Cuisine'].isin(cuisines_to_filter)
            filtered_df = filtered_df[cuisine_filter]
        
        # Enhanced food type filtering with stricter logic
        food_types_to_apply = []
        
        # Prioritize AI understanding
        if ai_understanding.get("food_types"):
            ai_food_types = ai_understanding["food_types"]
            # If user specified specific types (not default both)
            if len(ai_food_types) < 4:  # Less than all 4 types means specific preference
                food_types_to_apply = ai_food_types
        elif user_demographics and user_demographics.get("food_type"):
            # Use demographics as fallback
            demo_food_type = user_demographics["food_type"]
            if demo_food_type in ["Veg", "Non-Veg", "Vegan", "Jain"]:
                food_types_to_apply = [demo_food_type]
        
        # Apply food type filters
        if food_types_to_apply:
            food_type_conditions = []
            for food_type in food_types_to_apply:
                if food_type == "Vegan":
                    # Vegan: must be veg AND not contain dairy indicators
                    vegan_condition = (
                        filtered_df['Food Type'].str.contains('Veg', case=False, na=False) &
                        ~filtered_df['Item_Name'].str.contains('cheese|paneer|butter|ghee|milk|cream|curd', case=False, na=False)
                    )
                    food_type_conditions.append(vegan_condition)
                elif food_type == "Jain":
                    # Jain: must be veg AND not contain onion/garlic indicators
                    jain_condition = (
                        filtered_df['Food Type'].str.contains('Veg', case=False, na=False) &
                        ~filtered_df['Item_Name'].str.contains('onion|garlic|potato|ginger', case=False, na=False)
                    )
                    food_type_conditions.append(jain_condition)
                else:
                    # Regular Veg/Non-Veg filtering
                    condition = filtered_df['Food Type'].str.contains(food_type, case=False, na=False)
                    food_type_conditions.append(condition)
            
            if food_type_conditions:
                # Combine conditions with OR logic
                combined_food_filter = food_type_conditions[0]
                for condition in food_type_conditions[1:]:
                    combined_food_filter = combined_food_filter | condition
                filtered_df = filtered_df[combined_food_filter]
        
        # Apply area filters
        if ai_understanding.get("areas"):
            area_conditions = []
            for area in ai_understanding["areas"]:
                area_condition = filtered_df['Area'].str.contains(area, case=False, na=False)
                area_conditions.append(area_condition)
            
            if area_conditions:
                # Combine area conditions with OR
                combined_area_filter = area_conditions[0]
                for condition in area_conditions[1:]:
                    combined_area_filter = combined_area_filter | condition
                filtered_df = filtered_df[combined_area_filter]
        
        # Apply specific dish filters
        if ai_understanding.get("specific_dishes"):
            dish_conditions = []
            for dish in ai_understanding["specific_dishes"]:
                dish_condition = filtered_df['Item_Name'].str.contains(dish, case=False, na=False)
                dish_conditions.append(dish_condition)
            
            if dish_conditions:
                # Combine dish conditions with OR
                combined_dish_filter = dish_conditions[0]
                for condition in dish_conditions[1:]:
                    combined_dish_filter = combined_dish_filter | condition
                filtered_df = filtered_df[combined_dish_filter]
        
        # Enhanced price filtering with demographics consideration
        if 'Price' in filtered_df.columns:
            price_range = ai_understanding.get("price_range", {})
            
            # Use AI-extracted price range if available
            if price_range.get("min") is not None and price_range.get("max") is not None:
                min_price = price_range["min"]
                max_price = price_range["max"]
                filtered_df = filtered_df[(filtered_df['Price'] >= min_price) & (filtered_df['Price'] <= max_price)]
            
            # Fallback to enhanced price preference categories
            elif ai_understanding.get("price_preference"):
                price_pref = ai_understanding["price_preference"]
                if price_pref == "Ultra-Budget":
                    max_budget = 100
                    # Use user's daily budget if lower
                    if user_demographics and user_demographics.get("daily_budget"):
                        user_budget = float(user_demographics["daily_budget"])
                        max_budget = min(max_budget, user_budget)
                    filtered_df = filtered_df[filtered_df['Price'] <= max_budget]
                elif price_pref == "Budget":
                    min_price = 100
                    max_budget = 200
                    # Use user's daily budget if lower
                    if user_demographics and user_demographics.get("daily_budget"):
                        user_budget = float(user_demographics["daily_budget"])
                        max_budget = min(max_budget, user_budget)
                    filtered_df = filtered_df[(filtered_df['Price'] >= min_price) & (filtered_df['Price'] <= max_budget)]
                elif price_pref == "Mid-range":
                    min_price = 200
                    max_price = 500
                    # Adjust based on user demographics
                    if user_demographics and user_demographics.get("daily_budget"):
                        user_budget = float(user_demographics["daily_budget"])
                        max_price = min(max_price, user_budget)
                    filtered_df = filtered_df[(filtered_df['Price'] >= min_price) & (filtered_df['Price'] <= max_price)]
                elif price_pref == "Premium":
                    min_price = 500
                    # Cap at user's daily budget if available
                    if user_demographics and user_demographics.get("daily_budget"):
                        user_budget = float(user_demographics["daily_budget"])
                        if user_budget < min_price:
                            # If user budget is less than premium threshold, adjust
                            filtered_df = filtered_df[filtered_df['Price'] <= user_budget]
                        else:
                            filtered_df = filtered_df[filtered_df['Price'] >= min_price]
                    else:
                        filtered_df = filtered_df[filtered_df['Price'] >= min_price]
            
            # Use demographics budget as last resort
            elif user_demographics and user_demographics.get("daily_budget"):
                user_budget = float(user_demographics["daily_budget"])
                # Use 80% of daily budget as max spending per meal
                max_meal_budget = user_budget * 0.8
                filtered_df = filtered_df[filtered_df['Price'] <= max_meal_budget]
        
        # Apply dietary preference filters
        if ai_understanding.get("dietary_preferences"):
            dietary_prefs = ai_understanding["dietary_preferences"]
            dietary_conditions = []
            
            for pref in dietary_prefs:
                if pref == "Spicy":
                    spicy_condition = filtered_df['Item_Name'].str.contains(
                        'spicy|hot|chili|pepper|masala|tandoori', case=False, na=False
                    )
                    dietary_conditions.append(spicy_condition)
                elif pref == "Mild":
                    mild_condition = ~filtered_df['Item_Name'].str.contains(
                        'spicy|hot|chili|pepper', case=False, na=False
                    )
                    dietary_conditions.append(mild_condition)
                elif pref == "Sweet":
                    sweet_condition = filtered_df['Item_Name'].str.contains(
                        'sweet|dessert|ice cream|cake|laddu|gulab|kheer|halwa', case=False, na=False
                    )
                    dietary_conditions.append(sweet_condition)
                elif pref == "Healthy":
                    healthy_condition = filtered_df['Item_Name'].str.contains(
                        'salad|grilled|steamed|boiled|soup|fruit|juice|smoothie', case=False, na=False
                    )
                    dietary_conditions.append(healthy_condition)
                elif pref == "Fast Food":
                    fast_food_condition = filtered_df['Item_Name'].str.contains(
                        'burger|pizza|sandwich|wrap|roll|fries|nugget', case=False, na=False
                    )
                    dietary_conditions.append(fast_food_condition)
                elif pref == "Grilled":
                    grilled_condition = filtered_df['Item_Name'].str.contains(
                        'grilled|barbecue|bbq|tikka|kebab', case=False, na=False
                    )
                    dietary_conditions.append(grilled_condition)
                elif pref == "Fried":
                    fried_condition = filtered_df['Item_Name'].str.contains(
                        'fried|crispy|pakora|samosa|cutlet|vada', case=False, na=False
                    )
                    dietary_conditions.append(fried_condition)
            
            if dietary_conditions:
                # Combine dietary conditions with OR logic
                combined_dietary_filter = dietary_conditions[0]
                for condition in dietary_conditions[1:]:
                    combined_dietary_filter = combined_dietary_filter | condition
                filtered_df = filtered_df[combined_dietary_filter]
        
        # Apply restaurant type filters (if we have restaurant data)
        if ai_understanding.get("restaurant_type") and 'Restaurant_Name' in filtered_df.columns:
            restaurant_types = ai_understanding["restaurant_type"]
            restaurant_conditions = []
            
            for rest_type in restaurant_types:
                if rest_type == "Quick-Bites":
                    quick_condition = filtered_df['Item_Name'].str.contains(
                        'roll|wrap|sandwich|burger|pizza slice|quick|fast', case=False, na=False
                    )
                    restaurant_conditions.append(quick_condition)
                elif rest_type == "Street-Food":
                    street_condition = filtered_df['Item_Name'].str.contains(
                        'chaat|bhel|pani puri|vada pav|samosa|pakora|dosa|idli', case=False, na=False
                    )
                    restaurant_conditions.append(street_condition)
                elif rest_type == "Cafe":
                    cafe_condition = filtered_df['Item_Name'].str.contains(
                        'coffee|tea|cake|pastry|sandwich|salad|smoothie|juice', case=False, na=False
                    )
                    restaurant_conditions.append(cafe_condition)
            
            if restaurant_conditions:
                # Combine restaurant type conditions with OR logic
                combined_restaurant_filter = restaurant_conditions[0]
                for condition in restaurant_conditions[1:]:
                    combined_restaurant_filter = combined_restaurant_filter | condition
                filtered_df = filtered_df[combined_restaurant_filter]
        
        return filtered_df
    
    def rank_recommendations_with_context(self, filtered_df: pd.DataFrame, 
                                        ai_understanding: Dict, user_demographics: Dict = None) -> pd.DataFrame:
        """
        Rank recommendations based on AI understanding and context
        """
        if filtered_df.empty:
            return filtered_df
        
        scored_df = filtered_df.copy()
        scored_df['ai_score'] = 0.0
        
        # Base scoring
        scored_df['rating_score'] = scored_df['Dining_Rating'].fillna(3.0)
        scored_df['votes_score'] = scored_df['Votes'].fillna(1)
        
        # Normalize votes (0-2 scale)
        max_votes = scored_df['votes_score'].max()
        if max_votes > 0:
            scored_df['votes_normalized'] = (scored_df['votes_score'] / max_votes) * 2
        else:
            scored_df['votes_normalized'] = 1
        
        # Context-based scoring boosts
        confidence = ai_understanding.get('confidence', 0.5)
        
        # Boost for specific dishes mentioned
        if ai_understanding.get('specific_dishes'):
            for dish in ai_understanding['specific_dishes']:
                dish_match = scored_df['Item_Name'].str.contains(dish, case=False, na=False)
                scored_df.loc[dish_match, 'ai_score'] += 2.0 * confidence
        
        # Boost for preferred cuisines
        if ai_understanding.get('cuisines'):
            cuisine_match = scored_df['Cuisine'].isin(ai_understanding['cuisines'])
            scored_df.loc[cuisine_match, 'ai_score'] += 1.5 * confidence
        
        # Boost for preferred areas
        if ai_understanding.get('areas'):
            for area in ai_understanding['areas']:
                area_match = scored_df['Area'].str.contains(area, case=False, na=False)
                scored_df.loc[area_match, 'ai_score'] += 1.0 * confidence
        
        # Meal type context scoring
        meal_type = ai_understanding.get('meal_type')
        if meal_type and meal_type.strip():
            meal_type = meal_type.lower()
            if meal_type in ['breakfast']:
                breakfast_items = scored_df['Item_Name'].str.contains(
                    'dosa|idli|poha|upma|paratha|sandwich|coffee|tea', case=False, na=False)
                scored_df.loc[breakfast_items, 'ai_score'] += 1.0 * confidence
            elif meal_type in ['lunch', 'dinner']:
                main_items = scored_df['Item_Name'].str.contains(
                    'rice|biryani|curry|dal|roti|naan|thali', case=False, na=False)
                scored_df.loc[main_items, 'ai_score'] += 1.0 * confidence
            elif meal_type in ['snack']:
                snack_items = scored_df['Item_Name'].str.contains(
                    'chat|samosa|vada|bhaji|fries|burger|pizza', case=False, na=False)
                scored_df.loc[snack_items, 'ai_score'] += 1.0 * confidence
            elif meal_type in ['dessert']:
                dessert_items = scored_df['Item_Name'].str.contains(
                    'ice cream|cake|sweet|kulfi|gulab|rasmalai|kheer', case=False, na=False)
                scored_df.loc[dessert_items, 'ai_score'] += 1.0 * confidence
        
        # Enhanced dietary preferences scoring
        if ai_understanding.get('dietary_preferences'):
            for pref in ai_understanding['dietary_preferences']:
                pref_lower = pref.lower()
                if pref_lower == 'spicy':
                    spicy_items = scored_df['Item_Name'].str.contains(
                        'spicy|hot|chili|schezwan|andhra|kerala|masala|tandoori', case=False, na=False)
                    scored_df.loc[spicy_items, 'ai_score'] += 0.8 * confidence
                elif pref_lower == 'healthy':
                    healthy_items = scored_df['Item_Name'].str.contains(
                        'salad|soup|grilled|steamed|boiled|fruit|juice|smoothie', case=False, na=False)
                    scored_df.loc[healthy_items, 'ai_score'] += 0.8 * confidence
                elif pref_lower == 'sweet':
                    sweet_items = scored_df['Item_Name'].str.contains(
                        'sweet|dessert|ice cream|cake|laddu|gulab|kheer|halwa', case=False, na=False)
                    scored_df.loc[sweet_items, 'ai_score'] += 0.8 * confidence
                elif pref_lower == 'fast food':
                    fast_items = scored_df['Item_Name'].str.contains(
                        'burger|pizza|sandwich|wrap|roll|fries|nugget', case=False, na=False)
                    scored_df.loc[fast_items, 'ai_score'] += 0.7 * confidence
                elif pref_lower == 'grilled':
                    grilled_items = scored_df['Item_Name'].str.contains(
                        'grilled|barbecue|bbq|tikka|kebab', case=False, na=False)
                    scored_df.loc[grilled_items, 'ai_score'] += 0.7 * confidence
                elif pref_lower == 'fried':
                    fried_items = scored_df['Item_Name'].str.contains(
                        'fried|crispy|pakora|samosa|cutlet|vada', case=False, na=False)
                    scored_df.loc[fried_items, 'ai_score'] += 0.6 * confidence
                elif pref_lower == 'mild':
                    # Boost items that don't contain spicy indicators
                    mild_items = ~scored_df['Item_Name'].str.contains(
                        'spicy|hot|chili|pepper', case=False, na=False)
                    scored_df.loc[mild_items, 'ai_score'] += 0.5 * confidence
        
        # Food type preference scoring
        if ai_understanding.get('food_types') and len(ai_understanding['food_types']) < 4:
            for food_type in ai_understanding['food_types']:
                if food_type == 'Veg':
                    veg_items = scored_df['Food Type'].str.contains('Veg', case=False, na=False)
                    scored_df.loc[veg_items, 'ai_score'] += 0.5 * confidence
                elif food_type == 'Non-Veg':
                    nonveg_items = scored_df['Food Type'].str.contains('Non-Veg', case=False, na=False)
                    scored_df.loc[nonveg_items, 'ai_score'] += 0.5 * confidence
                elif food_type == 'Vegan':
                    vegan_items = (
                        scored_df['Food Type'].str.contains('Veg', case=False, na=False) &
                        ~scored_df['Item_Name'].str.contains('cheese|paneer|butter|ghee|milk|cream|curd', case=False, na=False)
                    )
                    scored_df.loc[vegan_items, 'ai_score'] += 0.7 * confidence
                elif food_type == 'Jain':
                    jain_items = (
                        scored_df['Food Type'].str.contains('Veg', case=False, na=False) &
                        ~scored_df['Item_Name'].str.contains('onion|garlic|potato|ginger', case=False, na=False)
                    )
                    scored_df.loc[jain_items, 'ai_score'] += 0.7 * confidence
        
        # Restaurant type scoring
        if ai_understanding.get('restaurant_type'):
            for rest_type in ai_understanding['restaurant_type']:
                if rest_type == 'Quick-Bites':
                    quick_items = scored_df['Item_Name'].str.contains(
                        'roll|wrap|sandwich|burger|pizza slice|quick|fast', case=False, na=False)
                    scored_df.loc[quick_items, 'ai_score'] += 0.6 * confidence
                elif rest_type == 'Street-Food':
                    street_items = scored_df['Item_Name'].str.contains(
                        'chaat|bhel|pani puri|vada pav|samosa|pakora|dosa|idli', case=False, na=False)
                    scored_df.loc[street_items, 'ai_score'] += 0.6 * confidence
                elif rest_type == 'Cafe':
                    cafe_items = scored_df['Item_Name'].str.contains(
                        'coffee|tea|cake|pastry|sandwich|salad|smoothie|juice', case=False, na=False)
                    scored_df.loc[cafe_items, 'ai_score'] += 0.6 * confidence
        
        # Calculate final score
        scored_df['final_score'] = (
            scored_df['rating_score'] + 
            scored_df['votes_normalized'] + 
            scored_df['ai_score']
        )
        
        # Sort by final score
        return scored_df.sort_values('final_score', ascending=False)
    
    def get_demographic_recommendations(self, df: pd.DataFrame, user_demographics: Dict, 
                                      ai_understanding: Dict, count: int = 2) -> List[Dict]:
        """
        Get recommendations based purely on user demographics (for fallback suggestions)
        """
        if not user_demographics or df.empty:
            return []
        
        demographic_df = df.copy()
        
        # Filter by user's preferred cuisines
        if user_demographics.get('cuisine_preferences'):
            try:
                cuisine_prefs = user_demographics['cuisine_preferences']
                if isinstance(cuisine_prefs, str):
                    cuisine_prefs = json.loads(cuisine_prefs)
                if isinstance(cuisine_prefs, list) and len(cuisine_prefs) > 0:
                    cuisine_filter = demographic_df['Cuisine'].isin(cuisine_prefs)
                    demographic_df = demographic_df[cuisine_filter]
            except:
                pass
        
        # Filter by food type preference
        if user_demographics.get('food_type'):
            food_type = user_demographics['food_type']
            if food_type in ['Veg', 'Non-Veg']:
                food_type_filter = demographic_df['Food Type'].str.contains(food_type, case=False, na=False)
                demographic_df = demographic_df[food_type_filter]
        
        # Filter by daily budget
        if user_demographics.get('daily_budget') and 'Price' in demographic_df.columns:
            try:
                daily_budget = float(user_demographics['daily_budget'])
                # Use 70% of daily budget for demographic recommendations
                max_price = daily_budget * 0.7
                demographic_df = demographic_df[demographic_df['Price'] <= max_price]
            except:
                pass
        
        if demographic_df.empty:
            return []
        
        # Score based on user preferences
        demographic_df['demo_score'] = 0.0
        demographic_df['rating_score'] = demographic_df['Dining_Rating'].fillna(3.0)
        demographic_df['votes_score'] = demographic_df['Votes'].fillna(1)
        
        # Normalize votes
        max_votes = demographic_df['votes_score'].max()
        if max_votes > 0:
            demographic_df['votes_normalized'] = (demographic_df['votes_score'] / max_votes) * 2
        else:
            demographic_df['votes_normalized'] = 1
        
        # Boost for exact cuisine matches
        if user_demographics.get('cuisine_preferences'):
            try:
                cuisine_prefs = user_demographics['cuisine_preferences']
                if isinstance(cuisine_prefs, str):
                    cuisine_prefs = json.loads(cuisine_prefs)
                if isinstance(cuisine_prefs, list):
                    for cuisine in cuisine_prefs:
                        exact_match = demographic_df['Cuisine'].str.lower() == cuisine.lower()
                        demographic_df.loc[exact_match, 'demo_score'] += 2.0
            except:
                pass
        
        # Boost for affordable options within budget
        if user_demographics.get('daily_budget'):
            try:
                daily_budget = float(user_demographics['daily_budget'])
                # Boost items that are good value (under 50% of daily budget)
                affordable_items = demographic_df['Price'] <= (daily_budget * 0.5)
                demographic_df.loc[affordable_items, 'demo_score'] += 1.0
            except:
                pass
        
        # Calculate final demographic score
        demographic_df['final_demo_score'] = (
            demographic_df['rating_score'] + 
            demographic_df['votes_normalized'] + 
            demographic_df['demo_score']
        )
        
        # Get top recommendations from different restaurants
        top_demos = demographic_df.nlargest(count * 3, 'final_demo_score')  # Get more to ensure variety
        
        recommendations = []
        used_restaurants = set()
        
        for _, item in top_demos.iterrows():
            if len(recommendations) >= count:
                break
                
            restaurant_name = item.get('Restaurant_Name', 'Unknown')
            if restaurant_name not in used_restaurants:
                recommendations.append({
                    'name': str(item.get('Item_Name', 'Unknown')),
                    'restaurant': str(restaurant_name),
                    'cuisine': str(item.get('Cuisine', 'Not specified')),
                    'food_type': str(item.get('Food Type', 'Not specified')),
                    'area': str(item.get('Area', 'Not specified')),
                    'price': float(item.get('Price', 0)) if pd.notna(item.get('Price')) else 0.0,
                    'rating': float(item.get('Dining_Rating', 0)) if pd.notna(item.get('Dining_Rating')) else 0.0,
                    'votes': int(item.get('Votes', 0)) if pd.notna(item.get('Votes')) else 0,
                    'score': round(float(item.get('final_demo_score', 0)), 2),
                    'source': 'demographics'
                })
                used_restaurants.add(restaurant_name)
        
        return recommendations
    
    def generate_explanation(self, ai_understanding: Dict, recommendations: List[Dict], 
                           user_demographics: Dict = None) -> str:
        """Generate a human-readable explanation of why these recommendations were chosen"""
        
        explanation_parts = []
        
        confidence = ai_understanding.get('confidence', 0.5)
        
        if confidence > 0.8:
            explanation_parts.append("🎯 I perfectly understood your request! Here's what I found:")
        elif confidence > 0.6:
            explanation_parts.append("✨ I understood your request well and found these great matches:")
        elif confidence > 0.4:
            explanation_parts.append("📝 Based on what I understood from your request:")
        else:
            explanation_parts.append("🍽️ Here are some popular options that might interest you:")
        
        # Add context about filters applied
        if ai_understanding.get('specific_dishes'):
            explanation_parts.append(f"🥘 Looking for {', '.join(ai_understanding['specific_dishes'])}")
        
        if ai_understanding.get('cuisines'):
            explanation_parts.append(f"🌶️ Focusing on {', '.join(ai_understanding['cuisines'])} cuisine")
        
        if ai_understanding.get('areas'):
            explanation_parts.append(f"📍 In the {', '.join(ai_understanding['areas'])} area(s)")
        
        # Price context
        price_range = ai_understanding.get('price_range', {})
        if price_range.get('min') is not None and price_range.get('max') is not None:
            min_price = int(price_range['min'])
            max_price = int(price_range['max'])
            if min_price == max_price:
                explanation_parts.append(f"💰 Around ₹{max_price} budget")
            else:
                explanation_parts.append(f"💰 Within ₹{min_price}-₹{max_price} budget")
        elif ai_understanding.get('price_preference'):
            price_pref = ai_understanding['price_preference']
            if price_pref == 'Budget':
                explanation_parts.append("💰 Budget-friendly options")
            elif price_pref == 'Premium':
                explanation_parts.append("💎 Premium dining options")
            else:
                explanation_parts.append("💰 Reasonably priced options")
        
        # Meal and dietary context
        if ai_understanding.get('meal_type') and ai_understanding['meal_type']:
            explanation_parts.append(f"🍽️ Perfect for {ai_understanding['meal_type'].lower()}")
        
        if ai_understanding.get('dietary_preferences'):
            dietary = ', '.join(ai_understanding['dietary_preferences']).lower()
            explanation_parts.append(f"🌿 Matching your {dietary} preferences")
        
        if ai_understanding.get('food_types') and len(ai_understanding['food_types']) == 1:
            food_type = ai_understanding['food_types'][0]
            if food_type == 'Veg':
                explanation_parts.append("🥗 Vegetarian options")
            elif food_type == 'Non-Veg':
                explanation_parts.append("🍖 Non-vegetarian options")
        
        # Context about urgency and group
        if ai_understanding.get('urgency') == 'Immediate':
            explanation_parts.append("⚡ Quick service options")
        elif ai_understanding.get('urgency') == 'Flexible':
            explanation_parts.append("⏰ For planned dining")
        
        if ai_understanding.get('group_size'):
            group_size = ai_understanding['group_size']
            if group_size == 'Couple':
                explanation_parts.append("💕 Perfect for couples")
            elif group_size in ['Small Group', 'Large Group']:
                explanation_parts.append("👥 Great for groups")
        
        if ai_understanding.get('mood_context') and ai_understanding['mood_context'] != 'general food search':
            explanation_parts.append(f"✨ {ai_understanding['mood_context']}")
        
        # Add demographic context if available
        if user_demographics:
            demo_parts = []
            if user_demographics.get('daily_budget'):
                daily_budget = float(user_demographics['daily_budget'])
                demo_parts.append(f"considering your ₹{int(daily_budget)} daily budget")
            
            if user_demographics.get('cuisine_preferences'):
                try:
                    prefs = user_demographics['cuisine_preferences']
                    if isinstance(prefs, str):
                        prefs = json.loads(prefs)
                    if isinstance(prefs, list) and len(prefs) > 0:
                        demo_parts.append(f"and your preference for {', '.join(prefs[:2])} cuisine")
                except:
                    pass
            
            if demo_parts:
                explanation_parts.append(f"👤 Personalized {' '.join(demo_parts)}")
        
        return " ".join(explanation_parts)