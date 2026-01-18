-- ResearchAssistant Database Schema
-- Run this in Supabase SQL Editor to create the required table

CREATE TABLE research_jobs (
  job_id TEXT PRIMARY KEY,  -- Use TEXT instead of UUID to match our uuid.uuid4() strings
  topic TEXT NOT NULL,
  user_id TEXT NOT NULL,
  status TEXT DEFAULT 'pending',
  progress JSONB DEFAULT '{
    "current_step": "not_started",
    "total_sections": 0,
    "completed_sections": 0,
    "current_section": null
  }'::jsonb,
  result JSONB DEFAULT NULL,
  error TEXT DEFAULT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Indexes for performance
CREATE INDEX idx_research_jobs_user_id ON research_jobs(user_id);
CREATE INDEX idx_research_jobs_status ON research_jobs(status);
CREATE INDEX idx_research_jobs_created_at ON research_jobs(created_at DESC);

-- Enable Row Level Security (RLS)
ALTER TABLE research_jobs ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can only see their own jobs
CREATE POLICY "Users can view their own jobs"
  ON research_jobs
  FOR SELECT
  USING (auth.uid()::text = user_id);

-- RLS Policy: Users can insert their own jobs
CREATE POLICY "Users can create their own jobs"
  ON research_jobs
  FOR INSERT
  WITH CHECK (auth.uid()::text = user_id);

-- RLS Policy: Users can update their own jobs
CREATE POLICY "Users can update their own jobs"
  ON research_jobs
  FOR UPDATE
  USING (auth.uid()::text = user_id);

-- RLS Policy: Service role can do anything (for backend)
CREATE POLICY "Service role has full access"
  ON research_jobs
  FOR ALL
  USING (true)
  WITH CHECK (true);

-- Optional: Function to auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_research_jobs_updated_at
  BEFORE UPDATE ON research_jobs
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- Verify table was created
SELECT 'research_jobs table created successfully!' as status;
