"""大运智能解析 Prompt 构建模块"""
from typing import Any, Dict, List, Optional


def _gender_label(gender: str) -> str:
    if gender == "male":
        return "男"
    if gender == "female":
        return "女"
    return "其他"


def _format_pillar(name: str, pillar: Dict[str, Any]) -> str:
    hs = pillar.get("heaven_stem", {}) or {}
    eb = pillar.get("earth_branch", {}) or {}
    hs_name = hs.get("name", "")
    hs_element = hs.get("element", "")
    hs_ten_god = hs.get("ten_god", "")
    eb_name = eb.get("name", "")
    eb_element = eb.get("element", "")
    return (
        f"{name}柱: {hs_name}{eb_name}，天干{hs_name}({hs_element},{hs_ten_god})，"
        f"地支{eb_name}({eb_element})"
    )


def _estimate_start_age(birth_year: Optional[int], destiny_year: Optional[int]) -> Optional[int]:
    if birth_year is None or destiny_year is None:
        return None
    return destiny_year - birth_year + 1


def _format_relation_list(relations: List[Dict[str, Any]]) -> str:
    if not relations:
        return "无明显刑冲合会克害破关系"
    lines = []
    for rel in relations:
        description = rel.get("description") or ""
        rel_type = rel.get("type") or ""
        if description:
            lines.append(f"- {description}（{rel_type}）")
    return "\n".join(lines) if lines else "无明显刑冲合会克害破关系"


def build_destiny_analysis_prompt(
    chart: Dict[str, Any],
    destiny_pillar: Dict[str, Any],
    relations: List[Dict[str, Any]],
) -> str:
    """构建大运智能解析 Prompt"""
    birth_year = None
    solar_datetime = chart.get("solar_datetime")
    if isinstance(solar_datetime, str) and len(solar_datetime) >= 4:
        try:
            birth_year = int(solar_datetime[:4])
        except ValueError:
            birth_year = None

    destiny_year = destiny_pillar.get("year")
    if not isinstance(destiny_year, int):
        destiny_year = None

    start_age = _estimate_start_age(birth_year, destiny_year)
    age_range = f"{start_age}~{start_age + 9}岁" if start_age is not None else "未知"

    pillars = [
        _format_pillar("年", chart.get("year_pillar", {})),
        _format_pillar("月", chart.get("month_pillar", {})),
        _format_pillar("日", chart.get("day_pillar", {})),
        _format_pillar("时", chart.get("hour_pillar", {})),
    ]

    destiny_hs = (destiny_pillar.get("heaven_stem") or {}).get("name", "")
    destiny_eb = (destiny_pillar.get("earth_branch") or {}).get("name", "")
    destiny_tg = (destiny_pillar.get("heaven_stem") or {}).get("ten_god", "")

    day_master = chart.get("day_master", {}) or {}
    day_master_text = (
        f"{day_master.get('name', '')}"
        f"（{day_master.get('yinyang', '')}{day_master.get('element', '')}）"
    )

    prompt = f"""你是一名精通子平八字命理的分析助手。

你的任务是基于提供的命盘与当前大运信息，给出简洁、克制、不夸张的大运运势分析。
请只使用提供的信息进行推断，不要引入新的四柱/大运/流年，不要编造关系。

【命盘基础信息】
性别: {_gender_label(chart.get("gender", ""))}
日主: {day_master_text}

【四柱八字】
{chr(10).join(pillars)}

【当前大运】
起运年份: {destiny_year or "未知"}
年龄范围: {age_range}
大运干支: {destiny_hs}{destiny_eb}
大运天干十神: {destiny_tg or "未知"}

【大运与本命干支关系（仅供引用）】
{_format_relation_list(relations)}

【关系知识速记】
- 合化/六合/三合/三会：表示聚合、协同或资源聚合趋势
- 六冲/相冲：表示冲击、变化或波动趋势
- 相刑/自刑/相害：表示压力、摩擦或牵制趋势
- 相克：表示制约或消耗趋势
- 破：表示破坏/破局趋势

【输出要求】
请严格按以下 JSON 格式输出，不要输出其他内容：
```json
{{
  "summary": "大运总势（约60-120字，总体走势 + 财富/健康/感情/事业等方面事项）",
  "tips": "行动建议（约40-80字，务实可行）"
}}
```

说明：
- 只允许引用上文列出的关系，不要编造刑冲合会克害破
- 字数控制简短，避免玄而又玄的措辞
- 允许使用 Markdown 的 **加粗** 或 *强调* 标记，强调关键内容或命主更关心的面向（如财运、姻缘/感情、事业、学业、身体、家庭等）
- 如有强调词，请保持克制，避免过度渲染
"""

    return prompt


def build_destiny_analysis_batch_prompt(
    chart: Dict[str, Any],
    destiny_items: List[Dict[str, Any]],
) -> str:
    """构建多条大运智能解析 Prompt"""
    birth_year = None
    solar_datetime = chart.get("solar_datetime")
    if isinstance(solar_datetime, str) and len(solar_datetime) >= 4:
        try:
            birth_year = int(solar_datetime[:4])
        except ValueError:
            birth_year = None

    pillars = [
        _format_pillar("年", chart.get("year_pillar", {})),
        _format_pillar("月", chart.get("month_pillar", {})),
        _format_pillar("日", chart.get("day_pillar", {})),
        _format_pillar("时", chart.get("hour_pillar", {})),
    ]

    day_master = chart.get("day_master", {}) or {}
    day_master_text = (
        f"{day_master.get('name', '')}"
        f"（{day_master.get('yinyang', '')}{day_master.get('element', '')}）"
    )

    items_text = []
    for item in destiny_items:
        destiny_pillar = item.get("destiny_pillar", {}) or {}
        relations = item.get("relations", []) or []
        destiny_year = destiny_pillar.get("year")
        destiny_year_val = destiny_year if isinstance(destiny_year, int) else None
        start_age = _estimate_start_age(birth_year, destiny_year_val)
        age_range = f"{start_age}~{start_age + 9}岁" if start_age is not None else "未知"
        destiny_hs = (destiny_pillar.get("heaven_stem") or {}).get("name", "")
        destiny_eb = (destiny_pillar.get("earth_branch") or {}).get("name", "")
        destiny_tg = (destiny_pillar.get("heaven_stem") or {}).get("ten_god", "")

        items_text.append(
            "\n".join([
                f"【大运 {destiny_year_val or '未知'}】",
                f"起运年份: {destiny_year_val or '未知'}",
                f"年龄范围: {age_range}",
                f"大运干支: {destiny_hs}{destiny_eb}",
                f"大运天干十神: {destiny_tg or '未知'}",
                "大运与本命干支关系（仅供引用）:",
                _format_relation_list(relations),
            ])
        )

    prompt = f"""你是一名精通子平八字命理的分析助手。

你的任务是基于提供的命盘与多条大运信息，给出简洁、克制、不夸张的大运运势分析。
请只使用提供的信息进行推断，不要引入新的四柱/大运/流年，不要编造关系。

【命盘基础信息】
性别: {_gender_label(chart.get("gender", ""))}
日主: {day_master_text}

【四柱八字】
{chr(10).join(pillars)}

{chr(10).join(items_text)}

【关系知识速记】
- 合化/六合/三合/三会：表示聚合、协同或资源聚合趋势
- 六冲/相冲：表示冲击、变化或波动趋势
- 相刑/自刑/相害：表示压力、摩擦或牵制趋势
- 相克：表示制约或消耗趋势
- 破：表示破坏/破局趋势

【输出要求】
请严格按以下 JSON 格式输出，不要输出其他内容：
```json
{{
  "items": [
    {{
      "year": 2024,
      "summary": "大运总势（约60-120字，总体走势 + 财富/健康/感情/事业等方面事项）",
      "tips": "行动建议（约40-80字，务实可行）"
    }}
  ]
}}
```

说明：
- items 内需覆盖上面列出的每一条大运（year 对应起运年份）
- 只允许引用上文列出的关系，不要编造刑冲合会克害破
- 字数控制简短，避免玄而又玄的措辞
- 允许使用 Markdown 的 **加粗** 或 *强调* 标记，强调关键内容或命主更关心的面向（如财运、姻缘/感情、事业、学业、身体、家庭等）
- 如有强调词，请保持克制，避免过度渲染
"""

    return prompt


def build_destiny_analysis_schema() -> Dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "summary": {"type": "string"},
            "tips": {"type": "string"},
        },
        "required": ["summary", "tips"],
    }


def build_destiny_analysis_batch_schema() -> Dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "year": {"type": "integer"},
                        "summary": {"type": "string"},
                        "tips": {"type": "string"},
                    },
                    "required": ["year", "summary", "tips"],
                },
            },
        },
        "required": ["items"],
    }
