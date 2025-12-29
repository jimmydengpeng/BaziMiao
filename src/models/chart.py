from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

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


class NaYinInfo(BaseModel):
    """纳音信息"""
    gan_zhi: str = Field(description="干支，如'己亥'")
    na_yin: str = Field(description="纳音，如'平地木'")


class JieQiInfo(BaseModel):
    """节气信息"""
    prev_jieqi: str = Field(default="", description="前一个节气")
    prev_distance: str = Field(default="", description="距前一节气的时间")
    next_jieqi: str = Field(default="", description="后一个节气")
    next_distance: str = Field(default="", description="距后一节气的时间")


class GanZhiRelation(BaseModel):
    """单个干支关系"""
    type: str = Field(description="关系类型：合化、相克、六合、三合、三会、六冲、相刑、相害、相生")
    positions: List[int] = Field(description="涉及的柱位置索引 [0=年,1=月,2=日,3=时]")
    description: str = Field(description="描述，如'癸戊合化火'")
    element: Optional[str] = Field(default=None, description="合化后的五行（如有）")


class GanZhiRelations(BaseModel):
    """干支关系汇总"""
    stem_relations: List[GanZhiRelation] = Field(default_factory=list, description="天干关系")
    branch_relations: List[GanZhiRelation] = Field(default_factory=list, description="地支关系")
    stem_branch_relations: List[GanZhiRelation] = Field(default_factory=list, description="天干地支相生关系")


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
    five_elements_count: Dict[str, int]
    five_elements_ratio: Dict[str, float]
    destiny_cycle: DestinyCycleInfo
    zodiac_animal: str = Field(default="", description="生肖属相")
    # 新增字段
    true_solar_datetime: Optional[datetime] = Field(default=None, description="真太阳时")
    birth_place: str = Field(default="", description="出生地点")
    birth_jieqi: Optional[JieQiInfo] = Field(default=None, description="出生节气信息")
    zodiac_sign: str = Field(default="", description="星座")
    star_mansion: str = Field(default="", description="星宿")
    day_master_display: str = Field(default="", description="命主五行展示，如'癸阴水'")
    fortune_element: str = Field(default="", description="天运五行（年柱纳音）")
    tai_yuan: Optional[NaYinInfo] = Field(default=None, description="胎元")
    tai_xi: Optional[NaYinInfo] = Field(default=None, description="胎息")
    shen_gong: Optional[NaYinInfo] = Field(default=None, description="身宫")
    ming_gong: Optional[NaYinInfo] = Field(default=None, description="命宫")
    ren_yuan_si_ling: str = Field(default="", description="人元司令分野")
    kong_wang: str = Field(default="", description="空亡")
    ganzi_relations: Optional[GanZhiRelations] = Field(default=None, description="干支关系")
