from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import sxtwl

from src.models.chart import (
    Chart,
    DestinyCycleInfo,
    DestinyPillarInfo,
    EarthBranchInfo,
    HeavenStemInfo,
    LunarDate,
    PillarInfo,
    SolarDate,
    StartAge,
)


class BaziPaipanEngine:
    """八字排盘引擎：负责确定性排盘，不做任何解读。"""

    TIAN_GAN_NAMES = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
    DI_ZHI_NAMES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
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
        use_true_solar_time: bool = False,
        tz_offset_hours: int = 0,
    ) -> Chart:
        """计算排盘，返回结构化 Chart。"""
        # TODO: 真太阳时、早晚子时、时区偏移在此调整
        _ = use_true_solar_time
        adjusted_dt = solar_datetime + timedelta(hours=tz_offset_hours)

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

        return Chart(
            name=name,
            gender=gender,
            solar_datetime=adjusted_dt,
            lunar_date=lunar_date,
            year_pillar=year_pillar,
            month_pillar=month_pillar,
            day_pillar=day_pillar,
            hour_pillar=hour_pillar,
            day_master=day_pillar.heaven_stem,
            five_elements_count=five_elements_count,
            destiny_cycle=destiny_cycle,
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
