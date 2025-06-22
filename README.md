# Agent Server with MCP Tools and Memory

A production-ready LangGraph ReAct agent with Model Context Protocol (MCP) server integration, SQLite memory persistence, and FastAPI endpoints for deployment on Coolify.

## 🏗️ Architecture

- **MCP Server** (`mcp_server.py`) - 50+ tools via `/mcp` endpoint
- **Agent Endpoint** (`agent_endpoint.py`) - Chat interface via `/agent` endpoint  
- **Memory Management** (`memory.py`) - SQLite persistence via `/memory` endpoints
- **Model Manager** (`model.py`) - Multi-provider LLM support (OpenAI, Gemini, Anthropic)

## 🚀 Quick Start

### Local Development

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set environment variables:**
```bash
export OPENAI_API_KEY="your-openai-key"
export PORT=8080  # Optional: default is 8080
```

3. **Run the server:**
```bash
python agent_endpoint.py
```

4. **Test the endpoints:**
```bash
python test_local.py
```

### Docker Deployment

1. **Build the image:**
```bash
docker build -t agent-server .
```

2. **Run with environment variables:**
```bash
docker run -p 8080:8080 \
  -e OPENAI_API_KEY="your-key" \
  -e PORT=8080 \
  agent-server
```

## ☁️ Coolify Deployment

### 1. GitHub Setup

1. Create a GitHub repository and push your code
2. The GitHub Actions workflow will automatically build and push to GHCR

### 2. Coolify Configuration

1. **Create New Service** → **Application** → **Dockerfile**
2. **Repository:** Your GitHub repository URL
3. **Branch:** `main`
4. **Base Directory:** `/` (root)
5. **Port:** `8080` (or your preferred port)

### 3. Environment Variables

Set these in Coolify's Environment Variables section:

**Required:**
```
PORT=8080
MCP_SERVER_URL=https://your-project-id.your-domain.com
OPENAI_API_KEY=your-openai-api-key
```

**Optional (LLM Configuration):**
```
LLM_PROVIDER=openai
LLM_MODEL_NAME=gpt-3.5-turbo
LLM_TEMPERATURE=0.7
```

**Alternative Providers:**
```
# For Google Gemini
GOOGLE_API_KEY=your-google-api-key
LLM_PROVIDER=google

# For Anthropic Claude
ANTHROPIC_API_KEY=your-anthropic-api-key
LLM_PROVIDER=anthropic
```

### 4. Network Configuration

- **Port:** `8080` (or your configured port)
- **Domain:** Your Coolify domain (e.g., `agent.yourdomain.com`)

## 📡 API Endpoints

### Agent Chat
```bash
POST /agent
{
  "message": "Hello, what tools do you have?"
}
```

### Memory Management
```bash
GET    /memory                    # Get full conversation memory
GET    /memory/category/files     # Get memory by tool category
GET    /memory/stats              # Get tool usage statistics
DELETE /memory/clear              # Clear conversation memory
```

### Available Tool Categories
- `files` - File system operations
- `terminal` - Shell commands and processes
- `browser` - Web automation
- `system` - System info and network
- `utility` - Math and time operations
- `other` - Uncategorized tools

## 🔧 Configuration

### Port Configuration
The server uses the `PORT` environment variable with a default of `8080`. You can change this in Coolify's environment variables.

### MCP Server URL
Set `MCP_SERVER_URL` to your Coolify domain:
```
MCP_SERVER_URL=https://your-project-id.your-domain.com
```

### LLM Providers
Supported providers with their environment variables:

| Provider | API Key Variable | Base URL Variable |
|----------|------------------|-------------------|
| OpenAI   | `OPENAI_API_KEY` | `OPENAI_BASE_URL` |
| Google   | `GOOGLE_API_KEY` | - |
| Anthropic| `ANTHROPIC_API_KEY` | - |

## 🛠️ Troubleshooting

### Common Issues

1. **Port conflicts:** Change the `PORT` environment variable in Coolify
2. **Environment variables not working:** Ensure they're set in Coolify's Environment Variables section
3. **Health check failures:** Check the container logs in Coolify dashboard

### Debug Commands

```bash
# Test locally
python test_local.py

# Check container logs
docker logs your-container-name

# Test endpoints
curl http://localhost:8080/
curl http://localhost:8080/memory/stats
```

## 📊 Features

- ✅ **50+ MCP Tools** - File system, terminal, browser automation, system info
- ✅ **SQLite Memory** - Persistent conversation history with tool categorization
- ✅ **Multi-LLM Support** - OpenAI, Google Gemini, Anthropic Claude
- ✅ **Production Ready** - Health checks, proper logging, security measures
- ✅ **Coolify Optimized** - Environment variable configuration, unique port
- ✅ **API Endpoints** - RESTful interface for chat and memory management

## 🔒 Security

- Non-root container user
- Dangerous command blacklist
- Environment variable configuration
- CORS middleware for web access
- Input validation and error handling 