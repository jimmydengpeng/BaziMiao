from __future__ import annotations

from typing import Dict, List

from fastapi import FastAPI, HTTPException

from src.api.schemas import ChatRequest, ReportRequest
from src.engine.bazi_engine import BaziPaipanEngine
from src.knowledge.base import retrieve_knowledge
from src.prompt.report_prompt import build_report_prompt
from src.rules.analysis import evaluate_chart

app = FastAPI(title="神机喵算 / BaziMiao API", version="0.1.0")
engine = BaziPaipanEngine()


@app.post("/api/bazi/report")
def generate_report(payload: ReportRequest):
    try:
        chart = engine.calculate_chart(
            name=payload.name or "匿名",
            gender=payload.gender,
            solar_datetime=payload.birth,
            tz_offset_hours=payload.tz_offset_hours,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"排盘失败: {exc}") from exc

    analysis = evaluate_chart(chart)
    knowledge = retrieve_knowledge(
        pattern_tags=analysis.pattern_tags, yi_yong_shen=analysis.yi_yong_shen, focus=payload.focus
    )
    prompt = build_report_prompt(chart, analysis, knowledge, payload.focus)
    report = _fake_llm_generate(prompt, payload.focus)

    return {
        "chart": chart.model_dump(),
        "analysis": analysis.model_dump(),
        "knowledge": [k.model_dump() for k in knowledge],
        "prompt": prompt,
        "report": report,
    }


@app.post("/api/bazi/chat")
def chat_with_chart(payload: ChatRequest):
    prompt = {
        "system": (
            "你在持续解读同一命盘，请保持前后一致。禁止新增格局或修改四柱。"
            "回答需要引用已给出的 chart/analysis 事实。"
        ),
        "user": {
            "chart": payload.chart,
            "analysis": payload.analysis,
            "history": [turn.model_dump() for turn in payload.history],
            "focus": payload.focus,
        },
    }
    reply = _fake_llm_generate(prompt, payload.focus)
    return {"reply": reply, "prompt": prompt}


def _fake_llm_generate(prompt: Dict, focus: List[str]) -> Dict:
    """
    本地占位，方便在未接入真实 LLM 时自测接口。
    返回结构遵循报告格式，真实环境应替换为 LLM API 调用。
    """
    focus_text = "、".join(focus) if focus else "事业/财富/情感/健康"
    sections = [
        {"title": "一、命局总体气质", "content": "根据提供的 pattern_tags 给出整体气质解读。"},
        {"title": "二、事业发展趋势", "content": f"结合用神与大运，围绕 {focus_text} 给出现实建议。"},
        {"title": "三、财富机会与风险", "content": "提示忌神岁运的风险，并给出稳健建议。"},
        {"title": "四、性格与人际特点", "content": "以日主五行与十神倾向描述性格与人际模式。"},
        {"title": "五、小结与建议", "content": "列出3-5条可执行的生活/决策建议。"},
    ]
    return {"overall_tone": "温和中肯", "sections": sections, "raw_prompt": prompt}
