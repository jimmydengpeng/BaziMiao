# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

神机喵算（BaziMiao）是一个基于八字排盘的 AI 命理 WebApp，核心理念是「确定性排盘 + 规则层 + 大模型解释」。系统使用 Python 后端（FastAPI）和 Vue3 前端，排盘、用忌神判定、标签由后端确定性/规则层完成，LLM 只负责解释与文案生成。

## 常用命令

### 后端开发
```bash
# 安装依赖（需要先安装 sxtwl，macOS 需先 brew install swig）
make setup

# 启动开发服务器（端口 8000）
make dev

# 代码格式化与检查
make fmt      # black 格式化
make lint     # ruff 静态检查

# 运行测试
make test     # pytest
```

### 前端开发
```bash
# 安装前端依赖
make web-setup

# 启动前端开发服务器（端口 5173，已配置 API 代理到 8000）
make web-dev

# 构建前端
make web-build
```

### 示例 API 请求
```bash
# 排盘接口
curl -X POST http://127.0.0.1:8000/api/bazi/chart \
  -H "Content-Type: application/json" \
  -d @tests/fixtures/sample_request.json

# 报告生成接口
curl -X POST http://127.0.0.1:8000/api/bazi/report \
  -H "Content-Type: application/json" \
  -d @tests/fixtures/sample_request.json
```

## 技术架构

### 后端结构（Python + FastAPI）

- **src/engine/bazi_engine.py** - 核心排盘引擎，使用 sxtwl 库计算四柱、藏干、大运等，支持阳历/农历转换、真太阳时校正
- **src/rules/analysis.py** - 规则层，基于五行计数计算身强弱、用忌神、标签，采用简化逻辑便于后续扩展
- **src/knowledge/base.py** - 知识模板检索，根据 pattern_tags、用忌神、focus 检索相关知识供 LLM 参考
- **src/prompt/report_prompt.py** - 构建 LLM Prompt，明确禁止模型重算八字或自创格局
- **src/llm/** - LLM 调用层，当前支持 Ollama 客户端（deepseek-r1:8b 等）
- **src/api/server.py** - FastAPI 路由，提供排盘、报告生成、聊天等接口
- **src/api/schemas.py** - API 请求/响应的 Pydantic 模型定义
- **src/models/** - 核心数据模型（Chart、Analysis、Knowledge 等）

### 前端结构（Vue3 + Vite + TypeScript）

- **src/web/src/App.vue** - 根组件
- **src/web/src/components/** - Vue 组件：
  - ChartPanel.vue - 命盘展示面板
  - ChatPanel.vue - 对话组件
  - MasterChat.vue - 喵大师通用聊天（无需命盘）
  - PillarPicker.vue - 四柱选择器
  - RegionPicker.vue - 地区选择器
- **src/web/vite.config.ts** - Vite 配置，已配置 `/api` 代理到 `http://127.0.0.1:8000`

### 关键设计原则

1. **职责分离**：排盘引擎（engine）只负责确定性计算，不做任何解读；规则层（rules）提供标签和用忌神；LLM 只负责生成解释文案
2. **上下文一致性**：每轮对话都携带同一份 `chart` 和 `analysis`，避免模型"记忆漂移"
3. **Prompt 约束**：明确禁止 LLM 重算八字、修改四柱、自创格局
4. **流式输出**：报告和聊天接口支持流式返回（/stream 端点），前端可实现打字机效果
5. **真太阳时支持**：engine 支持基于经纬度的真太阳时校正（src/engine/true_solar_time.py）

## API 接口说明

- `POST /api/bazi/chart` - 排盘：输入 BaziInput（支持阳历/农历/闰月），返回 Chart
- `POST /api/bazi/report` - 生成报告：可传入已排盘 chart 或直接传日期信息，返回完整报告
- `POST /api/bazi/report/stream` - 流式生成报告（NDJSON 格式）
- `POST /api/bazi/chat` - 命盘聊天：基于已有 chart/analysis 进行对话
- `POST /api/bazi/chat/stream` - 流式聊天
- `POST /api/bazi/general-chat/stream` - 通用聊天（无需命盘），用于喵大师等场景
- `POST /api/bazi/find-dates-by-pillars` - 根据四柱八字反查可能的日期范围
- `GET /api/ollama/test` - 测试 Ollama 连接

## 开发注意事项

### Python 环境
- **运行 Python 命令时请确保 conda 环境 `langchain` 已激活**
- 项目依赖 `sxtwl` 库（需要 swig 支持），macOS 用户需先 `brew install swig`

### 前后端协作
- 前端开发端口 5173，Vite 已配置 `/api` 请求代理到后端 `http://127.0.0.1:8000`
- 前端请求 `fetch("/api/bazi/report")` 会自动转发到后端

### 代码风格
- Python 使用 Black 格式化（4 空格缩进）和 Ruff 静态检查
- 前端使用 TypeScript，尽量添加类型注解
- **关键业务逻辑和语法处需添加中文注释**（维护者对前端不熟悉）

### 核心数据流

1. **排盘流程**：用户输入 → 农历/阳历转换（如需） → 真太阳时校正 → sxtwl 计算四柱/藏干/大运 → 返回 Chart
2. **报告生成**：Chart → 规则层分析（身强弱/用忌神） → 知识检索 → 构建 Prompt → LLM 生成 → 返回报告
3. **对话流程**：携带同一 Chart/Analysis + 历史消息 → Prompt 约束 → LLM 回复

### 扩展方向（TODO）

- 完善真太阳时、早晚子时、地理位置校正
- 增强规则层：月令权重、透干、合冲刑穿、格局判定、调候用神
- 接入向量检索替换模板知识库
- 添加回归测试用例验证排盘准确性

## 项目特性

- **MVP 项目**：以简单高效方式实现功能，后期可能小改
- **单人维护**：代码可随意修改，不需严格遵循现有框架，以功能正常为准
- **中文优先**：尽可能使用中文回复和注释
- **保持整洁**：代码和仓库需保持整洁
