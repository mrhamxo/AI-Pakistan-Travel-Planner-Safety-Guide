import React, { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { MapPin, Shield, DollarSign, Clock, AlertTriangle, ArrowRight, Compass, Map, TrendingUp, Calendar, Users, Sparkles } from 'lucide-react'
import { travelAPI } from '../services/api'
import './Home.css'

const POPULAR_DESTINATIONS = [
  { name: 'Hunza', emoji: '⛰️', days: '5-7', highlight: 'Attabad Lake' },
  { name: 'Swat', emoji: '🌲', days: '3-5', highlight: 'Kalam Valley' },
  { name: 'Skardu', emoji: '🏔️', days: '6-8', highlight: 'Shangrila' },
  { name: 'Naran', emoji: '🌊', days: '3-4', highlight: 'Saif ul Malook' },
  { name: 'Murree', emoji: '🌨️', days: '2-3', highlight: 'Mall Road' },
  { name: 'Chitral', emoji: '🏕️', days: '5-6', highlight: 'Kalash Valley' },
]

const POPULAR_ROUTES = [
  { origin: 'Islamabad', destination: 'Lahore', emoji: '🚗' },
  { origin: 'Islamabad', destination: 'Murree', emoji: '🏔️' },
  { origin: 'Lahore', destination: 'Karachi', emoji: '✈️' },
  { origin: 'Islamabad', destination: 'Swat', emoji: '🌲' },
  { origin: 'Islamabad', destination: 'Hunza', emoji: '⛰️' },
  { origin: 'Karachi', destination: 'Multan', emoji: '🚌' },
]

function Home() {
  const [origin, setOrigin] = useState('')
  const [destination, setDestination] = useState('')
  const [alertCount, setAlertCount] = useState(0)
  const [recentQueries, setRecentQueries] = useState([])
  const navigate = useNavigate()

  useEffect(() => {
    loadStats()
  }, [])

  const loadStats = async () => {
    try {
      // Load active alerts count
      const alerts = await travelAPI.getSafetyAlerts()
      setAlertCount(alerts.length)

      // Load recent queries
      const response = await fetch('http://localhost:8000/api/queries/history?limit=5')
      if (response.ok) {
        const queries = await response.json()
        setRecentQueries(queries)
      }
    } catch (error) {
      console.error('Error loading stats:', error)
    }
  }

  const handleQuickQuery = () => {
    if (origin && destination) {
      navigate(`/planner?origin=${encodeURIComponent(origin)}&destination=${encodeURIComponent(destination)}`)
    }
  }

  const handlePopularRoute = (route) => {
    navigate(`/planner?origin=${encodeURIComponent(route.origin)}&destination=${encodeURIComponent(route.destination)}`)
  }

  return (
    <div className="home">
      <div className="hero">
        <div className="hero-badge">🇵🇰 Pakistan's First AI Travel Agency</div>
        <h1 className="hero-title">Plan Your Dream Trip</h1>
        <p className="hero-subtitle">
          Complete trip planning with AI-powered itineraries, cost optimization, and safety guidance for Pakistan's most beautiful destinations
        </p>
        <Link to="/trip-wizard" className="hero-cta">
          <Sparkles size={20} /> Start Planning Your Trip <ArrowRight size={18} />
        </Link>
      </div>

      {/* Featured Destinations */}
      <div className="destinations-section">
        <h2>🏔️ Popular Destinations</h2>
        <div className="destinations-grid">
          {POPULAR_DESTINATIONS.map((dest, idx) => (
            <Link 
              key={idx} 
              to={`/trip-wizard?destination=${dest.name}`}
              className="destination-card"
            >
              <span className="dest-emoji">{dest.emoji}</span>
              <div className="dest-info">
                <h3>{dest.name}</h3>
                <span className="dest-highlight">{dest.highlight}</span>
                <span className="dest-days"><Calendar size={12} /> {dest.days} days</span>
              </div>
            </Link>
          ))}
        </div>
      </div>

      <div className="quick-search">
        <h2><Compass size={24} /> Quick Route Check</h2>
        <div className="search-form">
          <div className="input-group">
            <MapPin className="input-icon" />
            <input
              type="text"
              placeholder="From (e.g., Islamabad)"
              value={origin}
              onChange={(e) => setOrigin(e.target.value)}
              className="search-input"
              list="cities-from"
            />
            <datalist id="cities-from">
              <option value="Islamabad" />
              <option value="Lahore" />
              <option value="Karachi" />
              <option value="Peshawar" />
              <option value="Quetta" />
              <option value="Multan" />
              <option value="Faisalabad" />
              <option value="Rawalpindi" />
            </datalist>
          </div>
          <div className="input-group">
            <MapPin className="input-icon destination" />
            <input
              type="text"
              placeholder="To (e.g., Lahore)"
              value={destination}
              onChange={(e) => setDestination(e.target.value)}
              className="search-input"
              list="cities-to"
            />
            <datalist id="cities-to">
              <option value="Lahore" />
              <option value="Murree" />
              <option value="Swat" />
              <option value="Hunza" />
              <option value="Skardu" />
              <option value="Gilgit" />
              <option value="Chitral" />
              <option value="Karachi" />
            </datalist>
          </div>
          <button 
            onClick={handleQuickQuery} 
            className="search-button"
            disabled={!origin || !destination}
          >
            Plan My Trip <ArrowRight size={18} />
          </button>
        </div>

        <div className="popular-routes">
          <span className="popular-label">Popular routes:</span>
          <div className="route-chips">
            {POPULAR_ROUTES.map((route, idx) => (
              <button 
                key={idx} 
                className="route-chip"
                onClick={() => handlePopularRoute(route)}
              >
                {route.emoji} {route.origin} → {route.destination}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="stats-row">
        <Link to="/map" className="stat-card alerts">
          <AlertTriangle size={28} />
          <div className="stat-content">
            <span className="stat-number">{alertCount}</span>
            <span className="stat-label">Active Alerts</span>
          </div>
          <ArrowRight size={18} className="stat-arrow" />
        </Link>
        <div className="stat-card routes">
          <Map size={28} />
          <div className="stat-content">
            <span className="stat-number">50+</span>
            <span className="stat-label">Covered Routes</span>
          </div>
        </div>
        <div className="stat-card cities">
          <MapPin size={28} />
          <div className="stat-content">
            <span className="stat-number">20+</span>
            <span className="stat-label">Cities</span>
          </div>
        </div>
        <div className="stat-card queries">
          <TrendingUp size={28} />
          <div className="stat-content">
            <span className="stat-number">{recentQueries.length > 0 ? '24/7' : 'Live'}</span>
            <span className="stat-label">AI Support</span>
          </div>
        </div>
      </div>

      <div className="features">
        <div className="feature-card">
          <div className="feature-icon-wrapper">
            <Shield size={32} />
          </div>
          <h3>Safe Route Intelligence</h3>
          <p>AI evaluates routes based on weather, time of day, and historical safety patterns</p>
        </div>
        <div className="feature-card">
          <div className="feature-icon-wrapper">
            <DollarSign size={32} />
          </div>
          <h3>Cost Optimization</h3>
          <p>Compare transport options and get accurate fare estimates for buses, trains, and more</p>
        </div>
        <div className="feature-card">
          <div className="feature-icon-wrapper">
            <Clock size={32} />
          </div>
          <h3>Real-Time Alerts</h3>
          <p>Get instant notifications about floods, landslides, protests, and road closures</p>
        </div>
        <div className="feature-card">
          <div className="feature-icon-wrapper">
            <MapPin size={32} />
          </div>
          <h3>Northern Areas Support</h3>
          <p>Specialized guidance for Gilgit-Baltistan, Swat, and other scenic destinations</p>
        </div>
      </div>

      {recentQueries.length > 0 && (
        <div className="recent-section">
          <h2>Recent Searches</h2>
          <div className="recent-queries">
            {recentQueries.map((q, idx) => (
              <div 
                key={idx} 
                className="recent-query"
                onClick={() => navigate(`/planner?origin=${encodeURIComponent(q.origin || '')}&destination=${encodeURIComponent(q.destination || '')}`)}
              >
                <div className="query-route">
                  {q.origin && q.destination ? (
                    <><MapPin size={14} /> {q.origin} → {q.destination}</>
                  ) : (
                    <span className="query-text">{q.query_text.slice(0, 50)}...</span>
                  )}
                </div>
                <span className="query-time">
                  {q.created_at ? new Date(q.created_at).toLocaleDateString() : ''}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="risk-indicator">
        <h2>Safety Rating System</h2>
        <p>Our AI evaluates every route and provides clear safety recommendations</p>
        <div className="risk-levels">
          <div className="risk-level recommended">
            <span className="risk-dot"></span>
            <div className="risk-info">
              <strong>Recommended</strong>
              <span>Safe for all travelers</span>
            </div>
          </div>
          <div className="risk-level caution">
            <span className="risk-dot"></span>
            <div className="risk-info">
              <strong>Use Caution</strong>
              <span>Some precautions needed</span>
            </div>
          </div>
          <div className="risk-level avoid">
            <span className="risk-dot"></span>
            <div className="risk-info">
              <strong>Avoid</strong>
              <span>High risk - consider alternatives</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Home
