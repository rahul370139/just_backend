#!/usr/bin/env python3
"""
Test Data Population Script for AgentOps RCA Backend
Creates realistic test data matching the actual Supabase schema
"""

import os
import asyncio
import httpx
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

class TestDataPopulator:
    """Creates and populates test data in Supabase"""
    
    def __init__(self):
        self.headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json"
        }
    
    def create_test_incidents(self) -> List[Dict[str, Any]]:
        """Create realistic test incidents"""
        incidents = [
            {
                "incident_id": "inc_001_1754810000",
                "order_id": "ORD-2025-001",
                "incident_type": "delivery_delay",
                "severity": "medium",
                "status": "open",
                "eta_delta_hours": 3.5,
                "description": "Package delivery delayed due to weather conditions and route optimization issues",
                "created_at": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
                "resolved_at": None,
                "metadata": {
                    "created_by": "agentops",
                    "source": "automated_detection",
                    "priority": "normal"
                }
            },
            {
                "incident_id": "inc_002_1754811000",
                "order_id": "ORD-2025-002",
                "incident_type": "inventory_mismatch",
                "severity": "high",
                "status": "investigating",
                "eta_delta_hours": 8.0,
                "description": "Inventory count discrepancy detected during warehouse audit, affecting order fulfillment",
                "created_at": (datetime.utcnow() - timedelta(hours=1)).isoformat(),
                "resolved_at": None,
                "metadata": {
                    "created_by": "agentops",
                    "source": "warehouse_audit",
                    "priority": "high"
                }
            },
            {
                "incident_id": "inc_003_1754812000",
                "order_id": "ORD-2025-003",
                "incident_type": "payment_processing",
                "severity": "low",
                "status": "resolved",
                "eta_delta_hours": 1.0,
                "description": "Payment processing delay due to temporary banking system maintenance",
                "created_at": (datetime.utcnow() - timedelta(hours=4)).isoformat(),
                "resolved_at": (datetime.utcnow() - timedelta(hours=3)).isoformat(),
                "metadata": {
                    "created_by": "agentops",
                    "source": "payment_system",
                    "priority": "low"
                }
            }
        ]
        return incidents
    
    def create_test_artifacts(self) -> List[Dict[str, Any]]:
        """Create realistic test artifacts"""
        artifacts = [
            {
                "digest": "sha256:abc123def456ghi789",
                "mime_type": "application/json",
                "length": 2048,
                "pii_masked": False,
                "created_at": (datetime.utcnow() - timedelta(hours=3)).isoformat(),
                "file_path": "/logs/order_001_delivery.json",
                "metadata": {
                    "source": "delivery_system",
                    "version": "1.0.0",
                    "tags": ["delivery", "log"]
                }
            },
            {
                "digest": "sha256:def456ghi789abc123",
                "mime_type": "text/plain",
                "length": 1024,
                "pii_masked": True,
                "created_at": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
                "file_path": "/logs/warehouse_audit.txt",
                "metadata": {
                    "source": "warehouse_system",
                    "version": "2.1.0",
                    "tags": ["warehouse", "audit"]
                }
            },
            {
                "digest": "sha256:ghi789abc123def456",
                "mime_type": "application/xml",
                "length": 3072,
                "pii_masked": False,
                "created_at": (datetime.utcnow() - timedelta(hours=1)).isoformat(),
                "file_path": "/logs/payment_processing.xml",
                "metadata": {
                    "source": "payment_system",
                    "version": "3.0.0",
                    "tags": ["payment", "processing"]
                }
            }
        ]
        return artifacts
    
    def create_test_spans(self) -> List[Dict[str, Any]]:
        """Create realistic test spans"""
        spans = [
            {
                "span_id": "span_001_1754810000",
                "parent_id": None,
                "tool": "order_processing",
                "start_ts": int((datetime.utcnow() - timedelta(hours=3)).timestamp() * 1000000),
                "end_ts": int((datetime.utcnow() - timedelta(hours=2, minutes=55)).timestamp() * 1000000),
                "args_digest": "sha256:abc123def456ghi789",
                "result_digest": "sha256:def456ghi789abc123",
                "attributes": {
                    "operation": "process_order",
                    "status": "completed",
                    "duration_ms": 300000
                },
                "created_at": (datetime.utcnow() - timedelta(hours=2, minutes=55)).isoformat(),
                "order_id": "ORD-2025-001"
            },
            {
                "span_id": "span_002_1754811000",
                "parent_id": "span_001_1754810000",
                "tool": "delivery_scheduling",
                "start_ts": int((datetime.utcnow() - timedelta(hours=2, minutes=50)).timestamp() * 1000000),
                "end_ts": int((datetime.utcnow() - timedelta(hours=2, minutes=45)).timestamp() * 1000000),
                "args_digest": "sha256:def456ghi789abc123",
                "result_digest": "sha256:ghi789abc123def456",
                "attributes": {
                    "operation": "schedule_delivery",
                    "status": "failed",
                    "error": "route_optimization_failed"
                },
                "created_at": (datetime.utcnow() - timedelta(hours=2, minutes=45)).isoformat(),
                "order_id": "ORD-2025-001"
            },
            {
                "span_id": "span_003_1754812000",
                "parent_id": None,
                "tool": "warehouse_audit",
                "start_ts": int((datetime.utcnow() - timedelta(hours=2)).timestamp() * 1000000),
                "end_ts": int((datetime.utcnow() - timedelta(hours=1, minutes=55)).timestamp() * 1000000),
                "args_digest": "sha256:ghi789abc123def456",
                "result_digest": "sha256:abc123def456ghi789",
                "attributes": {
                    "operation": "audit_inventory",
                    "status": "completed",
                    "discrepancies_found": 3
                },
                "created_at": (datetime.utcnow() - timedelta(hours=1, minutes=55)).isoformat(),
                "order_id": "ORD-2025-002"
            }
        ]
        return spans
    
    async def populate_supabase(self) -> bool:
        """Populate Supabase with test data"""
        print("🚀 Populating Supabase with test data...")
        
        try:
            # Create artifacts first (spans reference them)
            artifacts = self.create_test_artifacts()
            print(f"📦 Creating {len(artifacts)} artifacts...")
            
            for artifact in artifacts:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{SUPABASE_URL}/rest/v1/artifacts",
                        headers=self.headers,
                        json=artifact
                    )
                    if response.status_code == 201:
                        print(f"✅ Created artifact: {artifact['digest'][:20]}...")
                    else:
                        print(f"⚠️  Artifact creation status: {response.status_code}")
            
            # Create incidents
            incidents = self.create_test_incidents()
            print(f"\n🚨 Creating {len(incidents)} incidents...")
            
            for incident in incidents:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{SUPABASE_URL}/rest/v1/incidents",
                        headers=self.headers,
                        json=incident
                    )
                    if response.status_code == 201:
                        print(f"✅ Created incident: {incident['incident_id']}")
                    else:
                        print(f"⚠️  Incident creation status: {response.status_code}")
            
            # Create spans
            spans = self.create_test_spans()
            print(f"\n🔗 Creating {len(spans)} spans...")
            
            for span in spans:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{SUPABASE_URL}/rest/v1/spans",
                        headers=self.headers,
                        json=span
                    )
                    if response.status_code == 201:
                        print(f"✅ Created span: {span['span_id']}")
                    else:
                        print(f"⚠️  Span creation status: {response.status_code}")
            
            print("\n🎉 Test data population completed!")
            return True
            
        except Exception as e:
            print(f"❌ Error populating test data: {e}")
            return False
    
    def print_insertion_instructions(self):
        """Print SQL INSERT statements for manual insertion"""
        print("\n📋 SQL INSERT Statements for Manual Insertion")
        print("=" * 60)
        print("If the API insertion fails, you can manually run these SQL commands:")
        print()
        
        # Artifacts
        print("-- Insert Artifacts")
        artifacts = self.create_test_artifacts()
        for artifact in artifacts:
            print(f"INSERT INTO artifacts (digest, mime_type, length, pii_masked, created_at, file_path, metadata)")
            print(f"VALUES ('{artifact['digest']}', '{artifact['mime_type']}', {artifact['length']}, {str(artifact['pii_masked']).lower()}, '{artifact['created_at']}', '{artifact['file_path']}', '{json.dumps(artifact['metadata'])}');")
            print()
        
        # Incidents
        print("-- Insert Incidents")
        incidents = self.create_test_incidents()
        for incident in incidents:
            print(f"INSERT INTO incidents (incident_id, order_id, incident_type, severity, status, eta_delta_hours, description, created_at, resolved_at, metadata)")
            resolved_at = f"'{incident['resolved_at']}'" if incident['resolved_at'] else 'NULL'
            eta_delta = str(incident['eta_delta_hours']) if incident['eta_delta_hours'] else 'NULL'
            print(f"VALUES ('{incident['incident_id']}', '{incident['order_id']}', '{incident['incident_type']}', '{incident['severity']}', '{incident['status']}', {eta_delta}, '{incident['description']}', '{incident['created_at']}', {resolved_at}, '{json.dumps(incident['metadata'])}');")
            print()
        
        # Spans
        print("-- Insert Spans")
        spans = self.create_test_spans()
        for span in spans:
            parent_id = f"'{span['parent_id']}'" if span['parent_id'] else 'NULL'
            print(f"INSERT INTO spans (span_id, parent_id, tool, start_ts, end_ts, args_digest, result_digest, attributes, created_at, order_id)")
            print(f"VALUES ('{span['span_id']}', {parent_id}, '{span['tool']}', {span['start_ts']}, {span['end_ts']}, '{span['args_digest']}', '{span['result_digest']}', '{json.dumps(span['attributes'])}', '{span['created_at']}', '{span['order_id']}');")
            print()

async def main():
    """Main function"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Missing Supabase environment variables")
        print("   Please check your .env file")
        return False
    
    populator = TestDataPopulator()
    
    # Try to populate via API
    success = await populator.populate_supabase()
    
    if not success:
        print("\n⚠️  API insertion failed. Showing manual insertion instructions...")
        populator.print_insertion_instructions()
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
