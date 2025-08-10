#!/usr/bin/env python3
"""
Debug script to test Groq API directly and see response format
"""

import os
import asyncio
import httpx
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

async def test_groq_api():
    """Test Groq API directly to see response format"""
    
    # Sample incident data
    incident_data = {
        "incident": {
            "incident_id": "bdeaa079-1d78-471d-a5df-8e16e44cf906",
            "order_id": "ORD-2025-001",
            "incident_type": "eta_missed",
            "severity": "medium",
            "status": "resolved",
            "eta_delta_hours": 8.0,
            "description": "Port congestion causing delivery delay",
            "created_at": "2025-08-10T02:41:25.077434Z"
        },
        "spans": [
            {
                "span_id": "span_001_1754810000",
                "tool": "order_processing",
                "status": "completed",
                "operation": "process_order"
            },
            {
                "span_id": "span_002_1754811000",
                "tool": "delivery_scheduling",
                "status": "failed",
                "operation": "schedule_delivery",
                "error": "route_optimization_failed"
            }
        ]
    }
    
    # Create prompt
    prompt = f"""
    You are an expert Root Cause Analysis specialist. Analyze the following incident data and provide a detailed analysis.

    INCIDENT DETAILS:
    - ID: {incident_data['incident']['incident_id']}
    - Order ID: {incident_data['incident']['order_id']}
    - Incident Type: {incident_data['incident']['incident_type']}
    - Severity: {incident_data['incident']['severity']}
    - Status: {incident_data['incident']['status']}
    - ETA Delta: {incident_data['incident']['eta_delta_hours']} hours
    - Description: {incident_data['incident']['description']}

    SPANS (Execution Traces):
    {json.dumps(incident_data['spans'], indent=2)}

    Please provide a comprehensive Root Cause Analysis including:
    1. A concise summary of the incident
    2. The root cause of the problem
    3. Contributing factors that led to this incident
    4. Specific recommendations to prevent similar incidents
    5. A professional email draft summarizing the findings for stakeholders

    Format your response as JSON with these exact keys:
    {{
        "summary": "Brief incident summary",
        "root_cause": "Main root cause",
        "contributing_factors": ["factor1", "factor2", "factor3"],
        "recommendations": ["rec1", "rec2", "rec3"],
        "email_draft": "Professional email content"
    }}
    """

    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": "You are an expert Root Cause Analysis specialist. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 2000,
            "temperature": 0.1
        }
        
        print("🔍 Testing Groq API...")
        print(f"Prompt: {prompt[:200]}...")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30.0
            )
            response.raise_for_status()
            
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            print(f"\n✅ Groq API Response:")
            print(f"Raw content: {content}")
            
            # Try to parse as JSON
            try:
                analysis = json.loads(content)
                print(f"\n✅ JSON parsed successfully:")
                print(json.dumps(analysis, indent=2))
            except json.JSONDecodeError as e:
                print(f"\n❌ JSON parsing failed: {e}")
                print(f"Content that failed to parse: {content}")
                
    except Exception as e:
        print(f"❌ Error in Groq API call: {e}")

if __name__ == "__main__":
    asyncio.run(test_groq_api())
