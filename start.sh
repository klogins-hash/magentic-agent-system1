#!/bin/bash

# Set default port if PORT environment variable is not set
PORT=${PORT:-8000}

# Start Magentic-UI with Groq and MCP configuration
exec magentic-ui --port $PORT --host 0.0.0.0 --config groq_config.json --mcp-config mcp_config.json
