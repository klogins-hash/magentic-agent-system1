#!/bin/bash

# Set default port if PORT environment variable is not set
PORT=${PORT:-8000}

# Start Magentic-UI with YAML configuration
exec magentic-ui --port $PORT --config config.yaml
