from __future__ import annotations

from typing import Dict, List

from src.models.analysis import Analysis
from src.models.chart import Chart
from src.models.knowledge import KnowledgeChunk


def build_report_prompt(
    chart: Chart, analysis: Analysis, knowledge: List[KnowledgeChunk], focus: List[str]
) -> Dict[str, str]:
    """构造给大模型的 system/user Prompt，强调“不重算只解读”."""
    system = (
        "你是一位严谨的传统命理师。你收到的八字、规则分析、知识片段均为事实。"
        "禁止自行重算八字、修改四柱、添加新格局或新十神。"
        "当信息不足时，请说明“目前信息不足以下定论”。"
        "输出使用温和理性语气，避免夸大或恐吓。"
    )

    user = {
        "chart": chart.model_dump(),
        "analysis": analysis.model_dump(),
        "retrieved_knowledge": [k.model_dump() for k in knowledge],
        "user_focus": list(focus),
        "output_expectation": {
            "format": {
                "overall_tone": "温和中肯",
                "sections": [
                    {"title": "一、命局总体气质", "content": "..."},
                    {"title": "二、事业发展趋势", "content": "..."},
                    {"title": "三、财富机会与风险", "content": "..."},
                    {"title": "四、性格与人际特点", "content": "..."},
                    {"title": "五、小结与建议", "content": "..."},
                ],
                "facts_ref": ["引用已提供的事实，不得新增结构化结论"],
            }
        },
    }

    return {"system": system, "user": user}

