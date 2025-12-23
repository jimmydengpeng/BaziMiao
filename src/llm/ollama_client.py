from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Dict, Iterable, Iterator, List, Optional


DEFAULT_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "deepseek-r1:8b")
DEFAULT_TEMPERATURE = float(os.getenv("OLLAMA_TEMPERATURE", "0.7"))
DEFAULT_TIMEOUT = float(os.getenv("OLLAMA_TIMEOUT", "60"))


class OllamaError(RuntimeError):
    pass


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


def stream_chat(
    messages: Iterable[Dict[str, str]],
    *,
    base_url: str = DEFAULT_BASE_URL,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> Iterator[str]:
    payload = _build_chat_payload(messages, stream=True, model=model, temperature=temperature)
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        f"{base_url}/api/chat",
        data=data,
        headers={"Content-Type": "application/json"},
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
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

                message = chunk.get("message") or {}
                content = message.get("content") or chunk.get("response") or ""
                if content:
                    yield content
                if chunk.get("done"):
                    break
    except (urllib.error.URLError, TimeoutError) as exc:
        raise OllamaError(f"Ollama 调用失败: {exc}") from exc


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
