# Deployment Guide - AI Pakistan Travel Guide

Deploy your app for **FREE** without credit card using **Vercel** (frontend) + **Deployra** (backend).

---

## 🆓 100% Free, No Credit Card Required

| Platform | For | Cost | Credit Card |
|----------|-----|------|-------------|
| **Vercel** | React Frontend | Free | ❌ Not required |
| **Deployra** | Python Backend | Free | ❌ Not required |
| **Groq** | AI/LLM API | Free | ❌ Not required |

---

## 🌐 Live Deployment URLs

| Service | URL |
|---------|-----|
| **Frontend** | https://ai-pakistan-travel-planner-safety-g.vercel.app |
| **Backend API** | https://your-app.deployra.app (after deployment) |
| **API Docs** | https://your-app.deployra.app/docs |

---

## Step 1: Get Your API Keys (Free)

### Groq API Key (Required for AI)
1. Go to https://console.groq.com
2. Sign up with Google/GitHub
3. Click "API Keys" → "Create API Key"
4. Copy and save your key: `gsk_xxxxx...`

---

## Step 2: Deploy Frontend on Vercel

### 2.1 Create Vercel Account
1. Go to https://vercel.com
2. Click **"Sign Up"** → **"Continue with GitHub"**
3. Authorize Vercel (no credit card needed!)

### 2.2 Deploy Frontend
1. Click **"Add New..."** → **"Project"**
2. Import your GitHub repository
3. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

4. Add Environment Variable:
   | Key | Value |
   |-----|-------|
   | `VITE_API_URL` | `https://your-backend-url.deployra.app` (update after backend deployment) |

5. Click **"Deploy"**

---

## Step 3: Deploy Backend on Deployra

### 3.1 Create Deployra Account
1. Go to https://deployra.com
2. Click **"Sign Up"** or **"Get Started"**
3. Sign up with **GitHub** (no credit card required!)

### 3.2 Create New Project
1. After login, click **"New Project"**
2. Enter project name: `ai-pakistan-travel-backend`
3. Click **"Create Project"**

### 3.3 Connect GitHub Repository
1. Click **"Connect GitHub Repository"**
2. Authorize Deployra to access your GitHub
3. Select your repository: `AI-Pakistan-Travel-Planner-Safety-Guide`

### 3.4 Create New Service
1. Click **"New Service"** within your project
2. Select **"Web Service"** as service type
3. Choose your connected repository

### 3.5 Configure Deployment Settings

| Setting | Value |
|---------|-------|
| **Root Directory** | `backend` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| **Python Version** | 3.11 (select from dropdown if available) |

> **Note:** Deployra uses `$PORT` environment variable. The Procfile is already configured for this.

### 3.6 Add Environment Variables

Click on **"Environment Variables"** and add these:

| Key | Value | Type |
|-----|-------|------|
| `GROQ_API_KEY` | Your Groq API key (gsk_xxx...) | Runtime |
| `CORS_ALLOW_ALL` | `true` | Runtime |

### 3.7 Deploy
1. Click **"Deploy"** button
2. Wait for the build to complete (may take 2-5 minutes)
3. Once deployed, you'll get a URL like: `https://your-app.deployra.app`

### 3.8 Verify Deployment
- Visit: `https://your-app.deployra.app/health`
- Should return: `{"status": "healthy"}`
- API Docs: `https://your-app.deployra.app/docs`

---

## Step 4: Connect Frontend to Backend

1. Copy your Deployra backend URL
2. Go to **Vercel** → Your project → **Settings** → **Environment Variables**
3. Update `VITE_API_URL` with your Deployra URL (e.g., `https://ai-pakistan-backend.deployra.app`)
4. Go to **Deployments** tab → Click **"Redeploy"** (or push a new commit)

---

## Environment Variables Reference

### Frontend (Vercel)
| Variable | Value |
|----------|-------|
| `VITE_API_URL` | Your Deployra backend URL |

### Backend (Deployra)
| Variable | Required | Value |
|----------|----------|-------|
| `GROQ_API_KEY` | ✅ Yes | Your Groq API key |
| `CORS_ALLOW_ALL` | ✅ Yes | `true` |
| `WEATHER_API_KEY` | ❌ No | OpenWeatherMap key (optional) |

---

## Files Required for Deployment

The following files are already configured in your `backend/` folder:

```
backend/
├── app/
│   ├── main.py              # FastAPI application
│   ├── database.py          # Database setup (auto-seeds)
│   └── ...
├── requirements.txt         # Python dependencies (pinned versions)
├── runtime.txt              # Python version: python-3.11.4
└── Procfile                 # Start command for Deployra
```

---

## Troubleshooting

### Build Fails - Python Version Issue
- Ensure `runtime.txt` contains: `python-3.11.4`
- If Deployra doesn't read runtime.txt, select Python 3.11 in settings

### "AI is not configured" Error
- Add `GROQ_API_KEY` environment variable
- Make sure it's set as **Runtime** variable

### CORS Errors
- Ensure `CORS_ALLOW_ALL=true` is set in environment variables
- This allows frontend to communicate with backend

### Bus Schedules Not Loading
- Database auto-seeds on first startup
- Wait 30 seconds after first deploy for initialization

### Port Binding Issues
If you see port errors, check your Procfile has:
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Frontend Can't Connect to Backend
1. Verify `VITE_API_URL` is correct in Vercel
2. Check backend is running: `https://your-backend-url/health`
3. Redeploy frontend after changing environment variables

---

## Free Tier Limits

### Vercel (Frontend)
- ✅ Unlimited static sites
- ✅ 100 GB bandwidth/month
- ✅ Automatic HTTPS

### Deployra (Backend)
- ✅ Free tier available
- ✅ Auto-sleeps after inactivity (wakes on request)
- ✅ Custom subdomains

### Groq (AI)
- ✅ 30 requests/minute
- ✅ Free tier available

---

## Quick Checklist

- [ ] GitHub repository pushed with latest code
- [ ] Vercel account created
- [ ] Deployra account created
- [ ] Groq API key obtained
- [ ] Frontend deployed on Vercel
- [ ] Backend deployed on Deployra
- [ ] `GROQ_API_KEY` set in Deployra
- [ ] `CORS_ALLOW_ALL=true` set in Deployra
- [ ] `VITE_API_URL` set in Vercel with Deployra URL
- [ ] Frontend redeployed after setting URL
- [ ] Tested: `/health` endpoint works
- [ ] Tested: Full app works

---

**Total Cost: $0 | Credit Card: Not Required | Deploy Time: ~15-20 minutes**
