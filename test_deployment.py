#!/usr/bin/env python3
"""
Test script to verify the deployment is working correctly.
Run this after deploying to Railway to test the endpoints.
"""

import asyncio
import httpx
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BASE_URL = os.getenv("RAILWAY_URL", "http://localhost:8000")
if not BASE_URL.startswith("http"):
    BASE_URL = f"https://{BASE_URL}"

async def test_health_check():
    """Test the health check endpoint."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/")
            print(f"✅ Health check: {response.status_code}")
            print(f"   Response: {response.json()}")
            return True
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return False

async def test_environment_variables():
    """Test if environment variables are properly set."""
    required_vars = ["SUPABASE_URL", "SUPABASE_KEY", "GROQ_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        return False
    else:
        print("✅ All required environment variables are set")
        return True

async def test_supabase_connection():
    """Test Supabase connection by listing incidents."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/incidents")
            print(f"✅ Supabase connection: {response.status_code}")
            if response.status_code == 200:
                incidents = response.json()
                print(f"   Found {len(incidents)} incidents")
            return True
        except Exception as e:
            print(f"❌ Supabase connection failed: {e}")
            return False

async def test_groq_connection():
    """Test Groq API connection by creating a test incident and analyzing it."""
    async with httpx.AsyncClient() as client:
        try:
            # Create a test incident
            test_incident = {
                "order_id": "TEST-001",
                "eta_delta_hours": 2.5,
                "problem_type": "test_connection",
                "details": {"test": True}
            }
            
            response = await client.post(f"{BASE_URL}/incidents", json=test_incident)
            if response.status_code != 200:
                print(f"❌ Failed to create test incident: {response.status_code}")
                return False
            
            incident_data = response.json()
            incident_id = incident_data["incident_id"]
            print(f"✅ Created test incident: {incident_id}")
            
            # Test RCA analysis
            rca_request = {
                "incident_id": incident_id,
                "analysis_depth": "quick"
            }
            
            rca_response = await client.post(f"{BASE_URL}/rca/analyze", json=rca_request)
            if rca_response.status_code == 200:
                print("✅ Groq API connection successful")
                rca_data = rca_response.json()
                print(f"   Root cause: {rca_data['root_cause'][:100]}...")
                print(f"   Confidence: {rca_data['confidence_score']}")
                print(f"   Tokens used: {rca_data['tokens_used']}")
                return True
            else:
                print(f"❌ RCA analysis failed: {rca_response.status_code}")
                print(f"   Response: {rca_response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Groq connection test failed: {e}")
            return False

async def main():
    """Run all tests."""
    print("🚀 Testing AgentOps RCA Backend Deployment")
    print(f"   Base URL: {BASE_URL}")
    print("=" * 50)
    
    tests = [
        ("Environment Variables", test_environment_variables),
        ("Health Check", test_health_check),
        ("Supabase Connection", test_supabase_connection),
        ("Groq API Connection", test_groq_connection),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 Testing: {test_name}")
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Deployment is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check your configuration.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
