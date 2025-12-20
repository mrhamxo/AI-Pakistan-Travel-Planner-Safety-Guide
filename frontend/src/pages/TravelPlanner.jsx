import React, { useState, useEffect, useRef, useCallback } from 'react'
import { useSearchParams } from 'react-router-dom'
import { 
  Send, User, MapPin, Clock, Shield, DollarSign, Copy, Check, AlertTriangle,
  MessageSquare, Plus, Trash2, Download, Star, Search, X, ChevronLeft,
  ChevronRight, History, Sparkles, Mic, MicOff
} from 'lucide-react'
import { travelAPI } from '../services/api'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import './TravelPlanner.css'

// LocalStorage keys
const STORAGE_KEYS = {
  SESSIONS: 'travel_planner_sessions',
  ACTIVE_SESSION: 'travel_planner_active_session',
  USER_PROFILE: 'travel_planner_user_profile',
}

// Generate unique ID
const generateId = () => `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`

// Create new session
const createNewSession = () => ({
  id: generateId(),
  title: 'New Chat',
  messages: [],
  createdAt: new Date().toISOString(),
  updatedAt: new Date().toISOString(),
})

function TravelPlanner() {
  const [searchParams] = useSearchParams()
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [copiedIdx, setCopiedIdx] = useState(null)
  const [showProfile, setShowProfile] = useState(false)
  const [showSidebar, setShowSidebar] = useState(true)
  const [showSearch, setShowSearch] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [isListening, setIsListening] = useState(false)
  
  // Session management
  const [sessions, setSessions] = useState([])
  const [activeSessionId, setActiveSessionId] = useState(null)
  const [messages, setMessages] = useState([])
  
  // User profile
  const [userProfile, setUserProfile] = useState({
    gender: '',
    travel_group: '',
    preferredBudget: '',
    homeCity: 'Islamabad'
  })
  
  // Favorites
  const [favorites, setFavorites] = useState([])
  
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)
  const recognitionRef = useRef(null)

  // Load sessions from localStorage on mount
  useEffect(() => {
    const savedSessions = localStorage.getItem(STORAGE_KEYS.SESSIONS)
    const savedActiveSession = localStorage.getItem(STORAGE_KEYS.ACTIVE_SESSION)
    const savedProfile = localStorage.getItem(STORAGE_KEYS.USER_PROFILE)
    
    if (savedSessions) {
      const parsedSessions = JSON.parse(savedSessions)
      setSessions(parsedSessions)
      
      if (savedActiveSession && parsedSessions.find(s => s.id === savedActiveSession)) {
        setActiveSessionId(savedActiveSession)
        const activeSession = parsedSessions.find(s => s.id === savedActiveSession)
        setMessages(activeSession?.messages || [])
      } else if (parsedSessions.length > 0) {
        setActiveSessionId(parsedSessions[0].id)
        setMessages(parsedSessions[0].messages || [])
      }
    } else {
      // Create initial session
      const newSession = createNewSession()
      setSessions([newSession])
      setActiveSessionId(newSession.id)
    }
    
    if (savedProfile) {
      setUserProfile(JSON.parse(savedProfile))
    }
  }, [])

  // Save sessions to localStorage whenever they change
  useEffect(() => {
    if (sessions.length > 0) {
      localStorage.setItem(STORAGE_KEYS.SESSIONS, JSON.stringify(sessions))
    }
  }, [sessions])

  // Save active session ID
  useEffect(() => {
    if (activeSessionId) {
      localStorage.setItem(STORAGE_KEYS.ACTIVE_SESSION, activeSessionId)
    }
  }, [activeSessionId])

  // Save user profile
  useEffect(() => {
    localStorage.setItem(STORAGE_KEYS.USER_PROFILE, JSON.stringify(userProfile))
  }, [userProfile])

  // Update session messages when messages change
  useEffect(() => {
    if (activeSessionId && messages.length > 0) {
      setSessions(prev => prev.map(session => {
        if (session.id === activeSessionId) {
          // Update session title based on first user message
          const firstUserMsg = messages.find(m => m.role === 'user')
          const title = firstUserMsg 
            ? firstUserMsg.content.slice(0, 30) + (firstUserMsg.content.length > 30 ? '...' : '')
            : session.title
          return {
            ...session,
            messages,
            title,
            updatedAt: new Date().toISOString()
          }
        }
        return session
      }))
    }
  }, [messages, activeSessionId])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, loading])

  // Handle URL params for initial query
  useEffect(() => {
    const origin = searchParams.get('origin')
    const destination = searchParams.get('destination')
    if (origin && destination) {
      const initialQuery = `Is it safe to travel from ${origin} to ${destination}?`
      setQuery(initialQuery)
    }
  }, [searchParams])

  // Initialize speech recognition
  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
      recognitionRef.current = new SpeechRecognition()
      recognitionRef.current.continuous = false
      recognitionRef.current.interimResults = false
      recognitionRef.current.lang = 'en-US'
      
      recognitionRef.current.onresult = (event) => {
        const transcript = event.results[0][0].transcript
        setQuery(prev => prev + ' ' + transcript)
        setIsListening(false)
      }
      
      recognitionRef.current.onerror = () => {
        setIsListening(false)
      }
      
      recognitionRef.current.onend = () => {
        setIsListening(false)
      }
    }
  }, [])

  const toggleVoiceInput = () => {
    if (!recognitionRef.current) {
      alert('Speech recognition is not supported in your browser.')
      return
    }
    
    if (isListening) {
      recognitionRef.current.stop()
      setIsListening(false)
    } else {
      recognitionRef.current.start()
      setIsListening(true)
    }
  }

  const handleCopy = async (text, idx) => {
    try {
      await navigator.clipboard.writeText(text)
      setCopiedIdx(idx)
      setTimeout(() => setCopiedIdx(null), 2000)
    } catch (err) {
      console.error('Failed to copy:', err)
    }
  }

  const toggleFavorite = (msgIdx) => {
    const msgId = `${activeSessionId}-${msgIdx}`
    setFavorites(prev => {
      if (prev.includes(msgId)) {
        return prev.filter(id => id !== msgId)
      }
      return [...prev, msgId]
    })
  }

  const isFavorite = (msgIdx) => {
    return favorites.includes(`${activeSessionId}-${msgIdx}`)
  }

  // Generate suggested follow-up questions based on response
  const generateSuggestions = (response, data) => {
    const suggestions = []
    
    if (data?.routes?.[0]) {
      const route = data.routes[0]
      if (route.risk_level === 'caution' || route.risk_level === 'avoid') {
        suggestions.push('What are safer alternative routes?')
      }
      if (route.transport_options?.length > 0) {
        suggestions.push('Which transport option is most comfortable?')
      }
    }
    
    if (data?.cost_estimate) {
      suggestions.push('How can I reduce travel costs?')
    }
    
    // Generic suggestions
    suggestions.push('What should I pack for this trip?')
    suggestions.push('Are there any hotels you recommend?')
    
    return suggestions.slice(0, 3)
  }

  const handleSend = async () => {
    if (!query.trim()) return

    const userMessage = { 
      role: 'user', 
      content: query,
      timestamp: new Date().toISOString()
    }
    setMessages(prev => [...prev, userMessage])
    setLoading(true)
    const currentQuery = query
    setQuery('')

    // Format conversation history for context-aware responses
    // Only include recent messages to keep request size reasonable
    const conversationHistory = messages.slice(-10).map(msg => ({
      type: msg.role === 'user' ? 'user' : 'ai',
      content: msg.content,
      timestamp: msg.timestamp
    }))

    try {
      const response = await travelAPI.queryTravel({
        query: currentQuery,
        user_profile: userProfile.gender || userProfile.travel_group ? userProfile : null,
        conversation_history: conversationHistory.length > 0 ? conversationHistory : null
      })

      const suggestions = generateSuggestions(response.response, {
        routes: response.routes,
        cost_estimate: response.cost_estimate
      })

      const aiMessage = {
        role: 'assistant',
        content: response.response,
        timestamp: new Date().toISOString(),
        data: {
          routes: response.routes,
          recommendations: response.recommendations,
          cost_estimate: response.cost_estimate,
          uncertainty_notes: response.uncertainty_notes
        },
        suggestions
      }
      setMessages(prev => [...prev, aiMessage])
    } catch (error) {
      const errorMessage = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toISOString(),
        error: true
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  // Session management functions
  const createSession = () => {
    const newSession = createNewSession()
    setSessions(prev => [newSession, ...prev])
    setActiveSessionId(newSession.id)
    setMessages([])
  }

  const switchSession = (sessionId) => {
    const session = sessions.find(s => s.id === sessionId)
    if (session) {
      setActiveSessionId(sessionId)
      setMessages(session.messages || [])
    }
  }

  const deleteSession = (sessionId, e) => {
    e.stopPropagation()
    setSessions(prev => {
      const filtered = prev.filter(s => s.id !== sessionId)
      if (filtered.length === 0) {
        const newSession = createNewSession()
        setActiveSessionId(newSession.id)
        setMessages([])
        return [newSession]
      }
      if (sessionId === activeSessionId) {
        setActiveSessionId(filtered[0].id)
        setMessages(filtered[0].messages || [])
      }
      return filtered
    })
  }

  const clearCurrentChat = () => {
    if (window.confirm('Clear all messages in this chat?')) {
      setMessages([])
      setSessions(prev => prev.map(s => 
        s.id === activeSessionId 
          ? { ...s, messages: [], title: 'New Chat', updatedAt: new Date().toISOString() }
          : s
      ))
    }
  }

  const exportChat = () => {
    if (messages.length === 0) {
      alert('No messages to export')
      return
    }
    
    let content = `AI Travel Planner - Chat Export\n`
    content += `Exported: ${new Date().toLocaleString()}\n`
    content += `${'='.repeat(50)}\n\n`
    
    messages.forEach(msg => {
      const role = msg.role === 'user' ? 'You' : 'AI'
      const time = new Date(msg.timestamp).toLocaleTimeString()
      content += `[${time}] ${role}:\n${msg.content}\n\n`
      
      if (msg.data?.routes?.[0]) {
        const route = msg.data.routes[0]
        content += `Route Details:\n`
        content += `- Distance: ${route.distance_km} km\n`
        content += `- Time: ${route.estimated_time_hours} hours\n`
        content += `- Safety: ${route.safety_score}/100\n\n`
      }
      
      if (msg.data?.cost_estimate) {
        content += `Cost Estimate: PKR ${Math.round(msg.data.cost_estimate.cheapest)} - ${Math.round(msg.data.cost_estimate.most_expensive)}\n\n`
      }
      
      content += `${'-'.repeat(40)}\n\n`
    })
    
    const blob = new Blob([content], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `travel-chat-${new Date().toISOString().split('T')[0]}.txt`
    a.click()
    URL.revokeObjectURL(url)
  }

  // Filter messages for search
  const filteredMessages = searchQuery 
    ? messages.filter(m => 
        m.content.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : messages

  const quickQueries = [
    "Islamabad to Lahore tomorrow",
    "Swat trip safety for family",
    "Cheapest way to Murree",
    "5-day trip plan for Hunza"
  ]

  const formatTime = (timestamp) => {
    if (!timestamp) return ''
    const date = new Date(timestamp)
    const now = new Date()
    const diff = now - date
    
    if (diff < 60000) return 'Just now'
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`
    if (diff < 86400000) return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    return date.toLocaleDateString()
  }

  return (
    <div className="travel-planner advanced">
      {/* Sidebar */}
      <div className={`planner-sidebar ${showSidebar ? 'open' : 'closed'}`}>
        <div className="sidebar-header">
          <h3><MessageSquare size={18} /> Chat History</h3>
          <button className="new-chat-btn" onClick={createSession} title="New Chat">
            <Plus size={18} />
          </button>
        </div>
        
        <div className="sessions-list">
          {sessions.map(session => (
            <div 
              key={session.id}
              className={`session-item ${session.id === activeSessionId ? 'active' : ''}`}
              onClick={() => switchSession(session.id)}
            >
              <div className="session-info">
                <span className="session-title">{session.title}</span>
                <span className="session-date">{formatTime(session.updatedAt)}</span>
              </div>
              <button 
                className="delete-session-btn"
                onClick={(e) => deleteSession(session.id, e)}
                title="Delete chat"
              >
                <Trash2 size={14} />
              </button>
            </div>
          ))}
        </div>
        
        <div className="sidebar-footer">
          <button className="sidebar-action" onClick={exportChat} title="Export Chat">
            <Download size={16} /> Export
          </button>
          <button className="sidebar-action" onClick={clearCurrentChat} title="Clear Chat">
            <Trash2 size={16} /> Clear
          </button>
        </div>
      </div>

      {/* Toggle sidebar button */}
      <button 
        className="sidebar-toggle"
        onClick={() => setShowSidebar(!showSidebar)}
      >
        {showSidebar ? <ChevronLeft size={20} /> : <ChevronRight size={20} />}
      </button>

      {/* Main chat area */}
      <div className="planner-main">
        <div className="planner-header">
          <div className="header-left">
            <h1>🧭 AI Travel Planner</h1>
            <p>Get personalized travel advice for Pakistan</p>
          </div>
          <div className="header-actions">
            <button 
              className={`header-btn ${showSearch ? 'active' : ''}`}
              onClick={() => setShowSearch(!showSearch)}
              title="Search in chat"
            >
              <Search size={18} />
            </button>
            <button 
              className="header-btn"
              onClick={() => setShowProfile(!showProfile)}
              title="User Profile"
            >
              <User size={18} />
            </button>
          </div>
        </div>

        {/* Search bar */}
        {showSearch && (
          <div className="search-bar animate-slide-in">
            <Search size={18} />
            <input
              type="text"
              placeholder="Search in conversation..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              autoFocus
            />
            {searchQuery && (
              <button onClick={() => setSearchQuery('')}>
                <X size={18} />
              </button>
            )}
          </div>
        )}

        {/* Profile panel */}
        {showProfile && (
          <div className="profile-panel animate-slide-in">
            <h3>Your Travel Profile</h3>
            <p className="profile-hint">This helps us give you more personalized advice</p>
            <div className="profile-inputs">
              <div>
                <label>Gender</label>
                <select
                  value={userProfile.gender}
                  onChange={(e) => setUserProfile({...userProfile, gender: e.target.value})}
                >
                  <option value="">Prefer not to say</option>
                  <option value="male">Male</option>
                  <option value="female">Female</option>
                  <option value="other">Other</option>
                </select>
              </div>
              <div>
                <label>Travel Group</label>
                <select
                  value={userProfile.travel_group}
                  onChange={(e) => setUserProfile({...userProfile, travel_group: e.target.value})}
                >
                  <option value="">Not specified</option>
                  <option value="solo">Solo</option>
                  <option value="family">Family</option>
                  <option value="group">Group</option>
                  <option value="couple">Couple</option>
                </select>
              </div>
              <div>
                <label>Home City</label>
                <select
                  value={userProfile.homeCity}
                  onChange={(e) => setUserProfile({...userProfile, homeCity: e.target.value})}
                >
                  <option value="Islamabad">Islamabad</option>
                  <option value="Lahore">Lahore</option>
                  <option value="Karachi">Karachi</option>
                  <option value="Peshawar">Peshawar</option>
                  <option value="Rawalpindi">Rawalpindi</option>
                  <option value="Multan">Multan</option>
                </select>
              </div>
              <div>
                <label>Budget Preference</label>
                <select
                  value={userProfile.preferredBudget}
                  onChange={(e) => setUserProfile({...userProfile, preferredBudget: e.target.value})}
                >
                  <option value="">Not specified</option>
                  <option value="budget">Budget-friendly</option>
                  <option value="moderate">Moderate</option>
                  <option value="luxury">Luxury</option>
                </select>
              </div>
            </div>
          </div>
        )}

        <div className="chat-container">
          <div className="messages">
            {filteredMessages.length === 0 && !searchQuery && (
              <div className="welcome-message animate-fade-in">
                <div className="welcome-icon">🗺️</div>
                <h3>Welcome to AI Travel Planner</h3>
                <p>Ask me anything about traveling in Pakistan. I'll help you with:</p>
                <div className="features-grid">
                  <div className="feature-item">
                    <Shield size={20} />
                    <span>Safety advice</span>
                  </div>
                  <div className="feature-item">
                    <DollarSign size={20} />
                    <span>Cost estimates</span>
                  </div>
                  <div className="feature-item">
                    <MapPin size={20} />
                    <span>Route options</span>
                  </div>
                  <div className="feature-item">
                    <Clock size={20} />
                    <span>Travel times</span>
                  </div>
                </div>
                
                <div className="session-info-box">
                  <History size={16} />
                  <span>Your conversations are saved automatically</span>
                </div>
                
                <p className="quick-start">Quick start:</p>
                <div className="quick-queries">
                  {quickQueries.map((q, idx) => (
                    <button 
                      key={idx} 
                      className="quick-query-btn"
                      onClick={() => setQuery(q)}
                    >
                      <Sparkles size={14} />
                      {q}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {searchQuery && filteredMessages.length === 0 && (
              <div className="no-results">
                <Search size={40} />
                <p>No messages found for "{searchQuery}"</p>
              </div>
            )}
            
            {filteredMessages.map((msg, idx) => (
              <div key={idx} className={`message ${msg.role} animate-slide-up`}>
                <div className="message-header">
                  <span className="message-time">{formatTime(msg.timestamp)}</span>
                  {msg.role === 'assistant' && !msg.error && (
                    <div className="message-actions">
                      <button 
                        className={`action-btn ${isFavorite(idx) ? 'favorited' : ''}`}
                        onClick={() => toggleFavorite(idx)}
                        title="Add to favorites"
                      >
                        <Star size={14} fill={isFavorite(idx) ? 'currentColor' : 'none'} />
                      </button>
                      <button 
                        className="action-btn"
                        onClick={() => handleCopy(msg.content, idx)}
                        title="Copy to clipboard"
                      >
                        {copiedIdx === idx ? <Check size={14} /> : <Copy size={14} />}
                      </button>
                    </div>
                  )}
                </div>
                <div className="message-content">
                  {msg.role === 'assistant' ? (
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {msg.content}
                    </ReactMarkdown>
                  ) : (
                    msg.content
                  )}
                </div>
                
                {msg.data && (
                  <div className="message-data animate-fade-in">
                    {msg.data.routes && msg.data.routes.length > 0 && (
                      <div className="route-info">
                        <h4><MapPin size={18} /> Route Details</h4>
                        {msg.data.routes.map((route, rIdx) => (
                          <div key={rIdx} className="route-card">
                            <div className="route-header">
                              <span className={`risk-badge ${route.risk_level}`}>
                                {route.risk_level === 'recommended' && '✅ '}
                                {route.risk_level === 'caution' && '⚠️ '}
                                {route.risk_level === 'avoid' && '🚫 '}
                                {route.risk_level}
                              </span>
                              <span className="safety-score">
                                <Shield size={14} /> Safety: {route.safety_score}/100
                              </span>
                            </div>
                            <div className="route-stats">
                              <div className="stat">
                                <Clock size={16} />
                                <span>{route.estimated_time_hours}h</span>
                              </div>
                              <div className="stat">
                                <MapPin size={16} />
                                <span>{route.distance_km} km</span>
                              </div>
                            </div>
                            {route.transport_options && route.transport_options.length > 0 && (
                              <div className="transport-section">
                                <h5><DollarSign size={14} /> Transport Options</h5>
                                <div className="transport-grid">
                                  {route.transport_options.map((opt, oIdx) => (
                                    <div key={oIdx} className="transport-card">
                                      <span className="transport-mode">{opt.mode}</span>
                                      <span className="transport-fare">PKR {Math.round(opt.estimated_fare_pkr)}</span>
                                      <span className="transport-time">{opt.estimated_time_hours}h</span>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}
                            {route.warnings && route.warnings.length > 0 && (
                              <div className="route-warnings">
                                <AlertTriangle size={14} />
                                {route.warnings.map((w, wIdx) => (
                                  <span key={wIdx}>{w}</span>
                                ))}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    )}
                    
                    {msg.data.cost_estimate && (
                      <div className="cost-summary">
                        <h4><DollarSign size={18} /> Cost Range (PKR)</h4>
                        <div className="cost-grid">
                          <div className="cost-item cheapest">
                            <span>Cheapest</span>
                            <strong>PKR {Math.round(msg.data.cost_estimate.cheapest)}</strong>
                          </div>
                          <div className="cost-item average">
                            <span>Average</span>
                            <strong>PKR {Math.round(msg.data.cost_estimate.average)}</strong>
                          </div>
                          <div className="cost-item expensive">
                            <span>Premium</span>
                            <strong>PKR {Math.round(msg.data.cost_estimate.most_expensive)}</strong>
                          </div>
                        </div>
                      </div>
                    )}

                    {msg.data.recommendations && msg.data.recommendations.length > 0 && (
                      <div className="recommendations">
                        <h4>💡 Safety Tips</h4>
                        <ul>
                          {msg.data.recommendations.map((rec, rIdx) => (
                            <li key={rIdx}>{rec}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {msg.data.uncertainty_notes && (
                      <div className="uncertainty-note">
                        <AlertTriangle size={16} />
                        <span>{msg.data.uncertainty_notes}</span>
                      </div>
                    )}
                  </div>
                )}

                {/* Suggested follow-ups */}
                {msg.suggestions && msg.suggestions.length > 0 && (
                  <div className="suggestions">
                    <span className="suggestions-label">
                      <Sparkles size={14} /> Follow-up questions:
                    </span>
                    <div className="suggestions-list">
                      {msg.suggestions.map((suggestion, sIdx) => (
                        <button
                          key={sIdx}
                          className="suggestion-btn"
                          onClick={() => setQuery(suggestion)}
                        >
                          {suggestion}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
            
            {loading && (
              <div className="message assistant loading animate-pulse">
                <div className="message-content">
                  <div className="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                  <span className="typing-text">Analyzing your route...</span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <div className="input-area">
            <div className="input-wrapper">
              <textarea
                ref={inputRef}
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask about your travel plans... (e.g., 'Is it safe to travel from Islamabad to Swat tomorrow?')"
                className="query-input"
                rows="2"
              />
              <div className="input-actions">
                <button 
                  className={`voice-btn ${isListening ? 'listening' : ''}`}
                  onClick={toggleVoiceInput}
                  title={isListening ? 'Stop listening' : 'Voice input'}
                >
                  {isListening ? <MicOff size={18} /> : <Mic size={18} />}
                </button>
                <button 
                  onClick={handleSend} 
                  disabled={loading || !query.trim()}
                  className="send-button"
                >
                  <Send size={20} />
                </button>
              </div>
            </div>
            <div className="input-hints">
              <span>Press Enter to send • Shift+Enter for new line</span>
              {messages.length > 0 && (
                <span className="message-count">{messages.length} messages in this chat</span>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default TravelPlanner
