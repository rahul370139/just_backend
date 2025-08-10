#!/bin/bash

# Get port from environment variable, default to 8000
PORT=${PORT:-8000}

echo "Starting AgentOps RCA Backend on port $PORT"

# Start the FastAPI application
exec uvicorn backend_fastapi:app --host 0.0.0.0 --port $PORT
