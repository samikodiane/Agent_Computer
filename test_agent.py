#!/usr/bin/env python3
"""
Simple test script to verify the agent server setup.
"""

import requests
import json
import time
import os

# Configuration - single port setup
BASE_URL = "http://localhost:8000"
MCP_URL = f"{BASE_URL}/mcp"
AGENT_URL = f"{BASE_URL}/agent"
MEMORY_URL = f"{BASE_URL}/memory"

def test_server():
    """Test if unified server is running."""
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"✅ Unified Server: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ Unified Server: {e}")
        return False

def test_mcp_endpoint():
    """Test if MCP endpoint is accessible."""
    try:
        response = requests.get(f"{MCP_URL}/", timeout=5)
        print(f"✅ MCP Endpoint: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ MCP Endpoint: {e}")
        return False

def test_agent_endpoint():
    """Test if agent endpoint is accessible."""
    try:
        response = requests.get(f"{AGENT_URL}", timeout=5)
        print(f"✅ Agent Endpoint: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ Agent Endpoint: {e}")
        return False

def test_chat():
    """Test chat functionality."""
    try:
        data = {"message": "Hello! Can you tell me what tools you have available?"}
        response = requests.post(f"{AGENT_URL}", json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Chat Test: {result['success']}")
            print(f"   Response: {result['response'][:100]}...")
            return True
        else:
            print(f"❌ Chat Test: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Chat Test: {e}")
        return False

def test_memory():
    """Test memory functionality."""
    try:
        # Get memory
        response = requests.get(f"{MEMORY_URL}", timeout=5)
        if response.status_code == 200:
            memory = response.json()
            print(f"✅ Memory Test: {len(memory['memory'])} items")
            return True
        else:
            print(f"❌ Memory Test: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Memory Test: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing Unified Agent Server Setup")
    print("=" * 40)
    
    # Check environment variables
    print("\n📋 Environment Check:")
    providers = ["OPENAI_API_KEY", "GOOGLE_API_KEY", "ANTHROPIC_API_KEY"]
    for provider in providers:
        if os.getenv(provider):
            print(f"✅ {provider}: Set")
        else:
            print(f"⚠️  {provider}: Not set")
    
    print(f"\n🔧 Configuration:")
    print(f"   LLM Provider: {os.getenv('LLM_PROVIDER', 'Not set')}")
    print(f"   Model: {os.getenv('LLM_MODEL_NAME', 'Not set')}")
    print(f"   Base URL: {BASE_URL}")
    
    # Test server
    print("\n🌐 Server Tests:")
    server_ok = test_server()
    
    if not server_ok:
        print("\n❌ Server test failed. Make sure the server is running:")
        print("   python agent_endpoint.py")
        return
    
    # Wait a moment for server to be ready
    time.sleep(2)
    
    # Test endpoints
    print("\n🔗 Endpoint Tests:")
    mcp_ok = test_mcp_endpoint()
    agent_ok = test_agent_endpoint()
    
    # Test functionality
    print("\n🤖 Functionality Tests:")
    chat_ok = test_chat()
    memory_ok = test_memory()
    
    # Summary
    print("\n📊 Test Summary:")
    print("=" * 40)
    print(f"   Unified Server: {'✅' if server_ok else '❌'}")
    print(f"   MCP Endpoint: {'✅' if mcp_ok else '❌'}")
    print(f"   Agent Endpoint: {'✅' if agent_ok else '❌'}")
    print(f"   Chat Function: {'✅' if chat_ok else '❌'}")
    print(f"   Memory Function: {'✅' if memory_ok else '❌'}")
    
    if all([server_ok, mcp_ok, agent_ok, chat_ok, memory_ok]):
        print("\n🎉 All tests passed! Your unified agent server is working correctly.")
        print(f"\n📡 Available endpoints:")
        print(f"   {BASE_URL}/ - Root info")
        print(f"   {BASE_URL}/mcp - MCP server")
        print(f"   {BASE_URL}/agent - Agent chat")
        print(f"   {BASE_URL}/memory - Memory management")
    else:
        print("\n⚠️  Some tests failed. Check the logs above for details.")

if __name__ == "__main__":
    main() 