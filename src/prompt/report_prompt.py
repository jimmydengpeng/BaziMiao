from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from src.models.analysis import Analysis
from src.models.chart import Chart
from src.models.knowledge import KnowledgeChunk


TIAN_GAN_NAMES = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
DI_ZHI_NAMES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

BAZI_REPORT_TEMPLATE = """
你是一名资深命理学家，熟读《三命通会》、《渊海子平》、《滴天髓》、《穷通宝鉴》、《子平真诠》等命理经典，
请根据以下命主信息进行深度命盘解析（仅基于已提供事实，不得重算或杜撰）：

命主信息:
- 出生日期（阳历）: {solar_date}
- 出生日期（农历）: {lunar_date}
- 出生时间: {birth_time}
- 四柱八字: {bazi_str}
- 性别: {gender}
- 当前时间：{cur_date_ymd}
- 当前大运：{cur_dayun_ganzhi}
- 当前流年：{cur_liunian_ganzhi}
- 日主: {day_master}
- 五行统计: {five_elements_count}
- 用神/忌神: {yi_yong_shen} / {ji_shen}
- 标签: {pattern_tags}
- 关键结论: {key_conclusions}
- 风险提示: {risk_points}
- 大运摘要: {luck_highlights}
- 用户关注方向: {focus_text}

请根据以上信息，提供一份详细的八字命理分析报告，包括但不限于以下方面:
1. 命主的五行特点和日主旺衰分析
2. 命局特点和格局分析
3. 性格特点和天赋才能
4. 事业发展方向和建议
5. 财运分析和理财建议
6. 健康状况分析和养生建议
7. 人际关系和婚姻分析

请重点解读：
1. 整体分析格局，考虑身强身弱，分析十神关系，体用平衡。注意逻辑合理，综合各种信息交叉验证。
2. 绘制命盘能量分布图（用ASCII字符呈现五行强弱）。
3. 结合已给出的大运与流年信息进行验证与解读；若缺少历史事件信息，请明确说明无法验证，不要编造。
4. 分析预测命主的感情状况（避免确定性断言，给出条件性建议）。
5. 分析预测2025年的运势（基于已提供事实给出趋势判断）。

可以参考的命理基础知识：
地支藏干：
子：癸
丑：己、辛、癸
寅：甲、丙、戊
卯：乙
辰：戊、乙、癸
巳：丙、庚、戊
午：丁、己
未：己、丁、乙
申：庚、壬、戊
酉：辛
戌：戊、辛、丁
亥：壬、甲

请使用专业但通俗易懂的语言，避免过于迷信的说法，注重实用性建议。
请严格输出 JSON，不要输出 Markdown、代码块或额外解释。
"""


def _format_lunar_date(chart: Chart) -> str:
    lunar = chart.lunar_date
    leap = "闰" if lunar.is_leap_month else ""
    return f"{lunar.year}年{leap}{lunar.month}月{lunar.day}日"


def _format_solar_date(chart: Chart) -> str:
    dt = chart.solar_datetime
    return f"{dt.year}年{dt.month}月{dt.day}日"


def _format_birth_time(chart: Chart) -> str:
    dt = chart.solar_datetime
    return f"{dt.hour}点{dt.minute}分"


def _format_pillar(pillar) -> str:
    return f"{pillar.heaven_stem.name}{pillar.earth_branch.name}"


def _format_bazi(chart: Chart) -> str:
    return " ".join(
        [
            _format_pillar(chart.year_pillar),
            _format_pillar(chart.month_pillar),
            _format_pillar(chart.day_pillar),
            _format_pillar(chart.hour_pillar),
        ]
    )


def _gender_label(gender: Optional[str]) -> str:
    if gender == "male":
        return "男"
    if gender == "female":
        return "女"
    return "其他"


def _format_elements_count(counts: Dict[str, int]) -> str:
    order = ["木", "火", "土", "金", "水"]
    parts = [f"{key}{counts.get(key, 0)}" for key in order]
    return "，".join(parts) if parts else "未知"


def _calculate_age_years(birth: datetime, today: datetime) -> int:
    years = today.year - birth.year
    if (today.month, today.day) < (birth.month, birth.day):
        years -= 1
    return max(years, 0)


def _current_dayun(chart: Chart, today: datetime) -> str:
    destiny_cycle = chart.destiny_cycle
    pillars = destiny_cycle.destiny_pillars
    if not pillars:
        return "未知"
    start_age = destiny_cycle.start_age.year
    age = _calculate_age_years(chart.solar_datetime, today)
    if age < start_age:
        return f"未起运（约{start_age}岁起运）"
    index = (age - start_age) // 10
    if index >= len(pillars):
        index = len(pillars) - 1
    pillar = pillars[index]
    return f"{pillar.heaven_stem.name}{pillar.earth_branch.name}"


def _current_liunian(today: datetime) -> str:
    try:
        import sxtwl
    except ImportError:
        return "未知"
    try:
        day = sxtwl.fromSolar(today.year, today.month, today.day)
        gz = day.getYearGZ()
        return f"{TIAN_GAN_NAMES[gz.tg]}{DI_ZHI_NAMES[gz.dz]}"
    except Exception:
        return "未知"


def _format_luck_highlights(analysis: Analysis) -> str:
    if not analysis.luck_highlights:
        return "暂无"
    parts = []
    for item in analysis.luck_highlights:
        summary = f"({item.summary})" if item.summary else ""
        parts.append(f"{item.start_age}岁起 {item.pillar}{summary}")
    return "；".join(parts)


def build_report_prompt(
    chart: Chart, analysis: Analysis, knowledge: List[KnowledgeChunk], focus: List[str]
) -> Dict[str, str]:
    """构造给大模型的 Prompt，强调“不重算只解读”。"""
    system = (
        "你是一位严谨的传统命理师。你收到的八字、规则分析、知识片段均为事实。"
        "禁止自行重算八字、修改四柱、添加新格局或新十神。"
        "当信息不足时，请说明“目前信息不足以下定论”。"
        "输出使用温和理性语气，避免夸大或恐吓。"
        "请严格输出 JSON，不要输出 Markdown、代码块或额外解释。"
    )

    today = datetime.now()
    focus_text = "、".join(focus) if focus else "暂无"
    report_instruction = BAZI_REPORT_TEMPLATE.format(
        solar_date=_format_solar_date(chart),
        lunar_date=_format_lunar_date(chart),
        birth_time=_format_birth_time(chart),
        bazi_str=_format_bazi(chart),
        gender=_gender_label(chart.gender),
        cur_date_ymd=f"{today.year}年{today.month}月{today.day}日",
        cur_dayun_ganzhi=_current_dayun(chart, today),
        cur_liunian_ganzhi=_current_liunian(today),
        day_master=chart.day_master.name,
        five_elements_count=_format_elements_count(chart.five_elements_count),
        yi_yong_shen="、".join(analysis.yi_yong_shen) if analysis.yi_yong_shen else "未知",
        ji_shen="、".join(analysis.ji_shen) if analysis.ji_shen else "未知",
        pattern_tags="、".join(analysis.pattern_tags) if analysis.pattern_tags else "暂无",
        key_conclusions="、".join(analysis.key_conclusions) if analysis.key_conclusions else "暂无",
        risk_points="、".join(analysis.risk_points) if analysis.risk_points else "暂无",
        luck_highlights=_format_luck_highlights(analysis),
        focus_text=focus_text,
    )

    user = {
        "report_instruction": report_instruction.strip(),
        "chart": chart.model_dump(mode="json"),
        "analysis": analysis.model_dump(mode="json"),
        "retrieved_knowledge": [k.model_dump() for k in knowledge],
        "user_focus": list(focus),
        "output_schema": {
            "overall_tone": "温和中肯",
            "sections": [
                {"title": "一、命局总体气质", "content": "..."},
                {"title": "二、事业发展趋势", "content": "..."},
                {"title": "三、财富机会与风险", "content": "..."},
                {"title": "四、性格与人际特点", "content": "..."},
                {"title": "五、小结与建议", "content": "..."},
                {"title": "六、健康与人际情感", "content": "..."},
                {"title": "七、近年趋势与提醒", "content": "..."},
            ],
            "facts_ref": ["引用已提供的事实，不得新增结构化结论"],
            "energy_chart": "使用 ASCII 字符呈现五行强弱",
        },
    }

    return {"system": system, "user": user}
