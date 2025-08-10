#!/usr/bin/env python3
"""
End-to-End Test Suite for AgentOps RCA Backend
Tests the complete pipeline: Supabase → RCA Analysis → Email Generation
"""

import asyncio
import httpx
import json
from datetime import datetime
from typing import Dict, Any, Optional

class EndToEndTester:
    """Comprehensive end-to-end testing for the RCA pipeline"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_results = {}
        
    async def test_health_check(self) -> bool:
        """Test the health check endpoint"""
        print("🔍 Testing health check...")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/health")
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
    
    async def test_supabase_connection(self) -> bool:
        """Test Supabase connectivity and data access"""
        print("\n🔍 Testing Supabase connection...")
        try:
            async with httpx.AsyncClient() as client:
                # Test incidents table
                response = await client.get(f"{self.base_url}/incidents")
                if response.status_code == 200:
                    incidents = response.json()
                    print(f"✅ Incidents table accessible: {len(incidents)} records")
                    
                    # Test spans table
                    response = await client.get(f"{self.base_url}/spans")
                    if response.status_code == 200:
                        spans = response.json()
                        print(f"✅ Spans table accessible: {len(spans)} records")
                        
                        # Test artifacts table
                        response = await client.get(f"{self.base_url}/artifacts")
                        if response.status_code == 200:
                            artifacts = response.json()
                            print(f"✅ Artifacts table accessible: {len(artifacts)} records")
                            
                            if len(incidents) > 0:
                                print(f"✅ All tables accessible with data")
                                return True
                            else:
                                print(f"⚠️  Tables accessible but no data found")
                                return False
                        else:
                            print(f"❌ Artifacts table failed: {response.status_code}")
                            return False
                    else:
                        print(f"❌ Spans table failed: {response.status_code}")
                        return False
                else:
                    print(f"❌ Incidents table failed: {response.status_code}")
                    return False
        except Exception as e:
            print(f"❌ Supabase connection error: {e}")
            return False
    
    async def test_data_relationships(self) -> bool:
        """Test that data relationships are working correctly"""
        print("\n🔍 Testing data relationships...")
        try:
            async with httpx.AsyncClient() as client:
                # Get incidents
                response = await client.get(f"{self.base_url}/incidents")
                if response.status_code != 200:
                    print(f"❌ Cannot fetch incidents: {response.status_code}")
                    return False
                
                incidents = response.json()
                if not incidents:
                    print("❌ No incidents data available")
                    return False
                
                # Test first incident's full data
                first_incident = incidents[0]
                incident_id = first_incident['incident_id']
                
                response = await client.get(f"{self.base_url}/incidents/{incident_id}/full")
                if response.status_code == 200:
                    full_data = response.json()
                    print(f"✅ Full incident data retrieved for: {incident_id}")
                    print(f"   Incident: {full_data['incident']['incident_id']}")
                    print(f"   Spans: {len(full_data['spans'])}")
                    print(f"   Artifacts: {len(full_data['artifacts'])}")
                    return True
                else:
                    print(f"❌ Full incident data failed: {response.status_code}")
                    return False
                    
        except Exception as e:
            print(f"❌ Data relationships error: {e}")
            return False
    
    async def test_rca_analysis(self) -> bool:
        """Test the complete RCA analysis pipeline"""
        print("\n🔍 Testing RCA analysis...")
        try:
            async with httpx.AsyncClient() as client:
                # Get first incident
                response = await client.get(f"{self.base_url}/incidents")
                if response.status_code != 200:
                    print(f"❌ Cannot fetch incidents: {response.status_code}")
                    return False
                
                incidents = response.json()
                if not incidents:
                    print("❌ No incidents data available")
                    return False
                
                # Test RCA analysis
                first_incident = incidents[0]
                incident_id = first_incident['incident_id']
                
                rca_request = {"incident_id": incident_id}
                response = await client.post(
                    f"{self.base_url}/rca/analyze",
                    json=rca_request
                )
                
                if response.status_code == 200:
                    rca_result = response.json()
                    print(f"✅ RCA analysis completed for: {incident_id}")
                    print(f"   Summary: {rca_result['summary'][:100]}...")
                    print(f"   Root Cause: {rca_result['root_cause'][:100]}...")
                    print(f"   Contributing Factors: {len(rca_result['contributing_factors'])}")
                    print(f"   Recommendations: {len(rca_result['recommendations'])}")
                    print(f"   Email Draft: {len(rca_result['email_draft'])} characters")
                    return True
                else:
                    print(f"❌ RCA analysis failed: {response.status_code}")
                    print(f"   Response: {response.text}")
                    return False
                    
        except Exception as e:
            print(f"❌ RCA analysis error: {e}")
            return False
    
    async def generate_email_draft(self) -> bool:
        """Test email draft generation specifically"""
        print("\n🔍 Testing email draft generation...")
        try:
            async with httpx.AsyncClient() as client:
                # Get first incident
                response = await client.get(f"{self.base_url}/incidents")
                if response.status_code != 200:
                    print(f"❌ Cannot fetch incidents: {response.status_code}")
                    return False
                
                incidents = response.json()
                if not incidents:
                    print("❌ No incidents data available")
                    return False
                
                # Test RCA analysis to get email draft
                first_incident = incidents[0]
                incident_id = first_incident['incident_id']
                
                rca_request = {"incident_id": incident_id}
                response = await client.post(
                    f"{self.base_url}/rca/analyze",
                    json=rca_request
                )
                
                if response.status_code == 200:
                    rca_result = response.json()
                    email_draft = rca_result.get('email_draft', '')
                    
                    if email_draft and len(email_draft) > 50:
                        print(f"✅ Email draft generated successfully")
                        print(f"   Length: {len(email_draft)} characters")
                        print(f"   Preview: {email_draft[:200]}...")
                        return True
                    else:
                        print(f"❌ Email draft is too short or empty")
                        return False
                else:
                    print(f"❌ Cannot generate email draft: {response.status_code}")
                    return False
                    
        except Exception as e:
            print(f"❌ Email draft generation error: {e}")
            return False
    
    def print_data_summary(self):
        """Print a summary of the test data"""
        print("\n📊 Data Summary")
        print("=" * 50)
        try:
            # This would be populated during tests
            pass
        except Exception as e:
            print(f"⚠️  Could not generate data summary: {e}")
    
    async def run_all_tests(self) -> Dict[str, bool]:
        """Run all end-to-end tests"""
        print("🚀 Starting AgentOps RCA Backend End-to-End Tests")
        print("=" * 60)
        
        # Run all tests
        self.test_results['health_check'] = await self.test_health_check()
        self.test_results['supabase_connection'] = await self.test_supabase_connection()
        self.test_results['data_relationships'] = await self.test_data_relationships()
        self.test_results['rca_analysis'] = await self.test_rca_analysis()
        self.test_results['email_draft'] = await self.generate_email_draft()
        
        # Print results
        print("\n📊 FINAL TEST RESULTS")
        print("=" * 60)
        
        test_names = {
            'health_check': 'Health Check',
            'supabase_connection': 'Supabase Connection',
            'data_relationships': 'Data Relationships',
            'rca_analysis': 'RCA Analysis',
            'email_draft': 'Email Draft Generation'
        }
        
        passed = 0
        for test_key, test_name in test_names.items():
            status = "✅ PASS" if self.test_results[test_key] else "❌ FAIL"
            print(f"{test_name:<25} {status}")
            if self.test_results[test_key]:
                passed += 1
        
        print(f"\nOverall: {passed}/{len(self.test_results)} tests passed")
        
        if passed == len(self.test_results):
            print("🎉 All tests passed! The pipeline is working correctly.")
        else:
            print("⚠️  Some tests failed. Check the errors above.")
        
        return self.test_results

async def main():
    """Main test function"""
    tester = EndToEndTester()
    results = await tester.run_all_tests()
    
    # Return exit code based on results
    all_passed = all(results.values())
    return 0 if all_passed else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
