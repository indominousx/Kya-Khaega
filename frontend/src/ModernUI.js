import React, { useState, useEffect } from 'react';
import './ModernUI.css';

// Cuisine options with icons
const CUISINE_OPTIONS = [
  { name: 'Indian (General)', icon: '🍛', color: '#FF6B35' },
  { name: 'North Indian', icon: '🥘', color: '#F7931E' },
  { name: 'South Indian', icon: '🌶️', color: '#00B9A8' },
  { name: 'Chinese', icon: '🥢', color: '#E91E63' },
  { name: 'Italian', icon: '🍝', color: '#FF5722' },
  { name: 'Continental', icon: '🍽️', color: '#2196F3' },
  { name: 'Maharashtrian', icon: '🌾', color: '#FF9800' },
  { name: 'Mughlai', icon: '👑', color: '#9C27B0' },
  { name: 'Beverages', icon: '🥤', color: '#00BCD4' },
  { name: 'Desserts', icon: '🍰', color: '#E91E63' },
  { name: 'Other', icon: '🍴', color: '#607D8B' }
];

// Popular areas in Pune
const POPULAR_AREAS = [
  'FC Road', 'Koregaon Park', 'Baner', 'Kothrud', 'Camp', 
  'Hinjawadi', 'Aundh', 'Viman Nagar'
];

const ModernUI = ({ 
  userPreferences, 
  onGetRecommendations, 
  onAISearch,
  isLoading, 
  user, 
  selectedArea: propSelectedArea, 
  selectedCuisines: propSelectedCuisines,
  selectedFoodTypes: propSelectedFoodTypes,
  priceRange: propPriceRange
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [budgetRange, setBudgetRange] = useState([0, 1000]);
  const [userBudget, setUserBudget] = useState(null);
  const [selectedBudgetRange, setSelectedBudgetRange] = useState('');
  const [isAISearch, setIsAISearch] = useState(false);
  
  // Use props instead of local state for controlled components
  const selectedArea = propSelectedArea || '';
  const selectedCuisines = propSelectedCuisines || [];
  const selectedFoodTypes = propSelectedFoodTypes || [];

  // Load user's daily budget from preferences
  useEffect(() => {
    if (userPreferences && userPreferences.daily_budget) {
      const dailyBudget = parseFloat(userPreferences.daily_budget);
      setUserBudget(dailyBudget);
      setBudgetRange([0, dailyBudget]);
      // Auto-select appropriate budget range
      if (dailyBudget <= 200) {
        setSelectedBudgetRange(`₹0-₹${dailyBudget}`);
      } else if (dailyBudget <= 500) {
        setSelectedBudgetRange(`₹200-₹${dailyBudget}`);
      } else {
        setSelectedBudgetRange(`₹500-₹${dailyBudget}`);
      }
    }
  }, [userPreferences]);

  // Note: Cuisine preferences are now handled by parent component

  const handleCuisineToggle = (cuisineName) => {
    const newSelectedCuisines = selectedCuisines.includes(cuisineName) 
      ? selectedCuisines.filter(c => c !== cuisineName)
      : [...selectedCuisines, cuisineName];
    
    console.log('Cuisine toggled:', cuisineName, 'New cuisines:', newSelectedCuisines);
    console.log('Current selected area:', selectedArea);
    
    // Immediately trigger recommendations when cuisine is selected/deselected
    if (onGetRecommendations) {
      onGetRecommendations({
        searchQuery,
        cuisines: newSelectedCuisines,
        budgetRange,
        selectedArea,
        userBudget,
        selectedBudgetRange
      });
    }
  };

  const handleAreaClick = (area) => {
    const newSelectedArea = selectedArea === area ? '' : area;
    
    console.log('Area clicked:', area, 'New selected area:', newSelectedArea);
    
    // Immediately trigger recommendations when area is selected/deselected
    if (onGetRecommendations) {
      onGetRecommendations({
        searchQuery,
        cuisines: selectedCuisines,
        budgetRange,
        selectedArea: newSelectedArea,
        userBudget,
        selectedBudgetRange
      });
    }
  };

  const handleBudgetRangeClick = (range) => {
    const newSelectedRange = selectedBudgetRange === range ? '' : range;
    setSelectedBudgetRange(newSelectedRange);
    
    let newBudgetRange = budgetRange;
    
    // Parse budget range and update budgetRange state
    if (range.includes('Under')) {
      const max = parseInt(range.match(/₹(\d+)/)[1]);
      newBudgetRange = [0, max];
      setBudgetRange(newBudgetRange);
    } else if (range.includes('-')) {
      const matches = range.match(/₹(\d+)-₹(\d+)/);
      if (matches) {
        newBudgetRange = [parseInt(matches[1]), parseInt(matches[2])];
        setBudgetRange(newBudgetRange);
      }
    } else if (range.includes('Above')) {
      const min = parseInt(range.match(/₹(\d+)/)[1]);
      newBudgetRange = [min, userBudget || 1000];
      setBudgetRange(newBudgetRange);
    }
    
    // Immediately trigger recommendations when budget is selected/deselected
    if (onGetRecommendations) {
      onGetRecommendations({
        searchQuery,
        cuisines: selectedCuisines,
        budgetRange: newBudgetRange,
        selectedArea,
        userBudget,
        selectedBudgetRange: newSelectedRange
      });
    }
  };

  const handleAISearch = () => {
    if (!searchQuery.trim()) {
      return;
    }

    setIsAISearch(true);
    console.log('AI Search triggered with query:', searchQuery);
    console.log('Current selected area:', selectedArea);

    if (onAISearch) {
      onAISearch({
        query: searchQuery.trim(),
        userArea: selectedArea,
        userPreferences
      });
    }
  };



  return (
    <div className="modern-container">
      {/* Header */}
      <div className="modern-header">
        <div className="app-icon">
          🍴
        </div>
        <h1 className="app-title">Kya Khaega</h1>
        <p className="app-subtitle">
          Your personal dining decision-maker. Find the perfect dish, not just a restaurant.
        </p>
      </div>

      {/* AI-Powered Search Bar */}
      <div className="search-section">
        <div className="search-container">
          <div className="ai-search-wrapper">
            <div className="search-input-container">
              <input
                type="text"
                placeholder="Tell me what you're craving... (e.g., 'I want something spicy for dinner', 'healthy lunch options', 'romantic dinner in Koregaon Park')"
                className="search-input ai-search-input"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter' && searchQuery.trim()) {
                    handleAISearch();
                  }
                }}
              />
              <div className="search-buttons">
                <button 
                  className="ai-search-btn"
                  onClick={handleAISearch}
                  disabled={isLoading || !searchQuery.trim()}
                >
                  {isLoading ? '🤖 Thinking...' : '🤖 AI Search'}
                </button>
              </div>
            </div>
            <div className="ai-search-info">
              <div className="ai-badge">
                <span className="ai-icon">✨</span>
                <span>AI-Powered</span>
              </div>
              <p className="ai-description">
                Describe what you want in natural language and I'll find the perfect match!
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Explore Cuisines */}
      <div className="section">
        <h2 className="section-title">Explore Cuisines</h2>
        <div className="cuisine-grid">
          {CUISINE_OPTIONS.map((cuisine) => (
            <div
              key={cuisine.name}
              className={`cuisine-card ${selectedCuisines.includes(cuisine.name) ? 'selected' : ''}`}
              onClick={() => handleCuisineToggle(cuisine.name)}
              style={{ '--cuisine-color': cuisine.color }}
            >
              <div className="cuisine-icon">{cuisine.icon}</div>
              <div className="cuisine-name">{cuisine.name}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Budget Section */}
      <div className="section">
        <h2 className="section-title">Budget</h2>
        <div className="budget-container">
          <div className="budget-display">
            <span className="currency-symbol">₹</span>
            <span className="budget-text">Your Budget Range</span>
          </div>
          <div className="budget-range">
            {[
              `Under ₹200`,
              `₹200-₹400`,
              `₹400-₹600`,
              `Above ₹600`
            ].map((range) => (
              <span
                key={range}
                className={`budget-value ${selectedBudgetRange === range ? 'selected' : ''}`}
                onClick={() => handleBudgetRangeClick(range)}
              >
                {range}
              </span>
            ))}
          </div>
          {userBudget && (
            <div className="user-budget-info">
              <span>💰 Your daily budget: ₹{userBudget}</span>
            </div>
          )}
        </div>
      </div>

      {/* Popular Areas */}
      <div className="section">
        <h2 className="section-title">Popular Areas</h2>
        <div className="areas-grid">
          {POPULAR_AREAS.map((area) => (
            <div
              key={area}
              className={`area-chip ${selectedArea === area ? 'selected' : ''}`}
              onClick={() => handleAreaClick(area)}
            >
              📍 {area}
            </div>
          ))}
        </div>
      </div>

      {/* Interactive Instructions */}
      <div className="interactive-info">
        <div className="info-card">
          <div className="info-icon">✨</div>
          <div className="info-content">
            <h3>Interactive Recommendations</h3>
            <p>Click on any cuisine, area, or budget range to instantly see personalized recommendations!</p>
          </div>
        </div>
        {isLoading && (
          <div className="loading-indicator">
            <div className="spinner"></div>
            <span>Finding perfect matches...</span>
          </div>
        )}
      </div>

      {/* User Info */}
      {user && (
        <div className="user-section">
          <div className="user-avatar">
            {user.email?.charAt(0).toUpperCase() || '👤'}
          </div>
          <div className="user-details">
            <span className="user-name">{userPreferences?.name || user.email}</span>
            <span className="user-preferences">
              {userPreferences ? 'Preferences loaded' : 'Default preferences'}
            </span>
          </div>
        </div>
      )}
    </div>
  );
};

export default ModernUI;