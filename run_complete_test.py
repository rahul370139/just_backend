#!/usr/bin/env python3
"""
Complete Pipeline Test Runner
This script sets up the environment and runs the complete end-to-end test
"""

import os
import sys
import subprocess
import asyncio
import time
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_environment():
    """Check if required environment variables are set"""
    print("🔍 Checking environment variables...")
    
    required_vars = {
        "SUPABASE_URL": "Supabase project URL",
        "SUPABASE_KEY": "Supabase anon key", 
        "GROQ_API_KEY": "Groq API key"
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        if not os.getenv(var):
            missing_vars.append(f"{var} ({description})")
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease create a .env file with these variables or set them in your environment.")
        print("See env_template.txt for reference.")
        return False
    
    print("✅ All environment variables are set")
    return True

def check_dependencies():
    """Check if required Python packages are installed"""
    print("\n📦 Checking Python dependencies...")
    
    required_packages = [
        "fastapi", "uvicorn", "httpx", "supabase", "dotenv"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nPlease install missing packages:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    print("✅ All required packages are installed")
    return True

def start_backend():
    """Start the FastAPI backend server"""
    print("\n🚀 Starting FastAPI backend server...")
    
    # Check if backend is already running
    try:
        import httpx
        import asyncio
        
        async def check_backend():
            async with httpx.AsyncClient() as client:
                response = await client.get("http://localhost:8000/health")
                return response.status_code == 200
        
        if asyncio.run(check_backend()):
            print("✅ Backend is already running")
            return True
    except:
        pass
    
    # Start backend in background
    try:
        backend_process = subprocess.Popen(
            [sys.executable, "backend_fastapi.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait a bit for server to start
        print("   Waiting for server to start...")
        time.sleep(5)
        
        # Check if server started successfully
        try:
            import httpx
            response = httpx.get("http://localhost:8000/health")
            if response.status_code == 200:
                print("✅ Backend server started successfully")
                return True
            else:
                print("❌ Backend server failed to start properly")
                return False
        except Exception as e:
            print(f"❌ Backend server error: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return False

def populate_test_data():
    """Populate Supabase with test data"""
    print("\n📊 Populating test data...")
    
    try:
        result = subprocess.run(
            [sys.executable, "populate_test_data.py"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print("✅ Test data populated successfully")
            return True
        else:
            print("❌ Failed to populate test data:")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Test data population timed out")
        return False
    except Exception as e:
        print(f"❌ Error populating test data: {e}")
        return False

def run_complete_test():
    """Run the complete pipeline test"""
    print("\n🧪 Running complete pipeline test...")
    
    try:
        result = subprocess.run(
            [sys.executable, "test_complete_pipeline.py"],
            capture_output=False,
            timeout=300  # 5 minutes timeout
        )
        
        if result.returncode == 0:
            print("✅ Complete pipeline test passed!")
            return True
        else:
            print("❌ Complete pipeline test failed")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Complete pipeline test timed out")
        return False
    except Exception as e:
        print(f"❌ Error running complete test: {e}")
        return False

def main():
    """Main execution flow"""
    print("🚀 AgentOps RCA Pipeline - Complete Test Runner")
    print("=" * 60)
    
    # Step 1: Environment check
    if not check_environment():
        print("\n❌ Environment setup failed. Please fix the issues above.")
        return False
    
    # Step 2: Dependencies check
    if not check_dependencies():
        print("\n❌ Dependencies check failed. Please install missing packages.")
        return False
    
    # Step 3: Start backend
    if not start_backend():
        print("\n❌ Backend startup failed. Please check the backend configuration.")
        return False
    
    # Step 4: Populate test data
    if not populate_test_data():
        print("\n❌ Test data population failed. Please check your Supabase connection.")
        return False
    
    # Step 5: Run complete test
    if not run_complete_test():
        print("\n❌ Complete pipeline test failed. Please check the test output above.")
        return False
    
    print("\n🎉 SUCCESS! Complete pipeline test completed successfully.")
    print("Your AgentOps RCA backend is working end-to-end!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
