#!/usr/bin/env python3
"""
Simple test script for the AgentOps RCA Backend
Tests basic functionality without complex setup
"""

import asyncio
import httpx
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"  # Change this to your Railway URL when deployed

async def test_health():
    """Test the health check endpoint"""
    print("🔍 Testing health check...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health check passed: {data['status']}")
                print(f"   Supabase: {data['checks']['supabase']}")
                print(f"   Groq: {data['checks']['groq']}")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

async def test_incidents():
    """Test getting incidents"""
    print("\n🔍 Testing incidents endpoint...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/incidents")
            if response.status_code == 200:
                incidents = response.json()
                print(f"✅ Found {len(incidents)} incidents")
                for incident in incidents[:3]:  # Show first 3
                    print(f"   - {incident['order_id']}: {incident['problem_type']}")
                return True
            else:
                print(f"❌ Incidents failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Incidents error: {e}")
        return False

async def test_rca_analysis():
    """Test RCA analysis with a sample incident"""
    print("\n🔍 Testing RCA analysis...")
    try:
        # First get incidents to find an ID
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/incidents")
            if response.status_code != 200:
                print("❌ Need incidents first")
                return False
            
            incidents = response.json()
            if not incidents:
                print("❌ No incidents found for RCA test")
                return False
            
            incident_id = incidents[0]['incident_id']
            print(f"   Using incident: {incident_id}")
            
            # Test RCA analysis
            rca_response = await client.post(
                f"{BASE_URL}/rca/analyze",
                json={"incident_id": incident_id}
            )
            
            if rca_response.status_code == 200:
                rca_data = rca_response.json()
                print("✅ RCA analysis successful!")
                print(f"   Summary: {rca_data['summary'][:100]}...")
                print(f"   Root Cause: {rca_data['root_cause'][:100]}...")
                print(f"   Contributing Factors: {len(rca_data['contributing_factors'])}")
                print(f"   Recommendations: {len(rca_data['recommendations'])}")
                print(f"   Email Draft: {len(rca_data['email_draft'])} characters")
                return True
            else:
                print(f"❌ RCA analysis failed: {rca_response.status_code}")
                print(f"   Response: {rca_response.text}")
                return False
                
    except Exception as e:
        print(f"❌ RCA analysis error: {e}")
        return False

async def test_full_incident():
    """Test getting full incident data"""
    print("\n🔍 Testing full incident data...")
    try:
        async with httpx.AsyncClient() as client:
            # Get incidents first
            response = await client.get(f"{BASE_URL}/incidents")
            if response.status_code != 200:
                print("❌ Need incidents first")
                return False
            
            incidents = response.json()
            if not incidents:
                print("❌ No incidents found")
                return False
            
            incident_id = incidents[0]['incident_id']
            
            # Get full incident data
            full_response = await client.get(f"{BASE_URL}/incidents/{incident_id}/full")
            if full_response.status_code == 200:
                full_data = full_response.json()
                print("✅ Full incident data retrieved!")
                print(f"   Incident: {full_data['incident']['incident_id']}")
                print(f"   Spans: {len(full_data['spans'])}")
                print(f"   Artifacts: {len(full_data['artifacts'])}")
                return True
            else:
                print(f"❌ Full incident failed: {full_response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Full incident error: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Starting AgentOps RCA Backend Tests")
    print("=" * 50)
    
    tests = [
        test_health,
        test_incidents,
        test_full_incident,
        test_rca_analysis
    ]
    
    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    for i, (test, result) in enumerate(zip(tests, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        test_name = test.__name__.replace("test_", "").replace("_", " ").title()
        print(f"{i+1:2d}. {test_name:<20} {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your backend is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
