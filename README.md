# Agent Server with MCP Tools and Memory

A LangGraph-based agent server with Model Context Protocol (MCP) tools integration and persistent conversation memory.

## Features

- **LangGraph ReAct Agent**: Powered by LangGraph with ReAct reasoning
- **MCP Tools Integration**: Access to file system, browser automation, math operations, and more
- **Persistent Memory**: SQLite-based conversation memory with chronological ordering
- **Single Conversation**: One conversation per container (simplified for project-based deployment)
- **Multiple LLM Providers**: Support for OpenAI, Google Gemini, and Anthropic
- **Coolify Ready**: Designed for deployment with Coolify using subdomain structure

## Architecture

```
┌─────────────────────────────────────┐
│        Agent Server Container       │
│           (Port 8000)               │
├─────────────────────────────────────┤
│  MCP Server (mcp_server.py)         │
│  - /mcp endpoint                    │
│  - All MCP tools                    │
├─────────────────────────────────────┤
│  Agent Endpoint (agent_endpoint.py) │
│  - /agent endpoint                  │
│  - /memory endpoint                 │
└─────────────────────────────────────┘
```

## Quick Start

### 1. Set Environment Variables

```bash
# LLM Configuration
export LLM_PROVIDER=openai  # openai, google, anthropic
export LLM_MODEL_NAME=gpt-3.5-turbo
export LLM_TEMPERATURE=0.7

# API Keys (set your preferred provider)
export OPENAI_API_KEY="your-openai-key"
export GOOGLE_API_KEY="your-google-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### 3. Run the Server

```bash
# Run both MCP server and agent endpoint
python mcp_server.py &
python agent_endpoint.py
```

Or use Docker:

```bash
docker build -t agent-server .
docker run -p 8000:8000 \
  -e OPENAI_API_KEY="your-key" \
  agent-server
```

## API Endpoints

All endpoints are available on the same port (8000):

### Root Info
```bash
GET /
```

### Chat with Agent
```bash
POST /agent
{
  "message": "What's the weather like today?"
}
```

### Get Conversation Memory
```bash
GET /memory
```

### Clear Memory
```bash
DELETE /memory
```

### MCP Server
```bash
/mcp - MCP server endpoint for tool access
```

## MCP Tools Available

The agent has access to various tools through the MCP server:

### File System Operations
- `list_dir` - List files and directories
- `read_file` - Read file contents
- `write_file` - Write content to files
- `delete_file` - Delete files
- `create_folder` - Create directories
- `search_files` - Search for files by pattern

### Browser Automation (Playwright)
- `browser_open_page` - Open web pages
- `browser_screenshot` - Take screenshots
- `browser_click` - Click elements
- `browser_type` - Type text into forms
- `browser_extract` - Extract data from pages

### System Operations
- `execute_shell_command` - Run shell commands (with safety checks)
- `get_system_info` - Get system information
- `list_processes` - List running processes

### Network Operations
- `http_request_tool` - Make HTTP requests
- `ping_host` - Ping remote hosts
- `download_url` - Download files from URLs

### Math and Time
- `math_operation` - Perform mathematical operations
- `time_operation` - Handle date/time operations

## Memory System

The memory system stores all conversation elements in chronological order:
- User messages
- Agent responses  
- Tool calls and results

Each container maintains a single conversation thread, making it perfect for project-based deployments.

## Environment Variables

### Required for LLM
- `LLM_PROVIDER`: Provider to use (openai, google, anthropic)
- `LLM_MODEL_NAME`: Model name for the selected provider
- `LLM_TEMPERATURE`: Temperature setting (0.0-1.0)

### Required API Keys (set one based on provider)
- `OPENAI_API_KEY`: OpenAI API key
- `GOOGLE_API_KEY`: Google API key  
- `ANTHROPIC_API_KEY`: Anthropic API key

### Optional Provider Settings
- `OPENAI_BASE_URL`: Custom OpenAI base URL
- `OPENAI_ORGANIZATION`: OpenAI organization ID

## Coolify Deployment

### URL Structure
When deployed with Coolify, your server will be available at:
```
project_id.my_domain_name.domain
```

### Environment Variables for Coolify
Set these in your Coolify project:
```bash
# Required
LLM_PROVIDER=openai
OPENAI_API_KEY=your-openai-key

# Optional
LLM_MODEL_NAME=gpt-3.5-turbo
LLM_TEMPERATURE=0.7
```

### Access Endpoints
- `https://project_id.my_domain_name.domain/` - Root info
- `https://project_id.my_domain_name.domain/agent` - Agent chat
- `https://project_id.my_domain_name.domain/memory` - Memory management
- `https://project_id.my_domain_name.domain/mcp` - MCP tools

## Security Notes

- Shell commands are filtered to prevent dangerous operations
- File operations are restricted to the workspace directory
- API keys should be stored securely as environment variables
- Consider using secrets management in production

## Testing

Run the test script to verify everything works:

```bash
python test_agent.py
```

## Troubleshooting

### Common Issues

1. **Server Connection Failed**: Ensure the server is running on port 8000
2. **Memory Database Error**: Check SQLite permissions in container
3. **API Key Issues**: Ensure correct environment variables are set

### Logs
Check container logs for detailed error information:
```bash
docker logs agent-server
``` 