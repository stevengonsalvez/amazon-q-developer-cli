import httpx
import asyncio
import json
import struct
from typing import AsyncGenerator, Optional, Union, List
from .models import AssistantResponseMessage, ChatMessage, ConversationState, UserInputMessage, ToolUseEvent, CitationEvent, FollowupPromptEvent, CodeReferenceEvent, MessageMetadataEvent, InvalidStateEvent

class QStreamingClient:
    def __init__(self, access_token: str, base_url: str = "https://q.us-east-1.amazonaws.com/"):
        self.access_token = access_token
        self.base_url = base_url.rstrip('/')
        self.client = httpx.AsyncClient(base_url=self.base_url)

    async def _parse_aws_event_stream(self, response_bytes: bytes) -> AsyncGenerator[Union[AssistantResponseMessage, ToolUseEvent, CitationEvent, FollowupPromptEvent, CodeReferenceEvent, MessageMetadataEvent, InvalidStateEvent], None]:
        """
        Parse AWS event stream format.
        AWS event streams use a binary framing protocol with headers and payload.
        
        Format:
        - Total message length (4 bytes, big-endian)
        - Headers length (4 bytes, big-endian) 
        - Prelude CRC (4 bytes, big-endian)
        - Headers (variable length)
        - Payload (variable length)
        - Message CRC (4 bytes, big-endian)
        """
        offset = 0
        buffer = response_bytes
        
        while offset < len(buffer):
            # Need at least 12 bytes for the prelude
            if offset + 12 > len(buffer):
                break
                
            try:
                # Read message length (4 bytes, big-endian)
                total_length = struct.unpack('>I', buffer[offset:offset+4])[0]
                
                # Read headers length (4 bytes, big-endian)
                headers_length = struct.unpack('>I', buffer[offset+4:offset+8])[0]
                
                # Skip prelude CRC (4 bytes)
                headers_start = offset + 12
                
                # Calculate payload start and length
                payload_start = headers_start + headers_length
                payload_length = total_length - headers_length - 16  # 16 = prelude (12) + message CRC (4)
                
                # Ensure we have the complete message
                if offset + total_length > len(buffer):
                    break
                
                # Extract headers
                headers_data = buffer[headers_start:payload_start]
                headers = self._parse_event_headers(headers_data)
                
                # Extract payload
                payload_data = buffer[payload_start:payload_start + payload_length]
                
                # Parse the event based on headers
                event_type = headers.get(':event-type')
                if event_type and payload_data:
                    try:
                        payload_str = payload_data.decode('utf-8')
                        event_data = json.loads(payload_str)
                        
                        # Yield the appropriate event type
                        if event_type == 'messageMetadataEvent':
                            yield MessageMetadataEvent(**event_data)
                        elif event_type == 'assistantResponseEvent':
                            yield AssistantResponseMessage(**event_data)
                        elif event_type == 'toolUseEvent':
                            yield ToolUseEvent(**event_data)
                        elif event_type == 'citationEvent':
                            yield CitationEvent(**event_data)
                        elif event_type == 'followupPromptEvent':
                            yield FollowupPromptEvent(**event_data)
                        elif event_type == 'codeReferenceEvent':
                            yield CodeReferenceEvent(**event_data)
                        elif event_type == 'invalidStateEvent':
                            yield InvalidStateEvent(**event_data)
                        else:
                            print(f"Unknown event type: {event_type}")
                            
                    except (json.JSONDecodeError, TypeError) as e:
                        print(f"Failed to parse event payload: {e}")
                        print(f"Payload: {payload_data[:100]}...")
                
                # Move to next message
                offset += total_length
                
            except (struct.error, IndexError) as e:
                print(f"Failed to parse event stream: {e}")
                break

    def _parse_event_headers(self, headers_data: bytes) -> dict:
        """Parse AWS event stream headers."""
        headers = {}
        offset = 0
        
        while offset < len(headers_data):
            try:
                # Header name length (1 byte)
                if offset >= len(headers_data):
                    break
                name_length = headers_data[offset]
                offset += 1
                
                # Header name
                if offset + name_length > len(headers_data):
                    break
                name = headers_data[offset:offset + name_length].decode('utf-8')
                offset += name_length
                
                # Header value type (1 byte) - we'll assume string (7)
                if offset >= len(headers_data):
                    break
                value_type = headers_data[offset]
                offset += 1
                
                # Header value length (2 bytes, big-endian)
                if offset + 2 > len(headers_data):
                    break
                value_length = struct.unpack('>H', headers_data[offset:offset+2])[0]
                offset += 2
                
                # Header value
                if offset + value_length > len(headers_data):
                    break
                value = headers_data[offset:offset + value_length].decode('utf-8')
                offset += value_length
                
                headers[name] = value
                
            except (struct.error, UnicodeDecodeError) as e:
                print(f"Failed to parse header: {e}")
                break
                
        return headers

    async def generate_assistant_response(
        self,
        user_message_content: str,
        conversation_id: Optional[str] = None,
        history: Optional[List[ChatMessage]] = None,
    ) -> AsyncGenerator[Union[AssistantResponseMessage, ToolUseEvent, CitationEvent, FollowupPromptEvent, CodeReferenceEvent, MessageMetadataEvent, InvalidStateEvent], None]:
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        # Create payload with correct structure matching Rust serialization
        payload = {
            "conversationState": {
                "currentMessage": {
                    "userInputMessage": {
                        "content": user_message_content
                    }
                },
                "chatTriggerType": "MANUAL"
            }
        }
        
        # Add optional fields
        if conversation_id:
            payload["conversationState"]["conversationId"] = conversation_id
            
        if history:
            # Convert history to proper format
            payload["conversationState"]["history"] = [
                msg.model_dump(by_alias=True, exclude_none=True) for msg in history
            ]

        response = await self.client.post(
            "/generateAssistantResponse",
            headers=headers,
            json=payload,
            timeout=None,  # Streaming responses can take a long time
        )
        response.raise_for_status()

        # Process the streaming response
        async for chunk in response.aiter_bytes():
            async for event in self._parse_aws_event_stream(chunk):
                yield event

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
