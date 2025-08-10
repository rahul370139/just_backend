#!/usr/bin/env python3
"""
AgentOps RCA Backend - FastAPI Application
Performs Root Cause Analysis on incidents using Groq LLM
"""

import os
import asyncio
import httpx
from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Environment variables
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
PORT = int(os.environ.get("PORT", 8000))

# Validate environment variables
if not all([SUPABASE_URL, SUPABASE_KEY, GROQ_API_KEY]):
    raise ValueError("Missing required environment variables: SUPABASE_URL, SUPABASE_KEY, GROQ_API_KEY")

print("✅ All environment variables configured")

# Pydantic models matching the actual Supabase schema
class Artifact(BaseModel):
    digest: str
    mime_type: str
    length: int
    pii_masked: bool = False
    file_path: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime

class Span(BaseModel):
    span_id: str
    parent_id: Optional[str] = None
    tool: str
    start_ts: int
    end_ts: int
    args_digest: str
    result_digest: str
    attributes: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    order_id: str

class Incident(BaseModel):
    incident_id: str
    order_id: str
    incident_type: str
    severity: str = "medium"
    status: str = "open"
    eta_delta_hours: Optional[float] = None
    description: str
    created_at: datetime
    resolved_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class IncidentWithRelations(BaseModel):
    incident: Incident
    spans: List[Span]
    artifacts: List[Artifact]

class RCARequest(BaseModel):
    incident_id: str

class RCAResponse(BaseModel):
    incident_id: str
    summary: str
    root_cause: str
    contributing_factors: List[str]
    recommendations: List[str]
    email_draft: str
    analysis_timestamp: datetime

# FastAPI app
app = FastAPI(
    title="AgentOps RCA Backend",
    description="Root Cause Analysis for incidents using Groq LLM",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test Supabase connection if configured
        if SUPABASE_URL and SUPABASE_KEY:
            supabase_healthy = await test_supabase_connection()
        else:
            supabase_healthy = "not_configured"
        
        # Test Groq connection if configured
        if GROQ_API_KEY:
            groq_healthy = await test_groq_connection()
        else:
            groq_healthy = "not_configured"
        
        return {
            "status": "healthy",
            "checks": {
                "supabase": supabase_healthy,
                "groq": groq_healthy,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    except Exception as e:
        return {"status": "degraded", "error": str(e), "timestamp": datetime.utcnow().isoformat()}

async def test_supabase_connection():
    """Test Supabase connection"""
    try:
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}"
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{SUPABASE_URL}/rest/v1/", headers=headers)
            return response.status_code == 200
    except:
        return False

async def test_groq_connection():
    """Test Groq connection"""
    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": "Hello"}],
            "max_tokens": 10
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=10.0
            )
            return response.status_code == 200
    except:
        return False

async def get_supabase_data(table: str, filters: Optional[Dict] = None) -> List[Dict]:
    """Generic function to get data from Supabase"""
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }
    
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    
    # Add filters if provided
    if filters:
        query_params = []
        for key, value in filters.items():
            if value is not None:
                query_params.append(f"{key}=eq.{value}")
        if query_params:
            url += "?" + "&".join(query_params)
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"Error fetching data from {table}: {e}")
        return []

async def get_incident_data(incident_id: str) -> Optional[IncidentWithRelations]:
    """Get incident data with related spans and artifacts"""
    try:
        # Get incident
        incidents = await get_supabase_data("incidents", {"incident_id": incident_id})
        if not incidents:
            return None
        
        incident_data = incidents[0]
        incident = Incident(**incident_data)
        
        # Get spans for this incident's order_id
        spans = await get_supabase_data("spans", {"order_id": incident.order_id})
        spans_list = [Span(**span) for span in spans]
        
        # Get artifacts referenced in spans
        artifact_digests = set()
        for span in spans_list:
            artifact_digests.add(span.args_digest)
            artifact_digests.add(span.result_digest)
        
        artifacts_list = []
        for digest in artifact_digests:
            artifacts = await get_supabase_data("artifacts", {"digest": digest})
            if artifacts:
                artifacts_list.append(Artifact(**artifacts[0]))
        
        return IncidentWithRelations(
            incident=incident,
            spans=spans_list,
            artifacts=artifacts_list
        )
        
    except Exception as e:
        print(f"Error getting incident data: {e}")
        return None

async def analyze_with_groq(incident_data: IncidentWithRelations) -> RCAResponse:
    """Analyze incident data using Groq LLM"""
    
    print(f"🔍 analyze_with_groq called for incident: {incident_data.incident.incident_id}")
    
    # Prepare data for LLM analysis
    incident = incident_data.incident
    spans = incident_data.spans
    artifacts = incident_data.artifacts
    
    # Create a comprehensive prompt for RCA
    prompt = f"""
    You are an expert Root Cause Analysis specialist. Analyze the following incident data and provide a detailed analysis.

    INCIDENT DETAILS:
    - ID: {incident.incident_id}
    - Order ID: {incident.order_id}
    - Incident Type: {incident.incident_type}
    - Severity: {incident.severity}
    - Status: {incident.status}
    - ETA Delta: {incident.eta_delta_hours or 'Not specified'} hours
    - Description: {incident.description}
    - Metadata: {incident.metadata}
    - Created: {incident.created_at}
    - Resolved: {incident.resolved_at or 'Not resolved'}

    SPANS (Execution Traces):
    {json.dumps([span.dict() for span in spans], indent=2, default=str)}

    ARTIFACTS:
    {json.dumps([artifact.dict() for artifact in artifacts], indent=2, default=str)}

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
            
            print(f"🔍 Raw Groq API response: {content[:200]}...")
            
            # Parse LLM response - handle markdown code blocks
            try:
                # Clean the content - remove markdown code blocks if present
                cleaned_content = content.strip()
                
                # Remove markdown code blocks
                if "```json" in cleaned_content:
                    start_idx = cleaned_content.find("```json") + 7
                    end_idx = cleaned_content.rfind("```")
                    if end_idx > start_idx:
                        cleaned_content = cleaned_content[start_idx:end_idx]
                elif "```" in cleaned_content:
                    start_idx = cleaned_content.find("```") + 3
                    end_idx = cleaned_content.rfind("```")
                    if end_idx > start_idx:
                        cleaned_content = cleaned_content[start_idx:end_idx]
                
                cleaned_content = cleaned_content.strip()
                
                print(f"Cleaned content: {cleaned_content[:200]}...")
                
                analysis = json.loads(cleaned_content)
                
                return RCAResponse(
                    incident_id=incident.incident_id,
                    summary=analysis.get("summary", "Analysis summary not available"),
                    root_cause=analysis.get("root_cause", "Root cause not identified"),
                    contributing_factors=analysis.get("contributing_factors", []),
                    recommendations=analysis.get("recommendations", []),
                    email_draft=analysis.get("email_draft", "Email draft not available"),
                    analysis_timestamp=datetime.utcnow()
                )
                
            except json.JSONDecodeError as e:
                print(f"JSON parsing failed: {e}")
                print(f"Content that failed to parse: {content}")
                # Fallback if LLM doesn't return valid JSON
                return RCAResponse(
                    incident_id=incident.incident_id,
                    summary="LLM analysis completed but response format was invalid",
                    root_cause="Analysis completed but root cause details unavailable",
                    contributing_factors=["Analysis completed"],
                    recommendations=["Review incident data manually"],
                    email_draft="Analysis completed. Please review the incident details manually.",
                    analysis_timestamp=datetime.utcnow()
                )
                
    except Exception as e:
        print(f"Error in Groq analysis: {e}")
        raise HTTPException(status_code=500, detail=f"LLM analysis failed: {str(e)}")

# API Endpoints
@app.get("/")
async def root():
    """Root endpoint - also serves as basic health check"""
    return {
        "status": "healthy",
        "message": "AgentOps RCA Backend",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": [
            "/health",
            "/incidents",
            "/incidents/{incident_id}",
            "/incidents/{incident_id}/full",
            "/rca/analyze",
            "/spans",
            "/artifacts"
        ]
    }

@app.get("/test")
async def test_endpoint():
    """Test endpoint to verify the app is working"""
    return {
        "message": "Test endpoint working",
        "function_location": "backend_fastapi.py",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/incidents")
async def get_incidents():
    """Get all incidents"""
    try:
        incidents = await get_supabase_data("incidents")
        return incidents
    except Exception as e:
        return {"status": "degraded", "error": str(e), "timestamp": datetime.utcnow().isoformat()}

@app.get("/incidents/{incident_id}")
async def get_incident(incident_id: str):
    """Get a specific incident"""
    try:
        incidents = await get_supabase_data("incidents", {"incident_id": incident_id})
        if not incidents:
            raise HTTPException(status_code=404, detail="Incident not found")
        return incidents[0]
    except HTTPException:
        raise
    except Exception as e:
        return {"status": "degraded", "error": str(e), "timestamp": datetime.utcnow().isoformat()}

@app.get("/incidents/{incident_id}/full")
async def get_incident_full(incident_id: str):
    """Get incident with all related data"""
    try:
        incident_data = await get_incident_data(incident_id)
        if not incident_data:
            raise HTTPException(status_code=404, detail="Incident not found")
        return incident_data
    except HTTPException:
        raise
    except Exception as e:
        return {"status": "degraded", "error": str(e), "timestamp": datetime.utcnow().isoformat()}

@app.post("/rca/analyze")
async def analyze_incident(request: RCARequest):
    """Perform Root Cause Analysis on an incident"""
    try:
        print(f"🔍 Starting RCA analysis for incident: {request.incident_id}")
        
        # Get incident data
        incident_data = await get_incident_data(request.incident_id)
        if not incident_data:
            print(f"❌ Incident not found: {request.incident_id}")
            raise HTTPException(status_code=404, detail="Incident not found")
        
        print(f"✅ Incident data retrieved: {len(incident_data.spans)} spans, {len(incident_data.artifacts)} artifacts")
        
        # Perform RCA analysis
        print("🚀 Calling Groq LLM for analysis...")
        rca_result = await analyze_with_groq(incident_data)
        print(f"✅ RCA analysis completed: {rca_result.summary[:100]}...")
        
        return rca_result
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ RCA analysis failed: {e}")
        return {"status": "degraded", "error": str(e), "timestamp": datetime.utcnow().isoformat()}

@app.get("/spans")
async def get_spans():
    """Get all spans"""
    try:
        spans = await get_supabase_data("spans")
        return spans
    except Exception as e:
        return {"status": "degraded", "error": str(e), "timestamp": datetime.utcnow().isoformat()}

@app.get("/artifacts")
async def get_artifacts():
    """Get all artifacts"""
    try:
        artifacts = await get_supabase_data("artifacts")
        return artifacts
    except Exception as e:
        return {"status": "degraded", "error": str(e), "timestamp": datetime.utcnow().isoformat()}

# Startup event
@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    print("🚀 AgentOps RCA Backend starting up...")
    
    # Test connections
    supabase_ok = await test_supabase_connection()
    groq_ok = await test_groq_connection()
    
    if not supabase_ok:
        print("⚠️  Warning: Supabase connection failed")
    if not groq_ok:
        print("⚠️  Warning: Groq connection failed")
    
    if supabase_ok and groq_ok:
        print("✅ All connections successful")
    else:
        print("⚠️  Some connections failed - check environment variables")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)