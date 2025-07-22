"""
Amazon Q LangChain Integration

This package provides LangChain-compatible wrappers for Amazon Q,
enabling seamless integration with the LangChain ecosystem.

Main exports:
- ChatAmazonQ: Drop-in replacement for ChatOpenAI
- TokenManager: Automatic CLI token management
"""

from .chat_model import ChatAmazonQ
from .token_manager import TokenManager

__version__ = "0.1.0"
__all__ = ["ChatAmazonQ", "TokenManager"]
