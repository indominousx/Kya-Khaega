import { useState } from 'react';
import { supabase } from './supabaseClient';
import './LoginPage.css';

const CUISINE_OPTIONS = ['Indian (General)', 'North Indian', 'South Indian', 'Chinese', 'Italian', 'Continental', 'Maharashtrian', 'Mughlai', 'Beverages', 'Desserts', 'Other'];
const FOOD_TYPE_OPTIONS = ['Veg', 'Non-Veg'];

function LoginPage({ onLogin }) {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    name: '',
    dailyBudget: 500,
    cuisinePreferences: [],
    foodType: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleCuisineChange = (cuisine) => {
    setFormData(prev => ({
      ...prev,
      cuisinePreferences: prev.cuisinePreferences.includes(cuisine)
        ? prev.cuisinePreferences.filter(c => c !== cuisine)
        : [...prev.cuisinePreferences, cuisine]
    }));
  };

  const handleFoodTypeChange = (foodType) => {
    setFormData(prev => ({
      ...prev,
      foodType: foodType
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      if (isLogin) {
        // Login existing user
        const { data, error } = await supabase.auth.signInWithPassword({
          email: formData.email,
          password: formData.password,
        });

        if (error) throw error;

        // Fetch user preferences
        const { data: preferences, error: prefError } = await supabase
          .from('user_preferences')
          .select('*')
          .eq('user_id', data.user.id)
          .single();

        if (prefError && prefError.code !== 'PGRST116') {
          console.error('Error fetching preferences:', prefError);
        }

        onLogin(data.user, preferences);
      } else {
        // Register new user
        const { data, error } = await supabase.auth.signUp({
          email: formData.email,
          password: formData.password,
          options: {
            data: {
              name: formData.name,
            }
          }
        });

        if (error) throw error;

        if (data.user) {
          // Check if email confirmation is required
          if (data.user && !data.session) {
            // Email confirmation required
            setError('Please check your email and click the confirmation link to complete registration.');
            return;
          }

          // If user is confirmed or confirmation is disabled, save preferences
          if (data.session) {
            const { error: prefError } = await supabase
              .from('user_preferences')
              .insert([
                {
                  user_id: data.user.id,
                  name: formData.name,
                  daily_budget: formData.dailyBudget,
                  cuisine_preferences: formData.cuisinePreferences,
                  food_type: formData.foodType,
                  email: formData.email
                }
              ]);

            if (prefError) {
              console.error('Error saving preferences:', prefError);
            }
          }

          // Auto-login after successful registration (only if session exists)
          if (data.session) {
            onLogin(data.user, {
              name: formData.name,
              daily_budget: formData.dailyBudget,
              cuisine_preferences: formData.cuisinePreferences,
              food_type: formData.foodType
            });
          } else {
            // Store preferences in localStorage temporarily for after confirmation
            localStorage.setItem('pendingUserPreferences', JSON.stringify({
              name: formData.name,
              daily_budget: formData.dailyBudget,
              cuisine_preferences: formData.cuisinePreferences,
              food_type: formData.foodType
            }));
          }
        }
      }
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <h2>{isLogin ? 'Welcome Back!' : 'Join Kya Khaega'}</h2>
        
        <div className="toggle-buttons">
          <button 
            className={isLogin ? 'active' : ''} 
            onClick={() => setIsLogin(true)}
          >
            Login
          </button>
          <button 
            className={!isLogin ? 'active' : ''} 
            onClick={() => setIsLogin(false)}
          >
            Sign Up
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          {!isLogin && (
            <div className="form-group">
              <label>Name</label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                required
                placeholder="Enter your name"
              />
            </div>
          )}

          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleInputChange}
              required
              placeholder="Enter your email"
            />
          </div>

          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleInputChange}
              required
              placeholder="Enter your password"
              minLength={6}
            />
          </div>

          {!isLogin && (
            <>
              <div className="form-group">
                <label>Daily Budget (₹)</label>
                <input
                  type="range"
                  name="dailyBudget"
                  min="100"
                  max="2000"
                  step="50"
                  value={formData.dailyBudget}
                  onChange={handleInputChange}
                />
                <div className="budget-display">₹{formData.dailyBudget}</div>
              </div>

              <div className="form-group">
                <label>Preferred Cuisines</label>
                <div className="checkbox-group">
                  {CUISINE_OPTIONS.map(cuisine => (
                    <label key={cuisine} className="checkbox-label">
                      <input
                        type="checkbox"
                        checked={formData.cuisinePreferences.includes(cuisine)}
                        onChange={() => handleCuisineChange(cuisine)}
                      />
                      {cuisine}
                    </label>
                  ))}
                </div>
              </div>

              <div className="form-group">
                <label>Food Type Preference</label>
                <div className="radio-group">
                  {FOOD_TYPE_OPTIONS.map(foodType => (
                    <label key={foodType} className="radio-label">
                      <input
                        type="radio"
                        name="foodType"
                        value={foodType}
                        checked={formData.foodType === foodType}
                        onChange={() => handleFoodTypeChange(foodType)}
                      />
                      {foodType}
                    </label>
                  ))}
                </div>
              </div>
            </>
          )}

          {error && <div className="error-message">{error}</div>}

          <button type="submit" className="submit-button" disabled={loading}>
            {loading ? 'Processing...' : (isLogin ? 'Login' : 'Create Account')}
          </button>
        </form>
      </div>
    </div>
  );
}

export default LoginPage;