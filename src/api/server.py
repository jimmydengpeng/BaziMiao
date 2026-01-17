from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.request
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Callable, Dict, Iterator, List, Optional, Union
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse

import logging

from src.api.schemas import (
    ChartRequest,
    ChatRequest,
    ReportRequest,
    PillarSearchRequest,
    GeneralChatRequest,
    FeedbackRequest,
    EnergyAnalysisRequest,
    DestinyAnalysisRequest,
    DestinyAnalysisBatchRequest,
    DestinyRelationsRequest,
)
from src.engine.bazi_engine import BaziPaipanEngine
from src.knowledge.base import retrieve_knowledge
from src.llm import LLMError, chat, chat_with_usage, stream_chat_with_reasoning
from src.models.chart import Chart, GanZhiRelations, PillarInfo
from src.api.energy_prompt import build_energy_analysis_schema
from src.api.destiny_prompt import build_destiny_analysis_schema, build_destiny_analysis_batch_schema
from src.prompt.report_prompt import (
    REPORT_SCHEMA_VERSION,
    REPORT_SECTIONS_PLAN,
    build_report_prompt,
    build_report_stream_prompt,
)
from src.rules.analysis import evaluate_chart

root_logger = logging.getLogger()
if not root_logger.handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

# 配置日志
feedback_logger = logging.getLogger("feedback")
feedback_logger.setLevel(logging.INFO)
energy_logger = logging.getLogger("energy_analysis")
energy_logger.setLevel(logging.INFO)
energy_logger.propagate = True
destiny_logger = logging.getLogger("destiny_analysis")
destiny_logger.setLevel(logging.INFO)
destiny_logger.propagate = True

app = FastAPI(title="神机喵算 / BaziMiao API", version="0.1.0")
engine = BaziPaipanEngine()


def _env_flag(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "y", "on"}


AI_LOG_DIR = os.getenv("AI_LOG_DIR", "logs").strip() or "logs"
AI_LOG_CONTENT = _env_flag("AI_LOG_CONTENT", True)
AI_LOG_MAX_CHARS = int(os.getenv("AI_LOG_MAX_CHARS", "20000") or "20000")


def _ensure_ai_loggers() -> tuple[logging.Logger, logging.Logger]:
    log_dir = Path(AI_LOG_DIR)
    log_dir.mkdir(parents=True, exist_ok=True)

    def _make_logger(name: str, filename: str) -> logging.Logger:
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        logger.propagate = False
        if logger.handlers:
            return logger
        handler = RotatingFileHandler(
            log_dir / filename,
            maxBytes=5 * 1024 * 1024,
            backupCount=3,
            encoding="utf-8",
        )
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)
        return logger

    metrics_logger = _make_logger("ai_metrics", "ai-metrics.log")
    content_logger = _make_logger("ai_content", "ai-content.log")
    return metrics_logger, content_logger


AI_METRICS_LOGGER, AI_CONTENT_LOGGER = _ensure_ai_loggers()


def _now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _estimate_tokens(text: str) -> int:
    # 没有 tiktoken 时的简易估算：英文约 4 chars/token，中文偏少但先给“量级”参考
    cleaned = text or ""
    return max(1, (len(cleaned) + 3) // 4)


def _build_dev_info(
    usage: Any,
    elapsed_ms: Optional[int],
    messages: List[Dict[str, Any]],
    raw_text: Optional[str],
) -> Dict[str, Any]:
    prompt_tokens = usage.get("prompt_tokens") if isinstance(usage, dict) else None
    completion_tokens = usage.get("completion_tokens") if isinstance(usage, dict) else None
    total_tokens = usage.get("total_tokens") if isinstance(usage, dict) else None

    prompt_est = _estimate_tokens(json.dumps(messages, ensure_ascii=False))
    completion_est = _estimate_tokens(raw_text or "")

    if prompt_tokens is None:
        prompt_tokens = prompt_est
    if completion_tokens is None:
        completion_tokens = completion_est
    if total_tokens is None:
        total_tokens = (prompt_tokens or 0) + (completion_tokens or 0)

    return {
        "elapsed_ms": elapsed_ms or 0,
        "prompt_tokens": int(prompt_tokens),
        "completion_tokens": int(completion_tokens),
        "total_tokens": int(total_tokens),
    }


def _truncate_text(text: str, max_chars: int = AI_LOG_MAX_CHARS) -> str:
    if not text:
        return ""
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 20] + f"...(truncated,len={len(text)})"


def _log_ai_metrics(event: Dict[str, Any]) -> None:
    try:
        payload = {"ts": _now_iso(), **event}
        AI_METRICS_LOGGER.info(json.dumps(payload, ensure_ascii=False))
    except Exception:
        # 不让日志失败影响主流程
        pass


def _log_ai_content(event: Dict[str, Any]) -> None:
    if not AI_LOG_CONTENT:
        return
    try:
        payload = {"ts": _now_iso(), **event}
        AI_CONTENT_LOGGER.info(json.dumps(payload, ensure_ascii=False))
    except Exception:
        pass


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


def _resolve_feature_enable_thinking(
    feature: str, provider: str, requested: Optional[bool] = None
) -> bool:
    if provider == "local":
        return True
    if requested is not None:
        return bool(requested)
    env_key = f"LLM_MODEL_{feature.upper()}_ENABLE_THINKING"
    env_value = (os.getenv(env_key) or "").strip()
    if env_value:
        return env_value.lower() in {"1", "true", "yes", "y", "on"}
    if feature == "energy":
        return False
    return _resolve_enable_thinking(provider)


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
    destiny_relations_map = _build_destiny_relations_map(chart)
    return {"chart": chart.model_dump(), "destiny_relations_map": destiny_relations_map}


@app.post("/api/bazi/report")
def generate_report(payload: ReportRequest):
    request_id = str(uuid4())
    _log_ai_content(
        {
            "kind": "request",
            "endpoint": "/api/bazi/report",
            "request_id": request_id,
            "payload": payload.model_dump(mode="json"),
        }
    )
    chart, analysis, knowledge, prompt = _prepare_report_context(payload)
    messages = _build_llm_messages(prompt)

    try:
        provider = _resolve_llm_provider()
        model = _resolve_llm_model("report", provider)
        temperature = _resolve_llm_temperature("report")
        timeout = _resolve_llm_timeout("report")
        enable_thinking = _resolve_feature_enable_thinking("report", provider)
        start_time = time.perf_counter()
        raw_text, usage = chat_with_usage(
            messages,
            provider=provider,
            model=model,
            temperature=temperature,
            enable_thinking=enable_thinking,
            timeout=timeout,
        )
        elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    except LLMError as exc:
        _log_ai_metrics(
            {
                "kind": "llm_error",
                "endpoint": "/api/bazi/report",
                "request_id": request_id,
                "provider": provider if "provider" in locals() else None,
                "model": model if "model" in locals() else None,
                "message": str(exc),
            }
        )
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    report = _normalize_llm_report(raw_text, prompt)
    prompt_text = json.dumps(messages, ensure_ascii=False)
    completion_text = raw_text or ""
    prompt_tokens = usage.get("prompt_tokens") if isinstance(usage, dict) else None
    completion_tokens = usage.get("completion_tokens") if isinstance(usage, dict) else None
    total_tokens = usage.get("total_tokens") if isinstance(usage, dict) else None
    _log_ai_metrics(
        {
            "kind": "llm_done",
            "endpoint": "/api/bazi/report",
            "request_id": request_id,
            "provider": provider,
            "model": model or "default",
            "enable_thinking": enable_thinking,
            "temperature": temperature,
            "timeout": timeout,
            "elapsed_ms": elapsed_ms if "elapsed_ms" in locals() else None,
            "usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
                "prompt_tokens_est": _estimate_tokens(prompt_text),
                "completion_tokens_est": _estimate_tokens(completion_text),
                "total_tokens_est": _estimate_tokens(prompt_text) + _estimate_tokens(completion_text),
            },
        }
    )
    _log_ai_content(
        {
            "kind": "response",
            "endpoint": "/api/bazi/report",
            "request_id": request_id,
            "raw_text": _truncate_text(raw_text or ""),
            "report": report,
        }
    )
    return {
        "chart": chart.model_dump(),
        "analysis": analysis.model_dump(),
        "knowledge": [k.model_dump() for k in knowledge],
        "prompt": prompt,
        "report": report,
    }


@app.post("/api/bazi/report/stream")
def generate_report_stream(payload: ReportRequest):
    report_id = str(uuid4())
    request_id = str(uuid4())
    _log_ai_content(
        {
            "kind": "request",
            "endpoint": "/api/bazi/report/stream",
            "request_id": request_id,
            "report_id": report_id,
            "payload": payload.model_dump(mode="json"),
        }
    )
    chart, analysis, knowledge, prompt = _prepare_report_context(
        payload, prompt_builder=lambda c, a, k, f: build_report_stream_prompt(c, a, k, f, report_id)
    )
    messages = _build_llm_messages(prompt)
    provider = _resolve_llm_provider()
    model = _resolve_llm_model("report", provider)
    temperature = _resolve_llm_temperature("report")
    timeout = _resolve_llm_timeout("report")
    enable_thinking = _resolve_feature_enable_thinking("report", provider)

    def _event_stream() -> Iterator[str]:
        stream_start = time.perf_counter()
        prompt_text = json.dumps(messages, ensure_ascii=False)
        stream_stats = {
            "thinking_chars": 0,
            "delta_chars": 0,
            "events_total": 0,
            "sections_done": 0,
            "last_section_id": None,
        }
        headers = {
            "type": "report_start",
            "report_id": report_id,
            "schema_version": REPORT_SCHEMA_VERSION,
            "sections": list(REPORT_SECTIONS_PLAN),
        }
        yield _sse_pack(headers)

        # 给前端的元数据（方便落库 / 二次打开时复用 chart/analysis）
        meta = {
            "type": "meta",
            "report_id": report_id,
            "chart": chart.model_dump(mode="json"),
            "analysis": analysis.model_dump(mode="json"),
            "knowledge": [k.model_dump() for k in knowledge],
            "prompt": prompt,
        }
        yield _sse_pack(meta)

        buffer = ""
        current_section: Optional[str] = None
        expected_section_index = 0
        last_seq: Dict[str, int] = {}
        saw_report_done = False
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
                    stream_stats["thinking_chars"] += len(chunk.reasoning)
                    yield _sse_pack(
                        {"type": "thinking_delta", "report_id": report_id, "text": chunk.reasoning}
                    )
                if chunk.content:
                    buffer += chunk.content

                    while True:
                        newline_index = buffer.find("\n")
                        if newline_index == -1:
                            break
                        line = buffer[:newline_index]
                        buffer = buffer[newline_index + 1 :]

                        trimmed = line.strip()
                        if not trimmed:
                            continue

                        event = _parse_report_event_json_line(trimmed, report_id)
                        if not event.get("ok"):
                            _log_ai_metrics(
                                {
                                    "kind": "stream_error",
                                    "endpoint": "/api/bazi/report/stream",
                                    "request_id": request_id,
                                    "report_id": report_id,
                                    "message": str(
                                        event.get("message") or "模型输出不符合事件协议（非JSON行）"
                                    ),
                                }
                            )
                            yield _sse_pack(
                                {
                                    "type": "error",
                                    "report_id": report_id,
                                    "message": str(event.get("message") or "模型输出不符合事件协议"),
                                    "recoverable": False,
                                }
                            )
                            return

                        data = event["event"]
                        validated = _validate_and_normalize_report_event(
                            data=data,
                            report_id=report_id,
                            sections_plan=REPORT_SECTIONS_PLAN,
                            expected_section_index=expected_section_index,
                            current_section=current_section,
                            last_seq=last_seq,
                        )
                        if not validated.get("ok"):
                            _log_ai_metrics(
                                {
                                    "kind": "stream_error",
                                    "endpoint": "/api/bazi/report/stream",
                                    "request_id": request_id,
                                    "report_id": report_id,
                                    "message": str(
                                        validated.get("message") or "模型输出不符合事件协议（字段校验失败）"
                                    ),
                                }
                            )
                            yield _sse_pack(
                                {
                                    "type": "error",
                                    "report_id": report_id,
                                    "message": str(
                                        validated.get("message") or "模型输出不符合事件协议"
                                    ),
                                    "recoverable": False,
                                }
                            )
                            return

                        extra_events = validated.get("extra_events") or []
                        events_to_emit = [*extra_events, validated["event"]]

                        current_section = validated.get("current_section")
                        expected_section_index = int(validated.get("expected_section_index", 0))

                        for normalized in events_to_emit:
                            stream_stats["events_total"] += 1
                            stream_stats["last_section_id"] = normalized.get("section_id")

                            if normalized.get("type") == "section_delta":
                                delta_text = normalized.get("delta")
                                if isinstance(delta_text, str):
                                    stream_stats["delta_chars"] += len(delta_text)
                            if normalized.get("type") == "section_done":
                                stream_stats["sections_done"] += 1

                            if normalized.get("type") == "report_done":
                                saw_report_done = True
                                normalized.setdefault(
                                    "thinking",
                                    "".join(thinking_chunks).strip() if thinking_chunks else "",
                                )
                                elapsed_ms = int((time.perf_counter() - stream_start) * 1000)
                                prompt_tokens_est = _estimate_tokens(prompt_text)
                                completion_tokens_est = max(
                                    1,
                                    (stream_stats["delta_chars"] + stream_stats["thinking_chars"] + 3) // 4,
                                )
                                normalized.setdefault(
                                    "dev_info",
                                    {
                                        "elapsed_ms": elapsed_ms,
                                        "prompt_tokens": prompt_tokens_est,
                                        "completion_tokens": completion_tokens_est,
                                        "total_tokens": prompt_tokens_est + completion_tokens_est,
                                    },
                                )
                                _log_ai_metrics(
                                    {
                                        "kind": "stream_done",
                                        "endpoint": "/api/bazi/report/stream",
                                        "request_id": request_id,
                                        "report_id": report_id,
                                        "provider": provider,
                                        "model": model or "default",
                                        "enable_thinking": enable_thinking,
                                        "temperature": temperature,
                                        "timeout": timeout,
                                        "elapsed_ms": elapsed_ms,
                                        "usage": {
                                            "prompt_tokens_est": prompt_tokens_est,
                                            "completion_tokens_est": completion_tokens_est,
                                            "total_tokens_est": prompt_tokens_est + completion_tokens_est,
                                        },
                                        "stream": stream_stats,
                                    }
                                )
                                _log_ai_content(
                                    {
                                        "kind": "stream_report_done",
                                        "endpoint": "/api/bazi/report/stream",
                                        "request_id": request_id,
                                        "report_id": report_id,
                                        "report": normalized.get("report"),
                                    }
                                )
                                yield _sse_pack(normalized)
                                return

                            yield _sse_pack(normalized)
        except LLMError as exc:
            _log_ai_metrics(
                {
                    "kind": "llm_error",
                    "endpoint": "/api/bazi/report/stream",
                    "request_id": request_id,
                    "report_id": report_id,
                    "provider": provider,
                    "model": model or "default",
                    "message": str(exc),
                }
            )
            yield _sse_pack(
                {
                    "type": "error",
                    "report_id": report_id,
                    "message": str(exc),
                    "recoverable": False,
                }
            )
            return

        # 兜底：模型最后一行可能没有换行符（常见），这里把尾巴再按“JSON Lines”处理一次
        if buffer.strip() and not saw_report_done:
            for tail_line in [line.strip() for line in buffer.splitlines() if line.strip()]:
                event = _parse_report_event_json_line(tail_line, report_id)
                if not event.get("ok"):
                    break

                validated = _validate_and_normalize_report_event(
                    data=event["event"],
                    report_id=report_id,
                    sections_plan=REPORT_SECTIONS_PLAN,
                    expected_section_index=expected_section_index,
                    current_section=current_section,
                    last_seq=last_seq,
                )
                if not validated.get("ok"):
                    break

                extra_events = validated.get("extra_events") or []
                events_to_emit = [*extra_events, validated["event"]]

                current_section = validated.get("current_section")
                expected_section_index = int(validated.get("expected_section_index", 0))

                for normalized in events_to_emit:
                    stream_stats["events_total"] += 1
                    stream_stats["last_section_id"] = normalized.get("section_id")

                    if normalized.get("type") == "section_delta":
                        delta_text = normalized.get("delta")
                        if isinstance(delta_text, str):
                            stream_stats["delta_chars"] += len(delta_text)
                    if normalized.get("type") == "section_done":
                        stream_stats["sections_done"] += 1

                    if normalized.get("type") == "report_done":
                        saw_report_done = True
                        normalized.setdefault(
                            "thinking", "".join(thinking_chunks).strip() if thinking_chunks else ""
                        )
                        elapsed_ms = int((time.perf_counter() - stream_start) * 1000)
                        prompt_tokens_est = _estimate_tokens(prompt_text)
                        completion_tokens_est = max(
                            1,
                            (stream_stats["delta_chars"] + stream_stats["thinking_chars"] + 3)
                            // 4,
                        )
                        normalized.setdefault(
                            "dev_info",
                            {
                                "elapsed_ms": elapsed_ms,
                                "prompt_tokens": prompt_tokens_est,
                                "completion_tokens": completion_tokens_est,
                                "total_tokens": prompt_tokens_est + completion_tokens_est,
                            },
                        )
                        _log_ai_metrics(
                            {
                                "kind": "stream_done",
                                "endpoint": "/api/bazi/report/stream",
                                "request_id": request_id,
                                "report_id": report_id,
                                "provider": provider,
                                "model": model or "default",
                                "enable_thinking": enable_thinking,
                                "temperature": temperature,
                                "timeout": timeout,
                                "elapsed_ms": elapsed_ms,
                                "usage": {
                                    "prompt_tokens_est": prompt_tokens_est,
                                    "completion_tokens_est": completion_tokens_est,
                                    "total_tokens_est": prompt_tokens_est + completion_tokens_est,
                                },
                                "stream": stream_stats,
                            }
                        )
                        _log_ai_content(
                            {
                                "kind": "stream_report_done",
                                "endpoint": "/api/bazi/report/stream",
                                "request_id": request_id,
                                "report_id": report_id,
                                "report": normalized.get("report"),
                            }
                        )
                        yield _sse_pack(normalized)
                        return

                    yield _sse_pack(normalized)

        # 流结束但没收到 report_done：按协议兜底为 error（避免前端一直等待）
        if buffer.strip() and not saw_report_done:
            _log_ai_metrics(
                {
                    "kind": "stream_error",
                    "endpoint": "/api/bazi/report/stream",
                    "request_id": request_id,
                    "report_id": report_id,
                    "message": "模型输出未按 JSON Lines 完整结束（存在未解析残留文本）",
                }
            )
            yield _sse_pack(
                {
                    "type": "error",
                    "report_id": report_id,
                    "message": "模型输出未按 JSON Lines 完整结束（存在未解析残留文本）",
                    "recoverable": False,
                }
            )
            return

        if not saw_report_done:
            _log_ai_metrics(
                {
                    "kind": "stream_error",
                    "endpoint": "/api/bazi/report/stream",
                    "request_id": request_id,
                    "report_id": report_id,
                    "message": "流式生成结束但未收到 report_done 事件",
                }
            )
            yield _sse_pack(
                {
                    "type": "error",
                    "report_id": report_id,
                    "message": "流式生成结束但未收到 report_done 事件",
                    "recoverable": False,
                }
            )

    return StreamingResponse(
        _event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@app.post("/api/bazi/report/stream-ndjson")
def generate_report_stream_ndjson(payload: ReportRequest):
    """兼容旧版 NDJSON 协议（meta/delta/thinking/done）。"""
    chart, analysis, knowledge, prompt = _prepare_report_context(payload)
    messages = _build_llm_messages(prompt)
    provider = _resolve_llm_provider()
    model = _resolve_llm_model("report", provider)
    temperature = _resolve_llm_temperature("report")
    timeout = _resolve_llm_timeout("report")
    enable_thinking = _resolve_feature_enable_thinking("report", provider)

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
                    yield json.dumps(
                        {"type": "delta", "text": chunk.content}, ensure_ascii=False
                    ) + "\n"
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
    request_id = str(uuid4())
    prompt = _build_chat_prompt(payload)
    _log_ai_content(
        {
            "kind": "request",
            "endpoint": "/api/bazi/chat",
            "request_id": request_id,
            "payload": payload.model_dump(mode="json"),
            "prompt": prompt,
        }
    )
    try:
        provider = _resolve_llm_provider()
        model = _resolve_llm_model("chat", provider)
        temperature = _resolve_llm_temperature("chat")
        timeout = _resolve_llm_timeout("chat")
        enable_thinking = _resolve_feature_enable_thinking("chat", provider)
        start_time = time.perf_counter()
        raw_text, usage = chat_with_usage(
            _build_llm_messages(prompt),
            provider=provider,
            model=model,
            temperature=temperature,
            enable_thinking=enable_thinking,
            timeout=timeout,
        )
        elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    except LLMError as exc:
        _log_ai_metrics(
            {
                "kind": "llm_error",
                "endpoint": "/api/bazi/chat",
                "request_id": request_id,
                "provider": provider if "provider" in locals() else None,
                "model": model if "model" in locals() else None,
                "message": str(exc),
            }
        )
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    reply = _normalize_llm_report(raw_text, prompt)
    prompt_text = json.dumps(_build_llm_messages(prompt), ensure_ascii=False)
    completion_text = raw_text or ""
    _log_ai_metrics(
        {
            "kind": "llm_done",
            "endpoint": "/api/bazi/chat",
            "request_id": request_id,
            "provider": provider,
            "model": model or "default",
            "enable_thinking": enable_thinking,
            "temperature": temperature,
            "timeout": timeout,
            "elapsed_ms": elapsed_ms,
            "usage": {
                "prompt_tokens": usage.get("prompt_tokens") if isinstance(usage, dict) else None,
                "completion_tokens": usage.get("completion_tokens") if isinstance(usage, dict) else None,
                "total_tokens": usage.get("total_tokens") if isinstance(usage, dict) else None,
                "prompt_tokens_est": _estimate_tokens(prompt_text),
                "completion_tokens_est": _estimate_tokens(completion_text),
                "total_tokens_est": _estimate_tokens(prompt_text) + _estimate_tokens(completion_text),
            },
        }
    )
    _log_ai_content(
        {
            "kind": "response",
            "endpoint": "/api/bazi/chat",
            "request_id": request_id,
            "raw_text": _truncate_text(raw_text or ""),
            "reply": reply,
        }
    )
    return {"reply": reply, "prompt": prompt}


@app.post("/api/bazi/chat/stream")
def chat_with_chart_stream(payload: ChatRequest):
    prompt = _build_chat_prompt(payload)
    messages = _build_llm_messages(prompt)
    request_id = str(uuid4())
    _log_ai_content(
        {
            "kind": "request",
            "endpoint": "/api/bazi/chat/stream",
            "request_id": request_id,
            "payload": payload.model_dump(mode="json"),
        }
    )
    provider = _resolve_llm_provider()
    model = _resolve_llm_model("chat", provider)
    temperature = _resolve_llm_temperature("chat")
    timeout = _resolve_llm_timeout("chat")
    enable_thinking = _resolve_feature_enable_thinking("chat", provider)

    def _event_stream() -> Iterator[str]:
        start_time = time.perf_counter()
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
            _log_ai_metrics(
                {
                    "kind": "llm_error",
                    "endpoint": "/api/bazi/chat/stream",
                    "request_id": request_id,
                    "provider": provider,
                    "model": model or "default",
                    "message": str(exc),
                }
            )
            yield json.dumps({"type": "error", "message": str(exc)}, ensure_ascii=False) + "\n"
            return

        reply_text = "".join(chunks).strip()
        if not reply_text:
            reply_text = "已收到。"
        elapsed_ms = int((time.perf_counter() - start_time) * 1000)
        prompt_text = json.dumps(messages, ensure_ascii=False)
        completion_text = reply_text + ("".join(thinking_chunks) if thinking_chunks else "")
        _log_ai_metrics(
            {
                "kind": "llm_done",
                "endpoint": "/api/bazi/chat/stream",
                "request_id": request_id,
                "provider": provider,
                "model": model or "default",
                "enable_thinking": enable_thinking,
                "temperature": temperature,
                "timeout": timeout,
                "elapsed_ms": elapsed_ms,
                "usage": {
                    "prompt_tokens_est": _estimate_tokens(prompt_text),
                    "completion_tokens_est": _estimate_tokens(completion_text),
                    "total_tokens_est": _estimate_tokens(prompt_text) + _estimate_tokens(completion_text),
                },
            }
        )
        _log_ai_content(
            {
                "kind": "response",
                "endpoint": "/api/bazi/chat/stream",
                "request_id": request_id,
                "reply_text": _truncate_text(reply_text),
                "thinking": _truncate_text("".join(thinking_chunks).strip()),
            }
        )
        yield json.dumps(
            {"type": "done", "reply": reply_text, "thinking": "".join(thinking_chunks).strip()},
            ensure_ascii=False,
        ) + "\n"

    return StreamingResponse(_event_stream(), media_type="application/x-ndjson")


@app.post("/api/bazi/general-chat/stream")
def general_chat_stream(payload: GeneralChatRequest):
    """通用聊天接口（无需命盘），用于喵大师等场景"""
    request_id = str(uuid4())
    def _build_default_system_prompt(is_deep: bool) -> str:
        worldview = (
            "神机喵算并非一言定命，而是因问而推，因心而算。"
            "小喵道童观其象，喵道长入其局。"
        )
        if is_deep:
            return (
                "你是神机喵算的命理推演者「喵道长」，精通子平八字命理。"
                "语气：稳、慢、克制。"
                "用词偏「权衡、侧重、并非绝对」，"
                "承认不确定性，但给出清晰判断。"
                "可用句式："
                "“此处不可只看一象。”"
                "“若从整体命局权衡，其侧重在于……”"
                "“此并非定论，而是命势所显之倾向。”"
                "要求：不提及AI/模型/算力等词；"
                "结论清楚，依据简洁，避免玄虚与空泛。"
                f"{worldview}"
            )
        return (
            "你是神机喵算的对话助手「小喵道童」，精通中国传统八字命理学。"
            "语气：轻、自然、陪伴感。"
            "用词直观，少用权衡词。"
            "禁止长段推演、反复对比。"
            "可用句式："
            "“我先帮你看个大概喵～”"
            "“从整体来看，这里有一个比较明显的倾向。”"
            "要求：不提及AI/模型/算力等词；"
            "尽量简洁，给出可理解的结论与下一步建议。"
            f"{worldview}"
        )

    system_prompt = payload.system_prompt or _build_default_system_prompt(payload.deep_think)
    provider = _resolve_llm_provider(payload.llm_provider)
    model = _resolve_llm_model("chat", provider)
    temperature = _resolve_llm_temperature("chat")
    timeout = _resolve_llm_timeout("chat")
    enable_thinking = _resolve_feature_enable_thinking("chat", provider, payload.deep_think)

    def _format_hidden_stems(stems: List[Any]) -> str:
        if not stems:
            return "无"
        parts = []
        for stem in stems:
            name = getattr(stem, "name", "") or ""
            element = getattr(stem, "element", "") or ""
            yinyang = getattr(stem, "yinyang", "") or ""
            ten_god = getattr(stem, "ten_god", "") or ""
            label = f"{name}"
            detail = " ".join([item for item in [element, yinyang, ten_god] if item])
            if detail:
                label = f"{label}({detail})"
            parts.append(label)
        return "、".join(parts) if parts else "无"

    def _format_pillar(label: str, pillar: PillarInfo) -> str:
        hs = pillar.heaven_stem
        eb = pillar.earth_branch
        stem_desc = f"{hs.name}({hs.element}{hs.yinyang} {hs.ten_god})".strip()
        branch_desc = f"{eb.name}({eb.element}{eb.yinyang})".strip()
        hidden_desc = _format_hidden_stems(eb.hidden_stems)
        return f"{label}：{hs.name}{eb.name}｜天干{stem_desc}｜地支{branch_desc}｜藏干{hidden_desc}"

    # 可选：命主上下文（前端简化传参，后端用提示词方式注入，避免改动更大结构）
    if payload.subject_enabled and (
        payload.subject_name
        or payload.subject_birth
        or payload.subject_gender
        or payload.subject_destiny
        or payload.subject_chart
    ):
        birth = payload.subject_birth or ""
        raw_gender = (payload.subject_gender or "").strip().lower()
        if raw_gender in ("male", "m", "man", "男"):
            gender_label = "男"
        elif raw_gender in ("female", "f", "woman", "女"):
            gender_label = "女"
        elif raw_gender:
            gender_label = payload.subject_gender or ""
        else:
            gender_label = ""
        subject_chart = None
        if payload.subject_chart:
            try:
                subject_chart = Chart.model_validate(payload.subject_chart)
            except Exception as exc:
                root_logger.warning("命主档案解析失败，已跳过: %s", exc)
                subject_chart = None
        current_year_pillar = None
        try:
            day_stem = (
                subject_chart.day_pillar.heaven_stem.name if subject_chart else None
            )
            current_year_pillar = engine.get_current_year_pillar(day_stem=day_stem)
        except Exception as exc:
            root_logger.warning("流年计算失败，已跳过: %s", exc)
            current_year_pillar = None
        system_prompt += "\n\n【当前对话命主信息】\n"
        system_prompt += f"- 姓名：{payload.subject_name or ''}\n"
        if gender_label:
            system_prompt += f"- 性别：{gender_label}\n"
        if current_year_pillar:
            system_prompt += (
                f"- 当前流年：{current_year_pillar.heaven_stem.name}"
                f"{current_year_pillar.earth_branch.name}\n"
            )
        if payload.subject_destiny:
            system_prompt += f"- 十年大运：{payload.subject_destiny}\n"
        if subject_chart:
            system_prompt += (
                "【八字四柱】\n"
                f"{_format_pillar('年柱', subject_chart.year_pillar)}\n"
                f"{_format_pillar('月柱', subject_chart.month_pillar)}\n"
                f"{_format_pillar('日柱', subject_chart.day_pillar)}\n"
                f"{_format_pillar('时柱', subject_chart.hour_pillar)}\n"
            )
            if subject_chart.destiny_cycle and subject_chart.destiny_cycle.destiny_pillars:
                destiny_lines = []
                for pillar in subject_chart.destiny_cycle.destiny_pillars:
                    label = f"{pillar.year} {pillar.heaven_stem.name}{pillar.earth_branch.name}"
                    if pillar.is_current:
                        label += "(当前)"
                    destiny_lines.append(label)
                system_prompt += f"【十年大运】\n{'；'.join(destiny_lines)}\n"
        system_prompt += (
            f"- 出生：{birth}\n"
            "当用户的问题与命理分析相关时，请结合以上命主信息进行推演；"
            "当问题与命理无关时，正常回答即可。"
        )

    # 构建对话消息
    messages = [{"role": "system", "content": system_prompt}]
    for turn in payload.history:
        messages.append({"role": turn.role, "content": turn.content})
    _log_ai_content(
        {
            "kind": "request",
            "endpoint": "/api/bazi/general-chat/stream",
            "request_id": request_id,
            "payload": payload.model_dump(mode="json"),
            "messages": messages,
        }
    )

    def _event_stream() -> Iterator[str]:
        start_time = time.perf_counter()
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
            _log_ai_metrics(
                {
                    "kind": "llm_error",
                    "endpoint": "/api/bazi/general-chat/stream",
                    "request_id": request_id,
                    "provider": provider,
                    "model": model or "default",
                    "message": str(exc),
                }
            )
            yield json.dumps({"type": "error", "message": str(exc)}, ensure_ascii=False) + "\n"
            return

        reply_text = "".join(chunks).strip()
        if not reply_text:
            reply_text = "我明白了，请问还有什么想了解的吗？"
        elapsed_ms = int((time.perf_counter() - start_time) * 1000)
        prompt_text = json.dumps(messages, ensure_ascii=False)
        completion_text = reply_text + ("".join(thinking_chunks) if thinking_chunks else "")
        _log_ai_metrics(
            {
                "kind": "llm_done",
                "endpoint": "/api/bazi/general-chat/stream",
                "request_id": request_id,
                "provider": provider,
                "model": model or "default",
                "enable_thinking": enable_thinking,
                "temperature": temperature,
                "timeout": timeout,
                "elapsed_ms": elapsed_ms,
                "usage": {
                    "prompt_tokens_est": _estimate_tokens(prompt_text),
                    "completion_tokens_est": _estimate_tokens(completion_text),
                    "total_tokens_est": _estimate_tokens(prompt_text) + _estimate_tokens(completion_text),
                },
            }
        )
        _log_ai_content(
            {
                "kind": "response",
                "endpoint": "/api/bazi/general-chat/stream",
                "request_id": request_id,
                "reply_text": _truncate_text(reply_text),
                "thinking": _truncate_text("".join(thinking_chunks).strip()),
            }
        )
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

    request_id = str(uuid4())
    _log_ai_content(
        {
            "kind": "request",
            "endpoint": "/api/bazi/energy-analysis",
            "request_id": request_id,
            "payload": payload.model_dump(mode="json"),
        }
    )
    try:
        chart_data = payload.chart
        prompt_text = build_energy_analysis_prompt(chart_data)

        provider = _resolve_llm_provider()
        model = _resolve_llm_model("energy", provider)
        temperature = _resolve_llm_temperature("energy")
        timeout = _resolve_llm_timeout("energy")
        enable_thinking = _resolve_feature_enable_thinking("energy", provider)
        response_format = {
            "type": "json_schema",
            "json_schema": {
                "name": "energy_analysis",
                "schema": build_energy_analysis_schema(),
                "strict": True,
            },
        }
        system_message = (
            "你是一位专业的八字命理师，"
            "请严格按要求的 JSON 格式输出分析结果。"
        )
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt_text},
        ]

        start_time = time.perf_counter()
        energy_logger.info(
            "energy_analysis llm_request provider=%s model=%s enable_thinking=%s temperature=%s timeout=%s",
            provider,
            model or "default",
            enable_thinking,
            temperature,
            timeout,
        )
        raw_text, usage = chat_with_usage(
            messages,
            provider=provider,
            model=model,
            temperature=temperature,
            enable_thinking=enable_thinking,
            response_format=response_format,
            timeout=timeout,
        )
        elapsed_ms = int((time.perf_counter() - start_time) * 1000)
        energy_logger.info(
            "energy_analysis llm_call provider=%s model=%s enable_thinking=%s temperature=%s timeout=%s "
            "elapsed_ms=%s prompt_tokens=%s completion_tokens=%s total_tokens=%s",
            provider,
            model or "default",
            enable_thinking,
            temperature,
            timeout,
            elapsed_ms,
            usage.get("prompt_tokens") if isinstance(usage, dict) else None,
            usage.get("completion_tokens") if isinstance(usage, dict) else None,
            usage.get("total_tokens") if isinstance(usage, dict) else None,
        )
        result = _extract_json(raw_text)

        if not result or "elements" not in result:
            # 解析失败，返回错误信息
            raise HTTPException(status_code=502, detail="AI 返回格式解析失败")

        _log_ai_metrics(
            {
                "kind": "llm_done",
                "endpoint": "/api/bazi/energy-analysis",
                "request_id": request_id,
                "provider": provider,
                "model": model or "default",
                "enable_thinking": enable_thinking,
                "temperature": temperature,
                "timeout": timeout,
                "elapsed_ms": elapsed_ms,
                "usage": {
                    "prompt_tokens": usage.get("prompt_tokens") if isinstance(usage, dict) else None,
                    "completion_tokens": usage.get("completion_tokens") if isinstance(usage, dict) else None,
                    "total_tokens": usage.get("total_tokens") if isinstance(usage, dict) else None,
                    "prompt_tokens_est": _estimate_tokens(json.dumps(messages, ensure_ascii=False)),
                    "completion_tokens_est": _estimate_tokens(raw_text or ""),
                    "total_tokens_est": _estimate_tokens(json.dumps(messages, ensure_ascii=False))
                    + _estimate_tokens(raw_text or ""),
                },
            }
        )
        _log_ai_content(
            {
                "kind": "response",
                "endpoint": "/api/bazi/energy-analysis",
                "request_id": request_id,
                "raw_text": _truncate_text(raw_text or ""),
                "result": result,
            }
        )
        dev_info = _build_dev_info(usage, elapsed_ms, messages, raw_text)
        return {**result, "dev_info": dev_info}
    except LLMError as exc:
        elapsed_ms = int((time.perf_counter() - start_time) * 1000) if "start_time" in locals() else None
        energy_logger.error(
            "energy_analysis llm_error elapsed_ms=%s message=%s",
            elapsed_ms,
            str(exc),
        )
        _log_ai_metrics(
            {
                "kind": "llm_error",
                "endpoint": "/api/bazi/energy-analysis",
                "request_id": request_id,
                "provider": provider if "provider" in locals() else None,
                "model": model if "model" in locals() else None,
                "elapsed_ms": elapsed_ms,
                "message": str(exc),
            }
        )
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        elapsed_ms = int((time.perf_counter() - start_time) * 1000) if "start_time" in locals() else None
        energy_logger.error(
            "energy_analysis error elapsed_ms=%s message=%s",
            elapsed_ms,
            str(exc),
        )
        _log_ai_metrics(
            {
                "kind": "error",
                "endpoint": "/api/bazi/energy-analysis",
                "request_id": request_id,
                "elapsed_ms": elapsed_ms,
                "message": str(exc),
            }
        )
        raise HTTPException(status_code=400, detail=f"分析失败: {exc}") from exc


def _build_destiny_pillar(destiny_data: Dict[str, Any]) -> PillarInfo:
    if not destiny_data:
        raise HTTPException(status_code=400, detail="缺少大运柱信息")
    return PillarInfo.model_validate(
        {
            "heaven_stem": destiny_data.get("heaven_stem", {}),
            "earth_branch": destiny_data.get("earth_branch", {}),
        }
    )


def _calculate_destiny_relations(chart: Chart, destiny_pillar: PillarInfo) -> GanZhiRelations:
    return engine.calculate_all_ganzi_relations(
        chart.year_pillar,
        chart.month_pillar,
        chart.day_pillar,
        chart.hour_pillar,
        destiny_pillar=destiny_pillar,
    )


def _filter_destiny_relations(relations: GanZhiRelations) -> List[Dict[str, Any]]:
    def is_destiny_relation(rel: Any) -> bool:
        if not getattr(rel, "pillars", None):
            return False
        if "destiny" not in rel.pillars:
            return False
        return any(pid in {"year", "month", "day", "hour"} for pid in rel.pillars)

    filtered: List[Dict[str, Any]] = []
    for rel in relations.stem_relations + relations.branch_relations:
        if is_destiny_relation(rel):
            filtered.append(rel.model_dump())
    return filtered


def _build_destiny_relations_map(chart: Chart) -> Dict[str, Any]:
    destiny_cycle = chart.destiny_cycle
    if not destiny_cycle or not destiny_cycle.destiny_pillars:
        return {}
    day_pillar = chart.day_pillar
    key_prefix = f"destiny_rel_{day_pillar.heaven_stem.name}{day_pillar.earth_branch.name}_"
    relations_map: Dict[str, Any] = {}
    for pillar in destiny_cycle.destiny_pillars:
        destiny_pillar = _build_destiny_pillar(pillar.model_dump())
        relations = _calculate_destiny_relations(chart, destiny_pillar)
        relations_map[f"{key_prefix}{pillar.year}"] = relations.model_dump()
    return relations_map


@app.post("/api/bazi/destiny-relations")
def destiny_relations(payload: DestinyRelationsRequest):
    """获取指定大运与本命四柱的干支关系"""
    try:
        chart = Chart.model_validate(payload.chart)
        destiny_pillar = _build_destiny_pillar(payload.destiny_pillar)
        relations = _calculate_destiny_relations(chart, destiny_pillar)
        return relations.model_dump()
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"关系计算失败: {exc}") from exc


@app.post("/api/bazi/destiny-analysis")
def analyze_destiny(payload: DestinyAnalysisRequest):
    """大运智能解析接口"""
    from src.api.destiny_prompt import build_destiny_analysis_prompt

    request_id = str(uuid4())
    _log_ai_content(
        {
            "kind": "request",
            "endpoint": "/api/bazi/destiny-analysis",
            "request_id": request_id,
            "payload": payload.model_dump(mode="json"),
        }
    )
    try:
        chart_data = payload.chart
        chart = Chart.model_validate(chart_data)
        destiny_pillar_data = payload.destiny_pillar
        destiny_pillar = _build_destiny_pillar(destiny_pillar_data)
        relations = _calculate_destiny_relations(chart, destiny_pillar)
        relation_list = _filter_destiny_relations(relations)

        prompt_text = build_destiny_analysis_prompt(chart_data, destiny_pillar_data, relation_list)

        provider = _resolve_llm_provider()
        model = _resolve_llm_model("destiny", provider)
        temperature = _resolve_llm_temperature("destiny")
        timeout = _resolve_llm_timeout("destiny")
        enable_thinking = _resolve_feature_enable_thinking("destiny", provider)
        response_format = {
            "type": "json_schema",
            "json_schema": {
                "name": "destiny_analysis",
                "schema": build_destiny_analysis_schema(),
                "strict": True,
            },
        }
        system_message = (
            "你是一位专业的八字命理师，"
            "请严格按要求的 JSON 格式输出分析结果。"
        )
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt_text},
        ]

        start_time = time.perf_counter()
        destiny_logger.info(
            "destiny_analysis llm_request provider=%s model=%s enable_thinking=%s temperature=%s timeout=%s",
            provider,
            model or "default",
            enable_thinking,
            temperature,
            timeout,
        )
        raw_text, usage = chat_with_usage(
            messages,
            provider=provider,
            model=model,
            temperature=temperature,
            enable_thinking=enable_thinking,
            response_format=response_format,
            timeout=timeout,
        )
        elapsed_ms = int((time.perf_counter() - start_time) * 1000)
        destiny_logger.info(
            "destiny_analysis llm_call provider=%s model=%s enable_thinking=%s temperature=%s timeout=%s "
            "elapsed_ms=%s prompt_tokens=%s completion_tokens=%s total_tokens=%s",
            provider,
            model or "default",
            enable_thinking,
            temperature,
            timeout,
            elapsed_ms,
            usage.get("prompt_tokens") if isinstance(usage, dict) else None,
            usage.get("completion_tokens") if isinstance(usage, dict) else None,
            usage.get("total_tokens") if isinstance(usage, dict) else None,
        )
        result = _extract_json(raw_text)

        if not result or "summary" not in result or "tips" not in result:
            raise HTTPException(status_code=502, detail="AI 返回格式解析失败")

        _log_ai_metrics(
            {
                "kind": "llm_done",
                "endpoint": "/api/bazi/destiny-analysis",
                "request_id": request_id,
                "provider": provider,
                "model": model or "default",
                "enable_thinking": enable_thinking,
                "temperature": temperature,
                "timeout": timeout,
                "elapsed_ms": elapsed_ms,
                "usage": {
                    "prompt_tokens": usage.get("prompt_tokens") if isinstance(usage, dict) else None,
                    "completion_tokens": usage.get("completion_tokens") if isinstance(usage, dict) else None,
                    "total_tokens": usage.get("total_tokens") if isinstance(usage, dict) else None,
                    "prompt_tokens_est": _estimate_tokens(json.dumps(messages, ensure_ascii=False)),
                    "completion_tokens_est": _estimate_tokens(raw_text or ""),
                    "total_tokens_est": _estimate_tokens(json.dumps(messages, ensure_ascii=False))
                    + _estimate_tokens(raw_text or ""),
                },
            }
        )
        _log_ai_content(
            {
                "kind": "response",
                "endpoint": "/api/bazi/destiny-analysis",
                "request_id": request_id,
                "raw_text": _truncate_text(raw_text or ""),
                "result": result,
            }
        )
        return result
    except LLMError as exc:
        elapsed_ms = int((time.perf_counter() - start_time) * 1000) if "start_time" in locals() else None
        destiny_logger.error(
            "destiny_analysis llm_error elapsed_ms=%s message=%s",
            elapsed_ms,
            str(exc),
        )
        _log_ai_metrics(
            {
                "kind": "llm_error",
                "endpoint": "/api/bazi/destiny-analysis",
                "request_id": request_id,
                "provider": provider if "provider" in locals() else None,
                "model": model if "model" in locals() else None,
                "elapsed_ms": elapsed_ms,
                "message": str(exc),
            }
        )
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        elapsed_ms = int((time.perf_counter() - start_time) * 1000) if "start_time" in locals() else None
        destiny_logger.error(
            "destiny_analysis error elapsed_ms=%s message=%s",
            elapsed_ms,
            str(exc),
        )
        _log_ai_metrics(
            {
                "kind": "error",
                "endpoint": "/api/bazi/destiny-analysis",
                "request_id": request_id,
                "elapsed_ms": elapsed_ms,
                "message": str(exc),
            }
        )
        raise HTTPException(status_code=400, detail=f"分析失败: {exc}") from exc


@app.post("/api/bazi/destiny-analysis-batch")
def analyze_destiny_batch(payload: DestinyAnalysisBatchRequest):
    """多条大运智能解析接口"""
    from src.api.destiny_prompt import build_destiny_analysis_batch_prompt

    request_id = str(uuid4())
    _log_ai_content(
        {
            "kind": "request",
            "endpoint": "/api/bazi/destiny-analysis-batch",
            "request_id": request_id,
            "payload": payload.model_dump(mode="json"),
        }
    )
    try:
        chart_data = payload.chart
        chart = Chart.model_validate(chart_data)
        destiny_items: List[Dict[str, Any]] = []
        input_years: List[int] = []
        for destiny_pillar_data in payload.destiny_pillars:
            destiny_pillar = _build_destiny_pillar(destiny_pillar_data)
            relations = _calculate_destiny_relations(chart, destiny_pillar)
            relation_list = _filter_destiny_relations(relations)
            destiny_items.append({
                "destiny_pillar": destiny_pillar_data,
                "relations": relation_list,
            })
            year = destiny_pillar_data.get("year")
            if isinstance(year, int):
                input_years.append(year)

        prompt_text = build_destiny_analysis_batch_prompt(chart_data, destiny_items)

        provider = _resolve_llm_provider()
        model = _resolve_llm_model("destiny", provider)
        temperature = _resolve_llm_temperature("destiny")
        timeout = _resolve_llm_timeout("destiny")
        enable_thinking = _resolve_feature_enable_thinking("destiny", provider)
        response_format = {
            "type": "json_schema",
            "json_schema": {
                "name": "destiny_analysis_batch",
                "schema": build_destiny_analysis_batch_schema(),
                "strict": True,
            },
        }
        system_message = (
            "你是一位专业的八字命理师，"
            "请严格按要求的 JSON 格式输出分析结果。"
        )
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt_text},
        ]

        start_time = time.perf_counter()
        destiny_logger.info(
            "destiny_analysis_batch llm_request provider=%s model=%s enable_thinking=%s temperature=%s timeout=%s",
            provider,
            model or "default",
            enable_thinking,
            temperature,
            timeout,
        )
        raw_text, usage = chat_with_usage(
            messages,
            provider=provider,
            model=model,
            temperature=temperature,
            enable_thinking=enable_thinking,
            response_format=response_format,
            timeout=timeout,
        )
        elapsed_ms = int((time.perf_counter() - start_time) * 1000)
        destiny_logger.info(
            "destiny_analysis_batch llm_call provider=%s model=%s enable_thinking=%s temperature=%s timeout=%s "
            "elapsed_ms=%s prompt_tokens=%s completion_tokens=%s total_tokens=%s",
            provider,
            model or "default",
            enable_thinking,
            temperature,
            timeout,
            elapsed_ms,
            usage.get("prompt_tokens") if isinstance(usage, dict) else None,
            usage.get("completion_tokens") if isinstance(usage, dict) else None,
            usage.get("total_tokens") if isinstance(usage, dict) else None,
        )
        result = _extract_json(raw_text)
        items = result.get("items") if isinstance(result, dict) else None
        if not isinstance(items, list):
            raise HTTPException(status_code=502, detail="AI 返回格式解析失败")

        normalized: List[Dict[str, Any]] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            year = item.get("year")
            summary = str(item.get("summary", "")).strip()
            tips = str(item.get("tips", "")).strip()
            if not isinstance(year, int) or not summary or not tips:
                continue
            normalized.append({
                "year": year,
                "summary": summary,
                "tips": tips,
            })

        if not normalized:
            raise HTTPException(status_code=502, detail="AI 返回格式解析失败")

        _log_ai_metrics(
            {
                "kind": "llm_done",
                "endpoint": "/api/bazi/destiny-analysis-batch",
                "request_id": request_id,
                "provider": provider,
                "model": model or "default",
                "enable_thinking": enable_thinking,
                "temperature": temperature,
                "timeout": timeout,
                "elapsed_ms": elapsed_ms,
                "usage": {
                    "prompt_tokens": usage.get("prompt_tokens") if isinstance(usage, dict) else None,
                    "completion_tokens": usage.get("completion_tokens") if isinstance(usage, dict) else None,
                    "total_tokens": usage.get("total_tokens") if isinstance(usage, dict) else None,
                    "prompt_tokens_est": _estimate_tokens(json.dumps(messages, ensure_ascii=False)),
                    "completion_tokens_est": _estimate_tokens(raw_text or ""),
                    "total_tokens_est": _estimate_tokens(json.dumps(messages, ensure_ascii=False))
                    + _estimate_tokens(raw_text or ""),
                },
            }
        )
        _log_ai_content(
            {
                "kind": "response",
                "endpoint": "/api/bazi/destiny-analysis-batch",
                "request_id": request_id,
                "raw_text": _truncate_text(raw_text or ""),
                "result": {"items": normalized},
            }
        )
        dev_info = _build_dev_info(usage, elapsed_ms, messages, raw_text)

        if input_years:
            by_year = {item["year"]: item for item in normalized}
            ordered = [by_year[year] for year in input_years if year in by_year]
            return {"items": ordered or normalized, "dev_info": dev_info}

        return {"items": normalized, "dev_info": dev_info}
    except LLMError as exc:
        elapsed_ms = int((time.perf_counter() - start_time) * 1000) if "start_time" in locals() else None
        destiny_logger.error(
            "destiny_analysis_batch llm_error elapsed_ms=%s message=%s",
            elapsed_ms,
            str(exc),
        )
        _log_ai_metrics(
            {
                "kind": "llm_error",
                "endpoint": "/api/bazi/destiny-analysis-batch",
                "request_id": request_id,
                "provider": provider if "provider" in locals() else None,
                "model": model if "model" in locals() else None,
                "elapsed_ms": elapsed_ms,
                "message": str(exc),
            }
        )
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        elapsed_ms = int((time.perf_counter() - start_time) * 1000) if "start_time" in locals() else None
        destiny_logger.error(
            "destiny_analysis_batch error elapsed_ms=%s message=%s",
            elapsed_ms,
            str(exc),
        )
        _log_ai_metrics(
            {
                "kind": "error",
                "endpoint": "/api/bazi/destiny-analysis-batch",
                "request_id": request_id,
                "elapsed_ms": elapsed_ms,
                "message": str(exc),
            }
        )
        raise HTTPException(status_code=400, detail=f"分析失败: {exc}") from exc


def _prepare_report_context(
    payload: ReportRequest,
    prompt_builder: Callable[[Chart, Any, List[Any], List[str]], Dict[str, Any]] = build_report_prompt,
):
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
    prompt = prompt_builder(chart, analysis, knowledge, payload.focus)
    return chart, analysis, knowledge, prompt


def _sse_pack(data: Dict[str, Any]) -> str:
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"


def _parse_report_event_json_line(line: str, report_id: str) -> Dict[str, Any]:
    try:
        parsed = json.loads(line)
    except json.JSONDecodeError:
        return {"ok": False, "message": f"非 JSON 行：{line[:80]}..."}
    if not isinstance(parsed, dict):
        return {"ok": False, "message": "事件必须是 JSON object"}
    parsed.setdefault("report_id", report_id)
    return {"ok": True, "event": parsed}


def _validate_and_normalize_report_event(
    *,
    data: Dict[str, Any],
    report_id: str,
    sections_plan: List[Dict[str, str]],
    expected_section_index: int,
    current_section: Optional[str],
    last_seq: Dict[str, int],
) -> Dict[str, Any]:
    event_type = str(data.get("type") or "").strip()
    if not event_type:
        return {"ok": False, "message": "缺少 type 字段"}

    allowed = {"section_start", "section_delta", "section_patch", "section_done", "report_done"}
    if event_type not in allowed:
        return {"ok": False, "message": f"不支持的事件 type：{event_type}"}

    data["report_id"] = report_id

    section_ids = [item.get("section_id") for item in sections_plan]
    section_titles = {item.get("section_id"): item.get("title") for item in sections_plan}

    if event_type == "report_done":
        # 新协议：report_done 仅表示流式生成结束，不再要求附带完整 report JSON。
        # 兼容旧协议：如果模型仍返回 report 对象，则透传；但若类型不对则丢弃，避免污染前端状态。
        report = data.get("report")
        if report is not None and not isinstance(report, dict):
            data.pop("report", None)
        return {
            "ok": True,
            "event": data,
            "current_section": current_section,
            "expected_section_index": expected_section_index,
        }

    section_id = str(data.get("section_id") or "").strip()
    if not section_id:
        return {"ok": False, "message": f"{event_type} 缺少 section_id"}
    if section_id not in section_titles:
        return {"ok": False, "message": f"未知 section_id：{section_id}"}
    data.setdefault("title", section_titles.get(section_id))

    expected_section_id = section_ids[expected_section_index] if expected_section_index < len(
        section_ids
    ) else None

    if event_type == "section_start":
        if current_section is not None:
            # 容错：模型偶发漏发上一段的 section_done，直接开始下一段的 section_start。
            # 当且仅当“当前段 == 期望段”且“收到的 section_id == 下一期望段”时，自动补一个 section_done。
            next_expected = (
                section_ids[expected_section_index + 1]
                if expected_section_index + 1 < len(section_ids)
                else None
            )
            if (
                expected_section_id
                and next_expected
                and current_section == expected_section_id
                and section_id == next_expected
            ):
                synthetic_done = {
                    "type": "section_done",
                    "report_id": report_id,
                    "section_id": current_section,
                }
                synthetic_done.setdefault("title", section_titles.get(current_section))
                return {
                    "ok": True,
                    "extra_events": [synthetic_done],
                    "event": data,
                    "current_section": section_id,
                    "expected_section_index": expected_section_index + 1,
                }

            return {
                "ok": False,
                "message": f"section_start 发生在上一段未结束时（当前段：{current_section}）",
            }
        if expected_section_id and section_id != expected_section_id:
            return {
                "ok": False,
                "message": f"section_start 顺序错误，期望 {expected_section_id}，但收到 {section_id}",
            }
        return {
            "ok": True,
            "event": data,
            "current_section": section_id,
            "expected_section_index": expected_section_index,
        }

    if current_section != section_id:
        return {
            "ok": False,
            "message": f"{event_type} 的 section_id 与当前生成段不一致：{section_id}",
        }

    if event_type == "section_delta":
        seq = data.get("seq")
        if not isinstance(seq, int):
            return {"ok": False, "message": "section_delta 缺少/非法 seq（必须是 int）"}
        delta = data.get("delta")
        if not isinstance(delta, str):
            return {"ok": False, "message": "section_delta 缺少/非法 delta（必须是 string）"}
        prev = last_seq.get(section_id, 0)
        if seq <= prev:
            return {"ok": False, "message": f"section_delta seq 非递增：{seq} <= {prev}"}
        last_seq[section_id] = seq
        return {
            "ok": True,
            "event": data,
            "current_section": current_section,
            "expected_section_index": expected_section_index,
        }

    if event_type == "section_patch":
        patch = data.get("patch")
        if not isinstance(patch, dict):
            return {"ok": False, "message": "section_patch 缺少/非法 patch（必须是 object）"}
        return {
            "ok": True,
            "event": data,
            "current_section": current_section,
            "expected_section_index": expected_section_index,
        }

    if event_type == "section_done":
        next_index = expected_section_index + 1
        return {
            "ok": True,
            "event": data,
            "current_section": None,
            "expected_section_index": next_index,
        }

    return {"ok": False, "message": "未知校验分支"}


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
