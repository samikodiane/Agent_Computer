# Agent script using LangGraph ReAct agent with our model configuration and MCP server integration

import os
import asyncio
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from model import get_model
from memory import get_checkpointer, get_memory_manager

# Get our configured model
model = get_model()

# Get memory manager and checkpointer
memory_manager = get_memory_manager()
checkpointer = get_checkpointer()

# Global variable to store the agent
agent = None

async def setup_agent_with_mcp():
    """Setup the agent with MCP server integration and memory."""
    global agent
    
    # Use the base URL for Coolify deployment: project_id.my_domain_name.domain
    base_url = os.getenv("MCP_SERVER_URL", "http://localhost:8000")
    mcp_url = f"{base_url}/mcp"
    
    # Use the official MultiServerMCPClient approach
    client = MultiServerMCPClient(
        {
            "mcp_server": {
                # Our MCP server runs on streamable-http transport
                "url": mcp_url,
                "transport": "streamable_http",
            }
        }
    )
    
    # Get tools from MCP server
    tools = await client.get_tools()
    
    # Create ReAct agent with our model, MCP tools, and memory
    agent = create_react_agent(
        model=model,
        tools=tools,
        prompt="You are a helpful assistant with access to various tools through the MCP server.",
        checkpointer=checkpointer  # Enable memory persistence
    )
    
    return agent

def get_agent():
    """Get the configured ReAct agent with MCP tools and memory."""
    global agent
    if agent is None:
        # Initialize the agent if not already done
        agent = asyncio.run(setup_agent_with_mcp())
    return agent

def invoke_agent_with_memory(message: str):
    """
    Invoke the agent with memory management for single conversation.
    
    Args:
        message: The user message
        
    Returns:
        Dict containing the agent's response and metadata
    """
    try:
        # Use a fixed thread_id since we only have one conversation per container
        config = {"configurable": {"thread_id": "main"}}
        
        # Invoke the agent
        response = agent.invoke(
            {"messages": [{"role": "user", "content": message}]},
            config=config
        )
        
        # Extract the last AI message as the response
        messages = response.get("messages", [])
        ai_messages = [msg for msg in messages if hasattr(msg, '__class__') and msg.__class__.__name__ == 'AIMessage']
        
        if ai_messages:
            last_ai_message = ai_messages[-1]
            response_content = last_ai_message.content
        else:
            response_content = "No response generated"
        
        return {
            "response": response_content,
            "message_count": len(messages),
            "success": True
        }
        
    except Exception as e:
        return {
            "response": f"Error: {str(e)}",
            "message_count": 0,
            "success": False,
            "error": str(e)
        }