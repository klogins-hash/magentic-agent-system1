#!/bin/bash

# Set default port if PORT environment variable is not set
PORT=${PORT:-8000}

# Start Magentic-UI without Docker (Railway compatible)
exec magentic-ui --run-without-docker --port $PORT --config config.yaml
