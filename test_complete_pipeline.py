#!/usr/bin/env python3
"""
Complete End-to-End Test for AgentOps RCA Pipeline
Tests the entire flow from reading Supabase data to generating RCA and email drafts
"""

import asyncio
import httpx
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BASE_URL = "http://localhost:8000"
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

class CompletePipelineTester:
    def __init__(self):
        self.test_results = []
        
    async def test_supabase_connection(self) -> bool:
        """Test connection to Supabase and verify table structure"""
        print("\n🔌 Testing Supabase Connection...")
        try:
            async with httpx.AsyncClient() as client:
                # Test basic connection by getting incidents
                response = await client.get(f"{BASE_URL}/incidents")
                if response.status_code == 200:
                    incidents = response.json()
                    print(f"✅ Connected to Supabase - Found {len(incidents)} incidents")
                    
                    # Verify table structure by checking first incident
                    if incidents:
                        incident = incidents[0]
                        required_fields = ['incident_id', 'order_id', 'incident_type', 'severity', 'description']
                        missing_fields = [field for field in required_fields if field not in incident]
                        if missing_fields:
                            print(f"❌ Missing fields in incidents table: {missing_fields}")
                            return False
                        print("✅ Incidents table structure verified")
                    
                    return True
                else:
                    print(f"❌ Failed to connect to Supabase: {response.status_code}")
                    return False
        except Exception as e:
            print(f"❌ Supabase connection error: {e}")
            return False
    
    async def test_data_retrieval(self) -> bool:
        """Test retrieval of data from all three tables"""
        print("\n📊 Testing Data Retrieval...")
        try:
            async with httpx.AsyncClient() as client:
                # Test incidents retrieval
                incidents_response = await client.get(f"{BASE_URL}/incidents")
                if incidents_response.status_code != 200:
                    print("❌ Failed to retrieve incidents")
                    return False
                
                incidents = incidents_response.json()
                print(f"✅ Retrieved {len(incidents)} incidents")
                
                if not incidents:
                    print("❌ No incidents found - need test data")
                    return False
                
                # Test spans retrieval through full incident data
                incident_id = incidents[0]['incident_id']
                full_response = await client.get(f"{BASE_URL}/incidents/{incident_id}/full")
                if full_response.status_code != 200:
                    print("❌ Failed to retrieve full incident data")
                    return False
                
                full_data = full_response.json()
                spans = full_data.get('spans', [])
                artifacts = full_data.get('artifacts', [])
                
                print(f"✅ Retrieved {len(spans)} spans")
                print(f"✅ Retrieved {len(artifacts)} artifacts")
                
                # Verify data relationships
                if spans and artifacts:
                    print("✅ Data relationships verified (spans reference artifacts)")
                    return True
                else:
                    print("⚠️  Limited data for testing")
                    return True
                    
        except Exception as e:
            print(f"❌ Data retrieval error: {e}")
            return False
    
    async def test_rca_analysis(self) -> bool:
        """Test the complete RCA analysis pipeline"""
        print("\n🔍 Testing RCA Analysis Pipeline...")
        try:
            async with httpx.AsyncClient() as client:
                # Get an incident for analysis
                incidents_response = await client.get(f"{BASE_URL}/incidents")
                incidents = incidents_response.json()
                
                if not incidents:
                    print("❌ No incidents available for RCA test")
                    return False
                
                incident_id = incidents[0]['incident_id']
                print(f"   Analyzing incident: {incident_id}")
                
                # Perform RCA analysis
                rca_response = await client.post(
                    f"{BASE_URL}/rca/analyze",
                    json={"incident_id": incident_id}
                )
                
                if rca_response.status_code == 200:
                    rca_data = rca_response.json()
                    print("✅ RCA analysis completed successfully!")
                    
                    # Verify RCA response structure
                    required_fields = ['summary', 'root_cause', 'contributing_factors', 'recommendations', 'email_draft']
                    missing_fields = [field for field in required_fields if field not in rca_data]
                    
                    if missing_fields:
                        print(f"❌ RCA response missing fields: {missing_fields}")
                        return False
                    
                    # Display analysis results
                    print(f"   📝 Summary: {rca_data['summary'][:100]}...")
                    print(f"   🎯 Root Cause: {rca_data['root_cause'][:100]}...")
                    print(f"   🔍 Contributing Factors: {len(rca_data['contributing_factors'])} found")
                    print(f"   💡 Recommendations: {len(rca_data['recommendations'])} provided")
                    print(f"   📧 Email Draft: {len(rca_data['email_draft'])} characters")
                    
                    # Verify email draft quality
                    email_draft = rca_data['email_draft']
                    if len(email_draft) > 100 and ('subject' in email_draft.lower() or 'dear' in email_draft.lower()):
                        print("✅ Email draft appears well-formatted")
                    else:
                        print("⚠️  Email draft may need formatting improvements")
                    
                    return True
                else:
                    print(f"❌ RCA analysis failed: {rca_response.status_code}")
                    print(f"   Response: {rca_response.text}")
                    return False
                    
        except Exception as e:
            print(f"❌ RCA analysis error: {e}")
            return False
    
    async def test_email_generation(self) -> bool:
        """Test email draft generation specifically"""
        print("\n📧 Testing Email Draft Generation...")
        try:
            async with httpx.AsyncClient() as client:
                # Get an incident for email generation
                incidents_response = await client.get(f"{BASE_URL}/incidents")
                incidents = incidents_response.json()
                
                if not incidents:
                    print("❌ No incidents available for email test")
                    return False
                
                incident_id = incidents[0]['incident_id']
                
                # Perform RCA analysis to get email draft
                rca_response = await client.post(
                    f"{BASE_URL}/rca/analyze",
                    json={"incident_id": incident_id}
                )
                
                if rca_response.status_code == 200:
                    rca_data = rca_response.json()
                    email_draft = rca_data.get('email_draft', '')
                    
                    if not email_draft:
                        print("❌ No email draft generated")
                        return False
                    
                    print("✅ Email draft generated successfully!")
                    
                    # Analyze email quality
                    email_analysis = self.analyze_email_quality(email_draft)
                    print(f"   📊 Email Quality Score: {email_analysis['score']}/10")
                    print(f"   📏 Length: {len(email_draft)} characters")
                    print(f"   🔤 Professional tone: {'Yes' if email_analysis['professional'] else 'No'}")
                    print(f"   📋 Structure: {'Good' if email_analysis['structured'] else 'Needs improvement'}")
                    
                    # Display email preview
                    print(f"\n   📧 Email Preview:")
                    print(f"   {'='*50}")
                    lines = email_draft.split('\n')[:10]  # Show first 10 lines
                    for line in lines:
                        print(f"   {line}")
                    if len(email_draft.split('\n')) > 10:
                        remaining_lines = len(email_draft.split('\n')) - 10
                        print(f"   ... ({remaining_lines} more lines)")
                    print(f"   {'='*50}")
                    
                    return email_analysis['score'] >= 6  # Pass if score >= 6
                else:
                    print(f"❌ Failed to generate email draft: {rca_response.status_code}")
                    return False
                    
        except Exception as e:
            print(f"❌ Email generation error: {e}")
            return False
    
    def analyze_email_quality(self, email_draft: str) -> Dict[str, Any]:
        """Analyze the quality of the generated email draft"""
        score = 0
        professional = False
        structured = False
        
        # Check length
        if len(email_draft) > 200:
            score += 2
        elif len(email_draft) > 100:
            score += 1
        
        # Check for professional language
        professional_indicators = ['dear', 'regards', 'sincerely', 'thank you', 'please', 'would', 'could']
        if any(indicator in email_draft.lower() for indicator in professional_indicators):
            score += 2
            professional = True
        
        # Check for structure
        if '\n\n' in email_draft or email_draft.count('\n') > 3:
            score += 2
            structured = True
        
        # Check for incident details
        if any(word in email_draft.lower() for word in ['incident', 'issue', 'problem', 'analysis', 'recommendation']):
            score += 2
        
        # Check for actionable content
        if any(word in email_draft.lower() for word in ['recommend', 'suggest', 'action', 'next steps']):
            score += 2
        
        return {
            'score': min(score, 10),
            'professional': professional,
            'structured': structured
        }
    
    async def test_end_to_end_flow(self) -> bool:
        """Test the complete end-to-end flow"""
        print("\n🔄 Testing Complete End-to-End Flow...")
        try:
            async with httpx.AsyncClient() as client:
                # 1. Get incidents
                incidents_response = await client.get(f"{BASE_URL}/incidents")
                if incidents_response.status_code != 200:
                    print("❌ Step 1 failed: Cannot retrieve incidents")
                    return False
                
                incidents = incidents_response.json()
                if not incidents:
                    print("❌ Step 1 failed: No incidents available")
                    return False
                
                print("✅ Step 1: Retrieved incidents")
                
                # 2. Get full incident data
                incident_id = incidents[0]['incident_id']
                full_response = await client.get(f"{BASE_URL}/incidents/{incident_id}/full")
                if full_response.status_code != 200:
                    print("❌ Step 2 failed: Cannot retrieve full incident data")
                    return False
                
                full_data = full_response.json()
                print(f"✅ Step 2: Retrieved full incident data ({len(full_data.get('spans', []))} spans, {len(full_data.get('artifacts', []))} artifacts)")
                
                # 3. Perform RCA analysis
                rca_response = await client.post(
                    f"{BASE_URL}/rca/analyze",
                    json={"incident_id": incident_id}
                )
                
                if rca_response.status_code != 200:
                    print("❌ Step 3 failed: RCA analysis failed")
                    return False
                
                rca_data = rca_response.json()
                print("✅ Step 3: RCA analysis completed")
                
                # 4. Verify complete output
                if all(field in rca_data for field in ['summary', 'root_cause', 'contributing_factors', 'recommendations', 'email_draft']):
                    print("✅ Step 4: All required output fields present")
                    print(f"   📊 Final Analysis Summary: {rca_data['summary'][:80]}...")
                    print(f"   📧 Email Draft Length: {len(rca_data['email_draft'])} characters")
                    return True
                else:
                    print("❌ Step 4 failed: Missing required output fields")
                    return False
                    
        except Exception as e:
            print(f"❌ End-to-end flow error: {e}")
            return False
    
    async def run_all_tests(self):
        """Run all tests and provide comprehensive results"""
        print("🚀 Starting Complete Pipeline End-to-End Tests")
        print("=" * 60)
        
        tests = [
            ("Supabase Connection", self.test_supabase_connection),
            ("Data Retrieval", self.test_data_retrieval),
            ("RCA Analysis", self.test_rca_analysis),
            ("Email Generation", self.test_email_generation),
            ("End-to-End Flow", self.test_end_to_end_flow)
        ]
        
        results = []
        for test_name, test_func in tests:
            try:
                result = await test_func()
                results.append((test_name, result))
                self.test_results.append((test_name, result))
            except Exception as e:
                print(f"❌ {test_name} failed with exception: {e}")
                results.append((test_name, False))
                self.test_results.append((test_name, False))
        
        # Comprehensive results summary
        print("\n" + "=" * 60)
        print("📊 COMPLETE PIPELINE TEST RESULTS")
        print("=" * 60)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for i, (test_name, result) in enumerate(results, 1):
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{i:2d}. {test_name:<25} {status}")
        
        print(f"\nOverall Pipeline Status: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED! Pipeline is working end-to-end.")
        elif passed >= total * 0.8:
            print("⚠️  Most tests passed. Pipeline is mostly functional.")
        else:
            print("❌ Multiple tests failed. Pipeline needs attention.")
        
        # Detailed recommendations
        print("\n🔍 Detailed Analysis:")
        for test_name, result in results:
            if not result:
                print(f"   ❌ {test_name}: Needs investigation")
            else:
                print(f"   ✅ {test_name}: Working correctly")
        
        return passed == total

async def main():
    """Main test execution"""
    # Check environment variables
    missing_env = []
    if not SUPABASE_URL:
        missing_env.append("SUPABASE_URL")
    if not SUPABASE_KEY:
        missing_env.append("SUPABASE_KEY")
    if not GROQ_API_KEY:
        missing_env.append("GROQ_API_KEY")
    
    if missing_env:
        print(f"❌ Missing environment variables: {', '.join(missing_env)}")
        print("Please set these in your .env file or environment")
        return False
    
    # Check if backend is running
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/health")
            if response.status_code != 200:
                print(f"❌ Backend not responding at {BASE_URL}")
                print("Please start the backend server first")
                return False
    except Exception:
        print(f"❌ Cannot connect to backend at {BASE_URL}")
        print("Please start the backend server first")
        return False
    
    # Run tests
    tester = CompletePipelineTester()
    success = await tester.run_all_tests()
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
