# FastAPI endpoint for agent interaction and memory management

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
import uvicorn
import os
from agent import get_agent, invoke_agent_with_memory
from memory import get_full_memory, clear_memory

app = FastAPI(title="Agent Server", description="LangGraph Agent with MCP Tools and Memory")

# Pydantic models for request/response
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    message_count: int
    success: bool
    error: str = None

class MemoryResponse(BaseModel):
    memory: List[Dict[str, Any]]

class DeleteResponse(BaseModel):
    success: bool
    message: str

@app.get("/")
async def root():
    """Root endpoint with basic info."""
    return {
        "message": "Agent Server is running",
        "endpoints": {
            "mcp": "/mcp",
            "agent": "/agent", 
            "memory": "/memory"
        }
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
        
        return ChatResponse(
            response=result["response"],
            message_count=result["message_count"],
            success=result["success"],
            error=result.get("error")
        )
        
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

@app.delete("/memory", response_model=DeleteResponse)
async def delete_memory():
    """
    Clear all conversation memory.
    This will reset the conversation history.
    """
    try:
        clear_memory()
        return DeleteResponse(
            success=True,
            message="Memory cleared successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Memory deletion error: {str(e)}")

if __name__ == "__main__":
    # Fixed configuration for container deployment
    host = "0.0.0.0"
    port = 8000
    
    print(f"Starting Agent Server on {host}:{port}")
    print("Available endpoints:")
    print("  POST /agent - Send message to agent")
    print("  GET  /memory - Get conversation memory")
    print("  DELETE /memory - Clear conversation memory")
    
    uvicorn.run(app, host=host, port=port) 