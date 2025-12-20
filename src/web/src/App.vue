<template>
  <div class="app-shell stack">
    <section class="hero">
      <div class="hero-content">
        <div class="logo-placeholder logo-image" :style="{ transform: `scale(${logoScale})` }">
          <img :src="logoUrl" alt="神机喵算 Logo" />
        </div>
        <h1>神机喵算</h1>
        <p class="subtitle">用 AI 读懂八字，看到趋势与选择</p>
        <button class="btn primary hero-btn" @click="revealForm">我们开始吧</button>
      </div>
    </section>

    <section class="panel stack" ref="formBlock" v-if="showForm">
      <div class="status-line">
        <strong>填写生辰</strong>
        <span class="muted">仅用于排盘，不会长期存储</span>
      </div>
      <div class="birth-grid">
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
          {{ loading ? "生成中..." : "生成报告" }}
        </button>
        <span class="muted" v-if="error">{{ error }}</span>
      </div>
    </section>

    <section class="report-layout" :class="{ 'report-grid': hasReport }" v-if="showForm">
      <div class="panel stack">
        <div class="status-line">
          <strong>命理报告</strong>
          <span class="badge">LLM 解释器</span>
        </div>
        <div v-if="!report" class="muted">生成报告后，将在此处展示详细解读。</div>
        <div v-else class="sections">
          <div class="section-card" v-for="(sec, idx) in report.sections" :key="idx">
            <h3>{{ sec.title }}</h3>
            <div>{{ sec.content }}</div>
          </div>
        </div>
      </div>
      <ChatPanel v-if="hasReport" :chart="chart" :analysis="analysis" :focus="focus" />
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from "vue";
import ChatPanel from "./components/ChatPanel.vue";
import type { Analysis, Chart, Report, ReportResponse } from "./types";
import logoUrl from "./assets/logo-bazi_meow.png";

const formBlock = ref<HTMLElement | null>(null);
const showForm = ref(false);
const form = ref({
  year: 1992,
  month: 8,
  day: 25,
  hour: 8,
  gender: "male"
});
const focus = ref<string[]>([]);
const loading = ref(false);
const error = ref("");
const chart = ref<Chart | null>(null);
const analysis = ref<Analysis | null>(null);
const report = ref<Report | null>(null);
const logoScale = ref(1);

const hasReport = computed(() => !!report.value);
const nowYear = new Date().getFullYear();
const years = Array.from({ length: nowYear - 1940 + 1 }, (_, idx) => nowYear - idx);
const months = Array.from({ length: 12 }, (_, idx) => idx + 1);
const hours = Array.from({ length: 24 }, (_, idx) => idx);
const days = computed(() => {
  const lastDay = new Date(form.value.year, form.value.month, 0).getDate();
  return Array.from({ length: lastDay }, (_, idx) => idx + 1);
});

const birthIso = computed(() => {
  const pad = (value: number) => String(value).padStart(2, "0");
  return `${form.value.year}-${pad(form.value.month)}-${pad(form.value.day)}T${pad(
    form.value.hour
  )}:00`;
});

const revealForm = async () => {
  showForm.value = true;
  await nextTick();
  formBlock.value?.scrollIntoView({ behavior: "smooth" });
};

const updateScrollState = () => {
  const maxShrinkPx = 220;
  const minScale = 0.65;
  const progress = Math.min(Math.max(window.scrollY / maxShrinkPx, 0), 1);
  logoScale.value = 1 - progress * (1 - minScale);
};

watch([() => form.value.year, () => form.value.month], () => {
  const lastDay = new Date(form.value.year, form.value.month, 0).getDate();
  if (form.value.day > lastDay) {
    form.value.day = lastDay;
  }
});

onMounted(() => {
  updateScrollState();
  window.addEventListener("scroll", updateScrollState, { passive: true });
});

onUnmounted(() => {
  window.removeEventListener("scroll", updateScrollState);
});

const submit = async () => {
  error.value = "";
  if (!birthIso.value) {
    error.value = "请填写出生日期时间";
    return;
  }
  loading.value = true;
  report.value = null;
  try {
    const res = await fetch("/api/bazi/report", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: "匿名",
        gender: form.value.gender,
        birth: birthIso.value,
        tz_offset_hours: 8,
        focus: focus.value
      })
    });
    if (!res.ok) throw new Error(await res.text());
    const data = (await res.json()) as ReportResponse;
    chart.value = data.chart;
    analysis.value = data.analysis;
    report.value = data.report;
  } catch (err) {
    error.value = err instanceof Error ? err.message : String(err);
  } finally {
    loading.value = false;
  }
};
</script>
