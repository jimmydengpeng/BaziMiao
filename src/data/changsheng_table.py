from __future__ import annotations

from typing import Dict, List

CHANG_SHENG_STAGES: List[str] = [
    "长生",
    "沐浴",
    "冠带",
    "临官",
    "帝旺",
    "衰",
    "病",
    "死",
    "墓",
    "绝",
    "胎",
    "养",
]

DI_ZHI_ORDER: List[str] = [
    "子",
    "丑",
    "寅",
    "卯",
    "辰",
    "巳",
    "午",
    "未",
    "申",
    "酉",
    "戌",
    "亥",
]

STEM_CHANG_SHENG_START: Dict[str, Dict[str, int]] = {
    "甲": {"start": "亥", "direction": 1},
    "乙": {"start": "午", "direction": -1},
    "丙": {"start": "寅", "direction": 1},
    "丁": {"start": "酉", "direction": -1},
    "戊": {"start": "寅", "direction": 1},
    "己": {"start": "酉", "direction": -1},
    "庚": {"start": "巳", "direction": 1},
    "辛": {"start": "子", "direction": -1},
    "壬": {"start": "申", "direction": 1},
    "癸": {"start": "卯", "direction": -1},
}


def build_chang_sheng_table() -> Dict[str, Dict[str, str]]:
    table: Dict[str, Dict[str, str]] = {}
    branch_count = len(DI_ZHI_ORDER)
    for stem, config in STEM_CHANG_SHENG_START.items():
        start_branch = config["start"]
        direction = config["direction"]
        start_index = DI_ZHI_ORDER.index(start_branch)
        mapping: Dict[str, str] = {}
        for i, stage in enumerate(CHANG_SHENG_STAGES):
            branch_index = (start_index + direction * i) % branch_count
            mapping[DI_ZHI_ORDER[branch_index]] = stage
        table[stem] = mapping
    return table


STEM_CHANG_SHENG_TABLE: Dict[str, Dict[str, str]] = build_chang_sheng_table()
