from __future__ import annotations

from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field


LlmProvider = Literal["local", "openai", "deepseek", "dashscope"]


class ChartRequest(BaseModel):
    name: Optional[str] = None
    gender: str = Field(..., description="male/female")
    year: int = Field(..., ge=1801, le=2100, description="年份，支持 1801-2100")
    month: int = Field(..., ge=1, le=12)
    day: int = Field(..., ge=1, le=31)
    hour: int = Field(0, ge=0, le=23)
    minute: int = Field(0, ge=0, le=59)
    calendar: Literal["solar", "lunar"] = Field("solar", description="输入历法")
    is_leap_month: bool = Field(False, description="农历是否闰月")
    tz_offset_hours: int = Field(0, description="相对于 UTC 的小时偏移")
    # 出生地点相关
    birth_place: str = Field("", description="出生地点名称")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="经度")
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="纬度")


class ReportRequest(BaseModel):
    chart: Optional[Dict] = None
    focus: List[str] = Field(default_factory=list, description="用户关注方向，如事业/财富/感情")
    name: Optional[str] = None
    gender: Optional[str] = Field(None, description="male/female")
    year: Optional[int] = Field(None, ge=1801, le=2100, description="年份，支持 1801-2100")
    month: Optional[int] = Field(None, ge=1, le=12)
    day: Optional[int] = Field(None, ge=1, le=31)
    hour: int = Field(0, ge=0, le=23)
    minute: int = Field(0, ge=0, le=59)
    calendar: Literal["solar", "lunar"] = Field("solar", description="输入历法")
    is_leap_month: bool = Field(False, description="农历是否闰月")
    tz_offset_hours: int = Field(0, description="相对于 UTC 的小时偏移")
    # 出生地点相关
    birth_place: str = Field("", description="出生地点名称")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="经度")
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="纬度")


class ChatTurn(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    chart: Dict
    analysis: Dict
    history: List[ChatTurn]
    focus: List[str] = Field(default_factory=list)


class GeneralChatRequest(BaseModel):
    """通用聊天请求（无需命盘）"""
    history: List[ChatTurn]
    system_prompt: Optional[str] = Field(None, description="自定义系统提示词")
    llm_provider: LlmProvider = Field(
        "openai", description="模型渠道：openai(云端兼容)"
    )
    # 可选：命主上下文（用于通用聊天里也能“带命主”提问）
    subject_enabled: bool = Field(False, description="是否启用命主上下文")
    subject_name: Optional[str] = Field(None, description="命主姓名（简化：仅姓名）")
    subject_birth: Optional[str] = Field(None, description="命主出生日期文本（简化：一段字符串即可）")
    subject_gender: Optional[str] = Field(None, description="命主性别（简化：男/女/其他）")
    subject_destiny: Optional[str] = Field(None, description="十年大运列表（简化：年份 + 干支）")
    subject_chart: Optional[Dict] = Field(None, description="命盘原始数据（前端档案）")
    # 可选：思考模式（云端 openai 兼容：enable_thinking）
    deep_think: bool = Field(False, description="是否启用思考模式（openai 有效）")


class PillarSearchRequest(BaseModel):
    """四柱反查请求"""
    year_pillar: str = Field(..., min_length=2, max_length=2, description="年柱（如：甲子）")
    month_pillar: str = Field(..., min_length=2, max_length=2, description="月柱（如：乙丑）")
    day_pillar: str = Field(..., min_length=2, max_length=2, description="日柱（如：丙寅）")
    hour_pillar: str = Field(..., min_length=2, max_length=2, description="时柱（如：丁卯）")
    start_year: int = Field(1801, ge=1800, le=2200, description="查找起始年份")
    end_year: int = Field(2099, ge=1800, le=2200, description="查找结束年份")


class FeedbackRequest(BaseModel):
    """消息反馈请求（点赞/点踩）"""
    session_id: str = Field(..., description="会话 ID")
    message_id: str = Field(..., description="消息 ID")
    feedback: Optional[Literal["like", "dislike"]] = Field(None, description="反馈类型，null 表示取消反馈")


class EnergyAnalysisRequest(BaseModel):
    """五行能量智能分析请求"""
    chart: Dict = Field(..., description="命盘数据")


class DestinyAnalysisRequest(BaseModel):
    """大运智能解析请求"""
    chart: Dict = Field(..., description="命盘数据")
    destiny_pillar: Dict = Field(..., description="大运柱信息")


class DestinyAnalysisBatchRequest(BaseModel):
    """多条大运智能解析请求"""
    chart: Dict = Field(..., description="命盘数据")
    destiny_pillars: List[Dict] = Field(..., description="大运柱信息列表")


class DestinyRelationsRequest(BaseModel):
    """大运与本命干支关系请求"""
    chart: Dict = Field(..., description="命盘数据")
    destiny_pillar: Dict = Field(..., description="大运柱信息")
