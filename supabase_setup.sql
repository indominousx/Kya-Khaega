-- SQL script to create user_preferences table in Supabase
-- Run this in your Supabase SQL editor

CREATE TABLE user_preferences (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  email TEXT NOT NULL,
  daily_budget INTEGER DEFAULT 500,
  cuisine_preferences TEXT[] DEFAULT '{}',
  food_type TEXT DEFAULT '',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row Level Security (RLS)
ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;

-- Create policy for users to only see their own preferences
CREATE POLICY "Users can view own preferences" 
ON user_preferences FOR SELECT 
USING (auth.uid() = user_id);

-- Create policy for users to insert their own preferences
CREATE POLICY "Users can insert own preferences" 
ON user_preferences FOR INSERT 
WITH CHECK (auth.uid() = user_id);

-- Create policy for users to update their own preferences
CREATE POLICY "Users can update own preferences" 
ON user_preferences FOR UPDATE 
USING (auth.uid() = user_id);

-- Create policy for users to delete their own preferences
CREATE POLICY "Users can delete own preferences" 
ON user_preferences FOR DELETE 
USING (auth.uid() = user_id);

-- Create function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_user_preferences_updated_at 
BEFORE UPDATE ON user_preferences 
FOR EACH ROW 
EXECUTE FUNCTION update_updated_at_column();