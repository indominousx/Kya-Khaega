import { createClient } from '@supabase/supabase-js'
import config from './config'

const supabaseUrl = config.supabase.url
const supabaseAnonKey = config.supabase.anonKey

// Validate environment variables
if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Missing Supabase environment variables')
}

// Validate URL format
if (!supabaseUrl.startsWith('https://') && !supabaseUrl.startsWith('http://')) {
  throw new Error('Invalid supabaseUrl: Must be a valid HTTP or HTTPS URL.')
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey)