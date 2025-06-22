# Coolify Deployment Guide

This guide will help you deploy your Agent Server to Coolify with proper port configuration and environment variables.

## 🚀 Step-by-Step Deployment

### 1. GitHub Repository Setup

1. **Create a new GitHub repository**
2. **Push your code:**
```bash
git add .
git commit -m "Add Coolify deployment configuration"
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
3. **Health Check Path:** `/` (root endpoint)

#### C. Environment Variables

**Required Variables:**
```
PORT=8080
MCP_SERVER_URL=https://your-project-id.your-domain.com
OPENAI_API_KEY=sk-your-openai-api-key
```

**Optional LLM Configuration:**
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
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
LLM_PROVIDER=anthropic
```

#### D. Network Configuration

1. **Port:** `8080` (must match your PORT environment variable)
2. **Domain:** Your Coolify domain (e.g., `agent.yourdomain.com`)
3. **SSL:** Enable if available

### 3. Deployment

1. **Click "Deploy"** in Coolify
2. **Monitor the build process:**
   - Check build logs for any errors
   - Ensure both MCP server and agent endpoint start successfully

3. **Verify deployment:**
   - Visit your domain: `https://your-project-id.your-domain.com`
   - You should see the API documentation

## 🔧 Troubleshooting

### Common Issues

#### 1. Port Conflicts
**Problem:** Container fails to start or health checks fail
**Solution:** 
- Change `PORT` environment variable in Coolify
- Update the port in Coolify's network settings
- Ensure both match

#### 2. Environment Variables Not Working
**Problem:** API keys not recognized or wrong provider used
**Solution:**
- Double-check environment variable names in Coolify
- Ensure no extra spaces or quotes
- Restart the deployment after changing variables

#### 3. Health Check Failures
**Problem:** Container shows as unhealthy
**Solution:**
- Check container logs in Coolify dashboard
- Verify the `/` endpoint responds correctly
- Ensure both services start properly

#### 4. MCP Server Connection Issues
**Problem:** Agent can't connect to MCP tools
**Solution:**
- Verify `MCP_SERVER_URL` is set correctly
- Ensure the URL matches your Coolify domain
- Check that both services are running on the same port

### Debug Commands

#### Check Container Logs
```bash
# In Coolify dashboard, go to your application
# Click on "Logs" tab to see real-time logs
```

#### Test Endpoints
```bash
# Test root endpoint
curl https://your-project-id.your-domain.com/

# Test memory stats
curl https://your-project-id.your-domain.com/memory/stats

# Test agent chat
curl -X POST https://your-project-id.your-domain.com/agent \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!"}'
```

## 📊 Monitoring

### Health Check
The container includes a health check that:
- Runs every 30 seconds
- Checks the root endpoint (`/`)
- Retries 3 times before marking as unhealthy

### Logs
Monitor these log messages:
- `"Starting Agent Server on port 8080"`
- `"MCP Server started successfully"`
- `"Agent Endpoint started successfully"`
- `"Both services are running on port 8080"`

### Performance
- **Memory:** ~500MB-1GB depending on usage
- **CPU:** Low to moderate usage
- **Storage:** SQLite database grows with conversation history

## 🔄 Updates

### Updating Your Deployment

1. **Push changes to GitHub:**
```bash
git add .
git commit -m "Update deployment"
git push origin main
```

2. **Redeploy in Coolify:**
   - Go to your application in Coolify
   - Click **"Redeploy"**
   - Monitor the build process

### Environment Variable Changes

1. **Update variables in Coolify dashboard**
2. **Redeploy the application**
3. **No code changes needed for configuration updates**

## 🎯 Best Practices

1. **Use unique ports:** Avoid common ports like 3000, 8000, 8080
2. **Secure API keys:** Never commit API keys to your repository
3. **Monitor logs:** Regularly check container logs for issues
4. **Test locally:** Use `test_local.py` before deploying
5. **Backup data:** SQLite database is persistent but consider backups

## 📞 Support

If you encounter issues:

1. **Check Coolify logs** first
2. **Verify environment variables** are set correctly
3. **Test locally** with `python test_local.py`
4. **Check GitHub Actions** for build issues
5. **Review this guide** for common solutions 