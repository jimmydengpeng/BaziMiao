<template>
  <div
    class="app-shell"
    :class="{
      'landing-layout': stage === 'landing',
      'main-layout': stage === 'detail' || stage === 'archive'
    }"
  >
    <section v-if="stage === 'landing'" class="hero hero-landing">
      <div class="hero-content">
        <img class="hero-title-image" :src="titleTextUrl" alt="神机喵算" />
        <p class="subtitle hero-slogan">用 AI 读懂八字，看到趋势与选择</p>
        <div class="hero-actions">
          <button class="btn primary hero-btn" type="button" @click="goToForm">我们开始吧</button>
        </div>
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
      <section v-if="formStep === 'choice'" class="form-entry panel">
        <div class="form-entry-title">选择开始方式</div>
        <p class="muted">新建会进入填写生辰页面，也可以从档案中直接选择。</p>
        <div class="form-entry-actions">
          <button class="btn primary form-action-btn" type="button" @click="startNewForm">
            新建
          </button>
          <button class="btn secondary form-action-btn" type="button" @click="goToArchive">
            从档案中选择
          </button>
        </div>
      </section>
      <section v-else class="form-shell">
        <div class="form-intro">
          <div class="status-line">
            <strong>填写生辰</strong>
            <span class="muted">仅用于排盘，不会长期存储</span>
          </div>
          <p class="muted">支持公历/农历切换，点击出生时间唤起选择器。</p>
        </div>
        <div class="form-layout">
          <div class="panel form-card stack">
            <div class="field-group">
              <label>姓名</label>
              <input v-model.trim="form.name" placeholder="请输入姓名" />
            </div>
            <div class="field-row">
              <div class="field-group">
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
              <div class="field-group calendar-row">
                <label>历法</label>
                <div class="segmented">
                  <button
                    class="segmented-btn"
                    :class="{ active: form.calendar === 'solar' }"
                    type="button"
                    @click="form.calendar = 'solar'"
                  >
                    公历
                  </button>
                  <button
                    class="segmented-btn"
                    :class="{ active: form.calendar === 'lunar' }"
                    type="button"
                    @click="form.calendar = 'lunar'"
                  >
                    农历
                  </button>
                  <button
                    class="segmented-btn"
                    :class="{ active: form.calendar === 'pillar' }"
                    type="button"
                    @click="openPillarPicker"
                  >
                    四柱
                  </button>
                </div>
              </div>
            </div>
            <div class="field-group">
              <label>出生时间（必填）</label>
              <button class="date-display" type="button" @click="pickerOpen = !pickerOpen">
                <span>{{ displayDate }}</span>
                <span v-if="!pickerOpen" class="chevron">&gt;</span>
              </button>
            </div>
            <div v-if="pickerOpen" class="picker-overlay" role="dialog" aria-modal="true">
              <div class="panel picker-card open">
                <div class="picker-head">
                  <div class="segmented">
                    <button
                      class="segmented-btn"
                      :class="{ active: form.calendar === 'solar' }"
                      type="button"
                      @click="form.calendar = 'solar'"
                    >
                      公历
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
                  <button class="btn ghost today-btn" type="button" @click="setToday">今天</button>
                </div>
                <div class="picker-grid">
                  <div class="picker-column">
                    <span class="picker-label">年</span>
                    <select v-model.number="form.year" class="picker-select">
                      <option v-for="year in years" :key="year" :value="year">{{ year }}</option>
                    </select>
                  </div>
                  <div class="picker-column">
                    <span class="picker-label">月</span>
                    <select v-model.number="form.month" class="picker-select">
                      <option v-for="month in monthOptions" :key="month.value" :value="month.value">
                        {{ month.label }}
                      </option>
                    </select>
                  </div>
                  <div class="picker-column">
                    <span class="picker-label">日</span>
                    <select v-model.number="form.day" class="picker-select">
                      <option v-for="day in days" :key="day" :value="day">{{ day }}</option>
                    </select>
                  </div>
                  <div class="picker-column">
                    <span class="picker-label">时</span>
                    <select v-model.number="form.hour" class="picker-select">
                      <option v-for="hour in hours" :key="hour" :value="hour">
                        {{ hour.toString().padStart(2, "0") }}
                      </option>
                    </select>
                  </div>
                  <div class="picker-column">
                    <span class="picker-label">分</span>
                    <select v-model.number="form.minute" class="picker-select">
                      <option v-for="minute in minutes" :key="minute" :value="minute">
                        {{ minute.toString().padStart(2, "0") }}
                      </option>
                    </select>
                  </div>
                </div>
                <div v-if="isLunar" class="field-group">
                  <label>闰月</label>
                  <label class="check">
                    <input v-model="form.isLeapMonth" type="checkbox" />
                    <span>本月为闰月</span>
                  </label>
                </div>
                <div class="picker-footer">
                  <span class="muted picker-note">选择好后点击确定收起。</span>
                  <button class="btn primary" type="button" @click="pickerOpen = false">
                    确定
                  </button>
                </div>
              </div>
            </div>
            <!-- 出生地点选择 -->
            <div class="field-group">
              <label>出生地点</label>
              <button class="date-display" type="button" @click="showRegionPicker = true">
                <span>{{ birthPlace.fullName }}</span>
                <span class="chevron">&gt;</span>
              </button>
              <span class="muted field-hint">
                选择地区后将根据经度计算真太阳时，使排盘更加精确。
              </span>
            </div>
            <div class="cta-row center">
              <button class="btn primary cta-primary" :disabled="loading" @click="submit">
                {{ loading ? "排盘中..." : "一键排盘" }}
              </button>
              <span class="muted" v-if="error">{{ error }}</span>
            </div>
          </div>
        </div>
      </section>

      <!-- 地区选择器弹窗 -->
      <RegionPicker
        v-if="showRegionPicker"
        v-model="birthPlace"
        @close="showRegionPicker = false"
      />

      <!-- 四柱输入选择器 -->
      <PillarPicker
        v-if="showPillarPicker"
        @close="showPillarPicker = false"
        @select="handlePillarSelect"
      />
    </section>

    <section v-else class="main-shell">
      <aside class="side-nav main-nav">
        <div class="brand-mini">
          <div class="logo-placeholder logo-image logo-mini">
            <img :src="logoUrl" alt="神机喵算 Logo" />
          </div>
          <div class="brand-text">
            <div class="brand-title">神机喵算</div>
            <div class="muted">命盘与报告</div>
          </div>
        </div>
        <div class="nav-section">
          <div class="nav-label">核心功能</div>
          <button
            class="nav-btn"
            type="button"
            :class="{ active: stage === 'detail' && activeTab === 'chart' }"
            @click="goToDetail('chart')"
          >
            八字命盘
          </button>
          <button
            class="nav-btn"
            type="button"
            :class="{ active: stage === 'detail' && activeTab === 'report' }"
            :disabled="!canViewReport"
            @click="goToDetail('report')"
          >
            命理报告
          </button>
          <button
            class="nav-btn"
            type="button"
            :class="{ active: stage === 'archive' }"
            @click="goToArchive"
          >
            档案列表
          </button>
        </div>
        <div class="nav-section nav-section-muted">
          <div class="nav-label">更多模块</div>
          <button class="nav-btn muted" type="button" disabled>运势测算</button>
          <button class="nav-btn muted" type="button" disabled>今日运势</button>
          <button class="nav-btn muted" type="button" disabled>命理百科</button>
        </div>
        <div class="nav-section">
          <div class="nav-label">快捷入口</div>
          <button class="nav-btn" type="button" @click="goToForm">新建排盘</button>
          <button class="nav-btn" type="button" @click="goToLanding">回到欢迎</button>
        </div>
      </aside>

      <main class="main-content">
        <section v-if="stage === 'archive'" class="archive-panel">
          <header class="archive-header">
            <div class="brand-left">
              <div>
                <div class="brand-title">档案列表</div>
                <div class="muted">已保存 {{ archives.length }} 份命盘档案</div>
              </div>
            </div>
            <div class="archive-actions">
              <button class="btn primary" type="button" @click="startNewFormFlow">
                新建档案
              </button>
            </div>
          </header>
          <div class="archive-content">
            <div class="archive-list">
              <div v-if="archives.length === 0" class="archive-empty panel">
                <h2>还没有档案</h2>
                <p class="muted">先填写姓名与生日信息，再保存到这里。</p>
                <button class="btn primary" type="button" @click="goToForm">去填写</button>
              </div>
              <button
                v-for="entry in archives"
                :key="entry.id"
                class="archive-card"
                type="button"
                :class="{ active: entry.id === activeArchiveId }"
                @click="openArchive(entry)"
              >
                <div class="archive-main">
                  <div class="archive-name">{{ entry.displayName }}</div>
                  <div class="archive-birth">{{ entry.birthLabel }}</div>
                </div>
                <div class="archive-pillars">
                  <div class="archive-pillar-row">
                    <span
                      v-for="(pillar, idx) in entry.pillars"
                      :key="`stem-${entry.id}-${idx}`"
                      :class="['archive-char', elementClass(pillar.stemElement)]"
                    >
                      {{ pillar.stem }}
                    </span>
                  </div>
                  <div class="archive-pillar-row">
                    <span
                      v-for="(pillar, idx) in entry.pillars"
                      :key="`branch-${entry.id}-${idx}`"
                      :class="['archive-char', elementClass(pillar.branchElement)]"
                    >
                      {{ pillar.branch }}
                    </span>
                  </div>
                </div>
                <div class="archive-arrow">›</div>
              </button>
            </div>
          </div>
        </section>

        <section v-else>
          <div v-if="activeTab === 'chart'" class="detail-panel">
            <ChartPanel :chart="chart" />
            <div class="panel stack">
              <div class="status-line">
                <strong>AI智能解析</strong>
                <span class="muted">基于当前命盘生成详细报告</span>
              </div>
              <div class="cta-row matrix">
                <button
                  class="btn primary ai-primary"
                  type="button"
                  :disabled="reportLoading || reportStreaming"
                  @click="generateReport"
                >
                  {{ reportLoading || reportStreaming ? "解析中..." : "AI智能解析" }}
                </button>
                <span v-if="error" class="muted cta-message">{{ error }}</span>
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
        </section>
      </main>

      <aside class="chat-column" :aria-hidden="stage === 'detail' ? !chatOpen : undefined">
        <div v-if="stage === 'detail'" class="chat-window" :class="{ open: chatOpen }">
          <ChatPanel :chart="chart" :analysis="analysis" :focus="focus" />
        </div>
        <div v-else class="archive-preview panel">
          <div class="archive-preview-title">档案提示</div>
          <p class="muted">
            选中某个档案后会进入命盘展示页，可继续生成报告或发起对话。
          </p>
          <div class="archive-tags">
            <span class="pill">四柱</span>
            <span class="pill">五行</span>
            <span class="pill">命盘</span>
          </div>
        </div>
      </aside>

      <button
        v-if="stage === 'detail'"
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
import { computed, onMounted, ref, watch } from "vue";
import ChatPanel from "./components/ChatPanel.vue";
import ChartPanel from "./components/ChartPanel.vue";
import RegionPicker from "./components/RegionPicker.vue";
import PillarPicker from "./components/PillarPicker.vue";
import type {
  Analysis,
  Chart,
  ChartResponse,
  Report,
  ReportResponse,
  ReportStreamEvent,
  MatchedDate
} from "./types";
import { getDefaultRegion, type SelectedRegion } from "./data/china-regions";
import logoUrl from "./assets/logo-bazi_meow.png";
import titleTextUrl from "./assets/title-text.png";

type ArchivePillar = {
  stem: string;
  branch: string;
  stemElement: string;
  branchElement: string;
};

type ArchiveEntry = {
  id: number;
  name: string;
  displayName: string;
  birthLabel: string;
  pillars: ArchivePillar[];
  chart: Chart;
};

const stage = ref<"landing" | "form" | "detail" | "archive">("landing");
const formStep = ref<"choice" | "edit">("choice");
const activeTab = ref<"chart" | "report">("chart");
const chatOpen = ref(false);
const form = ref({
  name: "",
  year: 2000,
  month: 1,
  day: 1,
  hour: 0,
  minute: 0,
  gender: "male",
  calendar: "solar",
  isLeapMonth: false
});
const birthPlace = ref<SelectedRegion>(getDefaultRegion());
const showRegionPicker = ref(false);
const showPillarPicker = ref(false);
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
const archives = ref<ArchiveEntry[]>([]);
const activeArchiveId = ref<number | null>(null);
const archiveCounter = ref(0);

const canChat = computed(() => !!chart.value && !!analysis.value);
const canViewReport = computed(() => reportStreaming.value || !!report.value);
const nowYear = new Date().getFullYear();
// 年份范围从 1801 到当前年份，与四柱查找范围一致
const years = Array.from({ length: nowYear - 1801 + 1 }, (_, idx) => nowYear - idx);
const hours = Array.from({ length: 24 }, (_, idx) => idx);
const minutes = Array.from({ length: 60 }, (_, idx) => idx);
const lunarMonthLabels = [
  "正月",
  "二月",
  "三月",
  "四月",
  "五月",
  "六月",
  "七月",
  "八月",
  "九月",
  "十月",
  "冬月",
  "腊月"
];
const monthOptions = computed(() =>
  Array.from({ length: 12 }, (_, idx) => {
    const value = idx + 1;
    const label =
      form.value.calendar === "lunar"
        ? lunarMonthLabels[idx]
        : `${value.toString().padStart(2, "0")}月`;
    return { value, label };
  })
);
const days = computed(() => {
  if (form.value.calendar === "lunar") {
    return Array.from({ length: 30 }, (_, idx) => idx + 1);
  }
  const lastDay = new Date(form.value.year, form.value.month, 0).getDate();
  return Array.from({ length: lastDay }, (_, idx) => idx + 1);
});

const isLunar = computed(() => form.value.calendar === "lunar");
const pickerOpen = ref(false);

const displayDate = computed(() => {
  const year = form.value.year;
  const monthLabel =
    form.value.calendar === "lunar"
      ? `${form.value.isLeapMonth ? "闰" : ""}${lunarMonthLabels[form.value.month - 1]}`
      : form.value.month.toString().padStart(2, "0");
  const day = form.value.day.toString().padStart(2, "0");
  const hour = form.value.hour.toString().padStart(2, "0");
  const minute = form.value.minute.toString().padStart(2, "0");
  return form.value.calendar === "lunar"
    ? `${year}年 ${monthLabel} ${day}日 ${hour}:${minute}`
    : `${year}-${monthLabel}-${day} ${hour}:${minute}`;
});

const updateBodyClass = (value: typeof stage.value) => {
  if (typeof document === "undefined") return;
  const classList = document.documentElement.classList;
  classList.remove("page-landing", "page-main");
  if (value === "landing") {
    classList.add("page-landing");
  } else {
    classList.add("page-main");
  }
};

const goToForm = () => {
  stage.value = "form";
  formStep.value = "choice";
  chatOpen.value = false;
};

const goToLanding = () => {
  stage.value = "landing";
  chatOpen.value = false;
};

const goToArchive = () => {
  stage.value = "archive";
  chatOpen.value = false;
};

const goToDetail = (tab: "chart" | "report" = "chart") => {
  stage.value = "detail";
  activeTab.value = tab;
  chatOpen.value = false;
  window.scrollTo({ top: 0, behavior: "smooth" });
};

const startNewForm = () => {
  formStep.value = "edit";
  window.scrollTo({ top: 0, behavior: "smooth" });
};

const startNewFormFlow = () => {
  stage.value = "form";
  formStep.value = "edit";
  chatOpen.value = false;
  window.scrollTo({ top: 0, behavior: "smooth" });
};

const openArchive = (entry: ArchiveEntry) => {
  activeArchiveId.value = entry.id;
  chart.value = entry.chart;
  analysis.value = null;
  report.value = null;
  reportDraft.value = "";
  reportStreaming.value = false;
  reportThinking.value = "";
  reportThinkingCollapsed.value = false;
  reportLoading.value = false;
  goToDetail("chart");
};

const toggleChat = () => {
  if (!canChat.value) return;
  chatOpen.value = !chatOpen.value;
};

const setToday = () => {
  const now = new Date();
  form.value.calendar = "solar";
  form.value.isLeapMonth = false;
  form.value.year = now.getFullYear();
  form.value.month = now.getMonth() + 1;
  form.value.day = now.getDate();
  form.value.hour = now.getHours();
  form.value.minute = now.getMinutes();
};

const openPillarPicker = () => {
  form.value.calendar = "pillar";
  showPillarPicker.value = true;
};

const handlePillarSelect = (date: MatchedDate) => {
  // 用户从四柱查找结果中选择了一个日期
  form.value.calendar = "solar";
  form.value.year = date.year;
  form.value.month = date.month;
  form.value.day = date.day;
  form.value.hour = date.hour;
  form.value.minute = date.minute;
  showPillarPicker.value = false;
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
    // 构建请求体，包含出生地点信息
    const requestBody: Record<string, unknown> = {
      name: form.value.name,
      gender: form.value.gender,
      year: form.value.year,
      month: form.value.month,
      day: form.value.day,
      hour: form.value.hour,
      minute: form.value.minute,
      calendar: form.value.calendar,
      is_leap_month: form.value.isLeapMonth,
      tz_offset_hours: 0,
      birth_place: birthPlace.value.fullName
    };
    // 如果选择了具体地区，传递经纬度
    if (birthPlace.value.province) {
      requestBody.longitude = birthPlace.value.lng;
      requestBody.latitude = birthPlace.value.lat;
    }
    const chartRes = await fetch("/api/bazi/chart", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(requestBody)
    });
    if (!chartRes.ok) throw new Error(await chartRes.text());
    const chartData = (await chartRes.json()) as ChartResponse;
    chart.value = chartData.chart;
    saveArchive(chartData.chart);
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

const saveArchive = (chartData: Chart) => {
  const name = form.value.name.trim();
  const displayName = name || `命主${archiveCounter.value + 1}`;
  archiveCounter.value += 1;

  const year = form.value.year;
  const month = form.value.month;
  const day = form.value.day;
  const hour = form.value.hour;
  const minute = form.value.minute;
  const minuteLabel = minute.toString().padStart(2, "0");
  const hourLabel = hour.toString().padStart(2, "0");

  const birthLabel =
    form.value.calendar === "lunar"
      ? `农历${year}年${form.value.isLeapMonth ? "闰" : ""}${
          lunarMonthLabels[month - 1]
        }${day}日 ${hourLabel}:${minuteLabel}`
      : `阳历${year}年${month}月${day}日 ${hourLabel}:${minuteLabel}`;

  const pillars = buildPillarsFromDate(year, month, day, hour);
  const entry: ArchiveEntry = {
    id: archiveCounter.value,
    name,
    displayName,
    birthLabel,
    pillars,
    chart: chartData
  };
  archives.value.unshift(entry);
  activeArchiveId.value = entry.id;
};

onMounted(() => updateBodyClass(stage.value));
watch(stage, (value) => updateBodyClass(value));

const buildPillarsFromDate = (year: number, month: number, day: number, hour: number) => {
  const stems = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"];
  const branches = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"];
  const indices = [
    { stem: year % 10, branch: year % 12 },
    { stem: (year + month) % 10, branch: (year + month) % 12 },
    { stem: (year + month + day) % 10, branch: (year + month + day) % 12 },
    { stem: (year + month + day + hour) % 10, branch: (year + month + day + hour) % 12 }
  ];

  // 临时占位：用日期生成四柱，后续接入真实排盘数据。
  return indices.map((item) => ({
    stem: stems[item.stem],
    branch: branches[item.branch],
    stemElement: elementForStem(stems[item.stem]),
    branchElement: elementForBranch(branches[item.branch])
  }));
};

const elementForStem = (stem: string) => {
  const map: Record<string, string> = {
    甲: "木",
    乙: "木",
    丙: "火",
    丁: "火",
    戊: "土",
    己: "土",
    庚: "金",
    辛: "金",
    壬: "水",
    癸: "水"
  };
  return map[stem] ?? "";
};

const elementForBranch = (branch: string) => {
  const map: Record<string, string> = {
    子: "水",
    丑: "土",
    寅: "木",
    卯: "木",
    辰: "土",
    巳: "火",
    午: "火",
    未: "土",
    申: "金",
    酉: "金",
    戌: "土",
    亥: "水"
  };
  return map[branch] ?? "";
};

const elementClass = (element: string) => {
  const map: Record<string, string> = {
    木: "element-wood",
    火: "element-fire",
    土: "element-earth",
    金: "element-metal",
    水: "element-water"
  };
  return map[element] ?? "element-neutral";
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
