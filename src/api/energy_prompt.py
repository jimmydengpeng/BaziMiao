"""五行能量智能分析 Prompt 构建模块"""
from typing import Any, Dict


def build_energy_analysis_prompt(chart: Dict[str, Any]) -> str:
    """
    构建五行能量智能分析的 Prompt

    发送四柱八字和藏干信息，让 AI 综合分析命局中五行的强弱，
    为每个五行的能量占比给一个分数（0-100），并给出简短描述。
    """
    # 提取四柱信息
    pillars = [
        chart.get("year_pillar", {}),
        chart.get("month_pillar", {}),
        chart.get("day_pillar", {}),
        chart.get("hour_pillar", {}),
    ]

    day_master = chart.get("day_master", {})
    day_master_name = day_master.get("name", "")
    day_master_element = day_master.get("element", "")

    # 构建四柱和藏干信息文本
    pillar_info = []
    for i, pillar in enumerate(pillars):
        hs = pillar.get("heaven_stem", {})
        eb = pillar.get("earth_branch", {})
        hidden = eb.get("hidden_stems", [])

        hidden_str = ", ".join([f"{h.get('name', '')}({h.get('element', '')})" for h in hidden]) if hidden else "无"
        pillar_info.append(
            f"{['年', '月', '日', '时'][i]}柱: 天干{hs.get('name', '')}({hs.get('element', '')}), "
            f"地支{eb.get('name', '')}({eb.get('element', '')}), 藏干: {hidden_str}"
        )

    # 构建藏干五行统计
    hidden_elements = {"木": 0, "火": 0, "土": 0, "金": 0, "水": 0}
    for pillar in pillars:
        eb = pillar.get("earth_branch", {})
        hidden = eb.get("hidden_stems", [])
        for h in hidden:
            element = h.get("element", "")
            if element in hidden_elements:
                hidden_elements[element] += 1

    element_counts = chart.get("five_elements_count", {}) or {}
    prompt = f"""你是一名精通子平八字命理的分析助手。

你的任务不是重新排盘，而是在已有的四柱与五行统计结果基础上，给出更符合命理直觉的五行能量强弱修正。
请尽量使用提供的数据结构（四柱干支、藏干、五行统计），不要引入其他命理体系或额外概念。

【命盘基础信息】
日主: {day_master_name}（{day_master_element}，{day_master.get('yinyang', '')}）

【四柱八字与藏干】
{chr(10).join(pillar_info)}

【五行数量统计（天干+地支+藏干）】
木: {element_counts.get('木', 0)}个, 火: {element_counts.get('火', 0)}个, 土: {element_counts.get('土', 0)}个, 金: {element_counts.get('金', 0)}个, 水: {element_counts.get('水', 0)}个

【藏干五行统计（辅助参考）】
木: {hidden_elements['木']}个, 火: {hidden_elements['火']}个, 土: {hidden_elements['土']}个, 金: {hidden_elements['金']}个, 水: {hidden_elements['水']}个

【分析原则】
1. 不否定统计中已出现的五行，不引入全新五行。
2. 修正体现“数量 ≠ 实际能量”，以小幅微调为主，避免极端变化。
3. 结合日主、月令、五行生克、藏干权重与整体平衡性，给出合理强弱判断。
4. 不需要判断季节强弱、是否成格、命局状态等额外结论。

【输出要求】
请严格按照以下 JSON 格式输出（不要添加任何其他内容）:
```json
{{
  "elements": {{
    "木": {{ "score": 分数, "description": "简短描述" }},
    "火": {{ "score": 分数, "description": "简短描述" }},
    "土": {{ "score": 分数, "description": "简短描述" }},
    "金": {{ "score": 分数, "description": "简短描述" }},
    "水": {{ "score": 分数, "description": "简短描述" }}
  }},
  "overall": "五行总势：整体能量格局与平衡特点（约40-80字，允许使用 Markdown 的 **加粗** 或 *强调* 标记）",
  "temperament": "性情底色：性格气质与倾向（约30-60字，可使用 Markdown 的 **加粗** 或 *强调* 标记）",
  "health": "身心气机：健康与调养建议（约40-80字，可使用 Markdown 的 **加粗** 或 *强调* 标记）"
}}
```

说明：
- 分数范围 0-100，反映该五行在命局中的相对能量强度
- 每个五行的描述要简洁有力(2到3句，每句4到6个字，总共15字以内，不要生成句号，每句短语用中文逗号"，"隔开)，体现五行特点
- overall/temperament/health 都需输出
  - overall: 语气客观，用五行理论分析，不要刻意混入十神概念
  - temperament: 回答简短，分析精辟，不要模板化，不要刻意混入十神概念
  - health: 用五行和中医理论分析，避免医疗结论，偏向调养建议
"""

    return prompt


def build_energy_analysis_schema() -> Dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "elements": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "木": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "score": {"type": "integer", "minimum": 0, "maximum": 100},
                            "description": {"type": "string"},
                        },
                        "required": ["score", "description"],
                    },
                    "火": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "score": {"type": "integer", "minimum": 0, "maximum": 100},
                            "description": {"type": "string"},
                        },
                        "required": ["score", "description"],
                    },
                    "土": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "score": {"type": "integer", "minimum": 0, "maximum": 100},
                            "description": {"type": "string"},
                        },
                        "required": ["score", "description"],
                    },
                    "金": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "score": {"type": "integer", "minimum": 0, "maximum": 100},
                            "description": {"type": "string"},
                        },
                        "required": ["score", "description"],
                    },
                    "水": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "score": {"type": "integer", "minimum": 0, "maximum": 100},
                            "description": {"type": "string"},
                        },
                        "required": ["score", "description"],
                    },
                },
                "required": ["木", "火", "土", "金", "水"],
            },
            "overall": {"type": "string"},
            "temperament": {"type": "string"},
            "health": {"type": "string"},
        },
        "required": ["elements", "overall", "temperament", "health"],
    }
