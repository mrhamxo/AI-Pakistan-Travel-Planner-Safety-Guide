# Deployment Guide - AI Pakistan Travel Guide

Deploy your app for **FREE** without credit card using **Vercel** (frontend) + **Koyeb** (backend).

---

## 🆓 100% Free, No Credit Card Required

| Platform | For | Cost | Credit Card |
|----------|-----|------|-------------|
| **Vercel** | React Frontend | Free | ❌ Not required |
| **Koyeb** | Python Backend | Free | ❌ Not required |
| **Groq** | AI/LLM API | Free | ❌ Not required |

---

## 🌐 Live Deployment URLs

| Service | URL |
|---------|-----|
| **Frontend** | https://ai-pakistan-travel-planner-safety-g.vercel.app |
| **Backend API** | https://productive-ludovika-hamza-student-beee9ced.koyeb.app |
| **API Docs** | https://productive-ludovika-hamza-student-beee9ced.koyeb.app/docs |

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
   | `VITE_API_URL` | `https://your-backend-url.koyeb.app` |

5. Click **"Deploy"**

---

## Step 3: Deploy Backend on Koyeb

### 3.1 Create Koyeb Account
1. Go to https://www.koyeb.com
2. Click **"Get started for free"**
3. Sign up with **GitHub** (no credit card!)

### 3.2 Create New App
1. Click **"Create App"**
2. Choose **"GitHub"** as deployment source
3. Select your repository

### 3.3 Configure Settings
| Setting | Value |
|---------|-------|
| **Branch** | `main` |
| **Builder** | Buildpack |
| **Work directory** | `backend` |
| **Run command** | `uvicorn app.main:app --host 0.0.0.0 --port 8000` |
| **Port** | `8000` |

### 3.4 Add Environment Variables (Runtime)
| Key | Value |
|-----|-------|
| `GROQ_API_KEY` | Your Groq API key |
| `CORS_ALLOW_ALL` | `true` |

### 3.5 Deploy
Click **"Deploy"** and wait for build to complete.

---

## Step 4: Connect Frontend to Backend

1. Copy your Koyeb backend URL
2. Go to Vercel → Your project → Settings → Environment Variables
3. Update `VITE_API_URL` with your Koyeb URL
4. Redeploy frontend

---

## Environment Variables Reference

### Frontend (Vercel)
| Variable | Value |
|----------|-------|
| `VITE_API_URL` | Your Koyeb backend URL |

### Backend (Koyeb)
| Variable | Required | Value |
|----------|----------|-------|
| `GROQ_API_KEY` | ✅ Yes | Your Groq API key |
| `CORS_ALLOW_ALL` | ✅ Yes | `true` |
| `WEATHER_API_KEY` | ❌ No | OpenWeatherMap key (optional) |

---

## Troubleshooting

### "AI is not configured" Error
- Add `GROQ_API_KEY` environment variable to backend

### CORS Errors
- Ensure `CORS_ALLOW_ALL=true` is set in Koyeb

### Bus Schedules Not Loading
- Database auto-seeds on startup
- Wait a few seconds after first deploy

### Build Fails on Koyeb
- Ensure `runtime.txt` has `python-3.11.4`
- Check `requirements.txt` has pinned versions

---

## Free Tier Limits

### Vercel
- ✅ Unlimited static sites
- ✅ 100 GB bandwidth/month

### Koyeb
- ✅ Free tier available
- ✅ Auto-sleeps after inactivity (wakes on request)

### Groq
- ✅ 30 requests/minute
- ✅ Free tier available

---

**Total Cost: $0 | Credit Card: Not Required | Deploy Time: ~15 minutes**
