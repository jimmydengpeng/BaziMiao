from __future__ import annotations

import os
from typing import Any, Dict, Iterable, Iterator, Optional

from src.llm.openai_client import (
    chat as openai_chat,
    chat_with_usage as openai_chat_with_usage,
    stream_chat as openai_stream_chat,
    stream_chat_with_reasoning as openai_stream_chat_with_reasoning,
)
from src.llm.ollama_client import (
    chat as ollama_chat,
    stream_chat as ollama_stream_chat,
    stream_chat_with_reasoning as ollama_stream_chat_with_reasoning,
)
from src.llm.types import ChatChunk, LLMProvider


DEFAULT_PROVIDER: LLMProvider = os.getenv("LLM_PROVIDER", "local")  # type: ignore[assignment]


def _resolve_provider(provider: Optional[str]) -> LLMProvider:
    if provider == "openai" or provider == "deepseek":
        return "openai"
    return "local"


def stream_chat(
    messages: Iterable[Dict[str, str]],
    *,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    enable_thinking: Optional[bool] = None,
    response_format: Optional[Dict[str, Any]] = None,
    timeout: Optional[float] = None,
) -> Iterator[str]:
    resolved = _resolve_provider(provider or DEFAULT_PROVIDER)
    if resolved == "openai":
        kwargs = {
            "model": model,
            "temperature": temperature,
            "enable_thinking": enable_thinking,
            "response_format": response_format,
        }
        if timeout is not None:
            kwargs["timeout"] = timeout
        yield from openai_stream_chat(messages, **kwargs)
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
    response_format: Optional[Dict[str, Any]] = None,
    timeout: Optional[float] = None,
) -> str:
    resolved = _resolve_provider(provider or DEFAULT_PROVIDER)
    if resolved == "openai":
        kwargs = {
            "model": model,
            "temperature": temperature,
            "enable_thinking": enable_thinking,
            "response_format": response_format,
        }
        if timeout is not None:
            kwargs["timeout"] = timeout
        return openai_chat(messages, **kwargs)
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
    response_format: Optional[Dict[str, Any]] = None,
    timeout: Optional[float] = None,
) -> Iterator[ChatChunk]:
    resolved = _resolve_provider(provider or DEFAULT_PROVIDER)
    if resolved == "openai":
        kwargs = {
            "model": model,
            "temperature": temperature,
            "enable_thinking": enable_thinking,
            "response_format": response_format,
        }
        if timeout is not None:
            kwargs["timeout"] = timeout
        yield from openai_stream_chat_with_reasoning(messages, **kwargs)
        return
    kwargs = {"model": model, "temperature": temperature}
    if timeout is not None:
        kwargs["timeout"] = timeout
    yield from ollama_stream_chat_with_reasoning(messages, **kwargs)


def chat_with_usage(
    messages: Iterable[Dict[str, str]],
    *,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    enable_thinking: Optional[bool] = None,
    response_format: Optional[Dict[str, Any]] = None,
    timeout: Optional[float] = None,
) -> tuple[str, Optional[Dict[str, Any]]]:
    resolved = _resolve_provider(provider or DEFAULT_PROVIDER)
    if resolved == "openai":
        kwargs = {
            "model": model,
            "temperature": temperature,
            "enable_thinking": enable_thinking,
            "response_format": response_format,
        }
        if timeout is not None:
            kwargs["timeout"] = timeout
        return openai_chat_with_usage(messages, **kwargs)
    kwargs = {"model": model, "temperature": temperature}
    if timeout is not None:
        kwargs["timeout"] = timeout
    return ollama_chat(messages, **kwargs), None
