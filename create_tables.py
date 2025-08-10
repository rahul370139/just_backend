#!/usr/bin/env python3
"""
Table Creation Script for AgentOps RCA Backend
Creates the proper table structure in Supabase
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

def print_schema_instructions():
    """Print instructions for creating the proper schema"""
    print("🚀 AgentOps RCA Database Schema Setup")
    print("=" * 50)
    print()
    print("The current tables exist but don't have the correct structure.")
    print("You need to recreate them with the proper schema.")
    print()
    print("📋 Follow these steps:")
    print()
    print("1. Go to your Supabase project dashboard:")
    print(f"   {SUPABASE_URL}")
    print()
    print("2. Navigate to SQL Editor")
    print()
    print("3. Run the following SQL commands:")
    print()
    print("-- Drop existing tables (if they exist)")
    print("DROP TABLE IF EXISTS spans CASCADE;")
    print("DROP TABLE IF EXISTS incidents CASCADE;")
    print("DROP TABLE IF EXISTS artifacts CASCADE;")
    print()
    print("-- Create incidents table")
    print("CREATE TABLE incidents (")
    print("    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),")
    print("    order_id TEXT NOT NULL,")
    print("    eta_delta_hours DECIMAL(10,2) NOT NULL,")
    print("    problem_type TEXT NOT NULL,")
    print("    status TEXT DEFAULT 'open',")
    print("    created_ts TIMESTAMP WITH TIME ZONE DEFAULT NOW(),")
    print("    details JSONB DEFAULT '{}'::jsonb")
    print(");")
    print()
    print("-- Create spans table")
    print("CREATE TABLE spans (")
    print("    span_id TEXT PRIMARY KEY,")
    print("    parent_id TEXT,")
    print("    tool TEXT NOT NULL,")
    print("    start_ts BIGINT NOT NULL,")
    print("    end_ts BIGINT NOT NULL,")
    print("    args_digest TEXT,")
    print("    result_digest TEXT,")
    print("    attributes JSONB DEFAULT '{}'::jsonb,")
    print("    incident_id UUID REFERENCES incidents(id) ON DELETE CASCADE,")
    print("    created_ts TIMESTAMP WITH TIME ZONE DEFAULT NOW()")
    print(");")
    print()
    print("-- Create artifacts table")
    print("CREATE TABLE artifacts (")
    print("    digest TEXT PRIMARY KEY,")
    print("    mime TEXT NOT NULL,")
    print("    length INTEGER NOT NULL,")
    print("    pii_masked BOOLEAN DEFAULT FALSE,")
    print("    created_ts TIMESTAMP WITH TIME ZONE DEFAULT NOW()")
    print(");")
    print()
    print("-- Create indexes")
    print("CREATE INDEX idx_spans_incident_id ON spans(incident_id);")
    print("CREATE INDEX idx_spans_tool ON spans(tool);")
    print("CREATE INDEX idx_incidents_problem_type ON incidents(problem_type);")
    print("CREATE INDEX idx_incidents_status ON incidents(status);")
    print()
    print("4. After running the SQL, come back and run:")
    print("   python setup_database.py")
    print()
    print("5. Then run the end-to-end tests:")
    print("   python test_end_to_end.py")

def main():
    """Main function"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Missing Supabase environment variables")
        print("   Please check your .env file")
        return False
    
    print_schema_instructions()
    return True

if __name__ == "__main__":
    main()
