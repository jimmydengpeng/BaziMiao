from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from src.models.analysis import Analysis
from src.models.chart import Chart
from src.models.knowledge import KnowledgeChunk


TIAN_GAN_NAMES = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
DI_ZHI_NAMES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

REPORT_SCHEMA_VERSION = "bazi_report_v1"

REPORT_SECTIONS_PLAN = [
    {"section_id": "chart_basic", "title": "八字基本命盘分析"},
    {"section_id": "personality", "title": "性格底色"},
    {"section_id": "appearance", "title": "外貌特点"},
    {"section_id": "talent_radar", "title": "特长天赋雷达图"},
    {"section_id": "career_industry", "title": "适合的工作/行业"},
    {"section_id": "wealth_career", "title": "财富/事业"},
    {"section_id": "love_marriage", "title": "姻缘/感情"},
    {"section_id": "family", "title": "家庭六亲"},
    {"section_id": "health", "title": "身体健康"},
    {"section_id": "recent_trend", "title": "近年趋势与提醒"},
    {"section_id": "summary", "title": "总结"},
]

RADAR_DIMENSIONS = [
    {"key": "learning", "label": "学习吸收"},
    {"key": "execution", "label": "执行落地"},
    {"key": "leadership", "label": "统筹领导"},
    {"key": "creativity", "label": "创意表达"},
    {"key": "business", "label": "商业嗅觉"},
    {"key": "relationship", "label": "人际协同"},
]

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
2. 分析命盘五行能量强弱。
3. 结合已给出的大运与流年信息进行验证与解读；若缺少历史事件信息，请明确说明无法验证，不要编造。
4. 分析预测命主的感情状况（避免确定性断言，给出条件性建议）。
5. 分析预测{cur_year}年的运势（基于已提供事实给出趋势判断）。

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
每个 section 都需要对你认为最重要/用户最可能关心的要点做“重点标记”，建议用 **加粗** 标出关键结论或关键词（避免整段都加粗）。
请严格输出 JSON。
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
        cur_year=today.year,
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


def build_report_stream_prompt(
    chart: Chart,
    analysis: Analysis,
    knowledge: List[KnowledgeChunk],
    focus: List[str],
    report_id: str,
) -> Dict[str, str]:
    """
    构造“事件流 JSON Lines”模式的报告 Prompt。

    约束：
    - 只输出 JSON Lines（每行一个事件 JSON）
    - 由服务端先发送 report_start，模型从 section_start 开始
    - 逐段输出，便于前端“分段解锁”渲染
    """
    system = (
        "你是一位严谨的传统命理师。你收到的八字、规则分析、知识片段均为事实。"
        "禁止自行重算八字、修改四柱、添加新格局或新十神。"
        "当信息不足时，必须明确说明“目前信息不足以下定论”，不得编造。"
        "输出语气温和理性，避免夸大或恐吓。"
        "\n\n"
        "【输出格式强约束】\n"
        "你必须只输出 JSON Lines：每一行必须是一个完整 JSON 对象。"
        "除 JSON 以外禁止输出任何字符（包括 Markdown、代码块、解释性文字）。"
        "每行必须以 { 开头，以 } 结尾；不允许输出数组；不允许输出多行 JSON。"
        "\n\n"
        "【事件协议】（只能输出以下 type）\n"
        "- section_start: {type, section_id}\n"
        "- section_delta: {type, section_id, seq, delta}\n"
        "- section_patch(可选): {type, section_id, patch:{...}}\n"
        "- section_done: {type, section_id}\n"
        "- report_done: {type}\n"
        "\n\n"
        "【硬性规则】\n"
        "1) 严格按 sections_plan 顺序生成，每段必须：section_start → 多条 section_delta →（可选1条 section_patch）→ section_done；在上一段 section_done 之前，禁止输出下一段 section_start。\n"
        "2) section_delta 的 delta 只用于拼接该段的 content_md（自然语言文本片段，长度适中，多条输出）。\n"
        "3) structured 尽量通过 section_patch 一次性给出（尤其是 talent_radar 的 dimensions 分数）。\n"
        "4) 禁止输出三引号代码块；正文允许使用简单 Markdown-lite（段落、列表、**加粗**、*强调*），但不要使用 # 标题。\n"
        "5) 每个 section 的正文必须包含“重点标记”：对关键结论/关键词使用 **加粗**（建议至少 3 处），避免整段都加粗。\n"
        "6) 事件可省略 title 字段（服务端会按 section_id 自动补 title）。\n"
        "7) 最后一行必须是 report_done；report_done 只需要包含 type，不要附带完整报告 JSON。\n"
        "8) final_report_schema 仅用于理解字段含义与写作口径，其中占位符不是事实；本次事实以 user.input_refs_backend/chart/analysis 为准，你不需要在任何事件里输出它。\n"
        "9) visualization_plan 中列出的图表必须在对应 section 的 section_patch 中输出 structured，禁止放进正文 delta。\n"
        "10) 所有图表分数范围为 0-100，仅用于相对强弱比较；信息不足时分数填 null，并在 notes/summary 说明原因。\n"
    )

    today = datetime.now()
    focus_text = "、".join(focus) if focus else "暂无"
    current_year = today.year
    trend_years = [current_year + offset for offset in range(5)]

    # 供模型参考的“最终落库 JSON”结构（示例/骨架，不要求字段完全一致，但 key 必须齐）
    final_report_schema = {
        "meta": {
            "version": REPORT_SCHEMA_VERSION,
            "generated_at": today.isoformat(),
            "language": "zh-CN",
            "tone": "温和中肯",
            "disclaimer": "本报告仅基于已提供事实进行解读，不构成确定性承诺或医疗/投资建议。",
        },
        "input_refs": {
            "solar_date": "<本次输入>",
            "lunar_date": "<本次输入>",
            "birth_time": "<本次输入>",
            "bazi_str": "<本次输入>",
            "gender": "<本次输入>",
            "cur_dayun": "<本次输入>",
            "cur_liunian": "<本次输入>",
            "day_master": "<本次输入>",
            "five_elements_count": "<本次输入>",
            "pattern_tags": ["<本次输入>"],
            "yong_shen": ["<本次输入>"],
            "ji_shen": ["<本次输入>"],
        },
        "sections": [
            {
                "id": "chart_basic",
                "title": "八字基本命盘分析",
                "summary": "一句话总括（可选）",
                "content_md": "正文（Markdown-lite，不允许代码块）",
                "structured": {
                    "day_master_strength": {
                        "label": "身强/身弱/偏强/偏弱/中和",
                        "confidence": 0.0,
                        "reasons": ["..."],
                    },
                    "strength_gauge": {
                        "score": 0,
                        "label": "身强/身弱/偏强/偏弱/中和",
                        "confidence": 0.0,
                        "notes": ["..."],
                    },
                    "pattern": {"name": "格局名称（若信息不足写“信息不足”）", "reasons": ["..."]},
                    "yong_ji": {
                        "yong_shen": ["..."],
                        "ji_shen": ["..."],
                        "notes": ["..."],
                    },
                },
            },
            {
                "id": "talent_radar",
                "title": "特长天赋雷达图",
                "content_md": "解释口径：十神 -> 能力维度 -> 职业倾向",
                "structured": {
                    "dimensions": [
                        {"key": "learning", "label": "学习吸收", "score": 0},
                    ],
                    "ten_gods_basis": [{"god": "正印", "weight": 0.0, "notes": "..."}],
                    "career_matches": ["..."],
                },
            },
            {
                "id": "wealth_career",
                "title": "财富/事业",
                "content_md": "财富来源结构与风险提示",
                "structured": {
                    "wealth_sources": [
                        {"key": "zhengcai", "label": "正财", "score": 0, "notes": "..."},
                        {"key": "piancai", "label": "偏财", "score": 0, "notes": "..."},
                        {"key": "skill", "label": "技能变现", "score": 0, "notes": "..."},
                        {"key": "resource", "label": "资源整合", "score": 0, "notes": "..."},
                        {"key": "investment", "label": "投资投机", "score": 0, "notes": "..."},
                        {"key": "accumulation", "label": "长期积累", "score": 0, "notes": "..."},
                    ],
                    "summary": "一句话总结财富结构特点",
                },
            },
            {
                "id": "recent_trend",
                "title": "近年趋势与提醒",
                "content_md": "未来 5 年趋势解读（结合当前大运）",
                "structured": {
                    "trend_lines": {
                        "years": trend_years,
                        "series": [
                            {"key": "overall", "label": "综合走势", "values": [0, 0, 0, 0, 0]},
                        ],
                        "dayun_context": "结合当前大运作解释",
                        "notes": ["..."],
                    }
                },
            },
            {
                "id": "summary",
                "title": "总结",
                "content_md": "行动优先级与落地建议",
                "structured": {
                    "action_priorities": [
                        {"rank": 1, "title": "行动要点", "score": 0, "why": "...", "how": "..."},
                        {"rank": 2, "title": "行动要点", "score": 0, "why": "...", "how": "..."},
                        {"rank": 3, "title": "行动要点", "score": 0, "why": "...", "how": "..."},
                        {"rank": 4, "title": "行动要点", "score": 0, "why": "...", "how": "..."},
                        {"rank": 5, "title": "行动要点", "score": 0, "why": "...", "how": "..."},
                    ],
                },
            },
        ],
    }

    user = {
        "sections_plan": list(REPORT_SECTIONS_PLAN),
        "radar_dimensions": list(RADAR_DIMENSIONS),
        "visualization_plan": {
            "chart_basic": {
                "charts": [
                    {
                        "id": "strength_gauge",
                        "type": "gauge",
                        "value_range": "0-100",
                        "note": "分数优先对齐 analysis.strength_score，标签使用身强/身弱/偏强/偏弱/中和。",
                    }
                ]
            },
            "recent_trend": {
                "charts": [
                    {
                        "id": "liunian_trend",
                        "type": "line",
                        "years": trend_years,
                        "series": [
                            {"key": "overall", "label": "综合走势", "value_range": "0-100"},
                        ],
                        "note": "趋势需结合当前大运与流年信息解读。",
                    }
                ]
            },
            "wealth_career": {
                "charts": [
                    {
                        "id": "wealth_sources",
                        "type": "stacked_bar_or_radar",
                        "value_range": "0-100",
                        "dimensions": [
                            {"key": "zhengcai", "label": "正财"},
                            {"key": "piancai", "label": "偏财"},
                            {"key": "skill", "label": "技能变现"},
                            {"key": "resource", "label": "资源整合"},
                            {"key": "investment", "label": "投资投机"},
                            {"key": "accumulation", "label": "长期积累"},
                        ],
                    }
                ]
            },
            "summary": {
                "charts": [
                    {
                        "id": "action_priorities",
                        "type": "rank_bar",
                        "count": 5,
                        "value_range": "0-100",
                    }
                ]
            },
        },
        "final_report_schema": final_report_schema,
        "constraints": {
            "focus_text": focus_text,
            "must_cover_year": current_year,
            "avoid_deterministic_claims": True,
        },
        "input_refs_backend": {
            "solar_date": _format_solar_date(chart),
            "lunar_date": _format_lunar_date(chart),
            "birth_time": _format_birth_time(chart),
            "bazi_str": _format_bazi(chart),
            "gender": _gender_label(chart.gender),
            "cur_date_ymd": f"{today.year}年{today.month}月{today.day}日",
            "cur_dayun": _current_dayun(chart, today),
            "cur_liunian": _current_liunian(today),
            "day_master": chart.day_master.name,
            "five_elements_count": _format_elements_count(chart.five_elements_count),
            "pattern_tags": analysis.pattern_tags,
            "yong_shen": analysis.yi_yong_shen,
            "ji_shen": analysis.ji_shen,
            "key_conclusions": analysis.key_conclusions,
            "risk_points": analysis.risk_points,
            "luck_highlights": [item.model_dump() for item in analysis.luck_highlights],
        },
        "chart": chart.model_dump(mode="json"),
        "analysis": analysis.model_dump(mode="json"),
        "retrieved_knowledge": [k.model_dump() for k in knowledge],
        "user_focus": list(focus),
    }

    return {"system": system, "user": user}
