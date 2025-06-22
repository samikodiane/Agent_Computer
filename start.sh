#!/bin/bash

# Start the MCP server in the background
echo "Starting MCP Server..."
python mcp_server.py &
MCP_PID=$!

# Wait a moment for MCP server to start
sleep 2

# Start the agent endpoint
echo "Starting Agent Endpoint..."
python agent_endpoint.py &
AGENT_PID=$!

# Function to handle shutdown
cleanup() {
    echo "Shutting down services..."
    kill $MCP_PID $AGENT_PID
    wait $MCP_PID $AGENT_PID
    exit 0
}

# Set up signal handlers
trap cleanup SIGTERM SIGINT

# Wait for both processes
wait $MCP_PID $AGENT_PID 