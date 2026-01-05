<template>
  <div class="flex flex-col gap-3">
    <div class="flex flex-col gap-3 rounded-2xl border border-[rgba(255,255,255,0.08)] bg-[var(--panel)] p-5 shadow-[0_12px_40px_rgba(0,0,0,0.35)]">
      <div class="flex items-center gap-2 text-sm">
        <strong class="text-white">命理报告</strong>
        <span class="rounded-[10px] border border-[rgba(255,255,255,0.08)] bg-[rgba(255,255,255,0.04)] px-2 py-1 text-xs text-[var(--muted)]">LLM 解释器</span>
      </div>

      <!-- 错误状态 -->
      <div v-if="error" class="text-sm text-[var(--muted)]">{{ error }}</div>

      <!-- 流式生成中 -->
      <div v-if="reportStreaming" class="grid gap-3">
        <div v-if="reportThinking" class="rounded-xl border border-dashed border-[rgba(255,255,255,0.08)] bg-[rgba(214,160,96,0.08)] p-4">
          <div class="mb-2 flex items-center justify-between gap-3">
            <h3 class="text-sm font-semibold text-[var(--accent)]">模型思考</h3>
          </div>
          <div class="whitespace-pre-wrap break-words text-[11px] leading-relaxed text-[var(--muted)]">
            {{ reportThinking }}
          </div>
        </div>
        <div class="rounded-xl border border-[rgba(255,255,255,0.08)] bg-[rgba(255,255,255,0.04)] p-4">
          <h3 class="mb-2 text-sm font-semibold text-[var(--accent)]">生成中...</h3>
          <div class="whitespace-pre-wrap break-words text-xs leading-relaxed">
            {{ reportDraft || '正在生成，请稍候...' }}
          </div>
        </div>
      </div>

      <!-- 报告已生成 -->
      <div v-else-if="report" class="grid gap-4">
        <div v-if="reportThinking" class="rounded-xl border border-dashed border-[rgba(255,255,255,0.08)] bg-[rgba(214,160,96,0.08)] p-4">
          <div class="mb-2 flex items-center justify-between gap-3">
            <h3 class="text-sm font-semibold text-[var(--accent)]">模型思考</h3>
            <button
              class="rounded-full border border-[rgba(255,255,255,0.08)] bg-[rgba(255,255,255,0.06)] px-2.5 py-1 text-xs text-[var(--text)] transition-all duration-200 hover:bg-[rgba(255,255,255,0.1)]"
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

        <div v-if="report.energy_chart" class="rounded-xl border border-[rgba(255,255,255,0.08)] bg-[rgba(255,255,255,0.04)] p-4">
          <h3 class="mb-2 text-sm font-semibold text-[var(--accent)]">五行能量图</h3>
          <pre class="m-0 rounded-lg border border-dashed border-[rgba(255,255,255,0.08)] bg-[rgba(15,20,33,0.6)] p-3 font-mono text-[11px] leading-relaxed text-[var(--text)] whitespace-pre overflow-x-auto max-w-full">{{ report.energy_chart }}</pre>
        </div>

        <div class="grid gap-3">
          <div class="rounded-xl border border-[rgba(255,255,255,0.08)] bg-[rgba(255,255,255,0.04)] p-4 break-words" v-for="(sec, idx) in report.sections" :key="idx">
            <h3 class="mb-2 text-sm font-semibold text-[var(--accent)]">{{ sec.title }}</h3>
            <div class="markdown-body text-xs leading-relaxed break-words" v-html="renderMarkdown(sec.content)"></div>
          </div>
        </div>
      </div>

      <!-- 未生成报告 -->
      <div v-else class="text-sm text-[var(--muted)]">
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
