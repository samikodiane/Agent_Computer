#!/bin/bash

# Get port from environment variable
PORT=${PORT:-8080}

echo "Starting Agent Server on port $PORT"
echo "Environment variables:"
echo "  PORT: $PORT"
echo "  MCP_SERVER_URL: ${MCP_SERVER_URL:-'Not set'}"
echo "  LLM_PROVIDER: ${LLM_PROVIDER:-'Not set'}"

# Start the MCP server in the background
echo "Starting MCP Server on port $PORT..."
python mcp_server.py &
MCP_PID=$!

# Wait a moment for MCP server to start
sleep 3

# Check if MCP server started successfully
if ! kill -0 $MCP_PID 2>/dev/null; then
    echo "ERROR: MCP server failed to start"
    exit 1
fi

echo "MCP Server started successfully (PID: $MCP_PID)"

# Start the agent endpoint
echo "Starting Agent Endpoint on port $PORT..."
python agent_endpoint.py &
AGENT_PID=$!

# Wait a moment for agent endpoint to start
sleep 2

# Check if agent endpoint started successfully
if ! kill -0 $AGENT_PID 2>/dev/null; then
    echo "ERROR: Agent endpoint failed to start"
    kill $MCP_PID 2>/dev/null
    exit 1
fi

echo "Agent Endpoint started successfully (PID: $AGENT_PID)"
echo "Both services are running on port $PORT"

# Function to handle shutdown
cleanup() {
    echo "Shutting down services..."
    kill $MCP_PID $AGENT_PID 2>/dev/null
    wait $MCP_PID $AGENT_PID 2>/dev/null
    echo "Services stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGTERM SIGINT

# Wait for both processes
wait $MCP_PID $AGENT_PID 