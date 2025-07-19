# Amazon Q Streaming Client (Python)

This package provides a Python client for interacting with the Amazon Q streaming API. It is designed to be used by developers building custom tools and agentic frameworks that leverage Amazon Q's capabilities.

## Installation

```bash
pip install amazon-q-streaming-client
```

## Usage

```python
import asyncio
from amazon_q_streaming_client import QStreamingClient

async def main():
    # Replace with your actual access token
    access_token = "YOUR_ACCESS_TOKEN"
    client = QStreamingClient(access_token)

    async for event in client.generate_assistant_response("Hello, Amazon Q!"):
        if event.text_response:
            print(event.text_response.text)

if __name__ == "__main__":
    asyncio.run(main())
```
