# 神机喵算（BaziMiao）总体方案

结合《AI算命WebApp实现方案.md》的建议，对现有骨架进行补全，形成可落地的一体化方案：产品流程、系统架构、数据结构、Prompt/LLM 流程、接口、前端与安全要求。

## 产品与交互
- 首页：产品名 + Slogan + CTA「开始占测」。
- 表单：姓名(可选)、性别、出生日期、公历时间、时区/城市、阳历/农历/闰月选项、「时间不清楚」兜底。
- 流程：提交→排盘/规则→LLM 生成报告→分章节展示→下方持续聊天。
- 报告结构：总体气质、事业/财富、情感婚恋、健康与生活、未来 3–5 年趋势、小结/建议、免责声明。
- 聊天：复用同一命盘 JSON，不重算，支持追问（创业/换工作/情感等）。

## 系统架构
- 前端（Vue3 + Vite + TS + Tailwind）：Landing、表单页、报告页、聊天组件；流式显示。
- 后端（FastAPI）：`engine` 排盘、`rules` 规则层、`knowledge` 检索、`prompt` 构造、`api` 路由、`llm` 调用（待接入）。
- LLM 层：OpenAI/本地模型，Function Calling/结构化输出；禁止模型重算命盘。
- 存储（MVP 可选）：日志、调用统计、命盘缓存；后续可接入 Redis/DB。

## 核心数据结构
- 输入 `BaziInput`（待放入 `src/models/input.py`）：name/gender/year/month/day/hour/calendar/is_leap_month/timezone。
- 命盘 `Chart`（现有 `src/models/chart.py`）：四柱、藏干、日主、五行计数、大运、起运日期。
- 规则输出 `Analysis`（现有 `src/models/analysis.py`）：身强弱/分值、用忌、标签、风险点、大运提示。
- 知识库 `KnowledgeChunk`（现有 `src/models/knowledge.py`）：来源/主题/摘要，检索基于 pattern_tags + 用忌 + focus。
- 报告 `Report`（待放入 `src/models/report.py`）：overall_tone、sections[{title,content}]、facts_ref。
- 对话 `ChatMessage`（待放入 `src/models/chat.py`）：role/content；请求附带 chart+analysis。

## 排盘与规则层
- 排盘：`src/engine/bazi_engine.py` 使用 sxtwl 计算四柱/大运；需补强真太阳时、早晚子时、时区地理偏移（TODO）。
- 规则层：`src/rules/analysis.py` 现为简版强弱/用忌/标签；后续扩展：月令权重、透干、合冲刑穿、格局判定、调候用神。
- 质量控制：离线回归用固定命盘 + 标准标签；大运/流年对齐校验。

## Prompt 与生成流程
- 阶段 1 报告：系统指令限制「不重算、不自创格局」，提供 chart+analysis+knowledge+focus，要求章节化 JSON 输出（facts_ref/interpretation/advice）。
- 阶段 2 对话：每轮携带同一 chart/analysis，附上对话历史摘要；回答需引用事实，避免自相矛盾。
- 安全：拒绝医疗/赌博/违法/确定性预测；语气温和、不恐吓。

## API 设计（FastAPI）
- `POST /api/bazi/chart`：入参 BaziInput（支持阳历/农历 + 闰月）；返回 chart，用于前端展示命盘。
- `POST /api/bazi/report`：可直接使用 BaziInput 生成报告，或传入已排盘 chart（推荐）；流程=规则→知识→Prompt→LLM（当前 `_fake_llm_generate` 占位）。
- `POST /api/bazi/chat`：入参 chart+analysis+history+focus；Prompt 约束复用同一命盘；出参 reply。
- 跨域：MVP 可全开，后续收紧。
- 入参模型当前定义在 `src/api/schemas.py`，可逐步与 `src/models` 对齐。

## 前端模块
- `BaziForm.vue`：收集信息，处理「时间不清楚」为默认时辰；校验时区。
- `ReportView.vue`：命盘摘要卡片（四柱、日主、身强弱、用忌）；章节化报告。
- `BaziChat.vue`：维持 messages，调用 `/api/bazi/chat`，打字机/流式效果；预设追问按钮。
- 视觉：主色可选温暖金/墨绿；字体选择「LXGW」或思源/衬线；保留品牌「神机喵算 / BaziMiao」。

## 安全与合规
- 页面与响应附声明：「仅供娱乐与自我反思，不构成医疗/法律/投资建议」。
- 模型指令拒绝极端话题（死亡、绝症、违法）。
- 隐私：不长期存储个人信息；如需日志可脱敏。

## 迭代路线
- Week1：完善排盘（真太阳时/子时）、规则回归。
- Week2：接入真实 LLM + 报告 Prompt 调优，增加向量检索替换模板。
- Week3：前端 MVP 闭环、流式输出。
- Week4：聊天强化、回归测试、缓存/监控接入。
