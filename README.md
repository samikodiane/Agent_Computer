# MCP Server with 50+ Tools

A lightweight Model Context Protocol (MCP) server with 50+ tools for file operations, terminal commands, browser automation, system info, and more. Designed for external AI agents to connect and use via HTTP.

## 🏗️ Architecture

- **MCP Server** (`mcp_server.py`) - 50+ tools via `/mcp` endpoint
- **Streamable HTTP Transport** - Accessible via HTTP/HTTPS
- **Containerized** - Ready for Coolify deployment

## 🚀 Quick Start

### Local Development

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set environment variables:**
```bash
export PORT=8080  # Optional: default is 8080
```

3. **Run the server:**
```bash
python mcp_server.py
```

4. **Test the endpoint:**
```bash
curl http://localhost:8080/mcp
```

### Docker Deployment

1. **Build the image:**
```bash
docker build -t mcp-server .
```

2. **Run with environment variables:**
```bash
docker run -p 8080:8080 \
  -e PORT=8080 \
  mcp-server
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

```
PORT=8080
```

### 4. Network Configuration

- **Port:** `8080` (must match your PORT environment variable)
- **Domain:** Your Coolify domain (e.g., `mcp.yourdomain.com`)

## 📡 MCP Endpoint

### Access Point
```
GET /mcp
```

### Available Tool Categories

- **File Operations:** `read_file`, `write_file`, `list_dir`, `delete_file`, `create_folder`, `search_files`, `zip_files`, `unzip_file`, `directory_tree`
- **Terminal Commands:** `execute_shell_command`, `list_processes`, `kill_process`
- **Browser Automation:** `browser_open_page`, `browser_screenshot`, `browser_click`, `browser_type`, `browser_extract`, `browser_scroll_and_extract`, `browser_fill_form`, `browser_handle_dialog`, `browser_upload_file`, `browser_get_network_requests`, `browser_execute_javascript`, `browser_get_page_info`, `browser_navigate_with_cookies`, `browser_compare_pages`, `browser_generate_accessibility_report`
- **System Info:** `get_system_info`, `ping_host`, `download_url`, `http_request_tool`
- **File Processing:** `search_and_replace`, `file_diff`, `format_code`
- **Math & Time:** `math_operation`, `time_operation`, `wait_operation`

## 🔧 Configuration

### Port Configuration
The server uses the `PORT` environment variable with a default of `8080`.

### Workspace Directory
Set `MCP_WORKSPACE` environment variable to control the base directory for file operations.

### Browser Configuration
Set `BROWSER_HEADLESS=true` for headless browser operations.

## 🛠️ External AI Agent Integration

### Using with LangGraph
```python
from langchain_mcp_adapters.client import MultiServerMCPClient

client = MultiServerMCPClient({
    "mcp_server": {
        "url": "https://your-mcp-server.com/mcp",
        "transport": "streamable_http",
    }
})

tools = await client.get_tools()
```

### Using with OpenAI Function Calling
```python
import requests

response = requests.get("https://your-mcp-server.com/mcp")
tools = response.json()
```

## 🔒 Security

- Non-root container user
- Dangerous command blacklist
- Environment variable configuration
- Input validation and error handling

## 📊 Features

- ✅ **50+ MCP Tools** - Comprehensive toolset for automation
- ✅ **Streamable HTTP** - Easy integration with any AI agent
- ✅ **Production Ready** - Health checks, proper logging, security measures
- ✅ **Coolify Optimized** - Environment variable configuration, unique port
- ✅ **Lightweight** - Minimal dependencies, fast startup 