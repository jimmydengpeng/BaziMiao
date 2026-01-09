from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


LLMProvider = Literal["local", "deepseek"]


@dataclass
class ChatChunk:
    content: str = ""
    reasoning: str = ""


class LLMError(RuntimeError):
    pass


class OllamaError(LLMError):
    pass


class DeepSeekError(LLMError):
    pass

