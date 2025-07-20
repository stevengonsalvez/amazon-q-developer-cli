#!/usr/bin/env python3
"""
Example usage of the Amazon Q Python Streaming Client

This example shows how to:
1. Export a token from the Amazon Q CLI
2. Use the token with the Python streaming client
3. Handle different event types
"""

import asyncio
import json
import subprocess
import sys
from amazon_q_streaming_client import QStreamingClient

async def main():
    print("🚀 Amazon Q Python Streaming Client Example")
    print("=" * 50)
    
    # Step 1: Export token from CLI
    print("1. Exporting token from Amazon Q CLI...")
    try:
        result = subprocess.run(
            ["q", "user", "export-token"],
            capture_output=True,
            text=True,
            check=True
        )
        
        token_data = json.loads(result.stdout)
        access_token = token_data["accessToken"]
        print("   ✅ Token exported successfully")
        
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Failed to export token: {e}")
        print("   Make sure you're logged in with: q login")
        return
    except json.JSONDecodeError as e:
        print(f"   ❌ Failed to parse token: {e}")
        return
    
    # Step 2: Use the streaming client
    print("\n2. Using the streaming client...")
    
    try:
        async with QStreamingClient(access_token=access_token) as client:
            print("   📤 Asking: 'Can you help me write a Python function to reverse a string?'")
            
            response_content = ""
            event_count = 0
            
            async for event in client.generate_assistant_response(
                user_message_content="Can you help me write a Python function to reverse a string?",
                conversation_id=None,
                history=None
            ):
                event_count += 1
                event_type = type(event).__name__
                
                # Handle different event types
                if event_type == "AssistantResponseMessage":
                    content = getattr(event, 'content', '')
                    if content:
                        response_content += content
                        print(f"   📝 {content}", end='', flush=True)
                
                elif event_type == "MessageMetadataEvent":
                    print(f"   📊 Conversation metadata received")
                
                elif event_type == "FollowupPromptEvent":
                    print(f"   💡 Follow-up suggestion available")
                
                elif event_type == "CitationEvent":
                    print(f"   📚 Citation provided")
                
                else:
                    print(f"   📨 Received {event_type}")
            
            print(f"\n\n   📊 Summary:")
            print(f"      Events received: {event_count}")
            print(f"      Response length: {len(response_content)} characters")
            print("   ✅ Example completed successfully!")
            
    except Exception as e:
        print(f"   ❌ Error using streaming client: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
