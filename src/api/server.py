from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from datetime import datetime
from typing import Any, Dict, Iterator, List, Optional, Union

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse

from src.api.schemas import ChartRequest, ChatRequest, ReportRequest, PillarSearchRequest, GeneralChatRequest, FeedbackRequest, EnergyAnalysisRequest
import logging

# 配置日志
feedback_logger = logging.getLogger("feedback")
feedback_logger.setLevel(logging.INFO)
from src.engine.bazi_engine import BaziPaipanEngine
from src.knowledge.base import retrieve_knowledge
from src.llm import LLMError, chat, stream_chat_with_reasoning
from src.models.chart import Chart
from src.api.energy_prompt import build_energy_analysis_schema
from src.prompt.report_prompt import build_report_prompt
from src.rules.analysis import evaluate_chart

app = FastAPI(title="神机喵算 / BaziMiao API", version="0.1.0")
engine = BaziPaipanEngine()


def _env_flag(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "y", "on"}


def _resolve_llm_provider(requested: Optional[str] = None) -> str:
    provider = (requested or "").strip()
    if provider in {"local", "openai"}:
        return provider
    if provider == "deepseek":
        return "openai"
    if provider == "dashscope":
        return "openai"
    fallback = os.getenv("LLM_PROVIDER", "local").strip() or "local"
    if fallback in {"deepseek", "dashscope"}:
        return "openai"
    return fallback if fallback in {"local", "openai"} else "local"


def _resolve_enable_thinking(provider: str, requested: Optional[bool] = None) -> bool:
    if provider == "local":
        return True
    if requested is not None:
        return bool(requested)
    return _env_flag(
        "OPENAI_COMPAT_ENABLE_THINKING",
        _env_flag("DASHSCOPE_ENABLE_THINKING", _env_flag("DEEPSEEK_ENABLE_THINKING", True)),
    )


def _resolve_llm_model(feature: str, provider: str) -> Optional[str]:
    env_key = f"LLM_MODEL_{feature.upper()}"
    env_value = (os.getenv(env_key) or "").strip()
    if env_value:
        return env_value
    if feature == "energy" and provider == "openai":
        return "qwen-plus-2025-12-01"
    return None


def _resolve_llm_temperature(feature: str) -> Optional[float]:
    env_key = f"LLM_MODEL_{feature.upper()}_TEMPERATURE"
    env_value = (os.getenv(env_key) or "").strip()
    if not env_value:
        return None
    try:
        return float(env_value)
    except ValueError:
        return None


def _resolve_llm_timeout(feature: str) -> Optional[float]:
    env_key = f"LLM_MODEL_{feature.upper()}_TIMEOUT"
    env_value = (os.getenv(env_key) or "").strip()
    if not env_value:
        return None
    try:
        return float(env_value)
    except ValueError:
        return None


def _build_solar_datetime(payload: Union[ChartRequest, ReportRequest]) -> datetime:
    if payload.calendar == "lunar":
        return engine.lunar_to_solar(
            year=payload.year,
            month=payload.month,
            day=payload.day,
            is_leap_month=payload.is_leap_month,
            hour=payload.hour,
            minute=payload.minute,
        )
    return datetime(payload.year, payload.month, payload.day, payload.hour, payload.minute)


def _normalize_name(name: Optional[str]) -> Optional[str]:
    if not name:
        return None
    trimmed = name.strip()
    return trimmed if trimmed else None


@app.post("/api/bazi/chart")
def generate_chart(payload: ChartRequest):
    solar_datetime = _build_solar_datetime(payload)
    chart = engine.calculate_chart(
        name=_normalize_name(payload.name),
        gender=payload.gender,
        solar_datetime=solar_datetime,
        tz_offset_hours=payload.tz_offset_hours,
        longitude=payload.longitude,
        latitude=payload.latitude,
        birth_place=payload.birth_place,
    )
    return {"chart": chart.model_dump()}


@app.post("/api/bazi/report")
def generate_report(payload: ReportRequest):
    chart, analysis, knowledge, prompt = _prepare_report_context(payload)
    messages = _build_llm_messages(prompt)

    try:
        provider = _resolve_llm_provider()
        model = _resolve_llm_model("report", provider)
        temperature = _resolve_llm_temperature("report")
        timeout = _resolve_llm_timeout("report")
        raw_text = chat(
            messages,
            provider=provider,
            model=model,
            temperature=temperature,
            enable_thinking=_resolve_enable_thinking(provider),
            timeout=timeout,
        )
    except LLMError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    report = _normalize_llm_report(raw_text, prompt)
    return {
        "chart": chart.model_dump(),
        "analysis": analysis.model_dump(),
        "knowledge": [k.model_dump() for k in knowledge],
        "prompt": prompt,
        "report": report,
    }


@app.post("/api/bazi/report/stream")
def generate_report_stream(payload: ReportRequest):
    chart, analysis, knowledge, prompt = _prepare_report_context(payload)
    messages = _build_llm_messages(prompt)
    provider = _resolve_llm_provider()
    enable_thinking = _resolve_enable_thinking(provider)
    model = _resolve_llm_model("report", provider)
    temperature = _resolve_llm_temperature("report")
    timeout = _resolve_llm_timeout("report")

    def _event_stream() -> Iterator[str]:
        meta = {
            "type": "meta",
            "chart": chart.model_dump(mode="json"),
            "analysis": analysis.model_dump(mode="json"),
            "knowledge": [k.model_dump() for k in knowledge],
            "prompt": prompt,
        }
        yield json.dumps(meta, ensure_ascii=False) + "\n"

        chunks: List[str] = []
        thinking_chunks: List[str] = []
        try:
            for chunk in stream_chat_with_reasoning(
                messages,
                provider=provider,
                model=model,
                temperature=temperature,
                enable_thinking=enable_thinking,
                timeout=timeout,
            ):
                if chunk.reasoning:
                    thinking_chunks.append(chunk.reasoning)
                    yield json.dumps(
                        {"type": "thinking", "text": chunk.reasoning}, ensure_ascii=False
                    ) + "\n"
                if chunk.content:
                    chunks.append(chunk.content)
                    yield json.dumps({"type": "delta", "text": chunk.content}, ensure_ascii=False) + "\n"
        except LLMError as exc:
            yield json.dumps({"type": "error", "message": str(exc)}, ensure_ascii=False) + "\n"
            return

        report_text = "".join(chunks).strip()
        report = _normalize_llm_report(report_text, prompt)
        done = {
            "type": "done",
            "report": report,
            "analysis": analysis.model_dump(mode="json"),
            "thinking": "".join(thinking_chunks).strip(),
        }
        yield json.dumps(done, ensure_ascii=False) + "\n"

    return StreamingResponse(_event_stream(), media_type="application/x-ndjson")


@app.post("/api/bazi/chat")
def chat_with_chart(payload: ChatRequest):
    prompt = _build_chat_prompt(payload)
    try:
        provider = _resolve_llm_provider()
        model = _resolve_llm_model("chat", provider)
        temperature = _resolve_llm_temperature("chat")
        timeout = _resolve_llm_timeout("chat")
        raw_text = chat(
            _build_llm_messages(prompt),
            provider=provider,
            model=model,
            temperature=temperature,
            enable_thinking=_resolve_enable_thinking(provider),
            timeout=timeout,
        )
    except LLMError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    reply = _normalize_llm_report(raw_text, prompt)
    return {"reply": reply, "prompt": prompt}


@app.post("/api/bazi/chat/stream")
def chat_with_chart_stream(payload: ChatRequest):
    prompt = _build_chat_prompt(payload)
    messages = _build_llm_messages(prompt)
    provider = _resolve_llm_provider()
    enable_thinking = _resolve_enable_thinking(provider)
    model = _resolve_llm_model("chat", provider)
    temperature = _resolve_llm_temperature("chat")
    timeout = _resolve_llm_timeout("chat")

    def _event_stream() -> Iterator[str]:
        chunks: List[str] = []
        thinking_chunks: List[str] = []
        try:
            for chunk in stream_chat_with_reasoning(
                messages,
                provider=provider,
                model=model,
                temperature=temperature,
                enable_thinking=enable_thinking,
                timeout=timeout,
            ):
                if chunk.reasoning:
                    thinking_chunks.append(chunk.reasoning)
                    yield json.dumps(
                        {"type": "thinking", "text": chunk.reasoning}, ensure_ascii=False
                    ) + "\n"
                if chunk.content:
                    chunks.append(chunk.content)
                    yield json.dumps({"type": "delta", "text": chunk.content}, ensure_ascii=False) + "\n"
        except LLMError as exc:
            yield json.dumps({"type": "error", "message": str(exc)}, ensure_ascii=False) + "\n"
            return

        reply_text = "".join(chunks).strip()
        if not reply_text:
            reply_text = "已收到。"
        yield json.dumps(
            {"type": "done", "reply": reply_text, "thinking": "".join(thinking_chunks).strip()},
            ensure_ascii=False,
        ) + "\n"

    return StreamingResponse(_event_stream(), media_type="application/x-ndjson")


@app.post("/api/bazi/general-chat/stream")
def general_chat_stream(payload: GeneralChatRequest):
    """通用聊天接口（无需命盘），用于喵大师等场景"""
    default_system = (
        "你是神机喵算的AI助手「喵大师」，精通中国传统八字命理学。"
        "你的回答应该：1）专业且易懂，用现代语言解释传统命理概念；"
        "2）客观中肯，不夸大也不贬低；3）注重实用建议和启发思考；"
        "4）保持友好、耐心的对话风格。"
    )
    system_prompt = payload.system_prompt or default_system
    provider = _resolve_llm_provider(payload.llm_provider)
    enable_thinking = _resolve_enable_thinking(provider, payload.deep_think)
    model = _resolve_llm_model("chat", provider)
    temperature = _resolve_llm_temperature("chat")
    timeout = _resolve_llm_timeout("chat")

    # 可选：命主上下文（前端只传姓名 + 出生日期文本，后端用提示词方式注入，避免改动更大结构）
    if payload.subject_enabled and payload.subject_name:
        birth = payload.subject_birth or ""
        system_prompt += (
            "\n\n【当前对话命主信息】\n"
            f"- 姓名：{payload.subject_name}\n"
            f"- 出生：{birth}\n"
            "当用户的问题与命理分析相关时，请结合以上命主信息进行推演；"
            "当问题与命理无关时，正常回答即可。"
        )

    # 构建对话消息
    messages = [{"role": "system", "content": system_prompt}]
    for turn in payload.history:
        messages.append({"role": turn.role, "content": turn.content})

    def _event_stream() -> Iterator[str]:
        chunks: List[str] = []
        thinking_chunks: List[str] = []
        try:
            for chunk in stream_chat_with_reasoning(
                messages,
                provider=provider,
                model=model,
                temperature=temperature,
                enable_thinking=enable_thinking,
                timeout=timeout,
            ):
                if chunk.reasoning:
                    thinking_chunks.append(chunk.reasoning)
                    yield json.dumps(
                        {"type": "thinking", "text": chunk.reasoning}, ensure_ascii=False
                    ) + "\n"
                if chunk.content:
                    chunks.append(chunk.content)
                    yield json.dumps({"type": "delta", "text": chunk.content}, ensure_ascii=False) + "\n"
        except LLMError as exc:
            yield json.dumps({"type": "error", "message": str(exc)}, ensure_ascii=False) + "\n"
            return

        reply_text = "".join(chunks).strip()
        if not reply_text:
            reply_text = "我明白了，请问还有什么想了解的吗？"
        yield json.dumps(
            {"type": "done", "reply": reply_text, "thinking": "".join(thinking_chunks).strip()},
            ensure_ascii=False,
        ) + "\n"

    return StreamingResponse(_event_stream(), media_type="application/x-ndjson")


@app.get("/api/ollama/test")
def test_ollama(prompt: str = "ping", model: Optional[str] = None, base_url: Optional[str] = None):
    ollama_base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    ollama_model = model or os.getenv("OLLAMA_MODEL", "deepseek-r1:8b")
    payload = {"model": ollama_model, "prompt": prompt, "stream": False}
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        f"{ollama_base_url}/api/generate",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

    try:
        with opener.open(request, timeout=15) as response:
            raw = response.read().decode("utf-8").strip()
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore").strip()
        detail = body or f"HTTP {exc.code} {exc.reason}"
        raise HTTPException(status_code=502, detail=f"Ollama 测试失败: {detail}") from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise HTTPException(status_code=502, detail=f"Ollama 测试失败: {exc}") from exc

    try:
        parsed = json.loads(raw) if raw else {}
    except json.JSONDecodeError:
        parsed = {"raw": raw}
    return {"ok": True, "base_url": ollama_base_url, "model": ollama_model, "result": parsed}


@app.post("/api/bazi/find-dates-by-pillars")
def find_dates_by_pillars(payload: PillarSearchRequest):
    """
    根据四柱八字查找对应的日期范围
    """
    try:
        matched_dates = engine.find_dates_by_pillars(
            year_pillar=payload.year_pillar,
            month_pillar=payload.month_pillar,
            day_pillar=payload.day_pillar,
            hour_pillar=payload.hour_pillar,
            start_year=payload.start_year,
            end_year=payload.end_year,
        )
        return {
            "matched_dates": matched_dates,
            "total_count": len(matched_dates),
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"查找失败: {exc}") from exc


@app.post("/api/bazi/feedback")
def submit_feedback(payload: FeedbackRequest):
    """
    接收用户对 AI 回复的反馈（点赞/点踩）
    MVP 阶段：记录到日志，后续可扩展到数据库
    """
    feedback_logger.info(
        f"Feedback received - session: {payload.session_id}, "
        f"message: {payload.message_id}, feedback: {payload.feedback}"
    )
    return {"ok": True, "message": "反馈已记录"}


@app.post("/api/bazi/energy-analysis")
def analyze_energy(payload: EnergyAnalysisRequest):
    """
    五行能量智能分析接口
    基于四柱八字和藏干信息，让 AI 智能分析命局中五行的强弱
    """
    from src.api.energy_prompt import build_energy_analysis_prompt

    try:
        chart_data = payload.chart
        prompt_text = build_energy_analysis_prompt(chart_data)

        provider = _resolve_llm_provider()
        model = _resolve_llm_model("energy", provider)
        temperature = _resolve_llm_temperature("energy")
        timeout = _resolve_llm_timeout("energy")
        response_format = {
            "type": "json_schema",
            "json_schema": {
                "name": "energy_analysis",
                "schema": build_energy_analysis_schema(),
                "strict": True,
            },
        }
        # 不启用思考模式，快速返回结果
        system_message = (
            "你是一位专业的八字命理师，"
            "请严格按要求的 JSON 格式输出分析结果。"
        )
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt_text},
        ]

        raw_text = chat(
            messages,
            provider=provider,
            model=model,
            temperature=temperature,
            enable_thinking=False,
            response_format=response_format,
            timeout=timeout,
        )
        result = _extract_json(raw_text)

        if not result or "elements" not in result:
            # 解析失败，返回错误信息
            raise HTTPException(status_code=502, detail="AI 返回格式解析失败")

        return result
    except LLMError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"分析失败: {exc}") from exc


def _prepare_report_context(payload: ReportRequest):
    if payload.chart:
        try:
            chart = Chart.model_validate(payload.chart)
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"命盘数据无效: {exc}") from exc
    else:
        if payload.year is None or payload.month is None or payload.day is None or not payload.gender:
            raise HTTPException(status_code=400, detail="缺少排盘所需的日期或性别信息")
        try:
            solar_datetime = _build_solar_datetime(payload)
            chart = engine.calculate_chart(
                name=_normalize_name(payload.name),
                gender=payload.gender,
                solar_datetime=solar_datetime,
                tz_offset_hours=payload.tz_offset_hours,
                longitude=payload.longitude,
                latitude=payload.latitude,
                birth_place=payload.birth_place,
            )
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"排盘失败: {exc}") from exc

    analysis = evaluate_chart(chart)
    knowledge = retrieve_knowledge(
        pattern_tags=analysis.pattern_tags, yi_yong_shen=analysis.yi_yong_shen, focus=payload.focus
    )
    prompt = build_report_prompt(chart, analysis, knowledge, payload.focus)
    return chart, analysis, knowledge, prompt


def _build_chat_prompt(payload: ChatRequest) -> Dict[str, Any]:
    return {
        "system": (
            "你在持续解读同一命盘，请保持前后一致。禁止新增格局或修改四柱。"
            "回答需要引用已给出的 chart/analysis 事实。"
            "请直接输出自然语言答复，不需要固定结构。"
        ),
        "user": {
            "chart": payload.chart,
            "analysis": payload.analysis,
            "history": [turn.model_dump() for turn in payload.history],
            "focus": payload.focus,
        },
    }


def _build_llm_messages(prompt: Dict[str, Any]) -> List[Dict[str, str]]:
    system = prompt.get("system", "")
    user = prompt.get("user", {})
    user_text = json.dumps(user, ensure_ascii=False, indent=2)
    return [{"role": "system", "content": system}, {"role": "user", "content": user_text}]


def _extract_json(text: str) -> Optional[Dict[str, Any]]:
    if not text:
        return None
    cleaned = text.strip()
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", cleaned, re.S)
    candidate = fenced.group(1) if fenced else None

    if not candidate:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1 and end > start:
            candidate = cleaned[start : end + 1]

    if not candidate:
        return None

    try:
        data = json.loads(candidate)
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def _normalize_llm_report(text: str, prompt: Dict[str, Any]) -> Dict[str, Any]:
    data = _extract_json(text)
    if isinstance(data, dict) and data.get("sections"):
        if not data.get("overall_tone"):
            data["overall_tone"] = "温和中肯"
        data.setdefault("raw_prompt", prompt)
        return data

    fallback_text = text.strip() if text else "模型未返回有效内容。"
    return {
        "overall_tone": "温和中肯",
        "sections": [{"title": "生成结果", "content": fallback_text}],
        "raw_prompt": prompt,
    }
