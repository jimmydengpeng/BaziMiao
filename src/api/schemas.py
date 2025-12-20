from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class ReportRequest(BaseModel):
    name: Optional[str] = None
    gender: str = Field(..., description="male/female")
    birth: datetime = Field(..., description="阳历出生时间，ISO 格式")
    tz_offset_hours: int = Field(0, description="相对于 UTC 的小时偏移")
    focus: List[str] = Field(default_factory=list, description="用户关注方向，如事业/财富/感情")


class ChatTurn(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    chart: Dict
    analysis: Dict
    history: List[ChatTurn]
    focus: List[str] = Field(default_factory=list)
