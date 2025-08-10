#!/usr/bin/env python3
"""
Minimal test backend to isolate the issue
"""

from fastapi import FastAPI
from datetime import datetime

app = FastAPI(title="Test Backend")

@app.get("/")
async def root():
    return {"message": "Test backend working", "timestamp": datetime.utcnow().isoformat()}

@app.get("/test")
async def test():
    return {"message": "Test endpoint", "timestamp": datetime.utcnow().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
