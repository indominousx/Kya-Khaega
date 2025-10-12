// Configuration file for environment variables
const config = {
  supabase: {
    url: process.env.REACT_APP_SUPABASE_URL || 'https://bxbiafbvprdmcayumxnx.supabase.co',
    anonKey: process.env.REACT_APP_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJ4YmlhZmJ2cHJkbWNheXVteG54Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjAxNjQ1MzcsImV4cCI6MjA3NTc0MDUzN30.02_mypsf-AbNXMH0hUUylDTziMyVyUKQbORy1ZXC1KE'
  },
  api: {
    baseUrl: process.env.REACT_APP_API_URL || 'http://localhost:5000'
  }
}

export default config