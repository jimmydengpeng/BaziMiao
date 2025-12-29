from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import sxtwl

from src.engine.true_solar_time import calculate_true_solar_time
from src.models.chart import (
    Chart,
    DestinyCycleInfo,
    DestinyPillarInfo,
    EarthBranchInfo,
    GanZhiRelation,
    GanZhiRelations,
    HeavenStemInfo,
    JieQiInfo,
    LunarDate,
    NaYinInfo,
    PillarInfo,
    SolarDate,
    StartAge,
)


class BaziPaipanEngine:
    """八字排盘引擎：负责确定性排盘，不做任何解读。"""

    TIAN_GAN_NAMES = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
    DI_ZHI_NAMES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
    # 十二生肖，与地支对应：子-鼠、丑-牛、寅-虎...
    ZODIAC_ANIMALS = ["鼠", "牛", "虎", "兔", "龙", "蛇", "马", "羊", "猴", "鸡", "狗", "猪"]
    SEXAGENARY_CYCLE = [
        "甲子",
        "乙丑",
        "丙寅",
        "丁卯",
        "戊辰",
        "己巳",
        "庚午",
        "辛未",
        "壬申",
        "癸酉",
        "甲戌",
        "乙亥",
        "丙子",
        "丁丑",
        "戊寅",
        "己卯",
        "庚辰",
        "辛巳",
        "壬午",
        "癸未",
        "甲申",
        "乙酉",
        "丙戌",
        "丁亥",
        "戊子",
        "己丑",
        "庚寅",
        "辛卯",
        "壬辰",
        "癸巳",
        "甲午",
        "乙未",
        "丙申",
        "丁酉",
        "戊戌",
        "己亥",
        "庚子",
        "辛丑",
        "壬寅",
        "癸卯",
        "甲辰",
        "乙巳",
        "丙午",
        "丁未",
        "戊申",
        "己酉",
        "庚戌",
        "辛亥",
        "壬子",
        "癸丑",
        "甲寅",
        "乙卯",
        "丙辰",
        "丁巳",
        "戊午",
        "己未",
        "庚申",
        "辛酉",
        "壬戌",
        "癸亥",
    ]

    HEAVEN_STEM_ELEMENT_MAP = {
        "甲": "木",
        "乙": "木",
        "丙": "火",
        "丁": "火",
        "戊": "土",
        "己": "土",
        "庚": "金",
        "辛": "金",
        "壬": "水",
        "癸": "水",
    }

    EARTH_BRANCH_ELEMENT_MAP = {
        "子": "水",
        "丑": "土",
        "寅": "木",
        "卯": "木",
        "辰": "土",
        "巳": "火",
        "午": "火",
        "未": "土",
        "申": "金",
        "酉": "金",
        "戌": "土",
        "亥": "水",
    }

    TIAN_GAN_YIN_YANG = {
        "甲": "阳",
        "乙": "阴",
        "丙": "阳",
        "丁": "阴",
        "戊": "阳",
        "己": "阴",
        "庚": "阳",
        "辛": "阴",
        "壬": "阳",
        "癸": "阴",
    }

    DI_ZHI_YIN_YANG = {
        "子": "阳",
        "丑": "阴",
        "寅": "阳",
        "卯": "阴",
        "辰": "阳",
        "巳": "阴",
        "午": "阳",
        "未": "阴",
        "申": "阳",
        "酉": "阴",
        "戌": "阳",
        "亥": "阴",
    }

    FIVE_ELEMENTS_RELATIONS = {
        "木": {"木": "比劫", "火": "食伤", "土": "财才", "金": "官杀", "水": "印枭"},
        "火": {"木": "印枭", "火": "比劫", "土": "食伤", "金": "财才", "水": "官杀"},
        "土": {"木": "官杀", "火": "印枭", "土": "比劫", "金": "食伤", "水": "财才"},
        "金": {"木": "财才", "火": "官杀", "土": "印枭", "金": "比劫", "水": "食伤"},
        "水": {"木": "食伤", "火": "财才", "土": "官杀", "金": "印枭", "水": "比劫"},
    }

    TEN_GODS = {
        ("同", "比劫"): "比肩",
        ("异", "比劫"): "劫财",
        ("同", "印枭"): "偏印",
        ("异", "印枭"): "正印",
        ("同", "官杀"): "七杀",
        ("异", "官杀"): "正官",
        ("同", "财才"): "偏财",
        ("异", "财才"): "正财",
        ("同", "食伤"): "食神",
        ("异", "食伤"): "伤官",
    }

    BRANCH_HIDDEN_STEM = {
        "子": ["癸"],
        "丑": ["己", "辛", "癸"],
        "寅": ["甲", "丙", "戊"],
        "卯": ["乙"],
        "辰": ["戊", "乙", "癸"],
        "巳": ["丙", "庚", "戊"],
        "午": ["丁", "己"],
        "未": ["己", "丁", "乙"],
        "申": ["庚", "壬", "戊"],
        "酉": ["辛"],
        "戌": ["戊", "辛", "丁"],
        "亥": ["壬", "甲"],
    }

    # 六十甲子纳音表
    NA_YIN_TABLE = {
        "甲子": "海中金", "乙丑": "海中金", "丙寅": "炉中火", "丁卯": "炉中火",
        "戊辰": "大林木", "己巳": "大林木", "庚午": "路旁土", "辛未": "路旁土",
        "壬申": "剑锋金", "癸酉": "剑锋金", "甲戌": "山头火", "乙亥": "山头火",
        "丙子": "涧下水", "丁丑": "涧下水", "戊寅": "城头土", "己卯": "城头土",
        "庚辰": "白蜡金", "辛巳": "白蜡金", "壬午": "杨柳木", "癸未": "杨柳木",
        "甲申": "泉中水", "乙酉": "泉中水", "丙戌": "屋上土", "丁亥": "屋上土",
        "戊子": "霹雳火", "己丑": "霹雳火", "庚寅": "松柏木", "辛卯": "松柏木",
        "壬辰": "长流水", "癸巳": "长流水", "甲午": "砂中金", "乙未": "砂中金",
        "丙申": "山下火", "丁酉": "山下火", "戊戌": "平地木", "己亥": "平地木",
        "庚子": "壁上土", "辛丑": "壁上土", "壬寅": "金箔金", "癸卯": "金箔金",
        "甲辰": "覆灯火", "乙巳": "覆灯火", "丙午": "天河水", "丁未": "天河水",
        "戊申": "大驿土", "己酉": "大驿土", "庚戌": "钗钏金", "辛亥": "钗钏金",
        "壬子": "桑柘木", "癸丑": "桑柘木", "甲寅": "大溪水", "乙卯": "大溪水",
        "丙辰": "砂中土", "丁巳": "砂中土", "戊午": "天上火", "己未": "天上火",
        "庚申": "石榴木", "辛酉": "石榴木", "壬戌": "大海水", "癸亥": "大海水",
    }

    # 二十四节气名称
    JIEQI_NAMES = [
        "小寒", "大寒", "立春", "雨水", "惊蛰", "春分",
        "清明", "谷雨", "立夏", "小满", "芒种", "夏至",
        "小暑", "大暑", "立秋", "处暑", "白露", "秋分",
        "寒露", "霜降", "立冬", "小雪", "大雪", "冬至",
    ]

    # 星座对应日期范围
    ZODIAC_SIGNS = [
        ("摩羯座", 1, 20), ("水瓶座", 2, 19), ("双鱼座", 3, 20),
        ("白羊座", 4, 20), ("金牛座", 5, 21), ("双子座", 6, 21),
        ("巨蟹座", 7, 23), ("狮子座", 8, 23), ("处女座", 9, 23),
        ("天秤座", 10, 23), ("天蝎座", 11, 22), ("射手座", 12, 22),
    ]

    # 二十八星宿
    STAR_MANSIONS = [
        "角宿东方青龙", "亢宿东方青龙", "氐宿东方青龙", "房宿东方青龙",
        "心宿东方青龙", "尾宿东方青龙", "箕宿东方青龙",
        "斗宿北方玄武", "牛宿北方玄武", "女宿北方玄武", "虚宿北方玄武",
        "危宿北方玄武", "室宿北方玄武", "壁宿北方玄武",
        "奎宿西方白虎", "娄宿西方白虎", "胃宿西方白虎", "昴宿西方白虎",
        "毕宿西方白虎", "觜宿西方白虎", "参宿西方白虎",
        "井宿南方朱雀", "鬼宿南方朱雀", "柳宿南方朱雀", "星宿南方朱雀",
        "张宿南方朱雀", "翼宿南方朱雀", "轸宿南方朱雀",
    ]

    # ========== 干支关系常量 ==========
    
    # 天干五合：两个天干相合，可能化为某一五行
    # 格式：{(干1, 干2): 合化五行}
    STEM_COMBINATIONS = {
        ("甲", "己"): "土",  # 甲己合化土
        ("乙", "庚"): "金",  # 乙庚合化金
        ("丙", "辛"): "水",  # 丙辛合化水
        ("丁", "壬"): "木",  # 丁壬合化木
        ("戊", "癸"): "火",  # 戊癸合化火
    }
    
    # 天干相冲
    STEM_CLASHES = [
        ("甲", "庚"),  # 甲庚冲
        ("乙", "辛"),  # 乙辛冲
        ("壬", "丙"),  # 壬丙冲
        ("癸", "丁"),  # 癸丁冲
    ]
    
    # 天干相克（特定克制关系）
    STEM_KE_PAIRS = [
        ("丙", "庚"),  # 丙克庚（火克金）
        ("丁", "辛"),  # 丁克辛（火克金）
    ]
    
    # 五行相克关系：A克B（用于其他计算）
    # 金克木、木克土、土克水、水克火、火克金
    FIVE_ELEMENTS_克 = {
        "金": "木",
        "木": "土",
        "土": "水",
        "水": "火",
        "火": "金",
    }
    
    # 五行相生关系：A生B
    # 金生水、水生木、木生火、火生土、土生金
    FIVE_ELEMENTS_生 = {
        "金": "水",
        "水": "木",
        "木": "火",
        "火": "土",
        "土": "金",
    }
    
    # 地支六合：两个地支相合，化为某一五行
    BRANCH_SIX_COMBINATIONS = {
        ("子", "丑"): "土",  # 子丑合化土
        ("寅", "亥"): "木",  # 寅亥合化木
        ("卯", "戌"): "火",  # 卯戌合化火
        ("辰", "酉"): "金",  # 辰酉合化金
        ("巳", "申"): "水",  # 巳申合化水
        ("午", "未"): "火",  # 午未合化火（日月合）
    }
    
    # 地支三合：三个地支相合，化为某一五行
    BRANCH_THREE_COMBINATIONS = {
        ("申", "子", "辰"): "水",  # 申子辰合水局
        ("亥", "卯", "未"): "木",  # 亥卯未合木局
        ("寅", "午", "戌"): "火",  # 寅午戌合火局
        ("巳", "酉", "丑"): "金",  # 巳酉丑合金局
    }
    
    # 地支三会：三个地支相会，代表某一方位/季节
    BRANCH_THREE_MEETINGS = {
        ("寅", "卯", "辰"): "木",  # 寅卯辰三会东方木
        ("巳", "午", "未"): "火",  # 巳午未三会南方火
        ("申", "酉", "戌"): "金",  # 申酉戌三会西方金
        ("亥", "子", "丑"): "水",  # 亥子丑三会北方水
    }
    
    # 地支六冲：两个地支相冲（对冲）
    BRANCH_SIX_CLASHES = [
        ("子", "午"),  # 子午冲
        ("丑", "未"),  # 丑未冲
        ("寅", "申"),  # 寅申冲
        ("卯", "酉"),  # 卯酉冲
        ("辰", "戌"),  # 辰戌冲
        ("巳", "亥"),  # 巳亥冲
    ]
    
    # 地支相刑
    # 无恩之刑：寅刑巳、巳刑申、申刑寅（三刑）
    # 恃势之刑：丑刑戌、戌刑未、未刑丑（三刑）
    # 无礼之刑：子刑卯、卯刑子（相刑）
    # 自刑：辰辰、午午、酉酉、亥亥
    BRANCH_PUNISHMENTS = {
        "无恩之刑": [("寅", "巳"), ("巳", "申"), ("申", "寅")],
        "恃势之刑": [("丑", "戌"), ("戌", "未"), ("未", "丑")],
        "无礼之刑": [("子", "卯"), ("卯", "子")],
        "自刑": [("辰", "辰"), ("午", "午"), ("酉", "酉"), ("亥", "亥")],
    }
    
    # 地支相害（六害）：两个地支相害
    BRANCH_HARMS = [
        ("子", "未"),  # 子未害
        ("丑", "午"),  # 丑午害
        ("寅", "巳"),  # 寅巳害
        ("卯", "辰"),  # 卯辰害
        ("申", "亥"),  # 申亥害
        ("酉", "戌"),  # 酉戌害
    ]

    def lunar_to_solar(
        self,
        year: int,
        month: int,
        day: int,
        is_leap_month: bool,
        hour: int = 0,
        minute: int = 0,
    ) -> datetime:
        lunar_day = sxtwl.fromLunar(year, month, day, is_leap_month)
        return datetime(
            lunar_day.getSolarYear(),
            lunar_day.getSolarMonth(),
            lunar_day.getSolarDay(),
            hour,
            minute,
        )

    def calculate_chart(
        self,
        name: Optional[str],
        gender: str,
        solar_datetime: datetime,
        use_true_solar_time: bool = True,
        tz_offset_hours: int = 0,
        longitude: Optional[float] = None,
        latitude: Optional[float] = None,
        birth_place: str = "",
    ) -> Chart:
        """
        计算排盘，返回结构化 Chart。

        Args:
            name: 姓名
            gender: 性别 ("male" / "female")
            solar_datetime: 阳历出生时间（北京时间）
            use_true_solar_time: 是否使用真太阳时排盘
            tz_offset_hours: 时区偏移（相对UTC）
            longitude: 出生地经度（用于计算真太阳时）
            latitude: 出生地纬度
            birth_place: 出生地点名称
        """
        # 先进行时区调整
        adjusted_dt = solar_datetime + timedelta(hours=tz_offset_hours)

        # 保存原始输入时间（作为阳历时间显示）
        original_solar_datetime = adjusted_dt

        # 计算真太阳时（如果提供了经度）
        true_solar_datetime: Optional[datetime] = None
        if longitude is not None and use_true_solar_time:
            true_solar_datetime = calculate_true_solar_time(
                adjusted_dt, longitude, latitude or 0.0
            )
            # 使用真太阳时进行排盘
            adjusted_dt = true_solar_datetime
        else:
            # 未提供经度时，真太阳时与输入时间一致
            true_solar_datetime = adjusted_dt

        birth_day = sxtwl.fromSolar(adjusted_dt.year, adjusted_dt.month, adjusted_dt.day)
        year_gz = birth_day.getYearGZ()
        month_gz = birth_day.getMonthGZ()
        day_gz = birth_day.getDayGZ()
        hour_gz = self._get_hour_gz(day_gz.tg, adjusted_dt.hour)

        day_stem_name = self.TIAN_GAN_NAMES[day_gz.tg]

        year_pillar = self._create_pillar_info(year_gz.tg, year_gz.dz, day_stem_name)
        month_pillar = self._create_pillar_info(month_gz.tg, month_gz.dz, day_stem_name)
        day_pillar = self._create_pillar_info(day_gz.tg, day_gz.dz, day_stem_name)
        hour_pillar = self._create_pillar_info(hour_gz[0], hour_gz[1], day_stem_name)

        destiny_cycle = self._calculate_dayun(
            birth_day=birth_day,
            hour=adjusted_dt.hour,
            minute=adjusted_dt.minute,
            gender=gender,
            day_stem=day_stem_name,
        )

        lunar_date = LunarDate(
            year=birth_day.getLunarYear(),
            month=birth_day.getLunarMonth(),
            day=birth_day.getLunarDay(),
            is_leap_month=birth_day.isLunarLeap(),
        )

        five_elements_count = self._calculate_five_elements(
            [year_pillar, month_pillar, day_pillar, hour_pillar]
        )
        five_elements_ratio = self._calculate_five_elements_ratio(five_elements_count)
        # 根据年柱地支计算生肖属相
        zodiac_animal = self.ZODIAC_ANIMALS[year_gz.dz]

        # 计算新增字段
        # 真太阳时：目前简化处理，与阳历相同（TODO: 实现真太阳时计算）
        true_solar_datetime = adjusted_dt

        # 计算星座
        zodiac_sign = self._calculate_zodiac_sign(adjusted_dt.month, adjusted_dt.day)

        # 计算星宿（简化：基于日期计算）
        star_mansion = self._calculate_star_mansion(birth_day)

        # 命主五行展示
        day_master_display = f"{day_pillar.heaven_stem.name}{day_pillar.heaven_stem.yinyang}{day_pillar.heaven_stem.element}"

        # 天运五行（年柱纳音）
        year_gz_str = f"{self.TIAN_GAN_NAMES[year_gz.tg]}{self.DI_ZHI_NAMES[year_gz.dz]}"
        fortune_element = self.NA_YIN_TABLE.get(year_gz_str, "")

        # 计算胎元
        tai_yuan = self._calculate_tai_yuan(month_gz.tg, month_gz.dz, day_stem_name)

        # 计算胎息（TODO: 实现真实计算）
        tai_xi = NaYinInfo(gan_zhi="戊辰", na_yin="大林木")

        # 计算身宫（TODO: 实现真实计算）
        shen_gong = self._calculate_shen_gong(month_gz.tg, month_gz.dz, hour_gz[0], hour_gz[1], day_stem_name)

        # 计算命宫
        ming_gong = self._calculate_ming_gong(month_gz.dz, hour_gz[1], day_stem_name)

        # 人元司令分野（TODO: 实现真实计算）
        ren_yuan_si_ling = self._calculate_ren_yuan_si_ling(birth_day)

        # 计算空亡
        kong_wang = self._calculate_kong_wang(day_gz.tg, day_gz.dz)

        # 计算节气信息
        birth_jieqi = self._calculate_birth_jieqi(birth_day, adjusted_dt.hour, adjusted_dt.minute)

        # 计算干支关系
        ganzi_relations = self.calculate_ganzi_relations(
            [year_pillar, month_pillar, day_pillar, hour_pillar]
        )

        return Chart(
            name=name,
            gender=gender,
            solar_datetime=original_solar_datetime,  # 显示原始输入的阳历时间
            lunar_date=lunar_date,
            year_pillar=year_pillar,
            month_pillar=month_pillar,
            day_pillar=day_pillar,
            hour_pillar=hour_pillar,
            day_master=day_pillar.heaven_stem,
            five_elements_count=five_elements_count,
            five_elements_ratio=five_elements_ratio,
            destiny_cycle=destiny_cycle,
            zodiac_animal=zodiac_animal,
            true_solar_datetime=true_solar_datetime,  # 真太阳时
            birth_place=birth_place,  # 出生地点
            birth_jieqi=birth_jieqi,
            zodiac_sign=zodiac_sign,
            star_mansion=star_mansion,
            day_master_display=day_master_display,
            fortune_element=fortune_element,
            tai_yuan=tai_yuan,
            tai_xi=tai_xi,
            shen_gong=shen_gong,
            ming_gong=ming_gong,
            ren_yuan_si_ling=ren_yuan_si_ling,
            kong_wang=kong_wang,
            ganzi_relations=ganzi_relations,
        )

    def _create_pillar_info(
        self, stem_index: int, branch_index: int, day_stem: str
    ) -> PillarInfo:
        stem_name = self.TIAN_GAN_NAMES[stem_index]
        branch_name = self.DI_ZHI_NAMES[branch_index]

        hidden_stem_list: List[HeavenStemInfo] = []
        for hidden_stem in self.BRANCH_HIDDEN_STEM[branch_name]:
            hidden_stem_list.append(
                HeavenStemInfo(
                    name=hidden_stem,
                    element=self.HEAVEN_STEM_ELEMENT_MAP[hidden_stem],
                    yinyang=self.TIAN_GAN_YIN_YANG[hidden_stem],
                    ten_god=self._calculate_stem_ten_god(hidden_stem, day_stem),
                )
            )

        heaven_stem = HeavenStemInfo(
            name=stem_name,
            element=self.HEAVEN_STEM_ELEMENT_MAP[stem_name],
            yinyang=self.TIAN_GAN_YIN_YANG[stem_name],
            ten_god=self._calculate_stem_ten_god(stem_name, day_stem),
        )

        earth_branch = EarthBranchInfo(
            name=branch_name,
            element=self.EARTH_BRANCH_ELEMENT_MAP[branch_name],
            yinyang=self.DI_ZHI_YIN_YANG[branch_name],
            hidden_stems=hidden_stem_list,
        )

        return PillarInfo(heaven_stem=heaven_stem, earth_branch=earth_branch)

    def _calculate_stem_ten_god(self, stem: str, day_stem: str) -> str:
        stem_element = self.HEAVEN_STEM_ELEMENT_MAP[stem]
        day_element = self.HEAVEN_STEM_ELEMENT_MAP[day_stem]
        relation = self.FIVE_ELEMENTS_RELATIONS[day_element][stem_element]
        stem_yinyang = self.TIAN_GAN_YIN_YANG[stem]
        day_yinyang = self.TIAN_GAN_YIN_YANG[day_stem]
        return self.TEN_GODS[("同" if stem_yinyang == day_yinyang else "异", relation)]

    def _get_hour_gz(self, day_stem: int, hour: int) -> Tuple[int, int]:
        branch_index = (hour + 1) // 2 % 12
        stem_index = ((day_stem % 10) * 2 + branch_index) % 10
        return stem_index, branch_index

    def _calculate_five_elements(self, pillars: List[PillarInfo]) -> Dict[str, int]:
        counts = {"木": 0, "火": 0, "土": 0, "金": 0, "水": 0}
        for pillar in pillars:
            counts[pillar.heaven_stem.element] += 1
            counts[pillar.earth_branch.element] += 1
            for hidden in pillar.earth_branch.hidden_stems:
                counts[hidden.element] += 1
        return counts

    def _calculate_five_elements_ratio(self, counts: Dict[str, int]) -> Dict[str, float]:
        total = sum(counts.values())
        if total == 0:
            return {key: 0.0 for key in counts}
        return {key: round(value / total * 100, 1) for key, value in counts.items()}

    def _calculate_dayun(
        self, birth_day: sxtwl.Day, hour: int, minute: int, gender: str, day_stem: str
    ) -> DestinyCycleInfo:
        year_gz = birth_day.getYearGZ()
        month_gz = birth_day.getMonthGZ()
        is_yang_year = self.TIAN_GAN_YIN_YANG[self.TIAN_GAN_NAMES[year_gz.tg]] == "阳"
        is_forward = (gender == "male" and is_yang_year) or (gender == "female" and not is_yang_year)

        _jieqi_idx, jieqi_time = self._get_nearest_jieqi_time(birth_day, is_forward)
        dayun_start_info = self._calculate_dayun_start_age(
            (birth_day.getSolarYear(), birth_day.getSolarMonth(), birth_day.getSolarDay(), hour, minute),
            (jieqi_time[0], jieqi_time[1], jieqi_time[2], jieqi_time[3], jieqi_time[4]),
        )
        start_age = dayun_start_info["start_age"]
        qiyun_date_solar = dayun_start_info["qiyun_date_solar"]

        destiny_pillars: List[DestinyPillarInfo] = []
        current_gz_index = self.SEXAGENARY_CYCLE.index(
            f"{self.TIAN_GAN_NAMES[month_gz.tg]}{self.DI_ZHI_NAMES[month_gz.dz]}"
        )
        first_cycle_year = qiyun_date_solar.year

        for i in range(8):
            current_gz_index = (current_gz_index + 1) % 60 if is_forward else (current_gz_index - 1 + 60) % 60
            gz = self.SEXAGENARY_CYCLE[current_gz_index]
            stem = gz[0]
            branch = gz[1]
            stem_index = self.TIAN_GAN_NAMES.index(stem)
            branch_index = self.DI_ZHI_NAMES.index(branch)
            pillar_info = self._create_pillar_info(stem_index, branch_index, day_stem)
            destiny_pillars.append(
                DestinyPillarInfo(
                    heaven_stem=pillar_info.heaven_stem,
                    earth_branch=pillar_info.earth_branch,
                    year=first_cycle_year + i * 10,
                )
            )

        return DestinyCycleInfo(
            destiny_pillars=destiny_pillars,
            start_age=start_age,
            qiyun_date_solar=dayun_start_info["qiyun_date_solar"],
            qiyun_date_lunar=dayun_start_info["qiyun_date_lunar"],
            is_forward=is_forward,
        )

    def _get_nearest_jieqi_time(
        self, day: sxtwl.Day, is_forward: bool
    ) -> Tuple[int, Tuple[int, int, int, int, int, int]]:
        _day = sxtwl.fromSolar(day.getSolarYear(), day.getSolarMonth(), day.getSolarDay())
        while True:
            if _day.hasJieQi():
                t = sxtwl.JD2DD(_day.getJieQiJD())
                return _day.getJieQi(), (t.Y, t.M, t.D, round(t.h), round(t.m), round(t.s))
            _day = _day.after(1) if is_forward else _day.before(1)

    def _calculate_dayun_start_age(self, birth_time: Tuple, jieqi_time: Tuple) -> dict:
        dt1 = datetime(birth_time[0], birth_time[1], birth_time[2], birth_time[3], birth_time[4])
        dt2 = datetime(jieqi_time[0], jieqi_time[1], jieqi_time[2], jieqi_time[3], jieqi_time[4])
        delta_minutes = abs(int((dt2 - dt1).total_seconds() / 60))

        days = delta_minutes // (24 * 60)
        remaining_minutes = delta_minutes % (24 * 60)
        hours = remaining_minutes // 60
        minutes = remaining_minutes % 60
        total_days = days + (hours / 24) + (minutes / (24 * 60))

        years = int(total_days // 3)
        remaining_days = total_days % 3
        months = int(remaining_days * 4)
        remaining_months_in_days = (remaining_days * 4) % 1
        final_days = int(remaining_months_in_days * 30)

        birth_date = dt1
        total_days_for_date = years * 365 + months * 30 + final_days
        qiyun_date = birth_date + timedelta(days=total_days_for_date)
        qiyun_date_day = sxtwl.fromSolar(qiyun_date.year, qiyun_date.month, qiyun_date.day)

        return {
            "raw_minutes": delta_minutes,
            "birth_to_jieqi": {"days": days, "hours": hours, "minutes": minutes},
            "start_age": StartAge(year=years, month=months, day=final_days),
            "qiyun_date_solar": SolarDate(year=qiyun_date.year, month=qiyun_date.month, day=qiyun_date.day),
            "qiyun_date_lunar": LunarDate(
                year=qiyun_date_day.getLunarYear(),
                month=qiyun_date_day.getLunarMonth(),
                day=qiyun_date_day.getLunarDay(),
                is_leap_month=qiyun_date_day.isLunarLeap(),
            ),
        }

    def _calculate_zodiac_sign(self, month: int, day: int) -> str:
        """根据月日计算星座"""
        for i, (sign, m, d) in enumerate(self.ZODIAC_SIGNS):
            if month == m and day <= d:
                return sign
            if month == m - 1 or (month == 12 and m == 1):
                prev_sign = self.ZODIAC_SIGNS[i - 1][0] if i > 0 else self.ZODIAC_SIGNS[-1][0]
                if month == m - 1 and day > self.ZODIAC_SIGNS[i - 1][2]:
                    return sign
        # 默认返回摩羯座（12月22日后）
        return "摩羯座"

    def _calculate_star_mansion(self, birth_day: sxtwl.Day) -> str:
        """计算星宿（简化版：基于日期索引）"""
        # 简化计算：基于儒略日计算星宿索引
        # TODO: 实现精确的星宿计算
        day_index = (birth_day.getSolarDay() + birth_day.getSolarMonth() * 2) % 28
        return self.STAR_MANSIONS[day_index]

    def _calculate_tai_yuan(self, month_stem_idx: int, month_branch_idx: int, day_stem: str) -> NaYinInfo:
        """
        计算胎元：月干进一位，月支进三位
        胎元 = (月干+1, 月支+3)
        """
        tai_yuan_stem_idx = (month_stem_idx + 1) % 10
        tai_yuan_branch_idx = (month_branch_idx + 3) % 12
        tai_yuan_stem = self.TIAN_GAN_NAMES[tai_yuan_stem_idx]
        tai_yuan_branch = self.DI_ZHI_NAMES[tai_yuan_branch_idx]
        gan_zhi = f"{tai_yuan_stem}{tai_yuan_branch}"
        na_yin = self.NA_YIN_TABLE.get(gan_zhi, "")
        return NaYinInfo(gan_zhi=gan_zhi, na_yin=na_yin)

    def _calculate_shen_gong(
        self, month_stem_idx: int, month_branch_idx: int,
        hour_stem_idx: int, hour_branch_idx: int, day_stem: str
    ) -> NaYinInfo:
        """
        计算身宫（简化版）
        身宫地支 = 14 - 月支 - 时支，若为负则加12
        身宫天干根据地支推算
        """
        shen_gong_branch_idx = (14 - month_branch_idx - hour_branch_idx) % 12
        # 身宫天干简化计算
        shen_gong_stem_idx = (month_stem_idx + shen_gong_branch_idx - month_branch_idx) % 10
        shen_gong_stem = self.TIAN_GAN_NAMES[shen_gong_stem_idx]
        shen_gong_branch = self.DI_ZHI_NAMES[shen_gong_branch_idx]
        gan_zhi = f"{shen_gong_stem}{shen_gong_branch}"
        na_yin = self.NA_YIN_TABLE.get(gan_zhi, "")
        return NaYinInfo(gan_zhi=gan_zhi, na_yin=na_yin)

    def _calculate_ming_gong(self, month_branch_idx: int, hour_branch_idx: int, day_stem: str) -> NaYinInfo:
        """
        计算命宫
        命宫地支 = 14 - 月支 - 时支（与身宫类似但计算方式略有不同）
        这里采用简化公式
        """
        ming_gong_branch_idx = (14 - month_branch_idx - hour_branch_idx) % 12
        # 命宫天干基于年干推算（简化）
        ming_gong_stem_idx = (ming_gong_branch_idx % 5) * 2 % 10
        ming_gong_stem = self.TIAN_GAN_NAMES[ming_gong_stem_idx]
        ming_gong_branch = self.DI_ZHI_NAMES[ming_gong_branch_idx]
        gan_zhi = f"{ming_gong_stem}{ming_gong_branch}"
        na_yin = self.NA_YIN_TABLE.get(gan_zhi, "")
        return NaYinInfo(gan_zhi=gan_zhi, na_yin=na_yin)

    def _calculate_ren_yuan_si_ling(self, birth_day: sxtwl.Day) -> str:
        """
        计算人元司令分野（简化版）
        基于月支藏干的当令情况
        """
        month_gz = birth_day.getMonthGZ()
        month_branch = self.DI_ZHI_NAMES[month_gz.dz]
        hidden_stems = self.BRANCH_HIDDEN_STEM.get(month_branch, [])
        if hidden_stems:
            # 返回主气（藏干第一位）+ "用事"
            main_stem = hidden_stems[0]
            element = self.HEAVEN_STEM_ELEMENT_MAP.get(main_stem, "")
            return f"{main_stem}{element}用事"
        return ""

    def _calculate_kong_wang(self, day_stem_idx: int, day_branch_idx: int) -> str:
        """
        计算空亡
        空亡是旬中没有的两个地支
        """
        # 找到日柱所在的旬首
        xun_start = (day_stem_idx - day_branch_idx) % 10
        # 空亡的两个地支是旬中缺失的
        kong_wang_1 = self.DI_ZHI_NAMES[(10 + xun_start) % 12]
        kong_wang_2 = self.DI_ZHI_NAMES[(11 + xun_start) % 12]
        return f"{kong_wang_1}{kong_wang_2}"

    def _calculate_birth_jieqi(self, birth_day: sxtwl.Day, hour: int, minute: int) -> JieQiInfo:
        """计算出生时间距离前后节气的时间"""
        birth_dt = datetime(
            birth_day.getSolarYear(), birth_day.getSolarMonth(), birth_day.getSolarDay(),
            hour, minute
        )

        # 向前找节气
        prev_jieqi_idx, prev_jieqi_time = self._get_nearest_jieqi_time(birth_day, is_forward=False)
        prev_jieqi_name = self.JIEQI_NAMES[prev_jieqi_idx % 24]
        prev_dt = datetime(prev_jieqi_time[0], prev_jieqi_time[1], prev_jieqi_time[2],
                          prev_jieqi_time[3], prev_jieqi_time[4])
        prev_delta = birth_dt - prev_dt
        prev_days = prev_delta.days
        prev_hours = prev_delta.seconds // 3600
        prev_distance = f"{prev_jieqi_name}后{prev_days}天{prev_hours}小时"

        # 向后找节气
        next_jieqi_idx, next_jieqi_time = self._get_nearest_jieqi_time(birth_day, is_forward=True)
        next_jieqi_name = self.JIEQI_NAMES[next_jieqi_idx % 24]
        next_dt = datetime(next_jieqi_time[0], next_jieqi_time[1], next_jieqi_time[2],
                          next_jieqi_time[3], next_jieqi_time[4])
        next_delta = next_dt - birth_dt
        next_days = next_delta.days
        next_hours = next_delta.seconds // 3600
        next_distance = f"{next_jieqi_name}前{next_days}天{next_hours}小时"

        return JieQiInfo(
            prev_jieqi=prev_jieqi_name,
            prev_distance=prev_distance,
            next_jieqi=next_jieqi_name,
            next_distance=next_distance,
        )

    def calculate_ganzi_relations(self, pillars: List[PillarInfo]) -> GanZhiRelations:
        """
        计算四柱之间的干支关系
        pillars: [year_pillar, month_pillar, day_pillar, hour_pillar]
        位置索引: 0=年, 1=月, 2=日, 3=时
        """
        stem_relations: List[GanZhiRelation] = []
        branch_relations: List[GanZhiRelation] = []
        stem_branch_relations: List[GanZhiRelation] = []
        
        # 提取四柱的天干和地支名称
        stems = [p.heaven_stem.name for p in pillars]
        branches = [p.earth_branch.name for p in pillars]
        
        # ========== 天干关系计算 ==========
        
        # 1. 天干五合
        for i in range(4):
            for j in range(i + 1, 4):
                pair = (stems[i], stems[j])
                pair_rev = (stems[j], stems[i])
                for combo_pair, element in self.STEM_COMBINATIONS.items():
                    if pair == combo_pair or pair_rev == combo_pair:
                        stem_relations.append(GanZhiRelation(
                            type="合化",
                            positions=[i, j],
                            description=f"{stems[i]}{stems[j]}合化{element}",
                            element=element,
                        ))
                        break
        
        # 2. 天干相冲
        for i in range(4):
            for j in range(i + 1, 4):
                pair = (stems[i], stems[j])
                pair_rev = (stems[j], stems[i])
                for clash_pair in self.STEM_CLASHES:
                    if pair == clash_pair or pair_rev == clash_pair:
                        stem_relations.append(GanZhiRelation(
                            type="相冲",
                            positions=[i, j],
                            description=f"{stems[i]}{stems[j]}冲",
                            element=None,
                        ))
                        break
        
        # 3. 天干相克（特定克制关系）
        for i in range(4):
            for j in range(4):
                if i == j:
                    continue
                pair = (stems[i], stems[j])
                # 检查是否是特定的克制对
                for ke_pair in self.STEM_KE_PAIRS:
                    if pair == ke_pair:
                        stem_relations.append(GanZhiRelation(
                            type="相克",
                            positions=[i, j],
                            description=f"{stems[i]}克{stems[j]}",
                            element=None,
                        ))
                        break
        
        # ========== 地支关系计算 ==========
        
        # 4. 地支六合
        for i in range(4):
            for j in range(i + 1, 4):
                pair = (branches[i], branches[j])
                pair_rev = (branches[j], branches[i])
                for combo_pair, element in self.BRANCH_SIX_COMBINATIONS.items():
                    if pair == combo_pair or pair_rev == combo_pair:
                        branch_relations.append(GanZhiRelation(
                            type="六合",
                            positions=[i, j],
                            description=f"{branches[i]}{branches[j]}合化{element}",
                            element=element,
                        ))
                        break
        
        # 5. 地支三合（需要三个地支都存在）
        for combo_set, element in self.BRANCH_THREE_COMBINATIONS.items():
            positions = []
            for branch in combo_set:
                for idx, b in enumerate(branches):
                    if b == branch and idx not in positions:
                        positions.append(idx)
                        break
            # 如果存在至少两个成员，记录半合
            if len(positions) >= 2:
                found_branches = [branches[p] for p in positions]
                if len(positions) == 3:
                    branch_relations.append(GanZhiRelation(
                        type="三合",
                        positions=sorted(positions),
                        description=f"{''.join(found_branches)}三合{element}局",
                        element=element,
                    ))
                else:
                    # 半合情况
                    branch_relations.append(GanZhiRelation(
                        type="半合",
                        positions=sorted(positions),
                        description=f"{''.join(found_branches)}半合{element}局",
                        element=element,
                    ))
        
        # 6. 地支三会（需要三个地支都存在）
        for combo_set, element in self.BRANCH_THREE_MEETINGS.items():
            positions = []
            for branch in combo_set:
                for idx, b in enumerate(branches):
                    if b == branch and idx not in positions:
                        positions.append(idx)
                        break
            if len(positions) == 3:
                found_branches = [branches[p] for p in positions]
                branch_relations.append(GanZhiRelation(
                    type="三会",
                    positions=sorted(positions),
                    description=f"{''.join(found_branches)}三会{element}方",
                    element=element,
                ))
        
        # 7. 地支六冲
        for i in range(4):
            for j in range(i + 1, 4):
                pair = (branches[i], branches[j])
                pair_rev = (branches[j], branches[i])
                for clash_pair in self.BRANCH_SIX_CLASHES:
                    if pair == clash_pair or pair_rev == clash_pair:
                        branch_relations.append(GanZhiRelation(
                            type="六冲",
                            positions=[i, j],
                            description=f"{branches[i]}{branches[j]}冲",
                            element=None,
                        ))
                        break
        
        # 8. 地支相刑
        for punishment_type, pairs in self.BRANCH_PUNISHMENTS.items():
            for pair in pairs:
                if pair[0] == pair[1]:
                    # 自刑：检查同一个地支出现两次
                    positions = [idx for idx, b in enumerate(branches) if b == pair[0]]
                    if len(positions) >= 2:
                        branch_relations.append(GanZhiRelation(
                            type="自刑",
                            positions=positions[:2],
                            description=f"{pair[0]}{pair[0]}自刑",
                            element=None,
                        ))
                else:
                    # 其他刑：检查两个地支是否都存在
                    pos1 = [idx for idx, b in enumerate(branches) if b == pair[0]]
                    pos2 = [idx for idx, b in enumerate(branches) if b == pair[1]]
                    if pos1 and pos2:
                        branch_relations.append(GanZhiRelation(
                            type="相刑",
                            positions=[pos1[0], pos2[0]],
                            description=f"{pair[0]}刑{pair[1]}（{punishment_type}）",
                            element=None,
                        ))
        
        # 9. 地支相害
        for i in range(4):
            for j in range(i + 1, 4):
                pair = (branches[i], branches[j])
                pair_rev = (branches[j], branches[i])
                for harm_pair in self.BRANCH_HARMS:
                    if pair == harm_pair or pair_rev == harm_pair:
                        branch_relations.append(GanZhiRelation(
                            type="相害",
                            positions=[i, j],
                            description=f"{branches[i]}{branches[j]}害",
                            element=None,
                        ))
                        break
        
        # ========== 天干地支相生关系计算（同柱）==========
        # 仅判断同一柱内：地支五行 是否 生 天干五行
        # 说明：根据产品需求，仅展示“地支生天干”的相生连线；不展示相克，也不展示“天干生地支”等其他方向。
        for i in range(4):
            stem_element = self.HEAVEN_STEM_ELEMENT_MAP[stems[i]]
            branch_element = self.EARTH_BRANCH_ELEMENT_MAP[branches[i]]
            
            # 检查地支生天干（branch_element 生 stem_element）
            if self.FIVE_ELEMENTS_生.get(branch_element) == stem_element:
                stem_branch_relations.append(GanZhiRelation(
                    type="相生",
                    positions=[i],
                    description=f"{branches[i]}{branch_element}生{stems[i]}{stem_element}",
                    element=stem_element,
                ))
        
        # 去除重复的关系（基于type + 排序后的positions）
        def dedupe(relations: List[GanZhiRelation]) -> List[GanZhiRelation]:
            seen_dict = {}
            for r in relations:
                # 使用排序后的 positions 作为去重的key
                # 这样 "子刑卯" 和 "卯刑子" 会被认为是同一个关系
                key = (r.type, tuple(sorted(r.positions)))
                if key not in seen_dict:
                    # 如果是首次遇到，直接添加
                    seen_dict[key] = r
                else:
                    # 如果已存在，保留 positions 本身已经有序的那个（更规范）
                    existing = seen_dict[key]
                    if list(r.positions) == sorted(r.positions) and list(existing.positions) != sorted(existing.positions):
                        # 当前的 positions 是有序的，替换之前无序的
                        seen_dict[key] = r
            return list(seen_dict.values())
        
        return GanZhiRelations(
            stem_relations=dedupe(stem_relations),
            branch_relations=dedupe(branch_relations),
            stem_branch_relations=dedupe(stem_branch_relations),
        )

    def find_dates_by_pillars(
        self,
        year_pillar: str,
        month_pillar: str,
        day_pillar: str,
        hour_pillar: str,
        start_year: int = 1801,
        end_year: int = 2099,
    ) -> List[Dict[str, Any]]:
        """
        根据四柱八字查找对应的日期
        
        Args:
            year_pillar: 年柱，如"甲子"
            month_pillar: 月柱，如"乙丑"
            day_pillar: 日柱，如"丙寅"
            hour_pillar: 时柱，如"丁卯"
            start_year: 查找起始年份
            end_year: 查找结束年份
            
        Returns:
            匹配的日期列表
        """
        matched_dates = []
        
        # 验证四柱格式
        if (
            len(year_pillar) != 2
            or len(month_pillar) != 2
            or len(day_pillar) != 2
            or len(hour_pillar) != 2
        ):
            raise ValueError("四柱格式错误，每柱应为两个字符（天干+地支）")
        
        # 遍历每一年
        for year in range(start_year, end_year + 1):
            # 遍历每一天（使用简单的日期遍历）
            for month in range(1, 13):
                # 确定每月的天数
                if month in [1, 3, 5, 7, 8, 10, 12]:
                    days_in_month = 31
                elif month in [4, 6, 9, 11]:
                    days_in_month = 30
                else:  # 2月
                    # 判断闰年
                    if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
                        days_in_month = 29
                    else:
                        days_in_month = 28
                
                for day in range(1, days_in_month + 1):
                    # 尝试计算这一天的四柱
                    try:
                        birth_day = sxtwl.fromSolar(year, month, day)
                        year_gz = birth_day.getYearGZ()
                        month_gz = birth_day.getMonthGZ()
                        day_gz = birth_day.getDayGZ()
                        
                        # 比对年柱、月柱、日柱
                        year_str = f"{self.TIAN_GAN_NAMES[year_gz.tg]}{self.DI_ZHI_NAMES[year_gz.dz]}"
                        month_str = f"{self.TIAN_GAN_NAMES[month_gz.tg]}{self.DI_ZHI_NAMES[month_gz.dz]}"
                        day_str = f"{self.TIAN_GAN_NAMES[day_gz.tg]}{self.DI_ZHI_NAMES[day_gz.dz]}"
                        
                        # 只有年月日都匹配时，才检查时柱
                        if (
                            year_str == year_pillar
                            and month_str == month_pillar
                            and day_str == day_pillar
                        ):
                            # 遍历每个时辰（24小时，每2小时一个时辰）
                            for hour in range(0, 24, 2):
                                hour_gz = self._get_hour_gz(day_gz.tg, hour)
                                hour_str = f"{self.TIAN_GAN_NAMES[hour_gz[0]]}{self.DI_ZHI_NAMES[hour_gz[1]]}"
                                
                                if hour_str == hour_pillar:
                                    # 找到匹配的日期时间
                                    # 计算农历信息用于显示
                                    lunar_year = birth_day.getLunarYear()
                                    lunar_month = birth_day.getLunarMonth()
                                    lunar_day = birth_day.getLunarDay()
                                    is_leap = birth_day.isLunarLeap()
                                    
                                    lunar_month_labels = [
                                        "正月", "二月", "三月", "四月", "五月", "六月",
                                        "七月", "八月", "九月", "十月", "冬月", "腊月"
                                    ]
                                    lunar_display = f"农历{lunar_year}年{'闰' if is_leap else ''}{lunar_month_labels[lunar_month - 1]}{lunar_day}日 {hour:02d}时"
                                    
                                    matched_dates.append({
                                        "year": year,
                                        "month": month,
                                        "day": day,
                                        "hour": hour,
                                        "minute": 0,
                                        "lunar_display": lunar_display,
                                    })
                    except Exception:
                        # 跳过无效日期
                        continue
        
        return matched_dates
