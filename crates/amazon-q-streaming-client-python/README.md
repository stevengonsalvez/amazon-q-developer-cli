# Amazon Q Streaming Client for Python

A Python client library for interacting with the Amazon Q streaming API, designed to work seamlessly with tokens exported from the Amazon Q CLI.

## Installation

```bash
pip install -e .
```

## Quick Start

### 1. Export Token from CLI

First, export your authentication token using the Amazon Q CLI:

```bash
q user export-token > tokens.json
```

### 2. Use the Python Client

```python
import asyncio
import json
from amazon_q_streaming_client import QStreamingClient

async def main():
    # Load the exported token
    with open('tokens.json', 'r') as f:
        token_data = json.load(f)
    
    access_token = token_data['accessToken']
    
    # Create and use the streaming client
    async with QStreamingClient(access_token=access_token) as client:
        async for event in client.generate_assistant_response(
            user_message_content="Hello, can you help me with Python?",
            conversation_id=None,
            history=None
        ):
            event_type = type(event).__name__
            print(f"Received {event_type}")
            
            # Handle different event types
            if hasattr(event, 'content'):
                print(f"Content: {event.content}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Features

- ✅ **Seamless CLI Integration**: Works with tokens exported from `q user export-token`
- ✅ **Proper AWS Event Stream Parsing**: Handles binary AWS event stream protocol
- ✅ **Multiple Event Types**: Supports all Amazon Q event types (AssistantResponse, ToolUse, Citation, etc.)
- ✅ **Conversation History**: Support for maintaining conversation context
- ✅ **Async/Await**: Modern Python async interface
- ✅ **Type Safety**: Full Pydantic model validation

## Event Types

The client yields different event types during streaming:

- `MessageMetadataEvent`: Metadata about the conversation
- `AssistantResponseMessage`: Text responses from the assistant
- `ToolUseEvent`: When the assistant uses tools
- `CitationEvent`: Source citations
- `FollowupPromptEvent`: Suggested follow-up questions
- `CodeReferenceEvent`: Code references and examples
- `InvalidStateEvent`: Error conditions

## Advanced Usage

### With Conversation History

```python
async with QStreamingClient(access_token=access_token) as client:
    # First message
    conversation_id = "my-conversation-123"
    history = []
    
    async for event in client.generate_assistant_response(
        user_message_content="Write a Python function to calculate fibonacci",
        conversation_id=conversation_id,
        history=history
    ):
        # Process events...
        pass
    
    # Follow-up message with context
    async for event in client.generate_assistant_response(
        user_message_content="Can you make it more efficient?",
        conversation_id=conversation_id,
        history=history  # Include previous conversation
    ):
        # Process events...
        pass
```

### Error Handling

```python
try:
    async with QStreamingClient(access_token=access_token) as client:
        async for event in client.generate_assistant_response("Hello"):
            print(f"Event: {event}")
except httpx.HTTPStatusError as e:
    print(f"HTTP error: {e.response.status_code}")
except Exception as e:
    print(f"Other error: {e}")
```

## Requirements

- Python 3.8+
- httpx
- pydantic

## Development

To run tests:

```bash
python test_updated_client.py
```

## Integration with Amazon Q CLI

This client is designed to work with the Amazon Q CLI's token export feature:

1. **Login**: `q login` (if not already logged in)
2. **Export Token**: `q user export-token`
3. **Use Token**: Pass the `accessToken` to the Python client

The client automatically handles token refresh and AWS event stream parsing.
