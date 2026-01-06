<template>
  <div class="flex flex-col gap-3">
    <div class="panel-card flex flex-col gap-4">
      <div class="flex items-center gap-2 text-sm">
        <strong class="text-white">命理报告</strong>
        <span class="rounded-[10px] border border-[rgba(255,255,255,0.08)] bg-[rgba(255,255,255,0.04)] px-2 py-1 text-xs text-[var(--muted)]">LLM 解释器</span>
      </div>

      <!-- AI 智能解析 CTA -->
      <div class="panel-tile flex flex-col gap-3">
        <div class="flex items-center gap-2 text-sm">
          <strong class="text-white">AI智能解析</strong>
          <span class="text-[var(--muted)] text-sm">基于当前命盘生成详细报告</span>
        </div>
        <div class="grid grid-cols-[repeat(auto-fit,minmax(200px,1fr))] items-center gap-3">
          <button
            class="btn-primary col-span-1 min-h-[48px] w-full text-base"
            type="button"
            :disabled="!chart || reportLoading || reportStreaming"
            @click="generateReport"
          >
            {{ reportLoading || reportStreaming ? '解析中...' : 'AI智能解析' }}
          </button>
          <span v-if="error" class="col-span-1 text-sm text-[var(--muted)]">{{ error }}</span>
          <span v-else-if="!chart" class="col-span-1 text-sm text-[var(--muted)]">
            未找到命盘数据，
            <router-link to="/bazi/form" class="text-[var(--accent)] hover:underline">去填写</router-link>
          </span>
        </div>
      </div>

      <!-- 流式生成中 -->
      <div v-if="reportStreaming" class="grid gap-3">
        <div v-if="reportThinking" class="panel-tile border-dashed border-[rgba(255,255,255,0.08)] bg-[rgba(214,160,96,0.08)]">
          <div class="mb-2 flex items-center justify-between gap-3">
            <h3 class="text-sm font-semibold text-[var(--accent)]">模型思考</h3>
          </div>
          <div class="whitespace-pre-wrap break-words text-[11px] leading-relaxed text-[var(--muted)]">
            {{ reportThinking }}
          </div>
        </div>
        <div class="panel-tile">
          <h3 class="mb-2 text-sm font-semibold text-[var(--accent)]">生成中...</h3>
          <div class="whitespace-pre-wrap break-words text-xs leading-relaxed">
            {{ reportDraft || '正在生成，请稍候...' }}
          </div>
        </div>
      </div>

      <!-- 报告已生成 -->
      <div v-else-if="report" class="grid gap-4">
        <div v-if="reportThinking" class="panel-tile border-dashed border-[rgba(255,255,255,0.08)] bg-[rgba(214,160,96,0.08)]">
          <div class="mb-2 flex items-center justify-between gap-3">
            <h3 class="text-sm font-semibold text-[var(--accent)]">模型思考</h3>
            <button
              class="btn-ghost rounded-full px-2.5 py-1 text-xs"
              type="button"
              @click="reportThinkingCollapsed = !reportThinkingCollapsed"
            >
              {{ reportThinkingCollapsed ? '展开' : '收起' }}
            </button>
          </div>
          <div v-if="!reportThinkingCollapsed" class="whitespace-pre-wrap break-words text-[11px] leading-relaxed text-[var(--muted)]">
            {{ reportThinking }}
          </div>
        </div>

        <div v-if="report.energy_chart" class="panel-tile">
          <h3 class="mb-2 text-sm font-semibold text-[var(--accent)]">五行能量图</h3>
          <pre class="m-0 rounded-lg border border-dashed border-[rgba(255,255,255,0.08)] bg-[rgba(15,20,33,0.6)] p-3 font-mono text-[11px] leading-relaxed text-[var(--text)] whitespace-pre overflow-x-auto max-w-full">{{ report.energy_chart }}</pre>
        </div>

        <div class="grid gap-3">
          <div class="panel-tile break-words" v-for="(sec, idx) in report.sections" :key="idx">
            <h3 class="mb-2 text-sm font-semibold text-[var(--accent)]">{{ sec.title }}</h3>
            <div class="markdown-body text-xs leading-relaxed break-words" v-html="renderMarkdown(sec.content)"></div>
          </div>
        </div>
      </div>

      <!-- 未生成报告 -->
      <div v-else class="text-sm text-[var(--muted)]">
        <template v-if="chart">
          点击上方 AI 智能解析按钮生成报告。
        </template>
        <template v-else>
          未找到命盘数据，
          <router-link :to="`/bazi/chart/${chartId}/pillars`" class="text-[var(--accent)] hover:underline">
            去填写后再生成报告
          </router-link>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useStore } from '../composables/useStore';
import type { ReportStreamEvent, ReportResponse } from '../types';

const route = useRoute();
const router = useRouter();
const { chart, analysis, report } = useStore();

const chartId = computed(() => route.params.id as string);
const error = ref('');
const reportLoading = ref(false);
const reportStreaming = ref(false);
const reportDraft = ref('');
const reportThinking = ref('');
const reportThinkingCollapsed = ref(false);

// 生成报告
const generateReport = async () => {
  if (!chart.value) {
    error.value = '暂无命盘数据，请先填写生辰信息';
    return;
  }
  if (reportStreaming.value || reportLoading.value) return;

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

    // 确保处于报告页
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
    error.value = streamErr instanceof Error ? streamErr.message : '生成报告失败';
    try {
      await fetchReportOnce();
      error.value = '';
    } catch (fallbackErr) {
      error.value = fallbackErr instanceof Error ? fallbackErr.message : '生成报告失败';
    }
  } finally {
    reportLoading.value = false;
  }
};

// 监听 report 变化，更新本地状态
watch(report, (newReport) => {
  if (newReport) {
    reportStreaming.value = false;
    reportDraft.value = '';
    reportLoading.value = false;
    error.value = '';
  }
}, { immediate: true });

// Markdown 渲染函数
const renderMarkdown = (text: string) => {
  if (!text) return '';

  const escape = (value: string) =>
    value.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

  const inline = (value: string) =>
    value
      .replace(/`([^`]+)`/g, '<code>$1</code>')
      .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
      .replace(/\*([^*]+)\*/g, '<em>$1</em>');

  const lines = escape(text).split(/\r?\n/);
  let html = '';
  let listType: 'ul' | 'ol' | null = null;

  const closeList = () => {
    if (listType) {
      html += `</${listType}>`;
      listType = null;
    }
  };

  const openList = (type: 'ul' | 'ol') => {
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
      html += '<br>';
      continue;
    }

    const unorderedMatch = /^\s*[-*]\s+(.+)$/.exec(rawLine);
    if (unorderedMatch) {
      openList('ul');
      html += `<li>${inline(unorderedMatch[1].trim())}</li>`;
      continue;
    }

    const orderedMatch = /^\s*\d+\.\s+(.+)$/.exec(rawLine);
    if (orderedMatch) {
      openList('ol');
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
</script>
