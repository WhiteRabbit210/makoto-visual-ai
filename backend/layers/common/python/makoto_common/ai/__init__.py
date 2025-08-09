"""
AI標準化モジュール
複数のLLMプロバイダーへの統一インターフェースを提供
"""

from .interface import (
    AIInterface,
    Message,
    ChatCompletion,
    StreamChunk,
    MessageRole,
    CompletionUsage
)

__all__ = [
    'AIInterface',
    'Message',
    'ChatCompletion',
    'StreamChunk',
    'MessageRole',
    'CompletionUsage'
]