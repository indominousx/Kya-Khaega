# Environment Setup for Kya-Khaega

## Backend Environment Configuration

The backend uses environment variables to securely store sensitive information. Follow these steps to set up your environment:

### 1. Copy the Environment Template
```bash
cd backend
cp .env.example .env
```

### 2. Fill in Your Environment Variables

Edit the `.env` file with your actual values:

```env
# Gemini AI API Configuration
GEMINI_API_KEY=your_actual_gemini_api_key_here

# Supabase Configuration
SUPABASE_URL=your_actual_supabase_url_here
SUPABASE_KEY=your_actual_supabase_anon_key_here

# Flask Configuration (optional)
FLASK_ENV=development
DEBUG=True
```

### 3. Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini AI API key for natural language processing | `AIzaSy...` |
| `SUPABASE_URL` | Supabase project URL | `https://your-project.supabase.co` |
| `SUPABASE_KEY` | Supabase anonymous/public API key | `eyJhbGciOi...` |

### 4. Security Notes

- **Never commit the `.env` file to Git** - it contains sensitive information
- The `.env.example` file shows the structure but contains placeholder values
- For production deployment (Render, Heroku, etc.), set these as environment variables in your hosting platform
- The backend will throw an error if required environment variables are missing

### 5. Local Development

After setting up your `.env` file:

```bash
cd backend
pip install -r requirements.txt
python app.py
```

The application will automatically load your environment variables from the `.env` file.

### 6. Production Deployment

For production deployment on platforms like Render:
1. Don't upload the `.env` file
2. Set the environment variables directly in your hosting platform's dashboard
3. Use the same variable names as shown in `.env.example`