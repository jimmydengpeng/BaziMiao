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

    prompt = f"""你是一位专业的八字命理师，请分析以下命局的五行能量分布。

【命主信息】
日主: {day_master_name}（{day_master_element}，{day_master.get('yinyang', '')}）

【四柱八字】
{chr(10).join(pillar_info)}

【藏干五行统计】
木: {hidden_elements['木']}个, 火: {hidden_elements['火']}个, 土: {hidden_elements['土']}个, 金: {hidden_elements['金']}个, 水: {hidden_elements['水']}个

【分析要求】
1. 综合考虑天干、地支、本气、余气、中气，分析日主的强弱
2. 评估每个五行的能量强度（0-100分），考虑：
   - 直接出现的数量
   - 月令的影响力
   - 五行之间的生克关系
   - 合冲刑穿等作用关系
3. 为每个五行给出能量分数和简短描述（10字以内）

【输出格式】
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
  "summary": "整体命局五行特点的简要总结（20字以内）"
}}
```

注意：
- 分数范围 0-100，反映该五行在命局中的能量强度
- 描述要简洁有力，体现五行特点
- 分析要客观中肯，符合命理学的传统理论
"""

    return prompt
