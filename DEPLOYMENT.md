# Deployment Guide - AI Pakistan Travel Guide

Deploy your app for **FREE** without credit card using **Vercel** (frontend) + **PythonAnywhere** (backend).

---

## 🆓 100% Free, No Credit Card Required

| Platform | For | Cost | Credit Card |
|----------|-----|------|-------------|
| **Vercel** | React Frontend | Free | ❌ Not required |
| **PythonAnywhere** | Python Backend | Free | ❌ Not required |
| **Groq** | AI/LLM API | Free | ❌ Not required* |

*Note: Check Groq's current policy. Alternative: Use Google AI Studio (Gemini) - always free without CC.

---

## Step 1: Get Your API Keys (Free)

### Groq API Key (Required for AI)
1. Go to https://console.groq.com
2. Sign up with Google/GitHub
3. Click "API Keys" → "Create API Key"
4. Copy and save your key: `gsk_xxxxx...`

### Alternative: Google Gemini (If Groq needs CC)
1. Go to https://aistudio.google.com
2. Sign in with Google account
3. Click "Get API Key" → "Create API key"
4. Save your key

---

## Step 2: Deploy Backend on PythonAnywhere

### 2.1 Create Account
1. Go to https://www.pythonanywhere.com
2. Click **"Start running Python online in less than a minute!"**
3. Choose **"Create a Beginner account"** (FREE)
4. Sign up with email (no credit card!)

### 2.2 Upload Your Code

**Option A: Using Git (Recommended)**
1. Open a **Bash console** in PythonAnywhere
2. Run:
```bash
git clone https://github.com/YOUR_USERNAME/AI-Pakistan-Travel-Planner-Safety-Guide.git
cd AI-Pakistan-Travel-Planner-Safety-Guide/backend
pip3 install --user -r requirements.txt
```

**Option B: Manual Upload**
1. Go to **Files** tab
2. Upload the `backend` folder contents

### 2.3 Create Web App
1. Go to **Web** tab
2. Click **"Add a new web app"**
3. Choose **"Manual configuration"**
4. Select **Python 3.10** (or latest available)

### 2.4 Configure WSGI
1. Click on the **WSGI configuration file** link
2. Delete all content and paste:

```python
import sys
import os

# Add your project directory to the path
project_home = '/home/YOUR_USERNAME/AI-Pakistan-Travel-Planner-Safety-Guide/backend'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variables
os.environ['GROQ_API_KEY'] = 'your_groq_api_key_here'
os.environ['CORS_ALLOW_ALL'] = 'true'

# Import the FastAPI app
from app.main import app

# PythonAnywhere uses WSGI, so we need an adapter
from fastapi.middleware.wsgi import WSGIMiddleware

# This won't work directly - we need ASGI
# For PythonAnywhere, we'll use a workaround
```

**⚠️ Important:** PythonAnywhere free tier has limitations with FastAPI. See alternative below.

### 2.5 Alternative: Use Flask Wrapper

Since PythonAnywhere free tier works best with WSGI (Flask), let me provide a simpler solution...

---

## 🌟 EASIER OPTION: Vercel for Everything

Actually, **Vercel can host both frontend AND backend** as serverless functions! This is easier.

---

## Step 2 (Revised): Deploy Everything on Vercel

### 2.1 Create Vercel Account
1. Go to https://vercel.com
2. Click **"Sign Up"**
3. Choose **"Continue with GitHub"**
4. Authorize Vercel (no credit card needed!)

### 2.2 Push Code to GitHub
```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

### 2.3 Deploy Frontend
1. In Vercel dashboard, click **"Add New..."** → **"Project"**
2. Import your GitHub repository
3. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

4. Add Environment Variable:
   - Key: `VITE_API_URL`
   - Value: `https://your-backend-url` (we'll update this later)

5. Click **"Deploy"**

### 2.4 Your Frontend URL
After deployment, you'll get a URL like:
`https://ai-pakistan-travel-frontend.vercel.app`

---

## Step 3: Deploy Backend (Options)

### Option A: Railway (Recommended - Easy)
Railway gives **$5 free credit/month** - enough for hobby projects.

1. Go to https://railway.app
2. Sign up with GitHub
3. Click **"New Project"** → **"Deploy from GitHub repo"**
4. Select your repository
5. Set **Root Directory**: `backend`
6. Add environment variables:
   - `GROQ_API_KEY` = your key
   - `CORS_ALLOW_ALL` = true
7. Deploy!

### Option B: Koyeb (Free, No CC)
1. Go to https://www.koyeb.com
2. Sign up (no credit card)
3. Create new app from GitHub
4. Configure for Python/FastAPI

### Option C: Deta Space (Free, No CC)
1. Go to https://deta.space
2. Sign up for free
3. Install Deta CLI
4. Deploy your Python app

---

## Step 4: Connect Frontend to Backend

After backend is deployed, update your frontend:

1. Go to Vercel dashboard → Your project → Settings → Environment Variables
2. Update `VITE_API_URL` to your backend URL
3. Redeploy frontend

---

## Quick Reference: Environment Variables

### Frontend (Vercel)
| Variable | Value |
|----------|-------|
| `VITE_API_URL` | Your backend URL (e.g., `https://your-app.railway.app`) |

### Backend (Railway/Koyeb)
| Variable | Required | Value |
|----------|----------|-------|
| `GROQ_API_KEY` | ✅ Yes | Your Groq API key |
| `CORS_ALLOW_ALL` | ✅ Yes | `true` |
| `WEATHER_API_KEY` | ❌ No | OpenWeatherMap key (optional) |
| `OPENROUTE_API_KEY` | ❌ No | OpenRouteService key (optional) |

---

## Recommended Stack (All Free, No CC)

| Component | Platform | Notes |
|-----------|----------|-------|
| **Frontend** | Vercel | Instant deploy from GitHub |
| **Backend** | Railway | $5 free credit, easy Python support |
| **AI** | Groq | Fast LLM inference |

---

## Testing Your Deployment

1. **Frontend**: Visit your Vercel URL
2. **Backend API**: Visit `https://your-backend-url/docs`
3. **Health Check**: Visit `https://your-backend-url/health`

---

## Troubleshooting

### "AI is not configured" Error
- Add `GROQ_API_KEY` environment variable to backend

### CORS Errors
- Add `CORS_ALLOW_ALL=true` to backend environment variables

### Frontend Can't Connect to Backend
- Check `VITE_API_URL` is set correctly in Vercel
- Make sure backend is running (check `/health` endpoint)

### Build Fails
- Check build logs for missing dependencies
- Ensure `requirements.txt` and `package.json` are correct

---

## Free Tier Limits

### Vercel (Frontend)
- ✅ Unlimited static sites
- ✅ 100 GB bandwidth/month
- ✅ Automatic HTTPS

### Railway (Backend)
- ✅ $5 free credit/month
- ✅ 500 hours execution time
- ✅ Sleeps after inactivity (wakes on request)

### Groq (AI)
- ✅ 30 requests/minute
- ✅ Free tier available

---

## Summary

1. **Sign up** for Vercel + Railway (both free, no CC)
2. **Get** Groq API key
3. **Deploy** frontend to Vercel
4. **Deploy** backend to Railway
5. **Connect** them via environment variables
6. **Done!** 🎉

---

**Total Cost: $0**
**Credit Card Required: No**
**Time to Deploy: ~15 minutes**
