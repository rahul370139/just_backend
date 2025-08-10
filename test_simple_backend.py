#!/usr/bin/env python3
"""
Simple test script to test the backend directly
"""

import asyncio
import os
from dotenv import load_dotenv
from backend_fastapi import get_incident_data, analyze_with_groq

# Load environment variables
load_dotenv()

async def test_backend_directly():
    """Test the backend functions directly"""
    
    incident_id = "bdeaa079-1d78-471d-a5df-8e16e44cf906"
    
    print(f"🔍 Testing backend directly for incident: {incident_id}")
    
    try:
        # Test getting incident data
        print("1. Testing get_incident_data...")
        incident_data = await get_incident_data(incident_id)
        if incident_data:
            print(f"✅ Incident data retrieved: {len(incident_data.spans)} spans, {len(incident_data.artifacts)} artifacts")
        else:
            print("❌ No incident data found")
            return
        
        # Test RCA analysis
        print("2. Testing analyze_with_groq...")
        rca_result = await analyze_with_groq(incident_data)
        print(f"✅ RCA analysis completed:")
        print(f"   Summary: {rca_result.summary}")
        print(f"   Root Cause: {rca_result.root_cause}")
        print(f"   Contributing Factors: {len(rca_result.contributing_factors)}")
        print(f"   Recommendations: {len(rca_result.recommendations)}")
        print(f"   Email Draft: {len(rca_result.email_draft)} characters")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_backend_directly())
