import React from 'react'
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom'
import { 
  Mail, Github, Linkedin, Twitter, MapPin, Phone, Globe, 
  Heart, Shield, Map, MessageSquare, Compass, Star
} from 'lucide-react'
import Home from './pages/Home'
import TravelPlanner from './pages/TravelPlanner'
import TripWizard from './pages/TripWizard'
import ItineraryView from './pages/ItineraryView'
import SafetyMap from './pages/SafetyMap'
import EmergencyGuide from './pages/EmergencyGuide'
import OfflineDownloads from './pages/OfflineDownloads'
import TransportSchedules from './pages/TransportSchedules'
import './App.css'

function NavLink({ to, children }) {
  const location = useLocation()
  const isActive = location.pathname === to
  
  return (
    <Link to={to} className={`nav-link ${isActive ? 'active' : ''}`}>
      {children}
    </Link>
  )
}

function App() {
  return (
    <Router>
      <div className="app">
        <nav className="navbar">
          <div className="nav-container">
            <Link to="/" className="nav-logo">
              🇵🇰 AI Pakistan Travel Guide
            </Link>
            <div className="nav-menu">
              <NavLink to="/">Home</NavLink>
              <NavLink to="/trip-wizard">Plan Trip</NavLink>
              <NavLink to="/planner">AI Chat</NavLink>
              <NavLink to="/transport">Bus Schedules</NavLink>
              <NavLink to="/map">Safety Map</NavLink>
              <NavLink to="/emergency">Emergency</NavLink>
            </div>
          </div>
        </nav>

        <main className="main-content">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/trip-wizard" element={<TripWizard />} />
            <Route path="/itinerary" element={<ItineraryView />} />
            <Route path="/planner" element={<TravelPlanner />} />
            <Route path="/transport" element={<TransportSchedules />} />
            <Route path="/map" element={<SafetyMap />} />
            <Route path="/emergency" element={<EmergencyGuide />} />
            <Route path="/downloads" element={<OfflineDownloads />} />
          </Routes>
        </main>

        <footer className="footer">
          <div className="footer-container">
            {/* Brand Section */}
            <div className="footer-brand">
              <Link to="/" className="footer-logo">
                🇵🇰 AI Pakistan Travel Guide
              </Link>
              <p className="footer-tagline">
                Your AI-powered virtual travel agency for exploring the beauty of Pakistan safely and affordably.
              </p>
              <div className="footer-social">
                <a href="mailto:mr.hamxa942@gmail.com" className="social-link" title="Email">
                  <Mail size={20} />
                </a>
                <a href="https://github.com/mrhamxo" target="_blank" rel="noopener noreferrer" className="social-link" title="GitHub">
                  <Github size={20} />
                </a>
                <a href="https://www.linkedin.com/in/muhammad-hamza-khattak/" target="_blank" rel="noopener noreferrer" className="social-link" title="LinkedIn">
                  <Linkedin size={20} />
                </a>
              </div>
            </div>

            {/* Quick Links */}
            <div className="footer-section">
              <h4 className="footer-heading">Quick Links</h4>
              <ul className="footer-links">
                <li><Link to="/"><Compass size={14} /> Home</Link></li>
                <li><Link to="/trip-wizard"><Star size={14} /> Plan Trip</Link></li>
                <li><Link to="/planner"><MessageSquare size={14} /> AI Chat</Link></li>
                <li><Link to="/map"><Map size={14} /> Safety Map</Link></li>
                <li><Link to="/emergency"><Shield size={14} /> Emergency Guide</Link></li>
              </ul>
            </div>

            {/* Popular Destinations */}
            <div className="footer-section">
              <h4 className="footer-heading">Popular Destinations</h4>
              <ul className="footer-links destinations">
                <li><MapPin size={14} /> Hunza Valley</li>
                <li><MapPin size={14} /> Skardu</li>
                <li><MapPin size={14} /> Swat Valley</li>
                <li><MapPin size={14} /> Fairy Meadows</li>
                <li><MapPin size={14} /> Naran Kaghan</li>
              </ul>
            </div>

            {/* Contact Info */}
            <div className="footer-section">
              <h4 className="footer-heading">Contact</h4>
              <ul className="footer-contact">
                <li>
                  <Mail size={14} />
                  <a href="mailto:mr.hamxa942@gmail.com">mr.hamxa942@gmail.com</a>
                </li>
                <li>
                  <MapPin size={14} />
                  <span>Islamabad, Pakistan</span>
                </li>
                <li>
                  <Globe size={14} />
                  <span>Available 24/7 for AI Assistance</span>
                </li>
              </ul>
            </div>
          </div>

          {/* Bottom Bar */}
          <div className="footer-bottom">
            <div className="footer-bottom-content">
              <p className="copyright">
                © {new Date().getFullYear()} AI Pakistan Travel Guide. Made with <Heart size={14} className="heart-icon" /> by <a href="mailto:mr.hamxa942@gmail.com">Hamza</a>
              </p>
              <p className="footer-disclaimer">
                ⚠️ Always verify travel information locally. Prices and conditions may vary by season.
              </p>
            </div>
          </div>
        </footer>
      </div>
    </Router>
  )
}

export default App
