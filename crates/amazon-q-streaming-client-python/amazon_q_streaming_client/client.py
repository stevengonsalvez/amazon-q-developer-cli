import httpx
import asyncio
import json
from typing import AsyncGenerator, Optional, Union
from .models import AssistantResponseMessage, ChatMessage, ConversationState, UserInputMessage, ToolUseEvent, CitationEvent, FollowupPromptEvent, CodeReferenceEvent, MessageMetadataEvent, InvalidStateEvent

class QStreamingClient:
    def __init__(self, access_token: str, base_url: str = "https://codewhisperer.us-east-1.amazonaws.com/"):
        self.access_token = access_token
        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=self.base_url)

    async def _parse_event_stream(self, response_bytes: bytes) -> AsyncGenerator[Union[AssistantResponseMessage, ToolUseEvent, CitationEvent, FollowupPromptEvent, CodeReferenceEvent, MessageMetadataEvent, InvalidStateEvent], None]:
        # This is a simplified parser based on common AWS event stream patterns.
        # A robust implementation would need to handle framing, checksums, etc.
        # For now, we'll assume each chunk is a complete JSON event.
        # In a real AWS event stream, you'd read a header, then the payload length, then the payload.
        # For simplicity, we're assuming the httpx aiter_bytes() yields full messages.
        try:
            event_data = json.loads(response_bytes.decode('utf-8'))
            # AWS event streams often have a top-level key that indicates the event type
            # and contains the actual event data. We'll look for that.
            if len(event_data) == 1:
                event_type = list(event_data.keys())[0]
                payload = event_data[event_type]

                if event_type == 'assistantResponseEvent':
                    yield AssistantResponseMessage(**payload)
                elif event_type == 'toolUseEvent':
                    yield ToolUseEvent(**payload)
                elif event_type == 'citationEvent':
                    yield CitationEvent(**payload)
                elif event_type == 'followupPromptEvent':
                    yield FollowupPromptEvent(**payload)
                elif event_type == 'codeReferenceEvent':
                    yield CodeReferenceEvent(**payload)
                elif event_type == 'messageMetadataEvent':
                    yield MessageMetadataEvent(**payload)
                elif event_type == 'invalidStateEvent':
                    yield InvalidStateEvent(**payload)
                else:
                    print(f"Unknown event type: {event_type}")
            else:
                print(f"Unexpected event data format: {event_data}")
        except json.JSONDecodeError:
            print(f"Could not decode JSON from chunk: {response_bytes}")

    async def generate_assistant_response(
        self,
        user_message_content: str,
        conversation_id: Optional[str] = None,
        history: Optional[list[ChatMessage]] = None,
    ) -> AsyncGenerator[Union[AssistantResponseMessage, ToolUseEvent, CitationEvent, FollowupPromptEvent, CodeReferenceEvent, MessageMetadataEvent, InvalidStateEvent], None]:
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        user_input_message = UserInputMessage(content=user_message_content)
        current_message = ChatMessage(root=user_input_message)

        conversation_state = ConversationState(
            conversation_id=conversation_id,
            history=history,
            current_message=current_message,
            chat_trigger_type="MANUAL", # Assuming manual for now
        )

        response = await self.client.post(
            "/generateAssistantResponse", # This endpoint is illustrative
            headers=headers,
            json=conversation_state.model_dump(by_alias=True, exclude_none=True),
            timeout=None, # Streaming responses can take a long time
        )
        response.raise_for_status()

        async for chunk in response.aiter_bytes():
            async for event in self._parse_event_stream(chunk):
                yield event

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
