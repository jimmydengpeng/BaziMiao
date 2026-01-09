from __future__ import annotations

import os
from typing import Dict, Iterable, Iterator, Optional

from src.llm.deepseek_client import (
    chat as deepseek_chat,
    stream_chat as deepseek_stream_chat,
    stream_chat_with_reasoning as deepseek_stream_chat_with_reasoning,
)
from src.llm.ollama_client import (
    chat as ollama_chat,
    stream_chat as ollama_stream_chat,
    stream_chat_with_reasoning as ollama_stream_chat_with_reasoning,
)
from src.llm.types import ChatChunk, LLMProvider


DEFAULT_PROVIDER: LLMProvider = os.getenv("LLM_PROVIDER", "local")  # type: ignore[assignment]


def _resolve_provider(provider: Optional[str]) -> LLMProvider:
    if provider == "deepseek":
        return "deepseek"
    return "local"


def stream_chat(
    messages: Iterable[Dict[str, str]],
    *,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    enable_thinking: Optional[bool] = None,
    timeout: Optional[float] = None,
) -> Iterator[str]:
    resolved = _resolve_provider(provider or DEFAULT_PROVIDER)
    if resolved == "deepseek":
        kwargs = {
            "model": model,
            "temperature": temperature,
            "enable_thinking": enable_thinking,
        }
        if timeout is not None:
            kwargs["timeout"] = timeout
        yield from deepseek_stream_chat(messages, **kwargs)
        return
    kwargs = {"model": model, "temperature": temperature}
    if timeout is not None:
        kwargs["timeout"] = timeout
    yield from ollama_stream_chat(messages, **kwargs)


def chat(
    messages: Iterable[Dict[str, str]],
    *,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    enable_thinking: Optional[bool] = None,
    timeout: Optional[float] = None,
) -> str:
    resolved = _resolve_provider(provider or DEFAULT_PROVIDER)
    if resolved == "deepseek":
        kwargs = {
            "model": model,
            "temperature": temperature,
            "enable_thinking": enable_thinking,
        }
        if timeout is not None:
            kwargs["timeout"] = timeout
        return deepseek_chat(messages, **kwargs)
    kwargs = {"model": model, "temperature": temperature}
    if timeout is not None:
        kwargs["timeout"] = timeout
    return ollama_chat(messages, **kwargs)


def stream_chat_with_reasoning(
    messages: Iterable[Dict[str, str]],
    *,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    enable_thinking: Optional[bool] = None,
    timeout: Optional[float] = None,
) -> Iterator[ChatChunk]:
    resolved = _resolve_provider(provider or DEFAULT_PROVIDER)
    if resolved == "deepseek":
        kwargs = {
            "model": model,
            "temperature": temperature,
            "enable_thinking": enable_thinking,
        }
        if timeout is not None:
            kwargs["timeout"] = timeout
        yield from deepseek_stream_chat_with_reasoning(messages, **kwargs)
        return
    kwargs = {"model": model, "temperature": temperature}
    if timeout is not None:
        kwargs["timeout"] = timeout
    yield from ollama_stream_chat_with_reasoning(messages, **kwargs)
