import axios from 'axios'

// Production URL from environment variable, fallback to localhost for development
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Log API URL in development for debugging
if (import.meta.env.DEV) {
  console.log('API Base URL:', API_BASE_URL)
}

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const travelAPI = {
  // Existing endpoints
  queryTravel: async (data) => {
    const response = await api.post('/api/travel/query', data)
    return response.data
  },

  getRoute: async (origin, destination) => {
    const response = await api.get(`/api/routes/${origin}/${destination}`)
    return response.data
  },

  getSafetyAlerts: async (region) => {
    const params = region ? { region } : {}
    const response = await api.get('/api/safety/alerts', { params })
    return response.data
  },

  createUserProfile: async (profile) => {
    const response = await api.post('/api/user/profile', profile)
    return response.data
  },

  // Trip Planning endpoints
  createTripPlan: async (tripData) => {
    const response = await api.post('/api/trip/plan', tripData)
    return response.data
  },

  quickTripPlan: async (query) => {
    const response = await api.post('/api/trip/quick-plan', { query })
    return response.data
  },

  getDestinations: async () => {
    const response = await api.get('/api/trip/destinations')
    return response.data
  },

  getPackingChecklist: async (destination, durationDays, travelType) => {
    const response = await api.get('/api/trip/packing-checklist', {
      params: { destination, duration_days: durationDays, travel_type: travelType }
    })
    return response.data
  },

  getEmergencyInfo: async (region) => {
    const params = region ? { region } : {}
    const response = await api.get('/api/trip/emergency-info', { params })
    return response.data
  },

  // Additional endpoints
  getRoutes: async () => {
    const response = await api.get('/api/routes')
    return response.data
  },

  getTransportOptions: async (origin, destination) => {
    const params = {}
    if (origin) params.origin = origin
    if (destination) params.destination = destination
    const response = await api.get('/api/transport-options', { params })
    return response.data
  },

  refreshAlerts: async () => {
    const response = await api.post('/api/alerts/refresh')
    return response.data
  },

  getQueryHistory: async (limit = 20) => {
    const response = await api.get('/api/queries/history', { params: { limit } })
    return response.data
  },
}

export default api
