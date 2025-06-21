# Local MCP Server

A comprehensive MCP (Model Context Protocol) server with file system, web automation, and utility tools.

## Features

### File System Tools
- List directories and files
- Read and write files
- Create and delete files/folders
- Search files by pattern
- Get file metadata
- Zip/unzip files
- Directory tree visualization

### System Tools
- Execute shell commands
- Get system information
- List and kill processes
- Ping hosts

### Web Tools
- HTTP requests
- Web browser automation (Playwright)
- Screenshot capture
- Web scraping
- Advanced browser interactions (forms, dialogs, file uploads)
- Network request monitoring
- Accessibility testing

### Utility Tools
- Math operations
- Time operations
- Search and replace in files
- File diffing
- Code formatting

## Installation

### Local Installation

1. Install the required packages:
```bash
pip install -r requirements.txt
```

2. Install Playwright browsers:
```bash
playwright install
```

### Docker Installation (Recommended)

Build and run the container:
```bash
# Build the image
docker build -t mcp-server .

# Run the container
docker run -p 8000:8000 mcp-server
```

For development with volume mounting:
```bash
docker run -p 8000:8000 -v $(pwd)/workspace:/app/workspace mcp-server
```

### Coolify Deployment (Recommended for Production)

This MCP server is optimized for deployment with Coolify and supports subdomain routing.

#### 1. Build and Push the Image

```bash
# Build the image
docker build -t mcp-server .

# Tag for your registry (replace with your registry)
docker tag mcp-server your-registry.com/mcp-server:latest

# Push to registry
docker push your-registry.com/mcp-server:latest
```

#### 2. Coolify Configuration

In Coolify, create a new application with these settings:

**Basic Settings:**
- **Name**: `mcp-server`
- **Image**: `your-registry.com/mcp-server:latest`
- **Port**: `8000`

**Environment Variables:**
```bash
MCP_HOST=0.0.0.0
MCP_PORT=8000
MCP_PATH=/mcp
MCP_WORKSPACE=/app/workspace
BROWSER_HEADLESS=true
LOG_LEVEL=INFO
```

**Domain Configuration:**
- **Subdomain**: `mcp` (or your preferred subdomain)
- **Domain**: `your-domain.com`
- **SSL**: Enable automatic SSL certificates

**Volumes:**
- **Source**: `mcp-workspace`
- **Destination**: `/app/workspace`

**Health Check:**
- **Path**: `/mcp`
- **Interval**: `30s`
- **Timeout**: `10s`
- **Retries**: `3`

#### 3. Access Your MCP Server

Once deployed, your MCP server will be available at:
- **URL**: `https://mcp.your-domain.com/mcp`
- **Health Check**: `https://mcp.your-domain.com/mcp`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_HOST` | `0.0.0.0` | Host to bind the server to |
| `MCP_PORT` | `8000` | Port to run the server on |
| `MCP_PATH` | `/mcp` | URL path for the MCP endpoint |
| `MCP_WORKSPACE` | `/app/workspace` | Directory for file operations |
| `BROWSER_HEADLESS` | `true` | Run browser in headless mode |
| `LOG_LEVEL` | `INFO` | Logging level |

## Usage

### Local
```bash
python mcp_server.py
```

### Docker
The server will start on `http://127.0.0.1:8000/mcp` when using Docker.

### Coolify
The server will be available at your configured subdomain, e.g., `https://mcp.your-domain.com/mcp`

## Container Features

- **Cross-platform compatibility**: Works on Linux, macOS, and Windows
- **Security**: Runs as non-root user
- **Health checks**: Automatic monitoring
- **Volume mounting**: Optional workspace directory
- **Browser automation**: Full Playwright support in containerized environment
- **Environment-based configuration**: Flexible deployment options
- **Subdomain support**: Optimized for reverse proxy setups

## Security

The server includes path safety checks to prevent access outside the allowed base directory. All file operations are restricted to the specified workspace directory.

## Browser Automation in Docker

The Docker setup includes:
- Chromium browser for web automation
- All necessary system dependencies
- Proper user permissions for browser operations
- Health checks to ensure the server is running correctly

## Coolify Integration Benefits

1. **Automatic SSL**: Coolify handles SSL certificates automatically
2. **Subdomain Routing**: Each container gets its own subdomain
3. **Health Monitoring**: Built-in health checks ensure service availability
4. **Persistent Storage**: Workspace volume persists across container restarts
5. **Easy Scaling**: Simple to scale horizontally if needed
6. **Environment Management**: Easy environment variable management through Coolify UI

## Dependencies

- `fastmcp`: MCP server framework
- `playwright`: Web browser automation
- `requests`: HTTP requests
- `psutil`: Cross-platform process management

All other dependencies are part of Python's standard library. 