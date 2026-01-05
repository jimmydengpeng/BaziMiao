<template>
  <div class="chart-report-tab">
    <div class="panel stack">
      <div class="status-line">
        <strong>命理报告</strong>
        <span class="badge">LLM 解释器</span>
      </div>

      <!-- 错误状态 -->
      <div v-if="error" class="muted">{{ error }}</div>

      <!-- 流式生成中 -->
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
            {{ reportDraft || '正在生成，请稍候...' }}
          </div>
        </div>
      </div>

      <!-- 报告已生成 -->
      <div v-else-if="report" class="report-layout">
        <div v-if="reportThinking" class="section-card thinking-card">
          <div class="thinking-header">
            <h3>模型思考</h3>
            <button
              class="btn ghost"
              type="button"
              @click="reportThinkingCollapsed = !reportThinkingCollapsed"
            >
              {{ reportThinkingCollapsed ? '展开' : '收起' }}
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

      <!-- 未生成报告 -->
      <div v-else class="muted">
        生成报告后，将在此处展示详细解读。
        <router-link :to="`/bazi/chart/${chartId}/pillars`" class="text-[var(--accent)] hover:underline">
          点击返回命盘页面生成报告
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { useRoute } from 'vue-router';
import { useStore } from '../composables/useStore';

const route = useRoute();
const { report } = useStore();

const chartId = computed(() => route.params.id as string);
const error = ref('');
const reportStreaming = ref(false);
const reportDraft = ref('');
const reportThinking = ref('');
const reportThinkingCollapsed = ref(false);

// 监听 report 变化，更新本地状态
watch(report, (newReport) => {
  if (newReport) {
    reportStreaming.value = false;
    reportDraft.value = '';
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
