from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Dict, Iterable, Iterator, Optional

from src.llm.types import ChatChunk, OllamaError


DEFAULT_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "deepseek-r1:8b")
DEFAULT_TEMPERATURE = float(os.getenv("OLLAMA_TEMPERATURE", "0.7"))
DEFAULT_TIMEOUT = float(os.getenv("OLLAMA_TIMEOUT", "60"))


def _parse_error_body(body: bytes) -> Optional[str]:
    if not body:
        return None
    try:
        text = body.decode("utf-8").strip()
    except UnicodeDecodeError:
        return None
    if not text:
        return None
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return text
    if isinstance(data, dict):
        detail = data.get("error")
        return detail if isinstance(detail, str) and detail else text
    return text


def _build_chat_payload(
    messages: Iterable[Dict[str, str]],
    stream: bool,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
) -> Dict:
    return {
        "model": model or DEFAULT_MODEL,
        "messages": list(messages),
        "stream": stream,
        "options": {"temperature": DEFAULT_TEMPERATURE if temperature is None else temperature},
    }


def _iter_chat_chunks(
    messages: Iterable[Dict[str, str]],
    *,
    base_url: str,
    model: Optional[str],
    temperature: Optional[float],
    timeout: float,
) -> Iterator[ChatChunk]:
    payload = _build_chat_payload(messages, stream=True, model=model, temperature=temperature)
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        f"{base_url}/api/chat",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

    def _coerce_text(value: Optional[str]) -> str:
        return value if isinstance(value, str) else ""

    try:
        with opener.open(request, timeout=timeout) as response:
            for raw_line in response:
                if not raw_line:
                    continue
                line = raw_line.decode("utf-8").strip()
                if not line:
                    continue
                try:
                    chunk = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if not isinstance(chunk, dict):
                    continue

                raw_message = chunk.get("message")
                message = raw_message if isinstance(raw_message, dict) else {}
                content = _coerce_text(message.get("content")) or _coerce_text(chunk.get("response"))
                reasoning = (
                    _coerce_text(message.get("reasoning_content"))
                    or _coerce_text(message.get("reasoning"))
                    or _coerce_text(message.get("thinking"))
                    or _coerce_text(chunk.get("reasoning_content"))
                    or _coerce_text(chunk.get("reasoning"))
                )

                if content or reasoning:
                    yield ChatChunk(content=content, reasoning=reasoning)
                if chunk.get("done"):
                    break
    except urllib.error.HTTPError as exc:
        detail = _parse_error_body(exc.read())
        message = f"Ollama 调用失败: HTTP {exc.code} {exc.reason}"
        if detail:
            message = f"{message} - {detail}"
        message = f"{message} (base_url={base_url}, model={model or DEFAULT_MODEL})"
        raise OllamaError(message) from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        message = f"Ollama 调用失败: {exc} (base_url={base_url}, model={model or DEFAULT_MODEL})"
        raise OllamaError(message) from exc


def stream_chat(
    messages: Iterable[Dict[str, str]],
    *,
    base_url: str = DEFAULT_BASE_URL,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> Iterator[str]:
    for chunk in _iter_chat_chunks(
        messages,
        base_url=base_url,
        model=model,
        temperature=temperature,
        timeout=timeout,
    ):
        if chunk.content:
            yield chunk.content


def chat(
    messages: Iterable[Dict[str, str]],
    *,
    base_url: str = DEFAULT_BASE_URL,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> str:
    return "".join(
        stream_chat(
            messages,
            base_url=base_url,
            model=model,
            temperature=temperature,
            timeout=timeout,
        )
    )


def stream_chat_with_reasoning(
    messages: Iterable[Dict[str, str]],
    *,
    base_url: str = DEFAULT_BASE_URL,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> Iterator[ChatChunk]:
    """
    与 stream_chat 行为类似，但会同时返回模型的可见回复与 reasoning 内容。
    """
    yield from _iter_chat_chunks(
        messages,
        base_url=base_url,
        model=model,
        temperature=temperature,
        timeout=timeout,
    )
