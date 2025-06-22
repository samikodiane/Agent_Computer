# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    procps \
    libxss1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium
RUN playwright install-deps

# Copy application files
COPY mcp_server.py .
COPY model.py .
COPY agent.py .
COPY memory.py .
COPY agent_endpoint.py .

# Create workspace directory and non-root user for security
RUN mkdir -p /app/workspace && \
    useradd -m -u 1000 mcpuser && \
    chown -R mcpuser:mcpuser /app

USER mcpuser

# Set workspace directory
ENV MCP_WORKSPACE=/app/workspace
ENV BROWSER_HEADLESS=true

# The base URL for everything
ENV MCP_SERVER_URL=https://project_id.my_domain_name.domain

# LLM Configuration
ENV LLM_PROVIDER=openai
ENV LLM_MODEL_NAME=gpt-3.5-turbo
ENV LLM_TEMPERATURE=0.7

# API Key environment variables (to be set at runtime)
ENV OPENAI_API_KEY=""
ENV GOOGLE_API_KEY=""
ENV ANTHROPIC_API_KEY=""

# Optional provider-specific environment variables
ENV OPENAI_BASE_URL=""
ENV OPENAI_ORGANIZATION=""

# Expose single port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Default command to run both MCP server and agent endpoint
CMD ["sh", "-c", "python mcp_server.py & python agent_endpoint.py"] 