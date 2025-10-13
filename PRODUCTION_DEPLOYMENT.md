# Production Deployment Guide for Kya-Khaega

## Environment Variables for Production

When deploying to production platforms (Render, Heroku, Vercel, etc.), you need to set these environment variables in your hosting platform's dashboard:

### Backend Environment Variables (Required)

Set these in your **Backend Service** configuration:

| Variable Name | Description | Your Value |
|---------------|-------------|------------|
| `GEMINI_API_KEY` | Google Gemini AI API key | `AIzaSyAjE2GUy5_saZHT7N_RUzOkK8jfG67lGiA` |
| `SUPABASE_URL` | Supabase project URL | `https://bxbiafbvprdmcayumxnx.supabase.co` |
| `SUPABASE_KEY` | Supabase anon key | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJ4YmlhZmJ2cHJkbWNheXVteG54Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjAxNjQ1MzcsImV4cCI6MjA3NTc0MDUzN30.02_mypsf-AbNXMH0hUUylDTziMyVyUKQbORy1ZXC1KE` |

### Frontend Environment Variables

Set these in your **Frontend Service** configuration:

| Variable Name | Description | Production Value |
|---------------|-------------|------------------|
| `REACT_APP_API_URL` | Backend API URL | Your backend service URL (e.g., `https://your-backend.onrender.com`) |

## Deployment Steps

### 1. Render Backend Deployment

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New" → "Web Service"
3. Connect your GitHub repository: `indominousx/Kya-Khaega`
4. Configure:
   - **Name**: `kya-khaega-backend`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
5. **Environment Variables** - Add all backend variables from table above
6. Deploy

### 2. Render Frontend Deployment

1. Click "New" → "Static Site"
2. Connect same repository: `indominousx/Kya-Khaega`
3. Configure:
   - **Name**: `kya-khaega-frontend`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `build`
4. **Environment Variables**:
   - `REACT_APP_API_URL`: `https://your-backend-url.onrender.com`
5. Deploy

### 3. Post-Deployment Configuration

After both services are deployed:

1. **Update Frontend Environment**:
   - Copy your backend service URL from Render
   - Update `REACT_APP_API_URL` in frontend environment variables
   - Redeploy frontend

2. **Test the Application**:
   - Visit your frontend URL
   - Test AI search functionality
   - Verify restaurant recommendations work

## Security Notes

- ✅ No sensitive data is committed to the repository
- ✅ All secrets are managed through environment variables
- ✅ Production and development environments are separated
- ✅ `.env` files are ignored by Git

## Troubleshooting

### Backend Issues
- Check that all 3 environment variables are set
- Verify the Gemini API key is valid
- Ensure Supabase credentials are correct

### Frontend Issues
- Confirm `REACT_APP_API_URL` points to your backend
- Check that backend is responding to requests
- Verify CORS is properly configured (should allow all origins)

### Environment Variable Issues
- Render: Check "Environment" tab in service settings
- Variables must be exact matches (case-sensitive)
- Restart services after changing environment variables