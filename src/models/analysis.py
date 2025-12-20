from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel


class LuckHighlight(BaseModel):
    start_age: int
    year: int
    pillar: str
    element_tendency: Optional[str] = None
    summary: Optional[str] = None


class Analysis(BaseModel):
    pattern: Optional[str] = None
    strength_score: Optional[int] = None
    yi_yong_shen: List[str] = []
    ji_shen: List[str] = []
    pattern_tags: List[str] = []
    key_conclusions: List[str] = []
    risk_points: List[str] = []
    luck_highlights: List[LuckHighlight] = []

