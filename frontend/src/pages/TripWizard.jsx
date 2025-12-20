import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { 
  MapPin, Users, DollarSign, Calendar, Compass, 
  ChevronRight, ChevronLeft, Loader, Check, 
  Mountain, Tent, Sparkles, Wallet
} from 'lucide-react'
import { travelAPI } from '../services/api'
import './TripWizard.css'

const STEPS = [
  { id: 1, title: 'Destination', icon: MapPin },
  { id: 2, title: 'Travelers', icon: Users },
  { id: 3, title: 'Budget', icon: DollarSign },
  { id: 4, title: 'Duration', icon: Calendar },
  { id: 5, title: 'Style', icon: Compass },
]

const TRAVEL_STYLES = [
  { id: 'budget', label: 'Budget', icon: Wallet, description: 'Hostels, public transport, street food' },
  { id: 'comfort', label: 'Comfort', icon: Sparkles, description: 'Good hotels, private transport, restaurants' },
  { id: 'adventure', label: 'Adventure', icon: Tent, description: 'Camping, trekking, off-road exploration' },
  { id: 'luxury', label: 'Luxury', icon: Mountain, description: 'Premium stays, private tours, fine dining' },
]

function TripWizard() {
  const navigate = useNavigate()
  const [currentStep, setCurrentStep] = useState(1)
  const [destinations, setDestinations] = useState([])
  const [loading, setLoading] = useState(false)
  const [generating, setGenerating] = useState(false)
  const [tripPlan, setTripPlan] = useState(null)
  const [error, setError] = useState(null)
  
  const [formData, setFormData] = useState({
    destination: '',
    travelType: 'family',
    numPeople: 4,
    budgetPkr: 150000,
    durationDays: 5,
    travelStyle: 'comfort',
    originCity: 'Islamabad',
    startDate: '',
    specialRequirements: [],
  })

  useEffect(() => {
    loadDestinations()
  }, [])

  const loadDestinations = async () => {
    try {
      const data = await travelAPI.getDestinations()
      setDestinations(data)
    } catch (err) {
      console.error('Error loading destinations:', err)
    }
  }

  const updateFormData = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  const nextStep = () => {
    if (currentStep < STEPS.length) {
      setCurrentStep(prev => prev + 1)
    }
  }

  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(prev => prev - 1)
    }
  }

  const canProceed = () => {
    switch (currentStep) {
      case 1: return formData.destination !== ''
      case 2: return formData.numPeople > 0
      case 3: return formData.budgetPkr >= 10000
      case 4: return formData.durationDays >= 1
      case 5: return formData.travelStyle !== ''
      default: return true
    }
  }

  const generateTripPlan = async () => {
    setGenerating(true)
    setError(null)
    
    try {
      const requestData = {
        destination: formData.destination,
        duration_days: formData.durationDays,
        travel_type: formData.travelType,
        num_people: formData.numPeople,
        budget_pkr: formData.budgetPkr,
        travel_style: formData.travelStyle,
        origin_city: formData.originCity,
        start_date: formData.startDate || null,
        special_requirements: formData.specialRequirements.length > 0 ? formData.specialRequirements : null,
      }
      
      const plan = await travelAPI.createTripPlan(requestData)
      setTripPlan(plan)
      
      // Navigate to itinerary view with the plan
      navigate('/itinerary', { state: { tripPlan: plan, formData } })
      
    } catch (err) {
      console.error('Error generating trip plan:', err)
      setError(err.response?.data?.detail || 'Failed to generate trip plan. Please try again.')
    } finally {
      setGenerating(false)
    }
  }

  const selectedDestination = destinations.find(d => d.name === formData.destination)

  return (
    <div className="trip-wizard">
      <div className="wizard-header">
        <h1>🗺️ Plan Your Dream Trip</h1>
        <p>Let our AI create a personalized itinerary for your Pakistan adventure</p>
      </div>

      {/* Progress Steps */}
      <div className="wizard-progress">
        {STEPS.map((step, idx) => (
          <div 
            key={step.id} 
            className={`progress-step ${currentStep === step.id ? 'active' : ''} ${currentStep > step.id ? 'completed' : ''}`}
            onClick={() => currentStep > step.id && setCurrentStep(step.id)}
          >
            <div className="step-icon">
              {currentStep > step.id ? <Check size={16} /> : <step.icon size={16} />}
            </div>
            <span className="step-title">{step.title}</span>
            {idx < STEPS.length - 1 && <div className="step-connector" />}
          </div>
        ))}
      </div>

      <div className="wizard-content">
        {/* Step 1: Destination */}
        {currentStep === 1 && (
          <div className="wizard-step animate-fade-in">
            <h2>Where do you want to go?</h2>
            <p className="step-description">Choose from Pakistan's most beautiful destinations</p>
            
            <div className="destinations-grid">
              {destinations.map(dest => (
                <div 
                  key={dest.name}
                  className={`destination-card ${formData.destination === dest.name ? 'selected' : ''}`}
                  onClick={() => updateFormData('destination', dest.name)}
                >
                  <div className="dest-image" style={{ background: `linear-gradient(135deg, #667eea, #764ba2)` }}>
                    <span className="dest-emoji">
                      {dest.name === 'Hunza' ? '⛰️' : 
                       dest.name === 'Skardu' ? '🏔️' :
                       dest.name === 'Swat' ? '🌲' :
                       dest.name === 'Naran' ? '🌊' :
                       dest.name === 'Murree' ? '🌨️' :
                       dest.name === 'Chitral' ? '🏕️' :
                       dest.name === 'Gilgit' ? '🗻' : '🏞️'}
                    </span>
                  </div>
                  <div className="dest-info">
                    <h3>{dest.name}</h3>
                    <span className="dest-region">{dest.region}</span>
                    <div className="dest-meta">
                      <span>{dest.min_days}+ days</span>
                      <span className={`difficulty ${dest.difficulty}`}>{dest.difficulty}</span>
                    </div>
                  </div>
                  {formData.destination === dest.name && (
                    <div className="selected-badge"><Check size={14} /></div>
                  )}
                </div>
              ))}
            </div>

            {selectedDestination && (
              <div className="destination-preview">
                <h4>About {selectedDestination.name}</h4>
                <p><strong>Best Season:</strong> {selectedDestination.best_season}</p>
                <p><strong>Highlights:</strong> {selectedDestination.highlights.join(', ')}</p>
              </div>
            )}
          </div>
        )}

        {/* Step 2: Travelers */}
        {currentStep === 2 && (
          <div className="wizard-step animate-fade-in">
            <h2>Who's traveling?</h2>
            <p className="step-description">Tell us about your travel group</p>

            <div className="form-section">
              <label>Travel Type</label>
              <div className="travel-type-options">
                {[
                  { id: 'solo', label: 'Solo', icon: '🧍', desc: 'Just me' },
                  { id: 'couple', label: 'Couple', icon: '💑', desc: '2 people' },
                  { id: 'family', label: 'Family', icon: '👨‍👩‍👧‍👦', desc: 'With kids' },
                  { id: 'group', label: 'Group', icon: '👥', desc: 'Friends/colleagues' },
                ].map(type => (
                  <div 
                    key={type.id}
                    className={`travel-type-card ${formData.travelType === type.id ? 'selected' : ''}`}
                    onClick={() => {
                      updateFormData('travelType', type.id)
                      if (type.id === 'solo') updateFormData('numPeople', 1)
                      else if (type.id === 'couple') updateFormData('numPeople', 2)
                      else if (type.id === 'family') updateFormData('numPeople', 4)
                    }}
                  >
                    <span className="type-icon">{type.icon}</span>
                    <span className="type-label">{type.label}</span>
                    <span className="type-desc">{type.desc}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="form-section">
              <label>Number of Travelers</label>
              <div className="people-counter">
                <button 
                  className="counter-btn"
                  onClick={() => updateFormData('numPeople', Math.max(1, formData.numPeople - 1))}
                >-</button>
                <span className="counter-value">{formData.numPeople}</span>
                <button 
                  className="counter-btn"
                  onClick={() => updateFormData('numPeople', Math.min(50, formData.numPeople + 1))}
                >+</button>
              </div>
            </div>

            <div className="form-section">
              <label>Starting City</label>
              <select 
                value={formData.originCity}
                onChange={(e) => updateFormData('originCity', e.target.value)}
                className="form-select"
              >
                <option value="Islamabad">Islamabad</option>
                <option value="Lahore">Lahore</option>
                <option value="Karachi">Karachi</option>
                <option value="Peshawar">Peshawar</option>
                <option value="Rawalpindi">Rawalpindi</option>
              </select>
            </div>
          </div>
        )}

        {/* Step 3: Budget */}
        {currentStep === 3 && (
          <div className="wizard-step animate-fade-in">
            <h2>What's your budget?</h2>
            <p className="step-description">Total budget for all travelers</p>

            <div className="budget-section">
              <div className="budget-display">
                <span className="budget-currency">PKR</span>
                <span className="budget-amount">{formData.budgetPkr.toLocaleString()}</span>
              </div>
              
              <input 
                type="range"
                min="30000"
                max="500000"
                step="10000"
                value={formData.budgetPkr}
                onChange={(e) => updateFormData('budgetPkr', parseInt(e.target.value))}
                className="budget-slider"
              />
              
              <div className="budget-labels">
                <span>PKR 30,000</span>
                <span>PKR 500,000</span>
              </div>

              <div className="budget-presets">
                {[50000, 100000, 150000, 200000, 300000].map(amount => (
                  <button 
                    key={amount}
                    className={`preset-btn ${formData.budgetPkr === amount ? 'active' : ''}`}
                    onClick={() => updateFormData('budgetPkr', amount)}
                  >
                    {amount >= 100000 ? `${amount/100000}L` : `${amount/1000}K`}
                  </button>
                ))}
              </div>

              <div className="budget-estimate">
                <p>~PKR {Math.round(formData.budgetPkr / formData.numPeople).toLocaleString()} per person</p>
              </div>
            </div>
          </div>
        )}

        {/* Step 4: Duration */}
        {currentStep === 4 && (
          <div className="wizard-step animate-fade-in">
            <h2>How long is your trip?</h2>
            <p className="step-description">Select the number of days</p>

            <div className="duration-section">
              <div className="duration-display">
                <span className="duration-value">{formData.durationDays}</span>
                <span className="duration-label">days</span>
              </div>

              <input 
                type="range"
                min="2"
                max="15"
                value={formData.durationDays}
                onChange={(e) => updateFormData('durationDays', parseInt(e.target.value))}
                className="duration-slider"
              />

              <div className="duration-presets">
                {[3, 5, 7, 10, 14].map(days => (
                  <button 
                    key={days}
                    className={`preset-btn ${formData.durationDays === days ? 'active' : ''}`}
                    onClick={() => updateFormData('durationDays', days)}
                  >
                    {days} days
                  </button>
                ))}
              </div>

              {selectedDestination && formData.durationDays < selectedDestination.min_days && (
                <div className="duration-warning">
                  ⚠️ {selectedDestination.name} typically requires at least {selectedDestination.min_days} days
                </div>
              )}

              <div className="form-section">
                <label>Start Date (Optional)</label>
                <input 
                  type="date"
                  value={formData.startDate}
                  onChange={(e) => updateFormData('startDate', e.target.value)}
                  className="form-input"
                  min={new Date().toISOString().split('T')[0]}
                />
              </div>
            </div>
          </div>
        )}

        {/* Step 5: Travel Style */}
        {currentStep === 5 && (
          <div className="wizard-step animate-fade-in">
            <h2>What's your travel style?</h2>
            <p className="step-description">This helps us recommend the right accommodations and activities</p>

            <div className="style-options">
              {TRAVEL_STYLES.map(style => (
                <div 
                  key={style.id}
                  className={`style-card ${formData.travelStyle === style.id ? 'selected' : ''}`}
                  onClick={() => updateFormData('travelStyle', style.id)}
                >
                  <div className="style-icon-wrapper">
                    <style.icon size={28} />
                  </div>
                  <h3>{style.label}</h3>
                  <p>{style.description}</p>
                  {formData.travelStyle === style.id && (
                    <div className="selected-check"><Check size={16} /></div>
                  )}
                </div>
              ))}
            </div>

            {/* Trip Summary */}
            <div className="trip-summary">
              <h3>Your Trip Summary</h3>
              <div className="summary-grid">
                <div className="summary-item">
                  <MapPin size={18} />
                  <span>{formData.destination}</span>
                </div>
                <div className="summary-item">
                  <Users size={18} />
                  <span>{formData.numPeople} {formData.travelType}</span>
                </div>
                <div className="summary-item">
                  <DollarSign size={18} />
                  <span>PKR {formData.budgetPkr.toLocaleString()}</span>
                </div>
                <div className="summary-item">
                  <Calendar size={18} />
                  <span>{formData.durationDays} days</span>
                </div>
              </div>
            </div>

            {error && (
              <div className="error-message">
                {error}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Navigation Buttons */}
      <div className="wizard-navigation">
        {currentStep > 1 && (
          <button className="nav-btn back-btn" onClick={prevStep}>
            <ChevronLeft size={18} /> Back
          </button>
        )}
        
        <div className="nav-spacer" />
        
        {currentStep < STEPS.length ? (
          <button 
            className="nav-btn next-btn" 
            onClick={nextStep}
            disabled={!canProceed()}
          >
            Next <ChevronRight size={18} />
          </button>
        ) : (
          <button 
            className="nav-btn generate-btn" 
            onClick={generateTripPlan}
            disabled={generating || !canProceed()}
          >
            {generating ? (
              <>
                <Loader size={18} className="spin" /> Generating Plan...
              </>
            ) : (
              <>
                Generate My Trip Plan <Sparkles size={18} />
              </>
            )}
          </button>
        )}
      </div>
    </div>
  )
}

export default TripWizard
