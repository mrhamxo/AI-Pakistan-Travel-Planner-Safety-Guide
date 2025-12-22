# AI Pakistan Travel Guide

> Your AI-powered virtual travel agency for planning safe, budget-friendly trips across Pakistan

---

## What is This?

**AI Pakistan Travel Guide** is a web application that helps you plan complete trips to Pakistani tourist destinations. Think of it as having a knowledgeable travel agent available 24/7 - but powered by AI.

### The Problem

Planning travel in Pakistan, especially to Northern Areas like Hunza, Skardu, or Swat, is challenging:
- How much will it cost? What's a realistic budget?
- Is it safe right now? What about the weather?
- What transport options exist? Buses, flights, private vehicles?
- What should I pack? What about altitude sickness?
- Where should I stay each night? What can I see?

### The Solution

This platform answers all these questions by:
1. **Generating complete trip itineraries** with day-by-day plans
2. **Breaking down costs** across transport, hotels, food, and activities
3. **Checking real-time safety conditions** including weather alerts
4. **Providing specialized advice** for northern areas (altitude, connectivity, fuel)
5. **Creating packing lists** tailored to your destination

---

## Features at a Glance

| Feature | Description |
|---------|-------------|
| **Trip Planning Wizard** | 5-step form to create your perfect trip |
| **AI Itinerary Generator** | Day-by-day plans with activities and timing |
| **Budget Optimizer** | Distributes your budget smartly |
| **Safety Alerts** | Real-time weather and road condition warnings |
| **Bus Schedules** | View transport operators, routes, and departure times |
| **Northern Areas Expert** | Special handling for Hunza, Skardu, etc. |
| **Emergency Guide** | Essential contacts and safety procedures |
| **Packing Checklist** | What to bring based on destination |
| **Real-Time Routes** | Live distance data from OpenRouteService API |

---

## How a Normal Person Uses This Website

### Step 1: Choose How to Plan

**Option A: Use the Trip Wizard (Easiest)**
- Click "Plan Trip" on the homepage
- Select your destination (like Hunza or Swat)
- Tell us who's traveling (solo, family, group)
- Set your budget using the slider
- Choose trip duration and style
- Get your complete plan!

**Option B: Just Ask the AI**
- Go to "AI Chat" 
- Type naturally: "Plan a 5-day family trip to Hunza for 4 people, budget 150,000 PKR"
- The AI understands and creates your plan

### Step 2: Review Your Itinerary

Your generated plan includes:
- **Each day** with where you'll go and what you'll do
- **Transport details** including cost and timing
- **Hotel suggestions** matching your budget
- **Activities** like sightseeing, meals, rest stops
- **Safety tips** specific to each day

### Step 3: Check the Details

Use the tabs to explore:
- **Daily Itinerary**: Expand each day to see activities
- **Cost Breakdown**: See exactly where your money goes
- **Safety & Tips**: Warnings about altitude, weather, roads
- **Packing List**: What to bring (check items off as you pack!)

### Step 4: Before You Travel

- Check **Safety Map** for any new alerts
- Review **Emergency Guide** for contacts
- Download or screenshot your plan for offline access

---

## User Use Cases

### Use Case 1: Solo Budget Traveler

**Scenario**: Ahmed wants to visit Skardu for the first time, alone, with a budget of PKR 50,000.

**How He Uses the Platform**:
1. Selects "Skardu" as destination
2. Chooses "Solo" traveler
3. Sets budget to PKR 50,000
4. Picks "Budget" travel style
5. Gets a 5-day plan with:
   - Cheapest transport (shared van)
   - Budget guesthouses
   - Essential sights only
   - Tips for traveling alone

**AI Recommendations**:
- Take Daewoo to Gilgit, then local transport
- Stay in budget guesthouses (PKR 2000-3000/night)
- Carry extra cash (ATMs rare)
- Share vehicle costs with other travelers

---

### Use Case 2: Family Northern Trip

**Scenario**: The Khan family (2 adults, 2 children) wants a safe, comfortable trip to Hunza with PKR 200,000 budget.

**How They Use the Platform**:
1. Selects "Hunza" as destination
2. Chooses "Family" with 4 people
3. Sets budget to PKR 200,000
4. Picks "Comfort" style
5. Duration: 7 days

**AI Recommendations**:
- Private Hiace (safer, more comfortable for kids)
- Family-friendly hotels with amenities
- Shorter driving segments (kids get tired)
- Rest days included
- No night travel
- Kid-friendly activities
- Extra snacks and entertainment suggestions

---

### Use Case 3: Group Adventure Tour

**Scenario**: 10 friends want an adventure trip to Chitral/Kalash Valley.

**How They Use the Platform**:
1. Selects "Chitral" as destination
2. Chooses "Group" with 10 people
3. Budget: PKR 300,000 total
4. Style: "Adventure"

**AI Recommendations**:
- Rent a Coaster (fits 10+ people)
- Mix of camping and basic hotels
- Trekking activities
- Kalash Valley cultural experience
- Cost split calculation (PKR 30,000 per person)
- Group safety tips

---

### Use Case 4: Disaster/Emergency Replanning

**Scenario**: User planned a trip to Swat, but there's a flood warning.

**How the Platform Helps**:
1. Shows alert on Safety Map (red marker)
2. When user asks about Swat, AI responds:
   - "Warning: Flood alert in Swat region"
   - "Recommendation: Postpone travel by 3-5 days"
   - "Alternative: Consider Naran-Kaghan instead"
3. Provides emergency contacts for the region
4. Suggests what to do if already en route

---

### Use Case 5: Budget-Constrained Traveler

**Scenario**: Student wants to visit Murree but only has PKR 15,000.

**How the Platform Helps**:
1. AI recognizes tight budget
2. Suggests:
   - Public transport (Daewoo bus: PKR 300-500)
   - Budget guesthouse (PKR 2000-3000/night)
   - Street food options
   - Free/cheap activities (Mall Road walking, viewpoints)
3. Cost-saving tips:
   - Travel on weekdays (cheaper hotels)
   - Share transport with others
   - Carry packed lunch
4. Total estimated cost: PKR 12,000-15,000

---

## Screenshots & Flow

```
Homepage                    Trip Wizard                 Itinerary View
┌─────────────────┐        ┌─────────────────┐        ┌─────────────────┐
│ Plan Your Trip  │───────▶│ Step 1: Where?  │        │ Day 1: Departure│
│ ┌─────────────┐ │        │ ○ Hunza         │        │ Day 2: Chilas   │
│ │Popular Dest │ │        │ ● Skardu        │        │ Day 3: Hunza    │
│ │ Hunza Swat  │ │        │ ○ Swat          │───────▶│ Day 4: Explore  │
│ └─────────────┘ │        └─────────────────┘        │ Day 5: Return   │
│                 │                                    │ Cost: PKR 85,000│
│ [Plan Trip Btn] │                                    └─────────────────┘
└─────────────────┘
```

---

## Quick Setup

### Requirements
- Python 3.11+
- Node.js 18+
- Groq API key (free at https://console.groq.com)

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux
pip install -r requirements.txt
echo "GROQ_API_KEY=your_key" > .env
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Access
- **App**: http://localhost:5173
- **API Docs**: http://localhost:8000/docs

---

## Supported Destinations

| Destination | Region | Difficulty | Min Days |
|-------------|--------|------------|----------|
| Hunza | Gilgit-Baltistan | Moderate | 5 |
| Skardu | Gilgit-Baltistan | Challenging | 6 |
| Swat | KPK | Easy | 3 |
| Naran | KPK | Easy | 3 |
| Chitral | KPK | Challenging | 5 |
| Gilgit | Gilgit-Baltistan | Moderate | 4 |
| Murree | Punjab | Easy | 2 |
| Kaghan | KPK | Easy | 3 |

---

## API Overview

| Endpoint | Purpose |
|----------|---------|
| `POST /api/trip/plan` | Generate complete trip plan |
| `POST /api/trip/quick-plan` | Natural language trip planning |
| `POST /api/travel/query` | Ask travel questions |
| `GET /api/safety/alerts` | Get current safety alerts |
| `GET /api/trip/destinations` | List all destinations |
| `GET /api/transport/schedules` | Get bus schedules and operators |
| `GET /api/transport/operators` | List all transport operators |

Full API documentation at `/docs` when running.

---

## Data Sources

| Data | Source | Type |
|------|--------|------|
| **Route Distances** | OpenRouteService API | Real-time (44 cities) |
| **Weather** | OpenWeatherMap API | Real-time |
| **Bus Schedules** | Database | 15 routes, 9 operators |
| **Transport Fares** | Database | Pre-seeded estimates |
| **Safety Scores** | Calculated | Based on weather + time |

---

## Limitations

**Current limitations (v2.0)**:
- Prices are estimates - actual costs may vary by season
- Weather data is current conditions, not forecasts
- No user accounts or saved trips
- No booking/payment integration
- English language only

**Works best for**:
- Planning 2-15 day trips
- Destinations in Northern Pakistan
- Budget range PKR 30,000 - 500,000
- Solo, couple, family, or groups up to 20

---

## Documentation

- [QUICK_START.md](QUICK_START.md) - How to use the platform
- [ARCHITECTURE.md](ARCHITECTURE.md) - Technical architecture
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Full project overview
- [SETUP.md](SETUP.md) - Detailed setup guide
- [DEPLOYMENT.md](DEPLOYMENT.md) - Deploy to cloud (Render)

---

## 🚀 Deploy to Cloud (Free)

This project is configured for **one-click deployment** to Render (100% free tier).

### Quick Deploy

1. Push code to GitHub
2. Go to [Render Dashboard](https://dashboard.render.com)
3. Click **New** → **Blueprint**
4. Connect your repo (auto-detects `render.yaml`)
5. Set `GROQ_API_KEY` environment variable
6. Done! Your app is live.

**Live URLs after deployment:**
- Frontend: `https://pakistan-travel-guide.onrender.com`
- Backend API: `https://pakistan-travel-api.onrender.com`
- API Docs: `https://pakistan-travel-api.onrender.com/docs`

📖 See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

---

## Future Plans

- [ ] User accounts & saved trips
- [ ] Hotel booking integration
- [ ] Mobile app (React Native)
- [ ] Urdu language support
- [ ] Offline mode (PWA)
- [ ] Real-time price updates

---

## Contributing

This is an open-source project. Contributions welcome!

Areas that need help:
- Adding more destinations
- Improving cost estimates
- Adding more transport options
- Urdu translation
- Mobile UI improvements

---

## License

MIT License - Free to use, modify, and distribute.

---

**Made for travelers who want to explore Pakistan safely and smartly.**
