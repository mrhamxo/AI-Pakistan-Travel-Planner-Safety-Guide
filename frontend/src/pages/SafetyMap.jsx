import React, { useEffect, useState, useCallback } from 'react'
import { MapContainer, TileLayer, Marker, Popup, CircleMarker } from 'react-leaflet'
import { AlertTriangle, RefreshCw, MapPin, Clock } from 'lucide-react'
import { travelAPI } from '../services/api'
import './SafetyMap.css'

// Severity colors for markers
const SEVERITY_COLORS = {
  safe: '#2196f3',      // Blue for safe/no alerts
  low: '#4caf50',       // Green for low risk
  medium: '#ff9800',    // Orange for medium risk
  high: '#f44336',      // Red for high risk
  critical: '#9c27b0',  // Purple for critical
}

// All major Pakistan cities with coordinates for the safety map
const ALL_CITIES = {
  // Major Cities
  islamabad: { lat: 33.6844, lon: 73.0479, name: 'Islamabad', type: 'capital' },
  lahore: { lat: 31.5204, lon: 74.3587, name: 'Lahore', type: 'major' },
  karachi: { lat: 24.8607, lon: 67.0011, name: 'Karachi', type: 'major' },
  peshawar: { lat: 34.0151, lon: 71.5249, name: 'Peshawar', type: 'major' },
  quetta: { lat: 30.1798, lon: 66.9750, name: 'Quetta', type: 'major' },
  multan: { lat: 30.1575, lon: 71.5249, name: 'Multan', type: 'major' },
  faisalabad: { lat: 31.4504, lon: 73.1350, name: 'Faisalabad', type: 'major' },
  rawalpindi: { lat: 33.5651, lon: 73.0169, name: 'Rawalpindi', type: 'major' },
  
  // Tourist Destinations - Northern Areas
  hunza: { lat: 36.3167, lon: 74.6500, name: 'Hunza', type: 'tourist' },
  skardu: { lat: 35.2971, lon: 75.6333, name: 'Skardu', type: 'tourist' },
  gilgit: { lat: 35.9208, lon: 74.4584, name: 'Gilgit', type: 'tourist' },
  chitral: { lat: 35.8518, lon: 71.7864, name: 'Chitral', type: 'tourist' },
  swat: { lat: 35.2227, lon: 72.3459, name: 'Swat', type: 'tourist' },
  naran: { lat: 34.9039, lon: 73.6501, name: 'Naran', type: 'tourist' },
  kaghan: { lat: 34.8333, lon: 73.6167, name: 'Kaghan', type: 'tourist' },
  murree: { lat: 33.9070, lon: 73.3903, name: 'Murree', type: 'tourist' },
  kalam: { lat: 35.4833, lon: 72.5833, name: 'Kalam', type: 'tourist' },
  
  // Key Passes & Routes
  khunjerab: { lat: 36.85, lon: 75.42, name: 'Khunjerab Pass', type: 'pass' },
  babusar: { lat: 35.1500, lon: 74.0167, name: 'Babusar Pass', type: 'pass' },
  lowari: { lat: 35.3000, lon: 71.8000, name: 'Lowari Pass', type: 'pass' },
  
  // Other Important Cities
  abbottabad: { lat: 34.1463, lon: 73.2117, name: 'Abbottabad', type: 'city' },
  mansehra: { lat: 34.3300, lon: 73.2000, name: 'Mansehra', type: 'city' },
  chilas: { lat: 35.4167, lon: 74.1000, name: 'Chilas', type: 'city' },
  mingora: { lat: 34.7717, lon: 72.3600, name: 'Mingora', type: 'city' },
  dir: { lat: 35.2000, lon: 71.8833, name: 'Dir', type: 'city' },
  
  // Coastal
  gwadar: { lat: 25.1264, lon: 62.3225, name: 'Gwadar', type: 'coastal' },
}

// Default city coordinates for alerts without coordinates (legacy support)
const CITY_COORDS = ALL_CITIES

function SafetyMap() {
  const [alerts, setAlerts] = useState([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [lastUpdated, setLastUpdated] = useState(null)
  const [selectedCity, setSelectedCity] = useState(null)

  const loadAlerts = useCallback(async () => {
    try {
      const data = await travelAPI.getSafetyAlerts()
      setAlerts(data)
      setLastUpdated(new Date())
    } catch (error) {
      console.error('Error loading alerts:', error)
    } finally {
      setLoading(false)
    }
  }, [])

  const handleRefresh = async () => {
    setRefreshing(true)
    try {
      // Trigger backend to fetch new weather alerts
      await fetch('http://localhost:8000/api/alerts/refresh', { method: 'POST' })
      await loadAlerts()
    } catch (error) {
      console.error('Error refreshing alerts:', error)
    } finally {
      setRefreshing(false)
    }
  }

  useEffect(() => {
    loadAlerts()
    // Auto-refresh every 5 minutes
    const interval = setInterval(loadAlerts, 5 * 60 * 1000)
    return () => clearInterval(interval)
  }, [loadAlerts])

  // Get coordinates for an alert
  const getAlertCoords = (alert) => {
    if (alert.coordinates && alert.coordinates.lat && alert.coordinates.lon) {
      return [alert.coordinates.lat, alert.coordinates.lon]
    }
    // Try to find coordinates from city name
    const region = alert.region.toLowerCase()
    for (const [city, coords] of Object.entries(CITY_COORDS)) {
      if (region.includes(city)) {
        return [coords.lat, coords.lon]
      }
    }
    // Default to Islamabad if no match
    return [33.6844, 73.0479]
  }

  // Calculate risk level for each city based on alerts
  const getCityRiskData = useCallback(() => {
    const cityRisks = {}
    
    // Initialize all cities with safe status
    Object.entries(ALL_CITIES).forEach(([key, city]) => {
      cityRisks[key] = {
        ...city,
        riskLevel: 'safe',
        alerts: [],
        alertCount: 0
      }
    })
    
    // Assign alerts to cities
    alerts.forEach(alert => {
      const region = alert.region.toLowerCase()
      Object.entries(ALL_CITIES).forEach(([key, city]) => {
        if (region.includes(key) || region.includes(city.name.toLowerCase())) {
          cityRisks[key].alerts.push(alert)
          cityRisks[key].alertCount++
          // Update risk level to highest severity
          const severityOrder = { safe: 0, low: 1, medium: 2, high: 3, critical: 4 }
          if (severityOrder[alert.severity] > severityOrder[cityRisks[key].riskLevel]) {
            cityRisks[key].riskLevel = alert.severity
          }
        }
      })
    })
    
    return cityRisks
  }, [alerts])

  const cityRiskData = getCityRiskData()

  // Default center: Pakistan
  const center = [30.3753, 69.3451]

  // Count cities by risk level
  const cityCounts = {
    safe: Object.values(cityRiskData).filter(c => c.riskLevel === 'safe').length,
    low: Object.values(cityRiskData).filter(c => c.riskLevel === 'low').length,
    medium: Object.values(cityRiskData).filter(c => c.riskLevel === 'medium').length,
    high: Object.values(cityRiskData).filter(c => c.riskLevel === 'high').length,
    critical: Object.values(cityRiskData).filter(c => c.riskLevel === 'critical').length,
  }
  
  const alertCounts = {
    low: alerts.filter(a => a.severity === 'low').length,
    medium: alerts.filter(a => a.severity === 'medium').length,
    high: alerts.filter(a => a.severity === 'high').length,
    critical: alerts.filter(a => a.severity === 'critical').length,
  }

  // Get marker size based on city type and risk
  const getMarkerSize = (city) => {
    const baseSize = {
      capital: 14,
      major: 12,
      tourist: 10,
      pass: 8,
      city: 9,
      coastal: 10,
    }
    const riskBonus = {
      safe: 0,
      low: 0,
      medium: 2,
      high: 4,
      critical: 6,
    }
    return (baseSize[city.type] || 10) + (riskBonus[city.riskLevel] || 0)
  }

  return (
    <div className="safety-map">
      <div className="map-header">
        <h1>🗺️ Live Safety Map</h1>
        <p>Real-time weather alerts, road risks, and disaster zones across Pakistan</p>
        <div className="header-actions">
          <button 
            className={`refresh-btn ${refreshing ? 'refreshing' : ''}`}
            onClick={handleRefresh}
            disabled={refreshing}
          >
            <RefreshCw size={18} className={refreshing ? 'spin' : ''} />
            {refreshing ? 'Refreshing...' : 'Refresh Alerts'}
          </button>
          {lastUpdated && (
            <span className="last-updated">
              <Clock size={14} />
              Last updated: {lastUpdated.toLocaleTimeString()}
            </span>
          )}
        </div>
      </div>

      <div className="map-stats">
        <div className="stat-card safe">
          <span className="stat-count">{cityCounts.safe}</span>
          <span className="stat-label">Safe Cities</span>
        </div>
        <div className="stat-card low">
          <span className="stat-count">{cityCounts.low}</span>
          <span className="stat-label">Low Risk</span>
        </div>
        <div className="stat-card medium">
          <span className="stat-count">{cityCounts.medium}</span>
          <span className="stat-label">Medium Risk</span>
        </div>
        <div className="stat-card high">
          <span className="stat-count">{cityCounts.high}</span>
          <span className="stat-label">High Risk</span>
        </div>
        <div className="stat-card critical">
          <span className="stat-count">{cityCounts.critical}</span>
          <span className="stat-label">Critical</span>
        </div>
      </div>

      <div className="map-container">
        <MapContainer
          center={center}
          zoom={5}
          style={{ height: '550px', width: '100%', borderRadius: '20px' }}
        >
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          />
          
          {/* Show all cities with their risk levels */}
          {Object.entries(cityRiskData).map(([key, city]) => {
            const coords = [city.lat, city.lon]
            const color = SEVERITY_COLORS[city.riskLevel] || SEVERITY_COLORS.safe
            const radius = getMarkerSize(city)
            
            return (
              <CircleMarker
                key={key}
                center={coords}
                radius={radius}
                pathOptions={{
                  color: color,
                  fillColor: color,
                  fillOpacity: city.riskLevel === 'safe' ? 0.5 : 0.7,
                  weight: city.riskLevel === 'safe' ? 1 : 2,
                }}
                eventHandlers={{
                  click: () => setSelectedCity(key)
                }}
              >
                <Popup>
                  <div className="city-popup">
                    <h3 className={`popup-title ${city.riskLevel}`}>
                      <MapPin size={18} />
                      {city.name}
                    </h3>
                    <div className="popup-content">
                      <p className={`risk-level-text ${city.riskLevel}`}>
                        Risk Level: <strong>{city.riskLevel.toUpperCase()}</strong>
                      </p>
                      <p className="city-type">
                        {city.type === 'capital' ? '🏛️ Capital City' :
                         city.type === 'major' ? '🏙️ Major City' :
                         city.type === 'tourist' ? '🏔️ Tourist Destination' :
                         city.type === 'pass' ? '🛤️ Mountain Pass' :
                         city.type === 'coastal' ? '🌊 Coastal City' : '📍 City'}
                      </p>
                      {city.alertCount > 0 ? (
                        <div className="city-alerts">
                          <p className="alerts-count">⚠️ {city.alertCount} Active Alert{city.alertCount > 1 ? 's' : ''}</p>
                          <ul className="alerts-list-popup">
                            {city.alerts.slice(0, 3).map((alert, idx) => (
                              <li key={idx} className={alert.severity}>
                                {alert.alert_type}
                              </li>
                            ))}
                          </ul>
                        </div>
                      ) : (
                        <p className="no-alerts-text">✅ No active alerts</p>
                      )}
                    </div>
                  </div>
                </Popup>
              </CircleMarker>
            )
          })}
        </MapContainer>
        
        <div className="map-legend">
          <h4>Risk Level Legend</h4>
          <div className="legend-items">
            <div className="legend-item">
              <span className="legend-dot safe"></span> Safe (No Alerts)
            </div>
            <div className="legend-item">
              <span className="legend-dot low"></span> Low Risk
            </div>
            <div className="legend-item">
              <span className="legend-dot medium"></span> Medium Risk
            </div>
            <div className="legend-item">
              <span className="legend-dot high"></span> High Risk
            </div>
            <div className="legend-item">
              <span className="legend-dot critical"></span> Critical
            </div>
          </div>
          <div className="legend-divider"></div>
          <h4>City Types</h4>
          <div className="legend-items city-types">
            <div className="legend-item">🏛️ Capital</div>
            <div className="legend-item">🏙️ Major City</div>
            <div className="legend-item">🏔️ Tourist Spot</div>
            <div className="legend-item">🛤️ Mountain Pass</div>
          </div>
        </div>
      </div>

      <div className="alerts-list">
        <h2>
          <AlertTriangle size={24} />
          Active Safety Alerts ({alerts.length})
        </h2>
        {loading ? (
          <div className="loading-state">
            <div className="loading-spinner"></div>
            <p>Loading alerts...</p>
          </div>
        ) : alerts.length === 0 ? (
          <div className="no-alerts">
            <div className="no-alerts-icon">✅</div>
            <h3>All Clear!</h3>
            <p>No active safety alerts at this time</p>
            <p className="note">This map shows real-time alerts for floods, landslides, fog, and other hazards</p>
          </div>
        ) : (
          <div className="alerts-grid">
            {alerts.map((alert) => (
              <div key={alert.id} className={`alert-card ${alert.severity}`}>
                <div className="alert-header">
                  <div className="alert-icon-wrapper">
                    <AlertTriangle size={20} />
                  </div>
                  <div className="alert-title">
                    <span className="alert-type">{alert.alert_type}</span>
                    <span className="alert-region">{alert.region}</span>
                  </div>
                  <span className={`severity-badge ${alert.severity}`}>
                    {alert.severity}
                  </span>
                </div>
                {alert.description && (
                  <div className="alert-body">
                    <p>{alert.description}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default SafetyMap
