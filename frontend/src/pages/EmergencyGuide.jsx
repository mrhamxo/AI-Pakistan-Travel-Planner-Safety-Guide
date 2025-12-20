import React, { useState, useEffect } from 'react'
import { Phone, AlertCircle, MapPin, Shield, Mountain, Wifi, Fuel, Cloud, Heart, Download } from 'lucide-react'
import { travelAPI } from '../services/api'
import './EmergencyGuide.css'

function EmergencyGuide() {
  const [emergencyInfo, setEmergencyInfo] = useState(null)
  const [activeRegion, setActiveRegion] = useState('general')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadEmergencyInfo()
  }, [])

  const loadEmergencyInfo = async () => {
    try {
      const info = await travelAPI.getEmergencyInfo()
      setEmergencyInfo(info)
    } catch (error) {
      console.error('Error loading emergency info:', error)
    } finally {
      setLoading(false)
    }
  }

  const regions = [
    { id: 'general', label: 'All Pakistan' },
    { id: 'gilgit_baltistan', label: 'Gilgit-Baltistan' },
    { id: 'kpk', label: 'KPK / Northern Areas' },
    { id: 'punjab', label: 'Punjab' },
  ]

  const emergencyTips = [
    {
      title: 'If Stuck During Travel',
      icon: AlertCircle,
      tips: [
        'Stay calm and assess your situation',
        'Contact emergency services (1122) immediately',
        'Share your live location with trusted contacts',
        'Stay in a safe, visible location',
        'Conserve phone battery for emergency calls',
        'If vehicle breakdown, use hazard lights and warning triangle'
      ]
    },
    {
      title: 'During Natural Disasters',
      icon: Cloud,
      tips: [
        'Move to higher ground immediately if flooding',
        'Never attempt to cross flooded roads',
        'Stay away from riverbanks and landslide-prone hillsides',
        'If earthquake, drop, cover, and hold on',
        'Listen to local radio/authorities for updates',
        'Have 3-day emergency food and water supply'
      ]
    },
    {
      title: 'Northern Areas Emergencies',
      icon: Mountain,
      tips: [
        'For altitude sickness: descend immediately if severe',
        'Carry altitude sickness medication (Diamox)',
        'KKH closures: wait at nearest rest stop, don\'t try to pass',
        'Winter travel: always carry warm clothes, blankets, and food',
        'Inform PTDC or local police of your travel plan',
        'Register with tourism police if required'
      ]
    },
    {
      title: 'Medical Emergencies',
      icon: Heart,
      tips: [
        'Know the nearest hospital before traveling',
        'Carry first aid kit with personal medications',
        'In remote areas, local dispensaries can help',
        'Helicopter evacuation available in Gilgit-Baltistan (very expensive)',
        'Travel insurance is highly recommended',
        'Keep blood type and medical history documented'
      ]
    }
  ]

  const offlineChecklist = [
    'Download offline Google Maps of your route',
    'Save emergency numbers in phone (not just contacts app)',
    'Screenshot hotel booking confirmations',
    'Save local transport operator numbers',
    'Download translation apps for Urdu/local languages',
    'Keep physical copies of CNIC/Passport',
    'Note down embassy contacts if foreign national',
  ]

  return (
    <div className="emergency-guide">
      <div className="guide-header">
        <h1>🆘 Emergency Travel Guide</h1>
        <p>Essential information to stay safe while traveling in Pakistan</p>
      </div>

      {/* Region Selector */}
      <div className="region-selector">
        {regions.map(region => (
          <button
            key={region.id}
            className={`region-btn ${activeRegion === region.id ? 'active' : ''}`}
            onClick={() => setActiveRegion(region.id)}
          >
            {region.label}
          </button>
        ))}
      </div>

      {/* Emergency Numbers */}
      <div className="emergency-numbers">
        <h2>
          <Phone className="section-icon" />
          Emergency Numbers
        </h2>
        
        {loading ? (
          <p>Loading emergency contacts...</p>
        ) : (
          <div className="numbers-grid">
            {/* General numbers always show */}
            {emergencyInfo?.all_regions?.general && Object.entries(emergencyInfo.all_regions.general).map(([key, value]) => (
              <a key={key} href={`tel:${value}`} className="number-card national">
                <div className="number">{value}</div>
                <div className="service-name">{key.replace(/_/g, ' ')}</div>
                <div className="service-type">National</div>
              </a>
            ))}
            
            {/* Region-specific numbers */}
            {activeRegion !== 'general' && emergencyInfo?.all_regions?.[activeRegion] && 
              Object.entries(emergencyInfo.all_regions[activeRegion]).map(([key, value]) => (
                <a key={key} href={`tel:${value}`} className="number-card regional">
                  <div className="number">{value}</div>
                  <div className="service-name">{key.replace(/_/g, ' ')}</div>
                  <div className="service-type">Regional</div>
                </a>
              ))
            }
          </div>
        )}
      </div>

      {/* Emergency Tips */}
      <div className="emergency-tips">
        <h2><Shield className="section-icon" /> Emergency Procedures</h2>
        <div className="tips-grid">
          {emergencyTips.map((section, idx) => (
            <div key={idx} className="tip-section">
              <h3>
                <section.icon className="tip-icon" />
                {section.title}
              </h3>
              <ul>
                {section.tips.map((tip, tipIdx) => (
                  <li key={tipIdx}>{tip}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>

      {/* Critical Information */}
      <div className="critical-info">
        <h2><MapPin className="section-icon" /> Northern Areas Critical Info</h2>
        <div className="info-grid">
          <div className="info-card altitude">
            <Mountain size={28} />
            <h4>Altitude Sickness</h4>
            <p>Hunza (2,500m), Skardu (2,200m), Khunjerab Pass (4,700m)</p>
            <ul>
              <li>Symptoms: headache, nausea, dizziness</li>
              <li>Prevention: ascend slowly, stay hydrated</li>
              <li>Treatment: descend immediately if severe</li>
            </ul>
          </div>
          
          <div className="info-card connectivity">
            <Wifi size={28} />
            <h4>Mobile Network Coverage</h4>
            <p>Best networks for northern areas:</p>
            <ul>
              <li>Jazz/Mobilink: Works till Hunza</li>
              <li>Zong: Good in Gilgit, spotty after</li>
              <li>No signal: Beyond Sost, Deosai, upper Swat valleys</li>
            </ul>
          </div>
          
          <div className="info-card fuel">
            <Fuel size={28} />
            <h4>Fuel Availability</h4>
            <p>Plan your fuel stops carefully:</p>
            <ul>
              <li>Last major pump before Gilgit: Chilas</li>
              <li>Last pump before Khunjerab: Aliabad</li>
              <li>Carry 10-20L extra for remote areas</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Offline Preparation */}
      <div className="offline-section">
        <h2><Download className="section-icon" /> Prepare for Offline Areas</h2>
        <p className="offline-intro">Many northern areas have no internet. Prepare before you go:</p>
        <div className="offline-checklist">
          {offlineChecklist.map((item, idx) => (
            <label key={idx} className="checklist-item">
              <input type="checkbox" />
              <span>{item}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Safety Tips from API */}
      {emergencyInfo?.tips && (
        <div className="api-tips">
          <h2>💡 General Safety Tips</h2>
          <ul>
            {emergencyInfo.tips.map((tip, idx) => (
              <li key={idx}>{tip}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Important Reminder */}
      <div className="safety-reminder">
        <h3>⚠️ Important Reminder</h3>
        <p>
          This guide provides general emergency guidance. Always prioritize your safety and 
          follow instructions from local authorities. In case of immediate danger, call 
          <strong> 1122 (Rescue)</strong> or <strong>15 (Police)</strong> without delay.
        </p>
        <p className="reminder-note">
          Save this page offline by taking screenshots or printing before traveling to remote areas.
        </p>
      </div>
    </div>
  )
}

export default EmergencyGuide
