<template>
  <div class="app-shell" :class="{ 'detail-layout': stage === 'detail' }">
    <section v-if="stage === 'landing'" class="hero hero-landing">
      <div class="hero-content">
        <div class="logo-placeholder logo-image">
          <img :src="logoUrl" alt="神机喵算 Logo" />
        </div>
        <h1>神机喵算</h1>
        <p class="subtitle">用 AI 读懂八字，看到趋势与选择</p>
        <button class="btn primary hero-btn" type="button" @click="goToForm">我们开始吧</button>
      </div>
    </section>

    <section v-else-if="stage === 'form'" class="form-page stack">
      <header class="brand-bar">
        <div class="brand-left">
          <div class="logo-placeholder logo-image logo-mini">
            <img :src="logoUrl" alt="神机喵算 Logo" />
          </div>
          <div>
            <div class="brand-title">神机喵算</div>
            <div class="muted">输入生辰，生成命理报告</div>
          </div>
        </div>
      </header>
      <section class="panel stack">
        <div class="status-line">
          <strong>填写生辰</strong>
          <span class="muted">仅用于排盘，不会长期存储</span>
        </div>
        <div class="birth-grid">
          <div class="field span-two">
            <label>姓名（可选）</label>
            <input v-model.trim="form.name" placeholder="可留空" />
          </div>
          <div class="field">
            <label>历法</label>
            <div class="segmented">
              <button
                class="segmented-btn"
                :class="{ active: form.calendar === 'solar' }"
                type="button"
                @click="form.calendar = 'solar'"
              >
                阳历
              </button>
              <button
                class="segmented-btn"
                :class="{ active: form.calendar === 'lunar' }"
                type="button"
                @click="form.calendar = 'lunar'"
              >
                农历
              </button>
            </div>
          </div>
          <div class="field">
            <label>出生年份</label>
            <select v-model.number="form.year">
              <option v-for="year in years" :key="year" :value="year">{{ year }}</option>
            </select>
          </div>
          <div class="field">
            <label>月份</label>
            <select v-model.number="form.month">
              <option v-for="month in months" :key="month" :value="month">{{ month }}</option>
            </select>
          </div>
          <div class="field">
            <label>日期</label>
            <select v-model.number="form.day">
              <option v-for="day in days" :key="day" :value="day">{{ day }}</option>
            </select>
          </div>
          <div class="field">
            <label>时辰</label>
            <select v-model.number="form.hour">
              <option v-for="hour in hours" :key="hour" :value="hour">{{ hour }} 点</option>
            </select>
          </div>
          <div class="field" v-if="isLunar">
            <label>闰月</label>
            <label class="check">
              <input v-model="form.isLeapMonth" type="checkbox" />
              <span>本月为闰月</span>
            </label>
          </div>
          <div class="field">
            <label>性别</label>
            <div class="segmented">
              <button
                class="segmented-btn"
                :class="{ active: form.gender === 'male' }"
                type="button"
                @click="form.gender = 'male'"
              >
                男
              </button>
              <button
                class="segmented-btn"
                :class="{ active: form.gender === 'female' }"
                type="button"
                @click="form.gender = 'female'"
              >
                女
              </button>
            </div>
          </div>
        </div>
        <div class="cta-row">
          <button class="btn primary" :disabled="loading" @click="submit">
            {{ loading ? "排盘中..." : "一键排盘" }}
          </button>
          <span class="muted" v-if="error">{{ error }}</span>
        </div>
      </section>
    </section>

    <section v-else class="detail-shell">
      <aside class="side-nav">
        <div class="brand-mini">
          <div class="logo-placeholder logo-image logo-mini">
            <img :src="logoUrl" alt="神机喵算 Logo" />
          </div>
          <div class="brand-text">
            <div class="brand-title">神机喵算</div>
            <div class="muted">命盘与报告</div>
          </div>
        </div>
        <button class="nav-btn" type="button" @click="goToLanding">回到主页</button>
        <button
          class="nav-btn"
          type="button"
          :class="{ active: activeTab === 'chart' }"
          @click="activeTab = 'chart'"
        >
          八字命盘
        </button>
        <button
          class="nav-btn"
          type="button"
          :class="{ active: activeTab === 'report' }"
          :disabled="!canViewReport"
          @click="activeTab = 'report'"
        >
          命理报告
        </button>
      </aside>

      <main class="detail-content">
        <div v-if="activeTab === 'chart'" class="detail-panel">
          <ChartPanel :chart="chart" />
          <div class="panel stack">
            <div class="status-line">
              <strong>AI智能解析</strong>
              <span class="muted">基于当前命盘生成详细报告</span>
            </div>
            <div class="cta-row">
              <button
                class="btn primary"
                type="button"
                :disabled="reportLoading || reportStreaming"
                @click="generateReport"
              >
                {{ reportLoading || reportStreaming ? "解析中..." : "AI智能解析" }}
              </button>
              <span v-if="error" class="muted">{{ error }}</span>
            </div>
          </div>
        </div>
        <div v-else class="panel stack">
          <div class="status-line">
            <strong>命理报告</strong>
            <span class="badge">LLM 解释器</span>
          </div>
          <div v-if="error" class="muted">{{ error }}</div>
          <div v-if="reportStreaming" class="sections">
            <div v-if="reportThinking" class="section-card thinking-card">
              <div class="thinking-header">
                <h3>模型思考</h3>
              </div>
              <div class="streaming-text thinking">
                {{ reportThinking }}
              </div>
            </div>
            <div class="section-card">
              <h3>生成中...</h3>
              <div class="streaming-text">
                {{ reportDraft || "正在生成，请稍候..." }}
              </div>
            </div>
          </div>
          <div v-else-if="report" class="report-layout">
            <div v-if="reportThinking" class="section-card thinking-card">
              <div class="thinking-header">
                <h3>模型思考</h3>
                <button
                  class="btn ghost"
                  type="button"
                  @click="reportThinkingCollapsed = !reportThinkingCollapsed"
                >
                  {{ reportThinkingCollapsed ? "展开" : "收起" }}
                </button>
              </div>
              <div v-if="!reportThinkingCollapsed" class="streaming-text thinking">
                {{ reportThinking }}
              </div>
            </div>
            <div v-if="report.energy_chart" class="section-card">
              <h3>五行能量图</h3>
              <pre class="energy-chart">{{ report.energy_chart }}</pre>
            </div>
            <div class="sections">
              <div class="section-card" v-for="(sec, idx) in report.sections" :key="idx">
                <h3>{{ sec.title }}</h3>
                <div class="markdown-body" v-html="renderMarkdown(sec.content)"></div>
              </div>
            </div>
          </div>
          <div v-else class="muted">生成报告后，将在此处展示详细解读。</div>
        </div>

      </main>

      <aside class="chat-column" :aria-hidden="!chatOpen">
        <div class="chat-window" :class="{ open: chatOpen }">
          <ChatPanel :chart="chart" :analysis="analysis" :focus="focus" />
        </div>
      </aside>

      <button
        class="chat-fab"
        type="button"
        :class="{ active: chatOpen }"
        :disabled="!canChat"
        aria-label="打开聊天"
        @click="toggleChat"
      >
        聊
      </button>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
import ChatPanel from "./components/ChatPanel.vue";
import ChartPanel from "./components/ChartPanel.vue";
import type {
  Analysis,
  Chart,
  ChartResponse,
  Report,
  ReportResponse,
  ReportStreamEvent
} from "./types";
import logoUrl from "./assets/logo-bazi_meow.png";

const stage = ref<"landing" | "form" | "detail">("landing");
const activeTab = ref<"chart" | "report">("chart");
const chatOpen = ref(false);
const form = ref({
  name: "",
  year: 2000,
  month: 8,
  day: 25,
  hour: 8,
  gender: "male",
  calendar: "solar",
  isLeapMonth: false
});
const focus = ref<string[]>([]);
const loading = ref(false);
const error = ref("");
const chart = ref<Chart | null>(null);
const analysis = ref<Analysis | null>(null);
const report = ref<Report | null>(null);
const reportDraft = ref("");
const reportStreaming = ref(false);
const reportThinking = ref("");
const reportThinkingCollapsed = ref(false);
const reportLoading = ref(false);

const canChat = computed(() => !!chart.value && !!analysis.value);
const canViewReport = computed(() => reportStreaming.value || !!report.value);
const nowYear = new Date().getFullYear();
const years = Array.from({ length: nowYear - 1940 + 1 }, (_, idx) => nowYear - idx);
const months = Array.from({ length: 12 }, (_, idx) => idx + 1);
const hours = Array.from({ length: 24 }, (_, idx) => idx);
const days = computed(() => {
  if (form.value.calendar === "lunar") {
    return Array.from({ length: 30 }, (_, idx) => idx + 1);
  }
  const lastDay = new Date(form.value.year, form.value.month, 0).getDate();
  return Array.from({ length: lastDay }, (_, idx) => idx + 1);
});

const isLunar = computed(() => form.value.calendar === "lunar");

const goToForm = () => {
  stage.value = "form";
  chatOpen.value = false;
};

const goToLanding = () => {
  stage.value = "landing";
  chatOpen.value = false;
};

const goToDetail = (tab: "chart" | "report" = "chart") => {
  stage.value = "detail";
  activeTab.value = tab;
  chatOpen.value = false;
  window.scrollTo({ top: 0, behavior: "smooth" });
};

const toggleChat = () => {
  if (!canChat.value) return;
  chatOpen.value = !chatOpen.value;
};

const renderMarkdown = (text: string) => {
  if (!text) return "";
  const escape = (value: string) =>
    value.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  const inline = (value: string) =>
    value
      .replace(/`([^`]+)`/g, "<code>$1</code>")
      .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
      .replace(/\*([^*]+)\*/g, "<em>$1</em>");

  const lines = escape(text).split(/\r?\n/);
  let html = "";
  let listType: "ul" | "ol" | null = null;

  const closeList = () => {
    if (listType) {
      html += `</${listType}>`;
      listType = null;
    }
  };

  const openList = (type: "ul" | "ol") => {
    if (listType && listType !== type) {
      closeList();
    }
    if (!listType) {
      listType = type;
      html += `<${type}>`;
    }
  };

  for (const rawLine of lines) {
    const line = rawLine.trim();
    if (!line) {
      closeList();
      html += "<br>";
      continue;
    }
    const unorderedMatch = /^\s*[-*]\s+(.+)$/.exec(rawLine);
    if (unorderedMatch) {
      openList("ul");
      html += `<li>${inline(unorderedMatch[1].trim())}</li>`;
      continue;
    }
    const orderedMatch = /^\s*\d+\.\s+(.+)$/.exec(rawLine);
    if (orderedMatch) {
      openList("ol");
      html += `<li>${inline(orderedMatch[1].trim())}</li>`;
      continue;
    }
    const headingMatch = /^\s{0,3}(#{1,4})\s+(.+)$/.exec(rawLine);
    if (headingMatch) {
      closeList();
      const level = Math.min(4, headingMatch[1].length);
      html += `<h${level}>${inline(headingMatch[2].trim())}</h${level}>`;
      continue;
    }
    closeList();
    html += `<p>${inline(rawLine)}</p>`;
  }

  closeList();
  return html;
};

watch([() => form.value.year, () => form.value.month, () => form.value.calendar], () => {
  const maxDay =
    form.value.calendar === "lunar" ? 30 : new Date(form.value.year, form.value.month, 0).getDate();
  if (form.value.day > maxDay) {
    form.value.day = maxDay;
  }
});

watch(
  () => form.value.calendar,
  (value) => {
    if (value === "solar") {
      form.value.isLeapMonth = false;
    }
  }
);

const submit = async () => {
  error.value = "";
  loading.value = true;
  try {
    const chartRes = await fetch("/api/bazi/chart", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: form.value.name,
        gender: form.value.gender,
        year: form.value.year,
        month: form.value.month,
        day: form.value.day,
        hour: form.value.hour,
        minute: 0,
        calendar: form.value.calendar,
        is_leap_month: form.value.isLeapMonth,
        tz_offset_hours: 0
      })
    });
    if (!chartRes.ok) throw new Error(await chartRes.text());
    const chartData = (await chartRes.json()) as ChartResponse;
    chart.value = chartData.chart;
    analysis.value = null;
  report.value = null;
  reportDraft.value = "";
  reportStreaming.value = false;
  reportThinking.value = "";
  reportThinkingCollapsed.value = false;
  reportLoading.value = false;
  goToDetail("chart");
  } catch (err) {
    error.value = err instanceof Error ? err.message : String(err);
  } finally {
    loading.value = false;
  }
};

const generateReport = async () => {
  if (!chart.value || reportStreaming.value || reportLoading.value) return;
  error.value = "";
  reportLoading.value = true;
  report.value = null;
  reportDraft.value = "";
  reportStreaming.value = false;
  reportThinking.value = "";
  reportThinkingCollapsed.value = false;

  const payload = JSON.stringify({
    chart: chart.value,
    focus: focus.value
  });

  const streamReport = async () => {
    const reportRes = await fetch("/api/bazi/report/stream", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: payload
    });
    if (!reportRes.ok) throw new Error(await reportRes.text());
    if (!reportRes.body) throw new Error("浏览器不支持流式响应");

    reportStreaming.value = true;
    goToDetail("report");

    const reader = reportRes.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let buffer = "";
    let doneReceived = false;

    const handleLine = (line: string) => {
      const trimmed = line.trim();
      if (!trimmed) return;
      let event: ReportStreamEvent;
      try {
        event = JSON.parse(trimmed) as ReportStreamEvent;
      } catch {
        return;
      }
      if (event.type === "meta") {
        analysis.value = event.analysis;
        return;
      }
      if (event.type === "delta") {
        reportDraft.value += event.text;
        return;
      }
      if (event.type === "thinking") {
        reportThinking.value += event.text;
        return;
      }
      if (event.type === "error") {
        throw new Error(event.message || "生成报告失败");
      }
      if (event.type === "done") {
        report.value = event.report;
        if (event.analysis) analysis.value = event.analysis;
        if (event.thinking) reportThinking.value = event.thinking;
        if (reportThinking.value) reportThinkingCollapsed.value = true;
        reportDraft.value = "";
        reportStreaming.value = false;
        doneReceived = true;
      }
    };

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() ?? "";
      lines.forEach(handleLine);
    }

    buffer += decoder.decode();
    if (buffer.trim()) {
      buffer.split("\n").forEach(handleLine);
    }

    if (!doneReceived) {
      throw new Error("流式响应未返回完成事件");
    }
  };

  const fetchReportOnce = async () => {
    const reportRes = await fetch("/api/bazi/report", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: payload
    });
    if (!reportRes.ok) throw new Error(await reportRes.text());
    const data = (await reportRes.json()) as ReportResponse;
    analysis.value = data.analysis;
    report.value = data.report;
    goToDetail("report");
  };

  try {
    await streamReport();
  } catch (streamErr) {
    reportStreaming.value = false;
    reportDraft.value = "";
    reportThinking.value = "";
    reportThinkingCollapsed.value = false;
    await fetchReportOnce();
  } finally {
    reportLoading.value = false;
  }
};
</script>
