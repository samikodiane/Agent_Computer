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

# Copy only the MCP server
COPY mcp_server.py .

# Create workspace directory and non-root user for security
RUN mkdir -p /app/workspace && \
    useradd -m -u 1000 mcpuser && \
    chown -R mcpuser:mcpuser /app

USER mcpuser

# Set workspace directory
ENV MCP_WORKSPACE=/app/workspace
ENV BROWSER_HEADLESS=true

# Use a unique default port for Coolify
ENV PORT=8080

# Expose the configurable port
EXPOSE 8080

# Health check with configurable port
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8080}/mcp || exit 1

# Run the MCP server directly
CMD ["python", "mcp_server.py"] 