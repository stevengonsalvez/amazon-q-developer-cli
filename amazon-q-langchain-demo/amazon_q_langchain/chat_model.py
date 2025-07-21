"""
ABOUTME: LangChain-compatible chat model wrapper for Amazon Q
Provides a drop-in replacement for ChatOpenAI using Amazon Q streaming client
"""

import asyncio
import logging
from typing import Any, Dict, Iterator, List, Optional, Union, AsyncIterator

from langchain_core.callbacks import CallbackManagerForLLMRun, AsyncCallbackManagerForLLMRun
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage, SystemMessage
from langchain_core.outputs import ChatGeneration, ChatResult, ChatGenerationChunk
from pydantic import Field

# Import the streaming client from the main project
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "crates" / "amazon-q-streaming-client-python"))

try:
    from amazon_q_streaming_client.client import QStreamingClient
    from amazon_q_streaming_client.models import AssistantResponseMessage, MessageMetadataEvent
except ImportError:
    # Fallback for when streaming client is not available
    QStreamingClient = None
    AssistantResponseMessage = None
    MessageMetadataEvent = None

from .token_manager import TokenManager

logger = logging.getLogger(__name__)


class ChatAmazonQ(BaseChatModel):
    """
    LangChain-compatible chat model for Amazon Q.
    
    This class provides a drop-in replacement for ChatOpenAI that uses
    the Amazon Q streaming API with automatic CLI token management.
    
    Example:
        ```python
        from amazon_q_langchain import ChatAmazonQ
        
        # Basic usage
        llm = ChatAmazonQ()
        response = llm.invoke("Hello, how can you help me?")
        
        # With streaming
        for chunk in llm.stream("Write a Python function"):
            print(chunk.content, end="", flush=True)
        ```
    """
    
    # Configuration
    auto_token_refresh: bool = Field(default=True, description="Automatically refresh tokens")
    cli_command: str = Field(default="q", description="Amazon Q CLI command")
    base_url: str = Field(default="https://q.us-east-1.amazonaws.com/", description="API base URL")
    request_timeout: Optional[float] = Field(default=None, description="Request timeout in seconds")
    
    # Internal state
    _token_manager: Optional[TokenManager] = None
    _client: Optional[QStreamingClient] = None
    
    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True
    
    def __init__(self, **kwargs):
        """Initialize ChatAmazonQ with optional configuration."""
        super().__init__(**kwargs)
        
        # Check if streaming client is available
        if QStreamingClient is None:
            raise RuntimeError(
                "Amazon Q streaming client not found. "
                "Please ensure the streaming client is properly installed."
            )
        
        # Initialize token manager
        if self.auto_token_refresh:
            self._token_manager = TokenManager(cli_command=self.cli_command)
            
            # Verify CLI is available
            if not self._token_manager.is_cli_available():
                raise RuntimeError(
                    f"Amazon Q CLI '{self.cli_command}' not found. "
                    "Please install and login with: q login"
                )
    
    @property
    def _llm_type(self) -> str:
        """Return identifier for this LLM type."""
        return "amazon-q"
    
    def _get_client(self) -> QStreamingClient:
        """Get or create streaming client with fresh token."""
        if self._token_manager:
            access_token = self._token_manager.get_token()
        else:
            raise RuntimeError("No token manager configured and no manual token provided")
        
        # Create new client with fresh token
        return QStreamingClient(
            access_token=access_token,
            base_url=self.base_url
        )
    
    def _convert_messages_to_amazon_q_format(self, messages: List[BaseMessage]) -> str:
        """
        Convert LangChain messages to Amazon Q format.
        
        For now, we'll concatenate all messages into a single user message.
        In the future, we could maintain conversation history properly.
        """
        content_parts = []
        
        for message in messages:
            if isinstance(message, HumanMessage):
                content_parts.append(f"User: {message.content}")
            elif isinstance(message, AIMessage):
                content_parts.append(f"Assistant: {message.content}")
            elif isinstance(message, SystemMessage):
                content_parts.append(f"System: {message.content}")
            else:
                content_parts.append(f"Message: {message.content}")
        
        return "\n".join(content_parts)
    
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Generate response synchronously."""
        # Run async version in sync context
        return asyncio.run(self._agenerate(messages, stop, run_manager, **kwargs))
    
    async def _agenerate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Generate response asynchronously."""
        try:
            # Convert messages to Amazon Q format
            user_message = self._convert_messages_to_amazon_q_format(messages)
            
            # Get streaming client
            client = self._get_client()
            
            # Collect response content
            response_content = ""
            metadata = {}
            
            async with client:
                async for event in client.generate_assistant_response(
                    user_message_content=user_message,
                    conversation_id=kwargs.get("conversation_id"),
                    history=None  # TODO: Implement conversation history
                ):
                    if isinstance(event, AssistantResponseMessage):
                        if event.content:
                            response_content += event.content
                            
                            # Stream to callback if available
                            if run_manager:
                                await run_manager.on_llm_new_token(event.content)
                    
                    elif isinstance(event, MessageMetadataEvent):
                        if event.conversation_id:
                            metadata["conversation_id"] = event.conversation_id
                        if event.utterance_id:
                            metadata["utterance_id"] = event.utterance_id
            
            # Create chat generation
            generation = ChatGeneration(
                message=AIMessage(content=response_content),
                generation_info=metadata
            )
            
            return ChatResult(generations=[generation])
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise
    
    def _stream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:
        """Stream response synchronously."""
        # Run async version in sync context
        async_gen = self._astream(messages, stop, run_manager, **kwargs)
        
        # Convert async generator to sync iterator
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            while True:
                try:
                    chunk = loop.run_until_complete(async_gen.__anext__())
                    yield chunk
                except StopAsyncIteration:
                    break
        finally:
            loop.close()
    
    async def _astream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> AsyncIterator[ChatGenerationChunk]:
        """Stream response asynchronously."""
        try:
            # Convert messages to Amazon Q format
            user_message = self._convert_messages_to_amazon_q_format(messages)
            
            # Get streaming client
            client = self._get_client()
            
            async with client:
                async for event in client.generate_assistant_response(
                    user_message_content=user_message,
                    conversation_id=kwargs.get("conversation_id"),
                    history=None  # TODO: Implement conversation history
                ):
                    if isinstance(event, AssistantResponseMessage):
                        if event.content:
                            # Create chunk
                            chunk = ChatGenerationChunk(
                                message=AIMessage(content=event.content),
                                generation_info={"event_type": "assistant_response"}
                            )
                            
                            # Send to callback if available
                            if run_manager:
                                await run_manager.on_llm_new_token(event.content, chunk=chunk)
                            
                            yield chunk
                    
                    elif isinstance(event, MessageMetadataEvent):
                        # Send metadata as a chunk
                        metadata_chunk = ChatGenerationChunk(
                            message=AIMessage(content=""),
                            generation_info={
                                "event_type": "metadata",
                                "conversation_id": event.conversation_id,
                                "utterance_id": event.utterance_id
                            }
                        )
                        yield metadata_chunk
            
        except Exception as e:
            logger.error(f"Error streaming response: {e}")
            raise
    
    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """Get identifying parameters for this model."""
        return {
            "model_name": "amazon-q",
            "base_url": self.base_url,
            "auto_token_refresh": self.auto_token_refresh,
        }
