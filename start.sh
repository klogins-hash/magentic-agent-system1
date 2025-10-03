#!/bin/bash

# Set default port if PORT environment variable is not set
PORT=${PORT:-8000}

# Start the FastAPI application
exec python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT
