#!/usr/bin/env python3
"""
Simple test script to verify the agent server works locally
"""

import requests
import time
import os

def test_agent_server():
    """Test the agent server endpoints"""
    
    # Set default port
    port = int(os.getenv("PORT", 8080))
    base_url = f"http://localhost:{port}"
    
    print(f"Testing Agent Server at {base_url}")
    print("=" * 50)
    
    # Test 1: Root endpoint
    print("1. Testing root endpoint...")
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            print("✅ Root endpoint working")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")
    
    # Test 2: Memory stats
    print("\n2. Testing memory stats...")
    try:
        response = requests.get(f"{base_url}/memory/stats", timeout=10)
        if response.status_code == 200:
            print("✅ Memory stats working")
            print(f"   Stats: {response.json()}")
        else:
            print(f"❌ Memory stats failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Memory stats error: {e}")
    
    # Test 3: Agent chat (if API key is available)
    print("\n3. Testing agent chat...")
    if os.getenv("OPENAI_API_KEY"):
        try:
            response = requests.post(
                f"{base_url}/agent",
                json={"message": "Hello! What tools do you have available?"},
                timeout=30
            )
            if response.status_code == 200:
                print("✅ Agent chat working")
                result = response.json()
                print(f"   Response: {result.get('response', 'No response')[:100]}...")
            else:
                print(f"❌ Agent chat failed: {response.status_code}")
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"❌ Agent chat error: {e}")
    else:
        print("⚠️  Skipping agent chat test (no OPENAI_API_KEY)")
    
    print("\n" + "=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    test_agent_server() 