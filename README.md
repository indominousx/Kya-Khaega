# Kya Khaega - Food Recommendation App

A web application that helps users find food recommendations in Pune based on their preferences.

## Features

- **User Authentication**: Login/Register with email and password
- **User Preferences**: Set daily budget, cuisine preferences, and food type (Veg/Non-Veg)
- **Personalized Recommendations**: Get food suggestions based on your preferences
- **Data Persistence**: User preferences stored in Supabase database

## Setup Instructions

### 1. Supabase Setup

1. Create a new project at [supabase.com](https://supabase.com)
2. Go to the SQL editor in your Supabase dashboard
3. Run the SQL script from `supabase_setup.sql` to create the user_preferences table
4. Go to Settings > API to get your project URL and anon key

### 2. Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Create environment file:
   ```
   cp .env.example .env
   ```

4. Update the `.env` file with your Supabase credentials:
   ```
   REACT_APP_SUPABASE_URL=your_supabase_project_url
   REACT_APP_SUPABASE_ANON_KEY=your_supabase_anon_key
   ```

5. Start the frontend:
   ```
   npm start
   ```

### 3. Backend Setup

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Install Python dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Start the Flask server:
   ```
   python app.py
   ```

## Usage

1. **Registration**: New users can sign up by providing:
   - Name and email
   - Password (minimum 6 characters)
   - Daily budget (₹100 - ₹2000)
   - Preferred cuisines (multiple selection)
   - Food type preference (Veg/Non-Veg)

2. **Login**: Existing users can log in with email and password

3. **Get Recommendations**: 
   - Your preferences are automatically loaded
   - Adjust filters as needed
   - Click "Find Me Food!" to get personalized recommendations

4. **Logout**: Click the logout button to sign out

## Tech Stack

- **Frontend**: React.js, Supabase Auth
- **Backend**: Flask (Python), Pandas
- **Database**: Supabase (PostgreSQL)
- **Data**: CSV files with restaurant and menu information

## Database Schema

### user_preferences table
- `id`: UUID (Primary Key)
- `user_id`: UUID (Foreign Key to auth.users)
- `name`: TEXT (User's name)
- `email`: TEXT (User's email)
- `daily_budget`: INTEGER (Daily food budget)
- `cuisine_preferences`: TEXT[] (Array of preferred cuisines)
- `food_type`: TEXT (Veg or Non-Veg preference)
- `created_at`: TIMESTAMP
- `updated_at`: TIMESTAMP

## API Endpoints

- `POST /api/recommend`: Get food recommendations based on filters
  - Request body: `{ cuisines: [], foodTypes: [], minPrice: number, maxPrice: number }`
  - Response: Array of recommended food items

## Security Features

- Row Level Security (RLS) enabled on user_preferences table
- Users can only access their own data
- CORS configured for frontend-backend communication
- Password hashing handled by Supabase Auth