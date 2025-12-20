# Quick Start Guide

Welcome to the **AI Pakistan Travel Guide** - your virtual travel agency for planning trips across Pakistan!

---

## What This Platform Does

This website helps you:
- **Plan complete trips** to destinations like Hunza, Swat, Skardu, and more
- **Get day-by-day itineraries** with activities, hotels, and transport
- **Know your costs upfront** with detailed budget breakdowns
- **Stay safe** with real-time weather alerts and safety advice
- **Pack right** with customized packing checklists

---

## How to Use (For Everyone)

### Option 1: Plan a Trip (Recommended)

1. **Go to the homepage** and click **"Plan Trip"** or select a destination
2. **Answer 5 simple questions**:
   - Where do you want to go? (e.g., Hunza)
   - Who's traveling? (solo, family, group)
   - What's your budget? (use the slider)
   - How many days? (2-15 days)
   - What style? (budget, comfort, adventure)
3. **Click "Generate My Trip Plan"**
4. **Wait 10-30 seconds** while the AI creates your itinerary
5. **Explore your plan**:
   - Day-by-day schedule
   - Cost breakdown
   - Safety tips
   - Packing checklist

### Option 2: Ask a Question (AI Chat)

1. Go to **"AI Chat"** in the menu
2. Type your question in natural language, for example:
   - "Is it safe to travel from Islamabad to Swat tomorrow?"
   - "What's the cheapest way to get to Murree?"
   - "Family trip to Hunza - what should we know?"
3. Get an AI-powered response with routes, costs, and safety info

### Option 3: Check Bus Schedules

1. Go to **"Bus Schedules"** in the menu
2. Browse all available operators:
   - 🚌 Daewoo Express
   - 🚐 Faisal Movers
   - 🏔️ NATCO (Northern Areas)
   - And more...
3. See departure times for each route
4. Use the search to find specific operators

### Option 4: Check Safety Alerts

1. Go to **"Safety Map"** in the menu
2. See color-coded alerts on the map:
   - 🟢 Green = Low risk
   - 🟡 Yellow = Medium risk
   - 🔴 Red = High risk
3. Click on markers for details

---

## Example Queries That Work Well

### Trip Planning
- "Plan a 5-day family trip to Hunza under 150k"
- "Solo budget trip to Skardu for 7 days"
- "Group tour to Swat for 10 people"
- "Luxury honeymoon in Gilgit-Baltistan"

### Safety Questions
- "Is it safe to travel to Swat in monsoon?"
- "Night travel from Lahore to Islamabad - safe?"
- "Road conditions on Karakoram Highway"

### Cost Questions
- "How much does Islamabad to Gilgit cost?"
- "Budget breakdown for Naran trip"
- "Cheapest transport to Murree"

---

## Running the Application Locally

### Prerequisites
- Python 3.11 or higher
- Node.js 18 or higher
- A Groq API key (free at https://console.groq.com)

### Step 1: Start the Backend

```bash
# Open terminal/command prompt
cd backend

# Create virtual environment (first time only)
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies (first time only)
pip install -r requirements.txt

# Create .env file with your API key
echo "GROQ_API_KEY=your_api_key_here" > .env

# Start the server
uvicorn app.main:app --reload
```

You should see: `Uvicorn running on http://127.0.0.1:8000`

### Step 2: Start the Frontend

```bash
# Open another terminal
cd frontend

# Install dependencies (first time only)
npm install

# Start the development server
npm run dev
```

You should see: `Local: http://localhost:5173`

### Step 3: Open in Browser

Go to: **http://localhost:5173**

---

## Common Issues & Solutions

### "AI is not configured"
**Problem**: You see a 503 error when asking questions
**Solution**: 
1. Make sure you have a `.env` file in the `backend/` folder
2. Add your Groq API key: `GROQ_API_KEY=your_key_here`
3. Restart the backend server

### "Cannot connect to server"
**Problem**: Frontend shows connection errors
**Solution**:
1. Make sure the backend is running (check for "Uvicorn running...")
2. Check that you're on the right ports (backend: 8000, frontend: 5173)

### "Weather features limited"
**Problem**: No weather alerts showing
**Solution**: 
1. Add OpenWeatherMap API key to `.env`
2. Get a free key at https://openweathermap.org/api
3. Add to `.env`: `WEATHER_API_KEY=your_key`

### Trip plan takes too long
**Problem**: Waiting more than 60 seconds
**Solution**:
1. This is normal for complex trips - AI needs time
2. If it fails, try a simpler request first
3. Check your internet connection

---

## Getting API Keys (Free)

### Groq API Key (Required)
1. Go to https://console.groq.com
2. Sign up for a free account
3. Create an API key
4. Copy it to your `.env` file

### OpenWeatherMap API Key (Optional)
1. Go to https://openweathermap.org/api
2. Sign up for free
3. Get your API key
4. Add to `.env` file

---

## Tips for Best Results

1. **Be specific**: "5-day family trip to Hunza" works better than "trip to north"
2. **Include budget**: Helps AI optimize your itinerary
3. **Mention group type**: Family trips get different advice than solo
4. **Check alerts before travel**: Weather can change rapidly in mountains
5. **Verify locally**: Prices and conditions may vary from estimates

---

## Need Help?

- Check **Emergency Guide** for emergency contacts
- See **Architecture** docs for technical details
- API documentation at `http://localhost:8000/docs`

---

**Happy traveling! Stay safe on the roads.**
