# Coolify Deployment Guide - MCP Server

This guide will help you deploy your MCP Server to Coolify with proper port configuration.

## 🚀 Step-by-Step Deployment

### 1. GitHub Repository Setup

1. **Create a new GitHub repository**
2. **Push your code:**
```bash
git add .
git commit -m "Add simplified MCP server for Coolify deployment"
git push origin main
```

3. **Monitor GitHub Actions:**
   - Go to your repository's **Actions** tab
   - The workflow will build and push to `ghcr.io/your-username/your-repo-name`

### 2. Coolify Configuration

#### A. Create New Application

1. **In Coolify Dashboard:**
   - Click **"New Service"** → **"Application"**
   - Select **"Dockerfile"** as build pack

2. **Repository Settings:**
   - **Repository URL:** `https://github.com/your-username/your-repo-name`
   - **Branch:** `main`
   - **Base Directory:** `/` (root directory)

#### B. Build Configuration

1. **Build Pack:** Dockerfile
2. **Port:** `8080` (or your preferred port)
3. **Health Check Path:** `/mcp` (MCP endpoint)

#### C. Environment Variables

**Required Variables:**
```
PORT=8080
```

**Optional Variables:**
```
MCP_WORKSPACE=/app/workspace
BROWSER_HEADLESS=true
```

#### D. Network Configuration

1. **Port:** `8080` (must match your PORT environment variable)
2. **Domain:** Your Coolify domain (e.g., `mcp.yourdomain.com`)
3. **SSL:** Enable if available

### 3. Deployment

1. **Click "Deploy"** in Coolify
2. **Monitor the build process:**
   - Check build logs for any errors
   - Ensure MCP server starts successfully

3. **Verify deployment:**
   - Visit your domain: `https://your-project-id.your-domain.com/mcp`
   - You should see the MCP server response

## 🔧 Troubleshooting

### Common Issues

#### 1. Port Conflicts
**Problem:** Container fails to start or health checks fail
**Solution:** 
- Change `PORT` environment variable in Coolify
- Update the port in Coolify's network settings
- Ensure both match

#### 2. Health Check Failures
**Problem:** Container shows as unhealthy
**Solution:**
- Check container logs in Coolify dashboard
- Verify the `/mcp` endpoint responds correctly
- Ensure MCP server starts properly

### Debug Commands

#### Check Container Logs
```bash
# In Coolify dashboard, go to your application
# Click on "Logs" tab to see real-time logs
```

#### Test Endpoints
```bash
# Test MCP endpoint
curl https://your-project-id.your-domain.com/mcp

# Test health check
curl https://your-project-id.your-domain.com/mcp
```

## 📊 Monitoring

### Health Check
The container includes a health check that:
- Runs every 30 seconds
- Checks the MCP endpoint (`/mcp`)
- Retries 3 times before marking as unhealthy

### Logs
Monitor these log messages:
- `"Starting MCP Server on 0.0.0.0:8080/mcp"`
- `"Available tools:"`
- `"Access MCP endpoint at: http://0.0.0.0:8080/mcp"`

### Performance
- **Memory:** ~200-500MB depending on usage
- **CPU:** Low usage
- **Storage:** Minimal, only workspace files

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