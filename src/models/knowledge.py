from __future__ import annotations

from pydantic import BaseModel


class KnowledgeChunk(BaseModel):
    source: str
    topic: str
    summary: str

