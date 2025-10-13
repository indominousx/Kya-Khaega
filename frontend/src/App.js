// File: frontend/src/App.js

// FIX: Removed 'import React' as it's not explicitly used and can cause build errors.
import { useState, useEffect } from 'react'; 
import Slider from 'rc-slider';
import 'rc-slider/assets/index.css';
import './App.css';
import LoginPage from './LoginPage';
import ModernUI from './ModernUI';
import { supabase } from './supabaseClient';
import config from './config';

const CUISINE_OPTIONS = ['Indian (General)', 'North Indian', 'South Indian', 'Chinese', 'Italian', 'Continental', 'Maharashtrian', 'Mughlai', 'Beverages', 'Desserts', 'Other'];
const FOOD_TYPE_OPTIONS = ['Veg', 'Non-Veg'];

// Pune area mapping with precise coordinates
const PUNE_AREAS = {
  'Hinjawadi':     { lat: 18.591684, lng: 73.734782, radius: 0.05 },
  'Baner':         { lat: 18.559658, lng: 73.779938, radius: 0.03 },
  'Wakad':         { lat: 18.599348, lng: 73.762495, radius: 0.03 },
  'Aundh':         { lat: 18.564997, lng: 73.807742, radius: 0.03 },
  'Shivajinagar':  { lat: 18.530429, lng: 73.847216, radius: 0.02 },
  'Koregaon Park': { lat: 18.536157, lng: 73.893059, radius: 0.02 },
  'FC Road':       { lat: 18.519601, lng: 73.855303, radius: 0.02 },
  'Camp':          { lat: 18.514321, lng: 73.877292, radius: 0.02 },
  'Kothrud':       { lat: 18.509592, lng: 73.807682, radius: 0.03 },
  'Karve Nagar':   { lat: 18.480440, lng: 73.826770, radius: 0.02 },
  'Deccan':        { lat: 18.516726, lng: 73.841941, radius: 0.02 },
  'Viman Nagar':   { lat: 18.567902, lng: 73.914297, radius: 0.03 },
  'Kalyani Nagar': { lat: 18.548075, lng: 73.904042, radius: 0.02 },
  'Hadapsar':      { lat: 18.508944, lng: 73.926021, radius: 0.03 },
  'Kondhwa':       { lat: 18.463520, lng: 73.892378, radius: 0.03 },
  'Bibvewadi':     { lat: 18.479291, lng: 73.868566, radius: 0.02 },
  'Warje':         { lat: 18.491313, lng: 73.807776, radius: 0.02 },
};

// Function to calculate distance between two coordinates
const calculateDistance = (lat1, lng1, lat2, lng2) => {
  const R = 6371; // Radius of the Earth in km
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLng = (lng2 - lng1) * Math.PI / 180;
  const a = 
    Math.sin(dLat/2) * Math.sin(dLat/2) +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * 
    Math.sin(dLng/2) * Math.sin(dLng/2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  return R * c; // Distance in km
};

// Function to determine user's area based on coordinates
const getUserArea = (latitude, longitude) => {
  let closestArea = null;
  let minDistance = Infinity;

  console.log(`Checking coordinates: ${latitude}, ${longitude}`);

  for (const [areaName, areaData] of Object.entries(PUNE_AREAS)) {
    const distance = calculateDistance(latitude, longitude, areaData.lat, areaData.lng);
    // Convert radius from degrees to km (1 degree ≈ 111 km)
    const radiusKm = areaData.radius * 111;
    
    console.log(`${areaName}: ${distance.toFixed(2)}km (radius: ${radiusKm.toFixed(1)}km) ${distance <= radiusKm ? 'MATCH' : 'no'}`);
    
    if (distance <= radiusKm && distance < minDistance) {
      minDistance = distance;
      closestArea = areaName;
    }
  }

  console.log(`Final detected area: ${closestArea} (${minDistance.toFixed(2)}km away)`);
  return closestArea;
};

function App() {
  const [user, setUser] = useState(null);
  const [userPreferences, setUserPreferences] = useState(null);
  const [selectedCuisines, setSelectedCuisines] = useState([]);
  const [selectedFoodTypes, setSelectedFoodTypes] = useState([]);
  const [priceRange, setPriceRange] = useState([100, 1000]);
  const [recommendations, setRecommendations] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [authLoading, setAuthLoading] = useState(true);
  const [userLocation, setUserLocation] = useState(null);
  const [locationError, setLocationError] = useState('');
  const [availableAreas, setAvailableAreas] = useState([]);
  const [selectedArea, setSelectedArea] = useState('');
  const [useModernUI, setUseModernUI] = useState(true); // Toggle for new UI

  // Get user location on app load
  useEffect(() => {
    const getUserLocation = () => {
      if (navigator.geolocation) {
        console.log('Requesting geolocation...');
        navigator.geolocation.getCurrentPosition(
          (position) => {
            const coords = {
              latitude: position.coords.latitude,
              longitude: position.coords.longitude
            };
            console.log('Location captured:', coords);
            
            const detectedArea = getUserArea(coords.latitude, coords.longitude);
            console.log('Detected area:', detectedArea);
            
            setUserLocation(coords);
            if (!detectedArea) {
              setLocationError('Your location is outside our service areas. Please select your area manually.');
            }
          },
          (error) => {
            console.error('Geolocation error:', error);
            let errorMsg = 'Location access denied. Please allow location access for better recommendations.';
            if (error.code === 1) {
              errorMsg = 'Location access denied. Please allow location access and refresh the page.';
            } else if (error.code === 2) {
              errorMsg = 'Location unavailable. Please select your area manually.';
            } else if (error.code === 3) {
              errorMsg = 'Location request timeout. Please select your area manually.';
            }
            setLocationError(errorMsg);
          },
          {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 300000 // Cache for 5 minutes
          }
        );
      } else {
        setLocationError('Geolocation is not supported by this browser.');
      }
    };

    getUserLocation();
  }, []);

  // Fetch available areas
  useEffect(() => {
    const fetchAreas = async () => {
      try {
        const API_URL = config.api.baseUrl;
        const response = await fetch(`${API_URL}/api/areas`);
        if (response.ok) {
          const data = await response.json();
          setAvailableAreas(data.areas || []);
        }
      } catch (error) {
        console.error('Failed to fetch areas:', error);
      }
    };

    fetchAreas();
  }, []);

  // Check for existing session on app load
  useEffect(() => {
    const checkSession = async () => {
      const { data: { session } } = await supabase.auth.getSession();
      if (session) {
        setUser(session.user);
        
        // Check for pending preferences from localStorage
        const pendingPrefs = localStorage.getItem('pendingUserPreferences');
        if (pendingPrefs) {
          const preferences = JSON.parse(pendingPrefs);
          // Save pending preferences to database
          await supabase
            .from('user_preferences')
            .insert([
              {
                user_id: session.user.id,
                name: preferences.name,
                daily_budget: preferences.daily_budget,
                cuisine_preferences: preferences.cuisine_preferences,
                food_type: preferences.food_type,
                email: session.user.email
              }
            ]);
          // Clear pending preferences
          localStorage.removeItem('pendingUserPreferences');
        }

        // Fetch user preferences
        const { data: preferences } = await supabase
          .from('user_preferences')
          .select('*')
          .eq('user_id', session.user.id)
          .single();
        
        if (preferences) {
          setUserPreferences(preferences);
          // Set initial values based on user preferences
          setSelectedCuisines(preferences.cuisine_preferences || []);
          setSelectedFoodTypes(preferences.food_type ? [preferences.food_type] : []);
          setPriceRange([100, preferences.daily_budget || 1000]);
        }
      }
      setAuthLoading(false);
    };

    checkSession();

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(async (event, session) => {
      setUser(session?.user || null);
      if (!session) {
        setUserPreferences(null);
        setSelectedCuisines([]);
        setSelectedFoodTypes([]);
        setPriceRange([100, 1000]);
      }
    });

    return () => subscription.unsubscribe();
  }, []);

  const handleLogin = (userData, preferences) => {
    setUser(userData);
    setUserPreferences(preferences);
    if (preferences) {
      setSelectedCuisines(preferences.cuisine_preferences || []);
      setSelectedFoodTypes(preferences.food_type ? [preferences.food_type] : []);
      setPriceRange([100, preferences.daily_budget || 1000]);
    }
  };

  const handleLogout = async () => {
    await supabase.auth.signOut();
    setUser(null);
    setUserPreferences(null);
    setSelectedCuisines([]);
    setSelectedFoodTypes([]);
    setPriceRange([100, 1000]);
    setRecommendations(null);
  };

  const handleCheckboxChange = (value, type) => {
    const updater = (prev) => prev.includes(value) ? prev.filter(item => item !== value) : [...prev, value];
    if (type === 'cuisine') setSelectedCuisines(updater);
    else setSelectedFoodTypes(updater);
  };

  const makeRecommendationRequest = async (cuisines, foodTypes, budgetRange, userArea) => {
    setIsLoading(true);
    setError('');
    setRecommendations(null);

    try {
      const API_URL = config.api.baseUrl;
      
      // Use provided userArea or auto-detect from location
      let finalUserArea = userArea;
      if (!finalUserArea && userLocation) {
        finalUserArea = getUserArea(userLocation.latitude, userLocation.longitude);
        console.log('Auto-detected area from coordinates:', finalUserArea);
      }
      
      const requestData = {
        cuisines,
        foodTypes,
        minPrice: budgetRange ? budgetRange[0] : priceRange[0],
        maxPrice: budgetRange ? budgetRange[1] : priceRange[1],
        userArea: finalUserArea,
        userLocation: userLocation,
        userId: user?.id,
        userPreferences: userPreferences
      };

      console.log('=== FRONTEND API REQUEST ===');
      console.log('Final userArea being sent:', finalUserArea);
      console.log('Complete request data:', requestData);
      
      const response = await fetch(`${API_URL}/api/recommend`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestData)
      });

      if (!response.ok) {
        throw new Error(`Network response was not ok. Status: ${response.status}`);
      }

      const data = await response.json();
      console.log('Received response:', data);
      
      // Handle the new response format
      if (data.recommendations) {
        setRecommendations(data.recommendations);
        
        // Log preference information
        if (data.preference_source) {
          console.log(`Recommendations based on ${data.preference_source} preferences:`, data.applied_preferences);
        }
      } else {
        // Handle legacy format for backward compatibility
        setRecommendations(data);
      }

    } catch (err) {
      setError('Failed to fetch recommendations. Please check the Vercel logs.');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSuggestClick = async () => {
    // Determine user's area if location is available or use manually selected area
    let userArea = selectedArea;
    if (!userArea && userLocation) {
      userArea = getUserArea(userLocation.latitude, userLocation.longitude);
    }
    
    await makeRecommendationRequest(selectedCuisines, selectedFoodTypes, priceRange, userArea);
  };

  // Handler for ModernUI component
  const handleModernUIRecommendations = async (params) => {
    const { searchQuery, cuisines, budgetRange, selectedArea: area, userBudget } = params;
    
    console.log('handleModernUIRecommendations called with:', {
      area,
      cuisines,
      budgetRange,
      userBudget
    });
    
    // Update state with modern UI selections
    setSelectedCuisines(cuisines);
    setSelectedArea(area);
    if (budgetRange) {
      setPriceRange([budgetRange[0], budgetRange[1]]);
    }
    
    // Call the suggestion logic with current values (not state that might be stale)
    // Use food type from user preferences as fallback if not explicitly set
    const effectiveFoodTypes = selectedFoodTypes.length > 0 ? selectedFoodTypes : 
                               (userPreferences?.food_type ? [userPreferences.food_type] : ['Veg']);
    
    console.log('Using effective food types:', effectiveFoodTypes);
    await makeRecommendationRequest(cuisines, effectiveFoodTypes, budgetRange, area);
  };

  if (authLoading) {
    return <div className="loading">Loading...</div>;
  }

  if (!user) {
    return <LoginPage onLogin={handleLogin} />;
  }

  // Render Modern UI
  if (useModernUI) {
    return (
      <div className="modern-layout">
        {/* Toggle Button */}
        <div style={{position: 'absolute', top: '20px', right: '20px', zIndex: 1000}}>
          <button 
            onClick={() => setUseModernUI(false)}
            style={{
              background: 'rgba(255,255,255,0.2)',
              color: 'white',
              border: '1px solid rgba(255,255,255,0.3)',
              padding: '8px 16px',
              borderRadius: '20px',
              cursor: 'pointer',
              backdropFilter: 'blur(10px)'
            }}
          >
            Switch to Classic UI
          </button>
          <button 
            onClick={handleLogout}
            style={{
              background: 'rgba(255,255,255,0.2)',
              color: 'white',
              border: '1px solid rgba(255,255,255,0.3)',
              padding: '8px 16px',
              borderRadius: '20px',
              cursor: 'pointer',
              backdropFilter: 'blur(10px)',
              marginLeft: '10px'
            }}
          >
            Logout
          </button>
        </div>
        
        <div className="main-content">
          {/* Left Panel - User Input */}
          <div className="left-panel">
            <ModernUI 
              userPreferences={userPreferences}
              onGetRecommendations={handleModernUIRecommendations}
              isLoading={isLoading}
              user={user}
              selectedArea={selectedArea}
              selectedCuisines={selectedCuisines}
              selectedFoodTypes={selectedFoodTypes}
              priceRange={priceRange}
            />
          </div>
          
          {/* Right Panel - Recommendations */}
          <div className="right-panel">
            {recommendations ? (
              <div className="recommendations-container">
                <div className="recommendations-header">
                  <h2>🍽️ Recommendations for You</h2>
                  <p>Based on your preferences • {recommendations.length} suggestions</p>
                </div>
                <div className="recommendations-list">
                  {recommendations.map((item, index) => (
                    <div key={index} className="recommendation-card">
                      <div className="card-header">
                        <h3>{item.Item_Name || item.name}</h3>
                        <div className="price-badge">₹{item.Price || item.price}</div>
                      </div>
                      <div className="restaurant-info">
                        <span className="restaurant-name">{item.Restaurant_Name || item.restaurant}</span>
                        <span className="area-info">📍 {item.Area || item.area}</span>
                      </div>
                      <div className="card-footer">
                        {(item.Dining_Rating || item.rating) && (
                          <div className="rating-info">
                            <span className="rating">⭐ {item.Dining_Rating || item.rating}</span>
                            {item.Votes && (
                              <span className="votes">({item.Votes} votes)</span>
                            )}
                          </div>
                        )}
                        <div className="cuisine-tag">
                          {item.Cuisine || item.cuisine} • {item['Food Type'] || item.food_type}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="no-recommendations">
                <div className="placeholder-content">
                  <div className="placeholder-icon">🍽️</div>
                  <h3>Select Your Preferences</h3>
                  <p>Choose your favorite cuisines, budget range, or area to get personalized food recommendations.</p>
                  <div className="placeholder-features">
                    <div className="feature-item">
                      <span className="feature-icon">🍛</span>
                      <span>Multiple Cuisines</span>
                    </div>
                    <div className="feature-item">
                      <span className="feature-icon">💰</span>
                      <span>Budget Friendly</span>
                    </div>
                    <div className="feature-item">
                      <span className="feature-icon">📍</span>
                      <span>Location Based</span>
                    </div>
                  </div>
                </div>
              </div>
            )}
            
            {error && (
              <div className="error-container">
                <div className="error-message">
                  <span className="error-icon">⚠️</span>
                  {error}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  // Render Classic UI
  return (
    <div className="container">
      {/* Toggle Button */}
      <div style={{position: 'absolute', top: '20px', right: '20px'}}>
        <button 
          onClick={() => setUseModernUI(true)}
          style={{
            background: '#d32f2f',
            color: 'white',
            border: 'none',
            padding: '8px 16px',
            borderRadius: '6px',
            cursor: 'pointer'
          }}
        >
          Switch to Modern UI
        </button>
      </div>
      
      <header>
        <div className="header-content">
          <div>
            <h1>Kya Khaega?</h1>
            <p>Let us help you decide what to eat in Pune!</p>
            {userLocation && (
              <p className="location-status">
                📍 Recommendations based on your location
                {getUserArea(userLocation.latitude, userLocation.longitude) && 
                  ` (${getUserArea(userLocation.latitude, userLocation.longitude)})`
                }
              </p>
            )}
            {locationError && (
              <p className="location-error">⚠️ {locationError}</p>
            )}
          </div>
          <div className="user-info">
            <span>Welcome, {userPreferences?.name || user.email}!</span>
            <button onClick={handleLogout} className="logout-btn">Logout</button>
          </div>
        </div>
      </header>
      <div className="selection-panel">
        {/* Area Selection */}
        <fieldset>
          <legend>Delivery Area</legend>
          {!userLocation && !selectedArea && (
            <p className="location-prompt">📍 Allow location access for automatic area detection, or select manually below:</p>
          )}
          {/* Debug info - remove in production */}
          {userLocation && (
            <div className="debug-info">
              <small>📍 Coords: {userLocation.latitude.toFixed(4)}, {userLocation.longitude.toFixed(4)}</small>
              <button 
                onClick={() => {
                  const area = getUserArea(userLocation.latitude, userLocation.longitude);
                  alert(`Detected area: ${area || 'None detected'}\nCoords: ${userLocation.latitude}, ${userLocation.longitude}`);
                }}
                className="debug-btn"
              >
                Test Area Detection
              </button>
            </div>
          )}
          <select 
            value={selectedArea} 
            onChange={(e) => setSelectedArea(e.target.value)}
            className="area-selector"
          >
            <option value="">
              {userLocation 
                ? (getUserArea(userLocation.latitude, userLocation.longitude) 
                    ? `Auto-detected: ${getUserArea(userLocation.latitude, userLocation.longitude)}` 
                    : 'Location detected - Select area manually')
                : 'Select your area'
              }
            </option>
            {availableAreas.map(area => (
              <option key={area} value={area}>{area}</option>
            ))}
          </select>
        </fieldset>

        <fieldset><legend>Select Cuisine(s)</legend>{CUISINE_OPTIONS.map(c => (<label key={c}><input type="checkbox" value={c} onChange={()=>handleCheckboxChange(c, 'cuisine')}/>{c}</label>))}</fieldset>
        <fieldset><legend>Select Food Type(s)</legend>{FOOD_TYPE_OPTIONS.map(ft => (<label key={ft}><input type="checkbox" value={ft} onChange={()=>handleCheckboxChange(ft, 'foodType')}/>{ft}</label>))}</fieldset>
        <fieldset><legend>Price Range</legend><div className="price-slider-container"><div className="price-display">₹{priceRange[0]} - ₹{priceRange[1]}</div>
        <Slider 
            range 
            min={0} 
            max={2000} 
            // FIX: Use 'value' instead of 'defaultValue' for a fully controlled component.
            value={priceRange} 
            onChange={(newRange) => setPriceRange(newRange)} 
            allowCross={false} 
            step={50}
        />
        </div></fieldset>
      </div>
      <button onClick={handleSuggestClick} disabled={isLoading}>{isLoading ? 'Thinking...':'Find Me Food!'}</button>
      <div className="results-panel">
        {error && <p className="error-message">{error}</p>}
        {recommendations && recommendations.length > 0 && (
          <div>
            {(selectedArea || (userLocation && getUserArea(userLocation.latitude, userLocation.longitude))) && (
              <p className="location-info">
                📍 Showing results for: {selectedArea || getUserArea(userLocation.latitude, userLocation.longitude)}
              </p>
            )}
            <ul>
              {recommendations.map((item, index) => {
                const currentUserArea = selectedArea || (userLocation ? getUserArea(userLocation.latitude, userLocation.longitude) : null);
                const isExactArea = currentUserArea && item.Area && item.Area.toLowerCase() === currentUserArea.toLowerCase();
                const isNearbyArea = currentUserArea && item.Area && item.Area.toLowerCase().includes(currentUserArea.toLowerCase());
                
                return (
                  <li key={index} className={isExactArea ? 'exact-area' : (isNearbyArea ? 'nearby-area' : 'distant-area')}>
                    <span className="item-name">{item.Item_Name}</span>
                    <span className="restaurant-name">at {item.Restaurant_Name}</span>
                    {item.Area && (
                      <span className={`restaurant-area ${isExactArea ? 'exact' : (isNearbyArea ? 'nearby' : 'distant')}`}>
                        📍 {item.Area}
                        {isExactArea && <span className="distance-badge exact">In your area</span>}
                        {!isExactArea && isNearbyArea && <span className="distance-badge nearby">Nearby</span>}
                        {!isExactArea && !isNearbyArea && <span className="distance-badge distant">Distant</span>}
                      </span>
                    )}
                    {item.Price && <span className="price-tag">₹{Math.round(item.Price)}</span>}
                    {item.Dining_Rating && (
                      <span className="rating-tag">
                        ⭐ {item.Dining_Rating}
                        {item.Votes && <span className="votes">({item.Votes} votes)</span>}
                      </span>
                    )}
                    <span className="tags">{item['Food Type']} | {item.Cuisine}</span>
                  </li>
                );
              })}
            </ul>
          </div>
        )}
        {recommendations && recommendations.length === 0 && (<p className="no-results">No results found. Try different filters!</p>)}
      </div>
    </div>
  );
}
export default App;