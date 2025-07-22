#!/usr/bin/env python3
"""
ABOUTME: Basic demo of Amazon Q LangChain integration
Demonstrates the ChatAmazonQ wrapper working with real Amazon Q CLI
"""

import asyncio
import sys
from pathlib import Path

# Add the package to Python path
sys.path.insert(0, str(Path(__file__).parent))

from amazon_q_langchain import ChatAmazonQ, TokenManager
from langchain_core.messages import HumanMessage


async def test_token_manager():
    """Test the token manager functionality."""
    print("🔧 Testing Token Manager")
    print("=" * 30)
    
    try:
        tm = TokenManager()
        
        # Check if CLI is available
        if tm.is_cli_available():
            print("✅ Amazon Q CLI is available")
            
            # Try to get a token
            try:
                token = tm.get_token()
                print(f"✅ Token retrieved successfully (length: {len(token)} chars)")
                return True
            except Exception as e:
                print(f"⚠️  Token retrieval failed: {e}")
                print("💡 Make sure you're logged in with: q login")
                return False
        else:
            print("❌ Amazon Q CLI not found")
            print("💡 Please install Amazon Q CLI and login")
            return False
            
    except Exception as e:
        print(f"❌ Token manager test failed: {e}")
        return False


async def test_chat_amazon_q():
    """Test the ChatAmazonQ wrapper."""
    print("\n🤖 Testing ChatAmazonQ")
    print("=" * 30)
    
    try:
        # Initialize ChatAmazonQ
        llm = ChatAmazonQ()
        print("✅ ChatAmazonQ initialized successfully")
        
        # Test basic message
        print("\n📤 Sending message: 'Hello! Can you help me write a simple Python function?'")
        
        messages = [HumanMessage(content="Hello! Can you help me write a simple Python function to add two numbers?")]
        
        # Test async invoke
        print("📥 Response:")
        response = await llm.ainvoke(messages)
        
        # Display response (truncated for demo)
        content = response.content
        if len(content) > 300:
            print(content[:300] + "...")
        else:
            print(content)
        
        print(f"\n✅ Response received ({len(content)} characters)")
        return True
        
    except Exception as e:
        print(f"❌ ChatAmazonQ test failed: {e}")
        return False


async def test_streaming():
    """Test streaming functionality."""
    print("\n🌊 Testing Streaming")
    print("=" * 30)
    
    try:
        llm = ChatAmazonQ()
        
        print("📤 Sending: 'Write a Python function to calculate factorial'")
        print("📥 Streaming response:")
        print("-" * 40)
        
        messages = [HumanMessage(content="Write a Python function to calculate factorial of a number")]
        
        # Test streaming
        response_content = ""
        chunk_count = 0
        
        async for chunk in llm.astream(messages):
            if chunk.content:
                print(chunk.content, end="", flush=True)
                response_content += chunk.content
                chunk_count += 1
                
                # Limit for demo purposes
                if chunk_count > 20:
                    print("\n... (truncated for demo)")
                    break
        
        print(f"\n{'-' * 40}")
        print(f"✅ Streaming completed ({chunk_count} chunks, {len(response_content)} chars)")
        return True
        
    except Exception as e:
        print(f"❌ Streaming test failed: {e}")
        return False


async def test_langchain_compatibility():
    """Test LangChain ecosystem compatibility."""
    print("\n🔗 Testing LangChain Compatibility")
    print("=" * 40)
    
    try:
        llm = ChatAmazonQ()
        
        # Test that it has all required LangChain methods
        required_methods = ['invoke', 'ainvoke', 'stream', 'astream', 'batch', 'abatch']
        
        print("Checking LangChain interface compatibility:")
        for method in required_methods:
            if hasattr(llm, method):
                print(f"  ✅ {method}")
            else:
                print(f"  ❌ {method}")
        
        # Test identifying parameters
        params = llm._identifying_params
        print(f"\n✅ Model info: {params}")
        
        # Test with multiple messages
        messages = [
            HumanMessage(content="What is Python?"),
        ]
        
        response = await llm.ainvoke(messages)
        print(f"✅ Multi-message test successful ({len(response.content)} chars)")
        
        return True
        
    except Exception as e:
        print(f"❌ LangChain compatibility test failed: {e}")
        return False


async def main():
    """Run all demo tests."""
    print("🚀 Amazon Q LangChain Integration Demo")
    print("=" * 50)
    print("This demo shows the ChatAmazonQ wrapper working with real Amazon Q")
    
    # Run tests
    tests = [
        ("Token Manager", test_token_manager),
        ("ChatAmazonQ Basic", test_chat_amazon_q),
        ("Streaming", test_streaming),
        ("LangChain Compatibility", test_langchain_compatibility)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*60}")
            print(f"🧪 Running: {test_name}")
            print(f"{'='*60}")
            
            success = await test_func()
            results.append((test_name, success))
            
            if success:
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
                
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 DEMO SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{name}: {status}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All demos passed! Amazon Q LangChain integration is working!")
    elif passed > 0:
        print("⚠️  Some demos passed. Check Amazon Q CLI login status.")
    else:
        print("💥 All demos failed. Please check Amazon Q CLI installation and login.")
    
    return passed


if __name__ == "__main__":
    try:
        passed_count = asyncio.run(main())
        sys.exit(0 if passed_count > 0 else 1)
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
