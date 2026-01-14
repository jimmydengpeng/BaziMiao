from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any, Dict, Iterable, Iterator, Optional

from src.llm.types import ChatChunk, OpenAICompatibleError


DEFAULT_BASE_URL = os.getenv(
    "OPENAI_COMPAT_BASE_URL",
    os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
)
DEFAULT_MODEL = os.getenv("OPENAI_COMPAT_MODEL", os.getenv("DASHSCOPE_MODEL", "deepseek-v3.2"))
DEFAULT_TEMPERATURE = float(
    os.getenv("OPENAI_COMPAT_TEMPERATURE", os.getenv("DASHSCOPE_TEMPERATURE", "0.7"))
)
DEFAULT_TIMEOUT = float(os.getenv("OPENAI_COMPAT_TIMEOUT", os.getenv("DASHSCOPE_TIMEOUT", "60")))


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
        detail = data.get("error") or data.get("message")
        return detail if isinstance(detail, str) and detail else text
    return text


def _normalize_base_url(base_url: str) -> str:
    trimmed = (base_url or "").strip()
    return trimmed[:-1] if trimmed.endswith("/") else trimmed


def _build_chat_payload(
    messages: Iterable[Dict[str, str]],
    stream: bool,
    *,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    enable_thinking: Optional[bool] = None,
    response_format: Optional[Dict[str, Any]] = None,
) -> Dict:
    payload: Dict = {
        "model": model or DEFAULT_MODEL,
        "messages": list(messages),
        "stream": stream,
        "temperature": DEFAULT_TEMPERATURE if temperature is None else temperature,
    }
    if enable_thinking is not None:
        payload["enable_thinking"] = bool(enable_thinking)
    if response_format:
        payload["response_format"] = response_format
    return payload


def _iter_chat_chunks(
    messages: Iterable[Dict[str, str]],
    *,
    api_key: str,
    base_url: str,
    model: Optional[str],
    temperature: Optional[float],
    enable_thinking: Optional[bool],
    response_format: Optional[Dict[str, Any]],
    timeout: float,
) -> Iterator[ChatChunk]:
    payload = _build_chat_payload(
        messages,
        stream=True,
        model=model,
        temperature=temperature,
        enable_thinking=enable_thinking,
        response_format=response_format,
    )
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    endpoint = f"{_normalize_base_url(base_url)}/chat/completions"
    request = urllib.request.Request(
        endpoint,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "Accept": "text/event-stream",
        },
    )
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

    def _coerce_text(value: object) -> str:
        return value if isinstance(value, str) else ""

    try:
        with opener.open(request, timeout=timeout) as response:
            event_data_lines: list[str] = []
            for raw_line in response:
                if not raw_line:
                    continue
                line = raw_line.decode("utf-8", errors="ignore").rstrip("\r\n")

                # SSE: 空行表示一个事件结束
                if line == "":
                    if not event_data_lines:
                        continue
                    data_text = "\n".join(event_data_lines).strip()
                    event_data_lines = []
                    if not data_text:
                        continue
                    if data_text == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data_text)
                    except json.JSONDecodeError:
                        continue
                    if not isinstance(chunk, dict):
                        continue
                    choices = chunk.get("choices")
                    if not isinstance(choices, list) or not choices:
                        continue
                    choice0 = choices[0] if isinstance(choices[0], dict) else {}
                    delta = choice0.get("delta")
                    delta = delta if isinstance(delta, dict) else {}

                    content = _coerce_text(delta.get("content"))
                    reasoning = (
                        _coerce_text(delta.get("reasoning_content"))
                        or _coerce_text(delta.get("reasoning"))
                        or _coerce_text(delta.get("thinking"))
                    )
                    if content or reasoning:
                        yield ChatChunk(content=content, reasoning=reasoning)
                    continue

                if not line.startswith("data:"):
                    continue
                data_part = line[len("data:") :].strip()
                event_data_lines.append(data_part)
    except urllib.error.HTTPError as exc:
        detail = _parse_error_body(exc.read())
        message = f"OpenAI 兼容云端调用失败: HTTP {exc.code} {exc.reason}"
        if detail:
            message = f"{message} - {detail}"
        message = f"{message} (base_url={base_url}, model={model or DEFAULT_MODEL})"
        raise OpenAICompatibleError(message) from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        message = f"OpenAI 兼容云端调用失败: {exc} (base_url={base_url}, model={model or DEFAULT_MODEL})"
        raise OpenAICompatibleError(message) from exc


def stream_chat_with_reasoning(
    messages: Iterable[Dict[str, str]],
    *,
    api_key: Optional[str] = None,
    base_url: str = DEFAULT_BASE_URL,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    enable_thinking: Optional[bool] = None,
    response_format: Optional[Dict[str, Any]] = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> Iterator[ChatChunk]:
    resolved_key = api_key or os.getenv("OPENAI_COMPAT_API_KEY", "").strip()
    if not resolved_key:
        resolved_key = os.getenv("DASHSCOPE_API_KEY", "").strip()
    if not resolved_key:
        raise OpenAICompatibleError("缺少 OPENAI_COMPAT_API_KEY，无法调用 OpenAI 兼容云端模型")
    yield from _iter_chat_chunks(
        messages,
        api_key=resolved_key,
        base_url=base_url,
        model=model,
        temperature=temperature,
        enable_thinking=enable_thinking,
        response_format=response_format,
        timeout=timeout,
    )


def stream_chat(
    messages: Iterable[Dict[str, str]],
    *,
    api_key: Optional[str] = None,
    base_url: str = DEFAULT_BASE_URL,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    enable_thinking: Optional[bool] = None,
    response_format: Optional[Dict[str, Any]] = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> Iterator[str]:
    for chunk in stream_chat_with_reasoning(
        messages,
        api_key=api_key,
        base_url=base_url,
        model=model,
        temperature=temperature,
        enable_thinking=enable_thinking,
        response_format=response_format,
        timeout=timeout,
    ):
        if chunk.content:
            yield chunk.content


def chat(
    messages: Iterable[Dict[str, str]],
    *,
    api_key: Optional[str] = None,
    base_url: str = DEFAULT_BASE_URL,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    enable_thinking: Optional[bool] = None,
    response_format: Optional[Dict[str, Any]] = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> str:
    return "".join(
        stream_chat(
            messages,
            api_key=api_key,
            base_url=base_url,
            model=model,
            temperature=temperature,
            enable_thinking=enable_thinking,
            response_format=response_format,
            timeout=timeout,
        )
    )
