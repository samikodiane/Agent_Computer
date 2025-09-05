# Coolify Deployment Guide for MCP Server

This guide helps you deploy the MCP Server to Coolify using Server-Sent Events (SSE) transport.

## 🚀 Quick Deployment

### 1. GitHub Repository Setup

1. **Push your code to GitHub** (if not already done)
2. **GitHub Actions** will automatically build and push to GHCR

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
MCP_WORKSPACE=/app/workspace
BROWSER_HEADLESS=true
LOG_LEVEL=INFO
```

### 4. Network Configuration

- **Port:** `8080` (must match your PORT environment variable)
- **Domain:** Your Coolify domain (e.g., `mcp.yourdomain.com`)

## 📡 MCP Endpoint Access

### SSE Endpoint
```
GET https://your-domain.com/mcp
```

**Transport:** Server-Sent Events (SSE) - Real-time streaming with automatic reconnection

### Testing the Endpoint
```bash
curl -H "Accept: text/event-stream" https://your-domain.com/mcp
```

## 🔧 Manual Docker Deployment

If you prefer to build and push manually:

### 1. Build and Tag
```bash
docker build -t ghcr.io/yourusername/mcp-server:latest .
```

### 2. Login to GHCR
```bash
echo $GITHUB_TOKEN | docker login ghcr.io -u yourusername --password-stdin
```

### 3. Push to GHCR
```bash
docker push ghcr.io/yourusername/mcp-server:latest
```

### 4. Coolify Configuration
- **Image:** `ghcr.io/yourusername/mcp-server:latest`
- **Port:** `8080`
- **Environment Variables:** As listed above

## 🛠️ External AI Agent Integration

### LangGraph Integration
```python
from langchain_mcp_adapters.client import MultiServerMCPClient

client = MultiServerMCPClient({
    "mcp_server": {
        "url": "https://your-domain.com/mcp",
        "transport": "sse",
    }
})

tools = await client.get_tools()
```

### Direct SSE Connection
```javascript
const eventSource = new EventSource('https://your-domain.com/mcp');

eventSource.onmessage = function(event) {
    console.log('Received:', event.data);
};

eventSource.onerror = function(error) {
    console.error('SSE Error:', error);
};
```

## 🔒 Security Considerations

- **HTTPS Required** - SSE connections should use HTTPS in production
- **CORS Configuration** - Ensure proper CORS headers for your domain
- **Rate Limiting** - Consider implementing rate limiting for the `/mcp` endpoint
- **Authentication** - Add authentication if needed for your use case

## 📊 Health Check

The server includes health checks and will automatically restart if needed. Monitor the logs in Coolify for any issues.

## 🚨 Troubleshooting

### Common Issues

1. **Port Mismatch** - Ensure PORT environment variable matches Coolify port configuration
2. **SSE Connection Issues** - Check that your client supports SSE transport
3. **Browser Automation** - Ensure BROWSER_HEADLESS=true for containerized environment

### Logs
Check Coolify logs for detailed error messages and debugging information.

## 🔄 Updates

### Updating Your Deployment

1. **Push changes to GitHub:**
```bash
git add .
git commit -m "Update MCP server"
git push origin main
```

2. **Redeploy in Coolify:**
   - Go to your application in Coolify
   - Click **"Redeploy"**
   - Monitor the build process

## 🎯 Best Practices

1. **Use unique ports:** Avoid common ports like 3000, 8000, 8080
2. **Monitor logs:** Regularly check container logs for issues
3. **Test locally:** Use `python mcp_server.py` before deploying
4. **Backup workspace:** Consider persistent storage for important files

## 📞 Support

If you encounter issues:

1. **Check Coolify logs** first
2. **Verify environment variables** are set correctly
3. **Test locally** with `python mcp_server.py`
4. **Check GitHub Actions** for build issues
5. **Review this guide** for common solutions 