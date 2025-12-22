# Deployment Guide - AI Pakistan Travel Guide

This guide covers deploying the AI Pakistan Travel Guide to **Render** (100% free tier).

---

## Quick Deploy to Render (Recommended)

### Option 1: One-Click Blueprint Deploy

1. **Push your code to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
   git push -u origin main
   ```

2. **Go to Render Dashboard**
   - Visit: https://dashboard.render.com
   - Sign up/login with GitHub

3. **Deploy Blueprint**
   - Click **"New"** → **"Blueprint"**
   - Connect your GitHub repository
   - Render will detect `render.yaml` automatically
   - Click **"Apply"**

4. **Set Environment Variables**
   After deployment, go to each service and set:
   
   **Backend (pakistan-travel-api):**
   - `GROQ_API_KEY` = Your Groq API key (required)
   - `WEATHER_API_KEY` = Your OpenWeatherMap key (optional)
   - `OPENROUTE_API_KEY` = Your OpenRouteService key (optional)

5. **Wait for deployment** (5-10 minutes)

6. **Access your app:**
   - Frontend: `https://pakistan-travel-guide.onrender.com`
   - Backend API: `https://pakistan-travel-api.onrender.com`
   - API Docs: `https://pakistan-travel-api.onrender.com/docs`

---

### Option 2: Manual Deploy (Step by Step)

#### Step 1: Deploy Backend

1. Go to https://dashboard.render.com
2. Click **"New"** → **"Web Service"**
3. Connect your GitHub repo
4. Configure:
   - **Name**: `pakistan-travel-api`
   - **Region**: Singapore (closest to Pakistan)
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free

5. Add Environment Variables:
   | Key | Value |
   |-----|-------|
   | `GROQ_API_KEY` | Your Groq API key |
   | `WEATHER_API_KEY` | (Optional) OpenWeatherMap key |
   | `CORS_ORIGINS` | `https://pakistan-travel-guide.onrender.com` |

6. Click **"Create Web Service"**

#### Step 2: Deploy Frontend

1. Click **"New"** → **"Static Site"**
2. Connect the same GitHub repo
3. Configure:
   - **Name**: `pakistan-travel-guide`
   - **Branch**: `main`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`

4. Add Environment Variable:
   | Key | Value |
   |-----|-------|
   | `VITE_API_URL` | `https://pakistan-travel-api.onrender.com` |

5. Click **"Create Static Site"**

---

## Getting Free API Keys

### 1. Groq API Key (Required)
- Go to: https://console.groq.com
- Sign up for free
- Generate API key
- Free tier: 30 requests/minute

### 2. OpenWeatherMap Key (Optional)
- Go to: https://openweathermap.org/api
- Sign up for free
- Get API key from dashboard
- Free tier: 1000 calls/day

### 3. OpenRouteService Key (Optional)
- Go to: https://openrouteservice.org/dev/#/signup
- Create account
- Get API key
- Free tier: 2000 requests/day

---

## Understanding Render Free Tier

### Limits
- **Web Services**: Spin down after 15 minutes of inactivity
- **Cold Start**: First request after sleep takes 30-60 seconds
- **Build Time**: 400 hours/month (plenty for this app)
- **Bandwidth**: 100 GB/month

### Tips for Free Tier
1. **Keep service warm**: Use a free cron service to ping `/health` every 10 minutes
2. **Optimize cold starts**: The app initializes AI on first request, not startup
3. **Database**: SQLite works fine for free tier (stored in ephemeral disk)

### Keeping Service Awake (Optional)
Use https://cron-job.org (free) to ping your API:
- URL: `https://pakistan-travel-api.onrender.com/health`
- Interval: Every 10 minutes

---

## Environment Variables Reference

### Backend Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `GROQ_API_KEY` | ✅ Yes | Groq LLM API key | `gsk_xxx...` |
| `WEATHER_API_KEY` | ❌ No | OpenWeatherMap key | `abc123...` |
| `OPENROUTE_API_KEY` | ❌ No | OpenRouteService key | `5b3ce3...` |
| `CORS_ORIGINS` | ❌ No | Allowed frontend URLs | `https://your-site.com` |
| `LOG_LEVEL` | ❌ No | Logging level | `INFO` |
| `GROQ_MODEL` | ❌ No | LLM model name | `llama-3.3-70b-versatile` |

### Frontend Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `VITE_API_URL` | ✅ Yes | Backend API URL | `https://pakistan-travel-api.onrender.com` |

---

## Troubleshooting

### "AI is not configured" Error
- **Cause**: Missing `GROQ_API_KEY`
- **Fix**: Add the environment variable in Render dashboard → Your Service → Environment

### CORS Errors
- **Cause**: Frontend URL not in `CORS_ORIGINS`
- **Fix**: Update `CORS_ORIGINS` in backend environment variables

### Slow First Load
- **Cause**: Free tier cold start
- **Fix**: Normal behavior. Wait 30-60 seconds. Consider upgrading or using a warm-up service.

### Build Fails
- **Cause**: Usually missing dependencies
- **Fix**: Check build logs in Render dashboard

### Database Lost on Redeploy
- **Cause**: SQLite uses ephemeral disk on free tier
- **Fix**: Normal behavior. App re-creates DB with seed data on startup.

---

## Custom Domain (Optional)

1. Go to your Static Site in Render
2. Click **"Settings"** → **"Custom Domains"**
3. Add your domain (e.g., `travel.yourdomain.com`)
4. Update DNS with provided CNAME
5. Wait for SSL certificate (automatic)

---

## Alternative Free Platforms

If Render doesn't work for you:

### Frontend Only
| Platform | Free Tier | Notes |
|----------|-----------|-------|
| **Vercel** | Yes | Great for React, no backend |
| **Netlify** | Yes | Similar to Vercel |
| **GitHub Pages** | Yes | Static only |
| **Cloudflare Pages** | Yes | Unlimited bandwidth |

### Full Stack
| Platform | Free Tier | Notes |
|----------|-----------|-------|
| **Railway** | $5/month credit | Good for full stack |
| **Fly.io** | Yes | Good performance |
| **Cyclic** | Yes | Simple Node/Python |
| **Deta** | Yes | Micro VMs |

---

## Production Checklist

Before going live:

- [ ] Set all required environment variables
- [ ] Test trip planning wizard
- [ ] Test AI chat functionality
- [ ] Verify safety alerts load
- [ ] Check bus schedules page
- [ ] Test on mobile devices
- [ ] Set up health check monitoring
- [ ] (Optional) Configure custom domain

---

## Support

- **GitHub Issues**: Report bugs on the repository
- **Render Docs**: https://render.com/docs
- **Groq Docs**: https://console.groq.com/docs

---

**Happy deploying! 🚀**

