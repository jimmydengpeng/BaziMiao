from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class SolarDate(BaseModel):
    year: int
    month: int
    day: int


class LunarDate(SolarDate):
    is_leap_month: bool = Field(default=False, description="是否闰月")


class StartAge(BaseModel):
    year: int
    month: int
    day: int


class HeavenStemInfo(BaseModel):
    name: str
    element: str
    yinyang: str
    ten_god: str


class EarthBranchInfo(BaseModel):
    name: str
    element: str
    yinyang: str
    hidden_stems: List[HeavenStemInfo]


class PillarInfo(BaseModel):
    heaven_stem: HeavenStemInfo
    earth_branch: EarthBranchInfo


class DestinyPillarInfo(BaseModel):
    heaven_stem: HeavenStemInfo
    earth_branch: EarthBranchInfo
    year: int


class DestinyCycleInfo(BaseModel):
    destiny_pillars: List[DestinyPillarInfo]
    start_age: StartAge
    qiyun_date_solar: SolarDate
    qiyun_date_lunar: LunarDate
    is_forward: bool


class Chart(BaseModel):
    name: Optional[str]
    gender: str
    solar_datetime: datetime
    lunar_date: LunarDate
    year_pillar: PillarInfo
    month_pillar: PillarInfo
    day_pillar: PillarInfo
    hour_pillar: PillarInfo
    day_master: HeavenStemInfo
    five_elements_count: dict
    destiny_cycle: DestinyCycleInfo

