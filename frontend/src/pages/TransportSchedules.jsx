import React, { useState, useEffect } from 'react'
import { Bus, Clock, MapPin, Building2, RefreshCw, Search, Filter, ChevronDown, ChevronUp } from 'lucide-react'
import './TransportSchedules.css'

const API_BASE = 'http://127.0.0.1:8000'

function TransportSchedules() {
  const [schedules, setSchedules] = useState([])
  const [operators, setOperators] = useState([])
  const [transportOptions, setTransportOptions] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedOperator, setSelectedOperator] = useState('all')
  const [expandedRoutes, setExpandedRoutes] = useState({})

  useEffect(() => {
    fetchSchedules()
  }, [])

  const fetchSchedules = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch(`${API_BASE}/api/transport/schedules`)
      if (!response.ok) throw new Error('Failed to fetch schedules')
      const data = await response.json()
      setSchedules(data.schedules || [])
      setOperators(data.operators || [])
      setTransportOptions(data.transport_options || [])
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const toggleRoute = (routeId) => {
    setExpandedRoutes(prev => ({
      ...prev,
      [routeId]: !prev[routeId]
    }))
  }

  const filteredSchedules = schedules.filter(schedule => {
    const matchesSearch = schedule.operator.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         schedule.route_code.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesOperator = selectedOperator === 'all' || schedule.operator === selectedOperator
    return matchesSearch && matchesOperator
  })

  const getOperatorColor = (operator) => {
    const colors = {
      'Daewoo Express': '#e74c3c',
      'Faisal Movers': '#3498db',
      'Skyways': '#9b59b6',
      'NATCO': '#27ae60',
      'Swat Coaches': '#f39c12',
      'New Khan Road Runners': '#1abc9c',
    }
    return colors[operator] || '#6c757d'
  }

  const getOperatorLogo = (operator) => {
    if (operator.includes('Daewoo')) return '🚌'
    if (operator.includes('Faisal')) return '🚐'
    if (operator.includes('NATCO')) return '🏔️'
    if (operator.includes('Swat')) return '⛰️'
    if (operator.includes('Skyways')) return '✈️'
    if (operator.includes('Wagon')) return '🚐'
    return '🚌'
  }

  if (loading) {
    return (
      <div className="transport-schedules-page">
        <div className="loading-container">
          <RefreshCw className="spin" size={48} />
          <p>Loading transport schedules...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="transport-schedules-page">
        <div className="error-container">
          <p>Error: {error}</p>
          <button onClick={fetchSchedules}>Try Again</button>
        </div>
      </div>
    )
  }

  return (
    <div className="transport-schedules-page">
      {/* Header */}
      <div className="schedules-header">
        <div className="header-content">
          <h1>🚌 Transport Schedules</h1>
          <p>Find bus timings, operators, and routes across Pakistan</p>
        </div>
        
        {/* Stats */}
        <div className="stats-bar">
          <div className="stat">
            <Bus size={20} />
            <span>{schedules.length} Routes</span>
          </div>
          <div className="stat">
            <Building2 size={20} />
            <span>{operators.length} Operators</span>
          </div>
          <div className="stat">
            <Clock size={20} />
            <span>{schedules.reduce((acc, s) => acc + (s.departure_times?.length || 0), 0)} Daily Departures</span>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="filters-section">
        <div className="search-box">
          <Search size={20} />
          <input
            type="text"
            placeholder="Search operators or routes..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        
        <div className="filter-box">
          <Filter size={20} />
          <select 
            value={selectedOperator} 
            onChange={(e) => setSelectedOperator(e.target.value)}
          >
            <option value="all">All Operators</option>
            {operators.map(op => (
              <option key={op} value={op}>{op}</option>
            ))}
          </select>
        </div>
        
        <button className="refresh-btn" onClick={fetchSchedules}>
          <RefreshCw size={18} />
          Refresh
        </button>
      </div>

      {/* Schedules Grid */}
      <div className="schedules-container">
        {filteredSchedules.length === 0 ? (
          <div className="no-results">
            <p>No schedules found matching your criteria</p>
          </div>
        ) : (
          <div className="schedules-grid">
            {filteredSchedules.map(schedule => (
              <div 
                key={schedule.id} 
                className="schedule-card"
                style={{ borderLeftColor: getOperatorColor(schedule.operator) }}
              >
                <div className="card-header" onClick={() => toggleRoute(schedule.id)}>
                  <div className="operator-info">
                    <span className="operator-logo">{getOperatorLogo(schedule.operator)}</span>
                    <div>
                      <h3>{schedule.operator}</h3>
                      <span className="route-code">{schedule.route_code}</span>
                    </div>
                  </div>
                  <div className="expand-icon">
                    {expandedRoutes[schedule.id] ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
                  </div>
                </div>
                
                <div className="card-body">
                  <div className="frequency">
                    <Clock size={16} />
                    <span>{schedule.frequency}</span>
                  </div>
                  
                  <div className="departures-preview">
                    {schedule.departure_times?.slice(0, 4).map((time, idx) => (
                      <span key={idx} className="time-badge">{time}</span>
                    ))}
                    {schedule.departure_times?.length > 4 && (
                      <span className="more-times">+{schedule.departure_times.length - 4} more</span>
                    )}
                  </div>
                </div>
                
                {expandedRoutes[schedule.id] && (
                  <div className="card-expanded">
                    <h4>All Departure Times</h4>
                    <div className="all-times">
                      {schedule.departure_times?.map((time, idx) => (
                        <span key={idx} className="time-badge-full">{time}</span>
                      ))}
                    </div>
                    {schedule.last_verified && (
                      <p className="last-verified">
                        Last verified: {new Date(schedule.last_verified).toLocaleDateString()}
                      </p>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Transport Options Section */}
      {transportOptions.length > 0 && (
        <div className="transport-options-section">
          <h2>🚗 Available Transport Options</h2>
          <div className="options-grid">
            {transportOptions.slice(0, 8).map(opt => (
              <div key={opt.id} className="option-card">
                <div className="option-header">
                  <span className="mode-icon">
                    {opt.mode === 'bus' ? '🚌' : opt.mode === 'train' ? '🚂' : '🚐'}
                  </span>
                  <span className="mode-name">{opt.mode}</span>
                </div>
                <div className="option-route">
                  <MapPin size={14} />
                  <span>{opt.origin} → {opt.destination}</span>
                </div>
                <div className="option-details">
                  <span className="fare">PKR {opt.fare_pkr?.toLocaleString()}</span>
                  <span className="time">{opt.time_hours}h</span>
                </div>
                {opt.safety_notes && (
                  <p className="safety-note">{opt.safety_notes}</p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Info Banner */}
      <div className="info-banner">
        <div className="banner-content">
          <h3>📞 Booking Information</h3>
          <p>For reservations, contact operators directly or visit their booking offices at major bus terminals.</p>
          <div className="booking-tips">
            <span>💡 Book 1-2 days in advance for popular routes</span>
            <span>💡 Daewoo & Faisal Movers offer online booking</span>
            <span>💡 NATCO tickets available at Pir Wadhai terminal</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default TransportSchedules
