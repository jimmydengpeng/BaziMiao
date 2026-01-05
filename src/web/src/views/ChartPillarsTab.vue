<template>
  <div class="chart-pillars-tab">
    <div v-if="chart" class="detail-panel">
      <!-- 命盘展示 -->
      <ChartPanel :chart="chart" />

      <!-- AI 智能解析 CTA -->
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
            {{ reportLoading || reportStreaming ? '解析中...' : 'AI智能解析' }}
          </button>
          <span v-if="error" class="muted cta-message">{{ error }}</span>
        </div>
      </div>
    </div>

    <div v-else class="panel">
      <p class="muted">未找到命盘数据，请先填写生辰信息。</p>
      <button class="btn primary mt-4" type="button" @click="goToForm">
        去填写
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import ChartPanel from '../components/ChartPanel.vue';
import { useStore } from '../composables/useStore';
import type { ReportStreamEvent, ReportResponse } from '../types';

const router = useRouter();
const route = useRoute();
const { chart, analysis, report } = useStore();

const error = ref('');
const reportLoading = ref(false);
const reportStreaming = ref(false);
const reportDraft = ref('');
const reportThinking = ref('');

// 生成报告
const generateReport = async () => {
  if (!chart.value || reportStreaming.value || reportLoading.value) return;

  error.value = '';
  reportLoading.value = true;
  report.value = null;
  reportDraft.value = '';
  reportStreaming.value = false;
  reportThinking.value = '';

  const payload = JSON.stringify({
    chart: chart.value,
    focus: []
  });

  const streamReport = async () => {
    const reportRes = await fetch('/api/bazi/report/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: payload
    });

    if (!reportRes.ok) throw new Error(await reportRes.text());
    if (!reportRes.body) throw new Error('浏览器不支持流式响应');

    reportStreaming.value = true;

    // 跳转到报告 Tab
    router.push(`/bazi/chart/${route.params.id}/report`);

    const reader = reportRes.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let buffer = '';
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

      if (event.type === 'meta') {
        analysis.value = event.analysis;
        return;
      }
      if (event.type === 'delta') {
        reportDraft.value += event.text;
        return;
      }
      if (event.type === 'thinking') {
        reportThinking.value += event.text;
        return;
      }
      if (event.type === 'error') {
        throw new Error(event.message || '生成报告失败');
      }
      if (event.type === 'done') {
        report.value = event.report;
        if (event.analysis) analysis.value = event.analysis;
        if (event.thinking) reportThinking.value = event.thinking;
        reportDraft.value = '';
        reportStreaming.value = false;
        doneReceived = true;
      }
    };

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() ?? '';
      lines.forEach(handleLine);
    }

    buffer += decoder.decode();
    if (buffer.trim()) {
      buffer.split('\n').forEach(handleLine);
    }

    if (!doneReceived) {
      throw new Error('流式响应未返回完成事件');
    }
  };

  const fetchReportOnce = async () => {
    const reportRes = await fetch('/api/bazi/report', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: payload
    });
    if (!reportRes.ok) throw new Error(await reportRes.text());
    const data = (await reportRes.json()) as ReportResponse;
    analysis.value = data.analysis;
    report.value = data.report;
    router.push(`/bazi/chart/${route.params.id}/report`);
  };

  try {
    await streamReport();
  } catch (streamErr) {
    reportStreaming.value = false;
    reportDraft.value = '';
    reportThinking.value = '';
    await fetchReportOnce();
  } finally {
    reportLoading.value = false;
  }
};

const goToForm = () => {
  router.push('/bazi/form');
};
</script>
