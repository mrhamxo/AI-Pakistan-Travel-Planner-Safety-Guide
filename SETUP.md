# Setup Guide - AI Pakistan Travel Guide

## Prerequisites

- **Python 3.11+** (check with `python --version`)
- **Node.js 18+** (check with `node --version`)
- **npm** (comes with Node.js)

---

## Quick Setup (5 Minutes)

### 1. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (see API Keys section below)
# Then start the server
uvicorn app.main:app --reload
```

**Expected output**: `Uvicorn running on http://127.0.0.1:8000`

### 2. Frontend Setup

```bash
# Open new terminal
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

**Expected output**: `Local: http://localhost:5173`

### 3. Open in Browser

Navigate to: **http://localhost:5173**

---

## API Keys

### Required: Groq API Key

The AI features require a Groq API key (free tier available).

1. Go to https://console.groq.com
2. Create an account
3. Generate an API key
4. Add to `backend/.env`:
   ```
   GROQ_API_KEY=gsk_your_key_here
   ```

### Optional: OpenWeatherMap API Key

For weather-based safety alerts:

1. Go to https://openweathermap.org/api
2. Sign up for free
3. Get your API key
4. Add to `backend/.env`:
   ```
   WEATHER_API_KEY=your_key_here
   ```

### Recommended: OpenRouteService API Key

For real-time route distances (highly recommended):

1. Go to https://openrouteservice.org/dev/#/signup
2. Create account
3. Get API key
4. Add to `backend/.env`:
   ```
   OPENROUTE_API_KEY=your_key_here
   ```

**Note**: Without this key, the app uses fallback distances (192 pre-configured routes). With the key, you get real-time data for 44 Pakistani cities.

---

## Complete .env Template

Create `backend/.env` with:

```env
# Required
GROQ_API_KEY=your_groq_api_key

# Optional but recommended
WEATHER_API_KEY=your_openweathermap_key

# Optional
OPENROUTE_API_KEY=your_openrouteservice_key
GROQ_MODEL=llama-3.3-70b-versatile

# Logging
LOG_LEVEL=INFO

# CORS (adjust if needed)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

---

## Verify Installation

1. **Check Backend API**:
   - Open http://localhost:8000/docs
   - You should see Swagger API documentation

2. **Check Frontend**:
   - Open http://localhost:5173
   - You should see the homepage with "Plan Trip" button

3. **Test Trip Planning**:
   - Click "Plan Trip"
   - Select a destination
   - Complete the wizard
   - If AI is configured correctly, you'll get a trip plan

4. **Test AI Chat**:
   - Go to "AI Chat"
   - Type "Plan a 3-day trip to Murree"
   - You should get an AI response

5. **Check Bus Schedules**:
   - Go to "Bus Schedules"
   - You should see 15 routes from 9 operators
   - Includes Daewoo, Faisal Movers, NATCO, etc.

---

## Common Issues

### "AI is not configured"

**Cause**: Missing or invalid GROQ_API_KEY

**Fix**:
1. Check `backend/.env` exists
2. Verify your API key is correct
3. Restart the backend server

### "Cannot connect to server"

**Cause**: Backend not running

**Fix**:
1. Ensure backend is running (check for "Uvicorn running...")
2. Check the port: should be 8000
3. Check CORS settings if frontend is on different port

### "Module not found"

**Cause**: Dependencies not installed or venv not activated

**Fix**:
```bash
# Make sure venv is activated
venv\Scripts\activate  # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### "Port already in use"

**Cause**: Another process using port 8000 or 5173

**Fix**:
```bash
# Use different ports
uvicorn app.main:app --reload --port 8001
# Update frontend to use new port if needed
```

### Weather features not working

**Cause**: Missing WEATHER_API_KEY

**Fix**: Add OpenWeatherMap API key to `.env` (optional feature)

---

## Running in Production

For production deployment:

```bash
# Backend
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Frontend (build)
npm run build
# Serve the dist folder with a web server
```

---

## Project Structure

```
ai-pakistan-travel-guide/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── database.py          # Database setup
│   │   ├── logging_config.py    # Logging configuration
│   │   ├── ai/                  # AI orchestration
│   │   ├── models/              # SQLAlchemy models
│   │   ├── schemas/             # Pydantic schemas
│   │   └── services/            # Business logic
│   ├── requirements.txt
│   └── .env                     # Your API keys (create this)
│
├── frontend/
│   ├── src/
│   │   ├── pages/              # React pages
│   │   │   ├── Home.jsx
│   │   │   ├── TripWizard.jsx
│   │   │   ├── TravelPlanner.jsx
│   │   │   ├── TransportSchedules.jsx  # Bus schedules (NEW)
│   │   │   ├── SafetyMap.jsx
│   │   │   └── EmergencyGuide.jsx
│   │   ├── services/           # API client
│   │   └── App.jsx             # Main app
│   └── package.json
│
└── docs/
    ├── README.md
    ├── ARCHITECTURE.md
    ├── PROJECT_SUMMARY.md
    └── QUICK_START.md
```

---

## Helpful Commands

```bash
# Backend
cd backend
uvicorn app.main:app --reload          # Start with auto-reload
uvicorn app.main:app --reload --port 8001  # Different port

# Frontend
cd frontend
npm run dev                             # Start dev server
npm run build                           # Production build
npm run preview                         # Preview production build

# Database
# Database is auto-created on first run
# Located at: backend/travel_safety.db
```

---

## Need Help?

- Check [QUICK_START.md](QUICK_START.md) for usage guide
- Check [ARCHITECTURE.md](ARCHITECTURE.md) for technical details
- API docs available at http://localhost:8000/docs

---

**Happy coding!**
