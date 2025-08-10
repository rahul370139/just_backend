-- Supabase Schema for AgentOps RCA Backend
-- Run this in your Supabase SQL editor

-- Create incidents table
CREATE TABLE IF NOT EXISTS incidents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id TEXT NOT NULL,
    incident_type TEXT NOT NULL,
    severity TEXT DEFAULT 'medium',
    eta_delta_hours DECIMAL(10,2) NOT NULL,
    problem_type TEXT NOT NULL,
    status TEXT DEFAULT 'open',
    description TEXT,
    created_ts TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resolved_ts TIMESTAMP WITH TIME ZONE,
    details JSONB DEFAULT '{}'::jsonb
);

-- Create spans table
CREATE TABLE IF NOT EXISTS spans (
    span_id TEXT PRIMARY KEY,
    parent_id TEXT,
    tool TEXT NOT NULL,
    start_ts BIGINT NOT NULL,
    end_ts BIGINT NOT NULL,
    args_digest TEXT,
    result_digest TEXT,
    attributes JSONB DEFAULT '{}'::jsonb,
    incident_id UUID REFERENCES incidents(id) ON DELETE CASCADE,
    order_id TEXT,
    created_ts TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create artifacts table
CREATE TABLE IF NOT EXISTS artifacts (
    digest TEXT PRIMARY KEY,
    mime_type TEXT NOT NULL,
    length INTEGER NOT NULL,
    pii_masked BOOLEAN DEFAULT FALSE,
    file_path TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_ts TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_spans_incident_id ON spans(incident_id);
CREATE INDEX IF NOT EXISTS idx_spans_tool ON spans(tool);
CREATE INDEX IF NOT EXISTS idx_incidents_problem_type ON incidents(problem_type);
CREATE INDEX IF NOT EXISTS idx_incidents_status ON incidents(status);

-- Insert sample data (optional)
INSERT INTO incidents (order_id, eta_delta_hours, problem_type, status, details) VALUES
('ORD-001', 2.5, 'eta_missed', 'open', '{"customer": "ABC Corp", "priority": "high"}'),
('ORD-002', 1.0, 'out_of_stock', 'open', '{"customer": "XYZ Ltd", "priority": "medium"}'),
('ORD-003', 3.0, 'weather_issue', 'closed', '{"customer": "DEF Inc", "priority": "low"}');

-- Enable Row Level Security (RLS) - uncomment if you want to use it
-- ALTER TABLE incidents ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE spans ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE artifacts ENABLE ROW LEVEL SECURITY;
