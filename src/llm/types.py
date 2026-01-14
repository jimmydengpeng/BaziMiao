from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


LLMProvider = Literal["local", "openai"]


@dataclass
class ChatChunk:
    content: str = ""
    reasoning: str = ""


class LLMError(RuntimeError):
    pass


class OllamaError(LLMError):
    pass


class OpenAICompatibleError(LLMError):
    pass
