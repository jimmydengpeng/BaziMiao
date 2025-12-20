from __future__ import annotations

from typing import List

from src.models.analysis import Analysis, LuckHighlight
from src.models.chart import Chart


SUPPORT_MAP = {"木": "水", "火": "木", "土": "火", "金": "土", "水": "金"}
CONTROL_MAP = {"木": "土", "火": "金", "土": "水", "金": "木", "水": "火"}


def evaluate_chart(chart: Chart) -> Analysis:
    """
    基于五行数量做一个轻量的规则层，给模型提供标签和用忌神提示。
    这里的逻辑故意保持简化，方便后续替换成更严谨的规则。
    """
    day_element = chart.day_master.element
    support = SUPPORT_MAP[day_element]
    control_by = CONTROL_MAP[day_element]
    control_target = {v: k for k, v in CONTROL_MAP.items()}[day_element]

    counts = chart.five_elements_count
    support_score = counts.get(day_element, 0) + counts.get(support, 0)
    pressure_score = counts.get(control_by, 0)
    leak_score = counts.get(control_target, 0)
    raw_score = support_score * 12 + leak_score * 6 - pressure_score * 10
    strength_score = max(0, min(100, 50 + raw_score))
    pattern = "身强" if strength_score >= 60 else "身弱"

    yi_yong_shen: List[str] = []
    ji_shen: List[str] = []
    if pattern == "身强":
        yi_yong_shen = [control_target, CONTROL_MAP[control_target]]
        ji_shen = [day_element, support, control_by]
    else:
        yi_yong_shen = [day_element, support]
        ji_shen = [control_target, control_by]

    pattern_tags = [pattern]
    if counts.get(control_by, 0) >= 3:
        pattern_tags.append("官杀偏旺")
    if counts.get(control_target, 0) >= 3:
        pattern_tags.append("食伤泄秀")
    if counts.get(day_element, 0) >= 3 and counts.get(support, 0) >= 2:
        pattern_tags.append("帮身有力")

    key_conclusions = [
        f"日主五行：{day_element}，身{pattern[-1]}",
        f"用神倾向：{'、'.join(yi_yong_shen)}",
    ]
    risk_points = [
        f"忌神：{'、'.join(ji_shen)}，相关岁运注意克泄耗与健康波动。",
        "规则层为简版，仅供生成器参考，可在后端扩展更严谨的判定。",
    ]

    luck_highlights: List[LuckHighlight] = []
    for idx, pillar in enumerate(chart.destiny_cycle.destiny_pillars[:3]):
        element_tendency = f"{pillar.heaven_stem.element}{pillar.earth_branch.element}"
        luck_highlights.append(
            LuckHighlight(
                start_age=chart.destiny_cycle.start_age.year + idx * 10,
                year=pillar.year,
                pillar=f"{pillar.heaven_stem.name}{pillar.earth_branch.name}",
                element_tendency=f"{element_tendency}气势",
                summary=f"大运五行侧重：{element_tendency}",
            )
        )

    return Analysis(
        pattern=pattern,
        strength_score=strength_score,
        yi_yong_shen=yi_yong_shen,
        ji_shen=ji_shen,
        pattern_tags=pattern_tags,
        key_conclusions=key_conclusions,
        risk_points=risk_points,
        luck_highlights=luck_highlights,
    )

