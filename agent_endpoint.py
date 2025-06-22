# FastAPI endpoint for agent interaction and memory management

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import uvicorn
import os
from agent import get_agent, invoke_agent_with_memory
from memory import get_full_memory, clear_memory, get_memory_by_category, get_tool_stats

app = FastAPI(title="Agent Server", description="LangGraph ReAct Agent with MCP Tools and Memory")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    message_count: int
    success: bool
    error: Optional[str] = None

class MemoryResponse(BaseModel):
    memory: List[Dict[str, Any]]

class StatsResponse(BaseModel):
    stats: Dict[str, int]

class ClearResponse(BaseModel):
    message: str
    success: bool

@app.get("/")
async def root():
    """Root endpoint with server information."""
    return {
        "message": "Agent Server with MCP Tools and Memory",
        "endpoints": {
            "chat": "/agent",
            "memory": "/memory",
            "memory_by_category": "/memory/category/{category}",
            "tool_stats": "/memory/stats",
            "clear_memory": "/memory/clear"
        },
        "available_categories": ["files", "terminal", "browser", "system", "utility", "other"]
    }

@app.post("/agent", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    """
    Send a message to the agent and get a response.
    The agent will use MCP tools and maintain conversation memory.
    """
    try:
        # Get the agent (will initialize if needed)
        agent = get_agent()
        
        # Invoke agent with the message
        result = invoke_agent_with_memory(request.message)
        
        return ChatResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")

@app.get("/memory", response_model=MemoryResponse)
async def get_memory():
    """
    Get the complete conversation memory in chronological order.
    Returns all user messages, agent responses, and tool calls.
    """
    try:
        memory = get_full_memory()
        return MemoryResponse(memory=memory)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Memory retrieval error: {str(e)}")

@app.get("/memory/category/{category}", response_model=MemoryResponse)
async def get_memory_by_category_endpoint(category: str):
    """Get memory filtered by tool category."""
    try:
        # Validate category
        valid_categories = ["files", "terminal", "browser", "system", "utility", "other"]
        if category not in valid_categories:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid category. Must be one of: {valid_categories}"
            )
        
        memory = get_memory_by_category(category)
        return MemoryResponse(memory=memory)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Memory retrieval error: {str(e)}")

@app.get("/memory/stats", response_model=StatsResponse)
async def get_tool_statistics():
    """Get tool usage statistics by category."""
    try:
        stats = get_tool_stats()
        return StatsResponse(stats=stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Statistics error: {str(e)}")

@app.delete("/memory/clear", response_model=ClearResponse)
async def clear_memory_endpoint():
    """
    Clear all conversation memory.
    This will reset the conversation history.
    """
    try:
        clear_memory()
        return ClearResponse(message="Memory cleared successfully", success=True)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Memory clearing error: {str(e)}")

if __name__ == "__main__":
    # Get port from environment or default to 8000
    port = int(os.getenv("PORT", 8000))
    
    print(f"Starting Agent Server on 0.0.0.0:{port}")
    print("Available endpoints:")
    print("  POST /agent - Send message to agent")
    print("  GET  /memory - Get conversation memory")
    print("  GET  /memory/category/{category} - Get memory by category")
    print("  GET  /memory/stats - Get tool statistics")
    print("  DELETE /memory/clear - Clear conversation memory")
    
    uvicorn.run(app, host="0.0.0.0", port=port) 