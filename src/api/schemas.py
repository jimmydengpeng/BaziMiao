from __future__ import annotations

from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class ChartRequest(BaseModel):
    name: Optional[str] = None
    gender: str = Field(..., description="male/female")
    year: int = Field(..., ge=1900, le=2100)
    month: int = Field(..., ge=1, le=12)
    day: int = Field(..., ge=1, le=31)
    hour: int = Field(0, ge=0, le=23)
    minute: int = Field(0, ge=0, le=59)
    calendar: Literal["solar", "lunar"] = Field("solar", description="输入历法")
    is_leap_month: bool = Field(False, description="农历是否闰月")
    tz_offset_hours: int = Field(0, description="相对于 UTC 的小时偏移")


class ReportRequest(BaseModel):
    chart: Optional[Dict] = None
    focus: List[str] = Field(default_factory=list, description="用户关注方向，如事业/财富/感情")
    name: Optional[str] = None
    gender: Optional[str] = Field(None, description="male/female")
    year: Optional[int] = Field(None, ge=1900, le=2100)
    month: Optional[int] = Field(None, ge=1, le=12)
    day: Optional[int] = Field(None, ge=1, le=31)
    hour: int = Field(0, ge=0, le=23)
    minute: int = Field(0, ge=0, le=59)
    calendar: Literal["solar", "lunar"] = Field("solar", description="输入历法")
    is_leap_month: bool = Field(False, description="农历是否闰月")
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
