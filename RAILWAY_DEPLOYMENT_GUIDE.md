# Railway Backend Deployment Guide

## Overview
This guide helps you connect your Next.js frontend (Vercel) with your FastAPI backend (Railway).

## Step 1: Deploy Backend to Railway

### 1.1 Railway Project Settings
In your Railway project dashboard:

**Option A - Using Root Directory (RECOMMENDED)**
- Go to Settings → Service Settings
- Set **Root Directory**: `backend`
- Set **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

**Option B - Using Config Files**
- The project includes `railway.toml`, `nixpacks.toml`, and `Procfile`
- Just push to Railway and it will auto-detect

### 1.2 Set Environment Variables in Railway
Add these to your Railway project:

```
SUPABASE_URL=https://guibojbykqgiuvqeceil.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
OPENAI_API_KEY=your-openai-key
GROQ_API_KEY=your-groq-key
ANTHROPIC_API_KEY=your-anthropic-key
VOYAGE_API_KEY=your-voyage-key
```

### 1.3 Get Your Railway URL
After deployment, Railway will give you a URL like:
`https://YOUR-PROJECT-NAME.railway.app` or
`https://YOUR-PROJECT-NAME.up.railway.app`

Copy this URL - you'll need it for the frontend.

## Step 2: Configure Frontend (Vercel/Local)

### 2.1 Update `.env` File
In your project root `.env` file, update:

```bash
NEXT_PUBLIC_API_URL=https://YOUR-RAILWAY-PROJECT.railway.app
```

Replace `YOUR-RAILWAY-PROJECT` with your actual Railway domain.

### 2.2 Set Vercel Environment Variables
In Vercel dashboard → Your Project → Settings → Environment Variables, add:

```
NEXT_PUBLIC_API_URL=https://YOUR-RAILWAY-PROJECT.railway.app
```

Make sure to add it for all environments (Production, Preview, Development).

## Step 3: Update Backend CORS (Optional)

If your Railway domain changes, the backend is already configured to accept it dynamically. You can also set this in Railway environment variables:

```
FRONTEND_URL=https://talk-o-app.vercel.app
```

## Step 4: Test the Connection

### 4.1 Test Backend Health
Visit: `https://YOUR-RAILWAY-PROJECT.railway.app/health`

You should see:
```json
{"status": "healthy"}
```

### 4.2 Test from Frontend
1. Redeploy your Vercel frontend
2. Go to your chat page
3. Send a message
4. Check if you get a response from the AI

## Backend Endpoints Available

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Root - API status |
| `/health` | GET | Health check |
| `/chat` | POST | Send chat message and get AI response |
| `/history/{user_id}` | GET | Get chat history for a user |
| `/users` | POST | Create/get user |
| `/register` | POST | Register new user |
| `/login` | POST | User login |
| `/verify` | POST | Email verification |

## Frontend API Calls

The frontend uses `NEXT_PUBLIC_API_URL` in these files:
- `app/chat/page.tsx` - Chat and history
- `app/api/auth/[...nextauth]/options.ts` - User creation
- `app/login/page.tsx` - Registration
- `app/verify-email/page.tsx` - Email verification

## Troubleshooting

### Issue: "Could not import module main"
**Solution**: Ensure Railway Root Directory is set to `backend` OR use the config files provided.

### Issue: CORS errors
**Solution**:
1. Check that FRONTEND_URL is set in Railway environment variables
2. Verify your Vercel domain is in the allowed_origins list in `backend/main.py`

### Issue: API calls failing with 500
**Solution**:
1. Check Railway logs for errors
2. Ensure all required environment variables are set
3. Verify API keys are valid

### Issue: "I'm having trouble connecting right now"
**Solution**:
1. Check that OPENAI_API_KEY is set in Railway (required for Stargirl)
2. Check that GROQ_API_KEY or ANTHROPIC_API_KEY is set (for fallback)
3. View Railway logs to see specific error messages

## Files Modified

- `backend/main.py` - Added dynamic CORS, removed root_path, added /verify endpoint
- `backend/rag/rag_pipeline.py` - Fixed API client initialization
- `backend/requirements.txt` - Added missing dependencies
- `.env` - Added NEXT_PUBLIC_API_URL
- `railway.toml`, `nixpacks.toml`, `Procfile`, `start.sh` - Deployment configs

## Quick Command Reference

### Test backend locally:
```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Test frontend locally:
```bash
npm run dev
```

### View Railway logs:
```bash
railway logs
```

## Need Help?

1. Check Railway logs for detailed error messages
2. Verify all environment variables are set correctly
3. Test the health endpoint first
4. Check CORS configuration if getting 403/401 errors
