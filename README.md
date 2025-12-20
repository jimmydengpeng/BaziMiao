# 神机喵算 (BaziMiao)

基于八字排盘 + 规则层 + 大模型解释器的 AI 命理 WebApp 骨架，核心思路是“确定性排盘，模型只负责讲解”。

## 目录结构
- `src/engine/bazi_engine.py`：确定性排盘（sxtwl 计算四柱/大运），不做解读。
- `src/rules/analysis.py`：轻量规则层，生成身强弱、用忌神、标签。
- `src/knowledge/base.py`：知识模板检索，供 LLM 参考。
- `src/prompt/report_prompt.py`：生成 LLM Prompt，限制“不重算只解释”。
- `src/api/server.py`：FastAPI 接口 `/api/bazi/report` 与 `/api/bazi/chat`。
- `src/api/schemas.py`：API 入参模型（Pydantic）。
- `src/web/`：前端 Vue3/Vite 工程，包含 Landing + 表单 + 报告 + 对话。
- `docs/architecture.md`：总体架构与产品/交互/Prompt/安全设计。
- `tests/fixtures/`：示例请求。

## 快速开始
1) 安装依赖
```bash
make setup
```
如果未安装 `sxtwl`，需要先安装其依赖，macOS 可以用 `brew install swig` 后再 `pip install sxtwl`。

2) 本地启动
```bash
make dev
```
默认使用 `uvicorn src.api.server:app --reload --port 8000`。

3) 前端启动
```bash
make web-setup
make web-dev
```
默认 Vite 开发端口 5173，已代理到本地 8000 的 API。

4) 示例请求
```bash
curl -X POST http://127.0.0.1:8000/api/bazi/report \
  -H "Content-Type: application/json" \
  -d @tests/fixtures/sample_request.json
```

## 设计要点
- 排盘、用忌神判定、标签均由后端确定性/规则层完成，LLM 只做解释与文案。
- 每轮对话都携带同一份 `chart` 与 `analysis`，避免模型“记忆漂移”。
- Prompt 中明确禁令：不得重算八字、不得自创格局。
- 现有规则为简版，可在 `rules/analysis.py` 中逐步替换更严谨的判定。
- 详细产品/架构/迭代路线见 `docs/architecture.md`。

## 前后端协作
- 前端开发端口 5173，Vite 代理 `/api` 到 `http://127.0.0.1:8000`。
- 因此前端请求 `fetch("/api/bazi/report")` 会转发到后端的 `/api/bazi/report`。

## Make 入口
- `make setup`：安装依赖。
- `make dev`：开发模式启动 API。
- `make web-setup`：安装前端依赖。
- `make web-dev`：启动前端 dev server（含 API 代理）。
- `make web-build`：前端构建。
- `make test`：预留测试入口。
- `make lint`：ruff 静态检查。
- `make fmt`：black 格式化。

## TODO
- 真太阳时、早晚子时、地理位置校正。
- 更完善的身强弱/格局/用忌神逻辑与回归用例。
- 接入真实 LLM 与向量检索替换 `_fake_llm_generate`。
