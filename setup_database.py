#!/usr/bin/env python3
"""
Database Setup Script for AgentOps RCA Backend
Creates tables and tests Supabase connection
"""

import os
import asyncio
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

async def test_supabase_connection():
    """Test basic Supabase connection"""
    print("🔍 Testing Supabase connection...")
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Missing Supabase environment variables")
        return False
    
    try:
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json"
        }
        
        # Test basic connection
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{SUPABASE_URL}/rest/v1/", headers=headers)
            print(f"✅ Supabase connection successful: {response.status_code}")
            return True
            
    except Exception as e:
        print(f"❌ Supabase connection failed: {e}")
        return False

async def check_tables():
    """Check if required tables exist"""
    print("\n🔍 Checking existing tables...")
    
    tables = ["incidents", "spans", "artifacts"]
    existing_tables = []
    
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    
    for table in tables:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{SUPABASE_URL}/rest/v1/{table}", headers=headers)
                if response.status_code == 200:
                    print(f"✅ Table '{table}' exists")
                    existing_tables.append(table)
                else:
                    print(f"❌ Table '{table}' not accessible: {response.status_code}")
        except Exception as e:
            print(f"❌ Error checking table '{table}': {e}")
    
    return existing_tables

async def create_sample_data():
    """Create sample data in the tables"""
    print("\n📝 Creating sample data...")
    
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    
    # Sample incident
    sample_incident = {
        "incident_id": "inc_test_001",
        "order_id": "ORD-TEST-001",
        "incident_type": "test_incident",
        "severity": "medium",
        "status": "open",
        "eta_delta_hours": 2.5,
        "description": "Test incident for RCA analysis",
        "metadata": {"test": True, "description": "Test incident for RCA analysis"}
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{SUPABASE_URL}/rest/v1/incidents",
                headers=headers,
                json=sample_incident
            )
            
            if response.status_code == 201:
                incident_data = response.json()
                print(f"✅ Created test incident: {incident_data}")
                return incident_data
            else:
                print(f"❌ Failed to create incident: {response.status_code} - {response.text}")
                return None
                
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        return None

async def main():
    """Main setup function"""
    print("🚀 Setting up AgentOps RCA Database")
    print("=" * 50)
    
    # Test connection
    if not await test_supabase_connection():
        print("❌ Cannot proceed without Supabase connection")
        return False
    
    # Check tables
    existing_tables = await check_tables()
    
    if len(existing_tables) < 3:
        print(f"\n⚠️  Only {len(existing_tables)}/3 tables exist")
        print("   You need to create the missing tables using supabase_schema.sql")
        print("   Go to your Supabase dashboard → SQL Editor and run the schema")
        return False
    
    print(f"\n✅ All required tables exist: {', '.join(existing_tables)}")
    
    # Try to create sample data
    sample_data = await create_sample_data()
    
    if sample_data:
        print("\n🎉 Database setup complete!")
        print("   You can now run the end-to-end tests")
        return True
    else:
        print("\n⚠️  Database setup partially complete")
        print("   Tables exist but sample data creation failed")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
