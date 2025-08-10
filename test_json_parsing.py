#!/usr/bin/env python3
"""
Test script to verify JSON parsing logic
"""

import json

def test_json_parsing():
    """Test the JSON parsing logic from the backend"""
    
    # Simulate the content we get from Groq API
    content = """```json
{
    "summary": "The incident bdeaa079-1d78-471d-a5df-8e16e44cf906 involved a missed ETA (eta_missed) of 8.0 hours due to port congestion, resulting in a medium-severity delay for Order ID ORD-2025-001, which has since been resolved.",
    "root_cause": "The root cause of the problem is the failure in route optimization during the delivery scheduling process, as indicated by the 'route_optimization_failed' error in span_002_1754811000.",
    "contributing_factors": [
        "Inadequate handling of port congestion in the delivery scheduling algorithm",
        "Insufficient real-time data on port conditions to inform scheduling decisions",
        "Potential lack of redundancy or fallback planning in the event of scheduling failures"
    ],
    "recommendations": [
        "Implement enhanced route optimization algorithms that can better account for real-time port congestion data",
        "Develop and integrate a more robust and dynamic delivery scheduling system capable of adapting to unexpected delays or changes in port conditions",
        "Conduct regular reviews and updates of the delivery scheduling process to ensure it remains resilient and effective in handling various operational scenarios"
    ],
    "email_draft": "Subject: Root Cause Analysis of Incident bdeaa079-1d78-471d-a5df-8e16e44cf906\\nDear Stakeholders,\\nA Root Cause Analysis was conducted on the incident bdeaa079-1d78-471d-a5df-8e16e44cf906, which involved a missed ETA due to port congestion. The analysis revealed that the failure in route optimization during delivery scheduling was the primary cause. Contributing factors included inadequate handling of port congestion, insufficient real-time data, and potential lack of redundancy in scheduling. Recommendations to prevent similar incidents include enhancing the route optimization algorithm, developing a more dynamic scheduling system, and conducting regular process reviews. These findings and recommendations are detailed in the attached report. Please do not hesitate to contact us for further discussion or clarification.\\nBest regards, [Your Name]"
}
```"""
    
    print("Original content:")
    print(content)
    print("\n" + "="*50 + "\n")
    
    # Apply the same logic from the backend
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
        print("\n" + "="*50 + "\n")
        
        analysis = json.loads(cleaned_content)
        
        print("✅ JSON parsed successfully:")
        print(json.dumps(analysis, indent=2))
        
        # Test the specific fields
        print(f"\nSummary: {analysis.get('summary', 'NOT_FOUND')}")
        print(f"Root Cause: {analysis.get('root_cause', 'NOT_FOUND')}")
        print(f"Contributing Factors: {len(analysis.get('contributing_factors', []))}")
        print(f"Recommendations: {len(analysis.get('recommendations', []))}")
        print(f"Email Draft: {len(analysis.get('email_draft', ''))} characters")
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing failed: {e}")
        print(f"Content that failed to parse: {cleaned_content}")

if __name__ == "__main__":
    test_json_parsing()
