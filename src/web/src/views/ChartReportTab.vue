<template>
  <div class="flex flex-col gap-3">
    <div class="report-section-card">
      <PanelHeader title="命理报告">
        <template #title>
          <div class="flex items-center gap-2 text-sm">
            <strong class="text-white">命理报告</strong>
            <span class="panel-tag">SSE 分段解锁</span>
          </div>
        </template>
        <template #actions>
          <button
            v-if="chart"
            class="flex items-center gap-1 rounded-xl border border-[var(--border)] px-3 py-1.5 text-[12px] font-medium transition-all duration-200 disabled:cursor-not-allowed disabled:opacity-60"
            :class="hasReport
              ? 'bg-[rgba(214,160,96,0.12)] text-[var(--accent-2)] hover:bg-[rgba(214,160,96,0.2)]'
              : 'bg-[rgba(255,255,255,0.04)] text-white/60 hover:bg-[rgba(255,255,255,0.08)]'"
            type="button"
            :disabled="isGenerating"
            @click="generateReport"
          >
            {{ isGenerating ? '秘算中...' : hasReport ? '再行秘算' : '神机秘算' }}
            <span
              class="icon-mask h-3 w-3 align-middle"
              :style="{ maskImage: `url(${thinkingIconUrl})`, WebkitMaskImage: `url(${thinkingIconUrl})` }"
              aria-hidden="true"
            ></span>
          </button>
          <button
            v-if="stream.isStreaming.value"
            class="btn-ghost px-3 py-1.5 text-xs"
            type="button"
            @click="cancelStream"
          >
            取消
          </button>
        </template>
      </PanelHeader>

    </div>

    <div v-if="!chart" class="report-section-card p-5 text-sm text-[var(--muted)]">
      未找到命盘数据，
      <router-link to="/bazi/form" class="text-[var(--accent)] hover:underline">去填写</router-link>
    </div>

    <!-- 未生成报告：引导卡片 -->
    <div v-else-if="!shouldShowStreamView && !report" class="report-section-card p-5 flex flex-col gap-3">
      <div class="flex items-start gap-3">
        <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-[rgba(255,255,255,0.1)] bg-white/5">
          <span
            class="icon-mask h-5 w-5 text-[var(--accent-2)]"
            :style="{ maskImage: `url(${thinkingIconUrl})`, WebkitMaskImage: `url(${thinkingIconUrl})` }"
            aria-hidden="true"
          ></span>
        </div>
        <div class="min-w-0">
          <div class="text-sm font-semibold text-white/90">神机秘算</div>
          <div class="mt-0.5 text-xs leading-relaxed text-[var(--muted)]">
            基于当前命盘生成详细报告，支持流式分段解锁，并在本地自动保存。
          </div>
        </div>
      </div>

      <button
        class="btn-primary min-h-[48px] w-full gap-2 text-base"
        type="button"
        :disabled="isGenerating"
        @click="generateReport"
      >
        {{ isGenerating ? '秘算中...' : '开始秘算' }}
        <span
          class="icon-mask h-4 w-4"
          :style="{ maskImage: `url(${thinkingIconUrl})`, WebkitMaskImage: `url(${thinkingIconUrl})` }"
          aria-hidden="true"
        ></span>
      </button>
    </div>

    <!-- 流式生成中：分段解锁 -->
    <div v-if="shouldShowStreamView" class="grid gap-3">
      <ReportSectionCard
        v-if="streamState.thinking || stream.isStreaming.value"
        title="推演过程"
        variant="accent"
      >
        <template #actions>
          <button
            v-if="!stream.isStreaming.value && streamState.thinking"
            class="btn-ghost rounded-full px-2.5 py-1 text-xs"
            type="button"
            @click="reportThinkingCollapsed = !reportThinkingCollapsed"
          >
            {{ reportThinkingCollapsed ? '展开' : '收起' }}
          </button>
        </template>

        <div v-if="stream.isStreaming.value" class="mb-2 flex items-center gap-3">
          <div class="relative">
            <div class="h-7 w-7 animate-spin rounded-full border-2 border-[rgba(255,255,255,0.14)] border-t-[var(--accent-2)]"></div>
            <img :src="sparkleIconUrl" class="absolute left-1/2 top-1/2 h-4 w-4 -translate-x-1/2 -translate-y-1/2 opacity-80" alt="" />
          </div>
          <div class="text-xs leading-relaxed text-[var(--muted)]">
            正在推演命盘要点并规划报告结构（可随时取消）。
          </div>
        </div>

        <div
          v-if="(stream.isStreaming.value || !reportThinkingCollapsed) && streamState.thinking"
          class="whitespace-pre-wrap break-words text-[11px] leading-relaxed text-[var(--muted)]"
        >
          {{ streamState.thinking }}
        </div>
      </ReportSectionCard>

      <ReportSectionCard
        v-if="mergedError"
        title="生成失败"
        variant="danger"
      >
        <template #actions>
          <button class="btn-primary px-3 py-1.5 text-xs" type="button" :disabled="isGenerating" @click="generateReport">
            重试全篇
          </button>
        </template>
        <div class="text-xs leading-relaxed text-[var(--muted)]">
          {{ mergedError }}
        </div>
      </ReportSectionCard>

      <ReportSectionCard
        v-for="item in streamSectionsPlan"
        :key="item.sectionId"
        :title="displaySectionTitle(item.sectionId, item.title)"
        :meta="sectionStatusLabel(item.sectionId)"
      >
        <div v-if="sectionById(item.sectionId).status === 'idle'" class="text-xs text-[var(--muted)]">
          <div class="flex items-center gap-2">
            <span class="h-2 w-2 rounded-full bg-white/20"></span>
            <span>等待解锁</span>
          </div>
        </div>

        <div v-else-if="sectionById(item.sectionId).status === 'generating'" class="grid gap-2">
          <div class="flex items-center gap-2 text-xs text-[var(--muted)]">
            <span class="h-3.5 w-3.5 animate-spin rounded-full border-2 border-white/15 border-t-[var(--accent-2)]"></span>
            <span>正在生成该段内容...</span>
          </div>
          <div
            v-if="sectionById(item.sectionId).contentMd"
            class="markdown-body report-section-content text-xs leading-relaxed break-words"
            v-html="renderMarkdown(sectionById(item.sectionId).contentMd)"
          ></div>
          <div class="animate-pulse space-y-2">
            <div class="h-3 w-2/3 rounded bg-white/10"></div>
            <div class="h-3 w-full rounded bg-white/10"></div>
            <div class="h-3 w-5/6 rounded bg-white/10"></div>
          </div>
        </div>

        <div v-else-if="sectionById(item.sectionId).status === 'done'" class="grid gap-3">
          <ReportTalentRadar
            v-if="item.sectionId === 'talent_radar' && radarDimensions(sectionById(item.sectionId).structured)"
            :dimensions="radarDimensions(sectionById(item.sectionId).structured)!"
          />
          <ReportStrengthGauge
            v-if="item.sectionId === 'chart_basic' && strengthGauge(sectionById(item.sectionId).structured)"
            v-bind="strengthGauge(sectionById(item.sectionId).structured)!"
          />
          <ReportTrendLine
            v-if="item.sectionId === 'recent_trend' && trendLines(sectionById(item.sectionId).structured)"
            v-bind="trendLines(sectionById(item.sectionId).structured)!"
          />
          <ReportWealthSources
            v-if="item.sectionId === 'wealth_career' && wealthSources(sectionById(item.sectionId).structured)"
            :sources="wealthSources(sectionById(item.sectionId).structured)!"
          />
          <ReportActionPriorities
            v-if="item.sectionId === 'summary' && actionPriorities(sectionById(item.sectionId).structured)"
            :items="actionPriorities(sectionById(item.sectionId).structured)!"
          />
          <div
            class="markdown-body report-section-content text-xs leading-relaxed break-words"
            v-html="renderMarkdown(sectionById(item.sectionId).contentMd)"
          ></div>
        </div>

        <div v-else class="text-xs text-[rgba(255,160,160,1)]">
          该段生成失败。
        </div>
      </ReportSectionCard>
    </div>

    <!-- 报告已生成 -->
    <div v-else-if="report" class="grid gap-3">
      <ReportSectionCard v-for="sec in finalSections" :key="sec.key" :title="displaySectionTitle(sec.id, sec.title)">
        <ReportTalentRadar
          v-if="sec.id === 'talent_radar' && radarDimensions(sec.structured)"
          :dimensions="radarDimensions(sec.structured)!"
        />
        <ReportStrengthGauge
          v-if="sec.id === 'chart_basic' && strengthGauge(sec.structured)"
          v-bind="strengthGauge(sec.structured)!"
        />
        <ReportTrendLine
          v-if="sec.id === 'recent_trend' && trendLines(sec.structured)"
          v-bind="trendLines(sec.structured)!"
        />
        <ReportWealthSources
          v-if="sec.id === 'wealth_career' && wealthSources(sec.structured)"
          :sources="wealthSources(sec.structured)!"
        />
        <ReportActionPriorities
          v-if="sec.id === 'summary' && actionPriorities(sec.structured)"
          :items="actionPriorities(sec.structured)!"
        />
        <div
          class="markdown-body report-section-content text-xs leading-relaxed break-words"
          v-html="renderMarkdown(sec.content)"
        ></div>
      </ReportSectionCard>
    </div>

    <ReportSectionCard v-if="shouldShowDebugPrompt" title="提示词（开发）" :meta="debugPromptCollapsed ? '已折叠' : '已展开'">
      <template #actions>
        <button
          class="btn-ghost rounded-full px-2.5 py-1 text-xs"
          type="button"
          @click="debugPromptCollapsed = !debugPromptCollapsed"
        >
          {{ debugPromptCollapsed ? '展开' : '收起' }}
        </button>
      </template>
      <div v-if="!debugPromptCollapsed" class="max-h-[52vh] overflow-auto rounded-xl border border-white/10 bg-black/25 p-3">
        <pre class="whitespace-pre-wrap break-words text-[11px] leading-relaxed text-white/70">{{ safeStringify(debugPrompt) }}</pre>
      </div>
      <div v-else class="text-xs text-[var(--muted)]">
        开发阶段用于排查提示词/入参，后期可隐藏或删除。
      </div>
    </ReportSectionCard>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useStore } from '../composables/useStore';
import PanelHeader from '../components/PanelHeader.vue';
import ReportSectionCard from '../components/ReportSectionCard.vue';
import ReportTalentRadar from '../components/ReportTalentRadar.vue';
import ReportStrengthGauge from '../components/ReportStrengthGauge.vue';
import ReportTrendLine from '../components/ReportTrendLine.vue';
import ReportWealthSources from '../components/ReportWealthSources.vue';
import ReportActionPriorities from '../components/ReportActionPriorities.vue';
import { useBaziReportStream } from '../composables/useBaziReportStream';
import type { BaziReportV1, LegacyReport, Report } from '../types';
import { normalizeChartForRequest } from '../utils/chart';
import thinkingIconUrl from '../assets/svg/thinking-tripple-full.svg';
import sparkleIconUrl from '../assets/sparkles.png';
import type { ArchiveReportState } from '../utils/storage';

const route = useRoute();
const router = useRouter();
const { chart, analysis, report, activeArchiveId, updateActiveArchiveReportState } = useStore();

const chartId = computed(() => route.params.id as string);
const reportThinkingCollapsed = ref(false);
const stream = useBaziReportStream();
const uiError = ref('');
const debugPromptCollapsed = ref(true);

// 开发早期用于排查模型输出/提示词；生产构建默认不显示（后期可直接删掉这块）
const ENABLE_DEBUG_PROMPT_PANEL = import.meta.env.DEV;

const streamState = stream.state;
const streamHasSections = computed(() => streamState.sectionsPlan.length > 0);
const streamSectionsPlan = computed(() => streamState.sectionsPlan);
const mergedError = computed(() => uiError.value || streamState.error || '');
const shouldShowStreamView = computed(() =>
  stream.isStreaming.value || (!!mergedError.value || (!report.value && streamHasSections.value))
);
const isGenerating = computed(() => stream.isStreaming.value);
const hasReport = computed(() => !!report.value);

const legacyRawPrompt = computed(() => {
  const value = report.value;
  if (!value) return null;
  const maybe = value as LegacyReport;
  return maybe?.raw_prompt ?? null;
});

const debugPrompt = computed(() => streamState.prompt ?? legacyRawPrompt.value ?? null);
const shouldShowDebugPrompt = computed(() => ENABLE_DEBUG_PROMPT_PANEL && !!debugPrompt.value);

const safeStringify = (value: unknown) => {
  try {
    return JSON.stringify(value, null, 2);
  } catch (err) {
    return err instanceof Error ? err.message : String(err);
  }
};

const isBaziReportV1 = (value: Report | null): value is BaziReportV1 => {
  if (!value || typeof value !== 'object') return false;
  return 'meta' in value && 'input_refs' in value && 'sections' in value;
};

const toFinalSections = (value: Report): Array<{ key: string; id?: string; title: string; content: string; structured?: unknown }> => {
  if (isBaziReportV1(value)) {
    return value.sections.map((sec) => ({
      key: sec.id,
      id: sec.id,
      title: sec.title,
      content: sec.content_md,
      structured: sec.structured,
    }));
  }
  const legacy = value as LegacyReport;
  return legacy.sections.map((sec, idx) => ({
    key: `${idx}-${sec.title}`,
    title: sec.title,
    content: sec.content,
  }));
};

const finalSections = computed(() => (report.value ? toFinalSections(report.value) : []));

const sectionById = (sectionId: string) => streamState.sections[sectionId] ?? {
  sectionId,
  title: sectionId,
  status: 'idle',
  contentMd: '',
};

const sectionStatusLabel = (sectionId: string) => {
  const status = sectionById(sectionId).status;
  if (status === 'idle') return '等待中';
  if (status === 'generating') return '生成中...';
  if (status === 'done') return '';
  return '错误';
};

const displaySectionTitle = (sectionId: string | undefined, fallbackTitle: string) => {
  if (sectionId === 'talent_radar') return '天赋特长';
  return fallbackTitle;
};

const radarDimensions = (structured: unknown): Array<{ key: string; label: string; score: number }> | null => {
  const dims = (structured as any)?.dimensions ?? (structured as any)?.structured?.dimensions;
  if (!Array.isArray(dims)) return null;
  const normalized = dims
    .filter((item) => item && typeof item === 'object')
    .map((item) => ({
      key: String((item as any).key ?? ''),
      label: String((item as any).label ?? ''),
      score: Number((item as any).score ?? 0),
    }))
    .filter((item) => item.key && item.label);
  return normalized.length ? normalized : null;
};

const getStructuredBlock = (structured: unknown, key: string) => {
  if (!structured || typeof structured !== 'object') return null;
  const raw = (structured as any)?.[key] ?? (structured as any)?.structured?.[key];
  return raw && typeof raw === 'object' ? raw : null;
};

const normalizeNotes = (value: unknown) => {
  if (!Array.isArray(value)) return [];
  return value.map((item) => String(item ?? '')).filter((item) => item);
};

const strengthGauge = (structured: unknown): {
  score: number | null;
  label?: string;
  confidence?: number | null;
  notes?: string[];
} | null => {
  const raw = getStructuredBlock(structured, 'strength_gauge');
  if (!raw) return null;
  const scoreRaw = (raw as any).score;
  const score = scoreRaw === null || scoreRaw === undefined ? null : Number(scoreRaw);
  return {
    score: Number.isFinite(score as number) ? (score as number) : null,
    label: (raw as any).label ? String((raw as any).label) : undefined,
    confidence: (raw as any).confidence ?? null,
    notes: normalizeNotes((raw as any).notes),
  };
};

const trendLines = (structured: unknown): {
  years: number[];
  series: Array<{ key: string; label: string; values: Array<number | null> }>;
  dayunContext?: string;
  notes?: string[];
} | null => {
  const raw = getStructuredBlock(structured, 'trend_lines');
  if (!raw) return null;
  const years = Array.isArray((raw as any).years)
    ? (raw as any).years.map((item: unknown) => Number(item)).filter((item: number) => Number.isFinite(item))
    : [];
  const series = Array.isArray((raw as any).series) ? (raw as any).series : [];
  const normalizedSeries = series
    .filter((item: any) => item && typeof item === 'object')
    .map((item: any) => ({
      key: String(item.key ?? ''),
      label: String(item.label ?? ''),
      values: Array.isArray(item.values)
        ? item.values.map((value: unknown) => {
          if (value === null || value === undefined) return null;
          const num = Number(value);
          return Number.isFinite(num) ? num : null;
        })
        : [],
    }))
    .filter((item: any) => item.key && item.label);
  if (!years.length || !normalizedSeries.length) return null;
  return {
    years,
    series: normalizedSeries,
    dayunContext: (raw as any).dayun_context ? String((raw as any).dayun_context) : '',
    notes: normalizeNotes((raw as any).notes),
  };
};

const wealthSources = (structured: unknown): Array<{ key: string; label: string; score: number | null; notes?: string }> | null => {
  const raw = getStructuredBlock(structured, 'wealth_sources');
  if (!Array.isArray(raw)) return null;
  const normalized = raw
    .filter((item) => item && typeof item === 'object')
    .map((item: any) => ({
      key: String(item.key ?? ''),
      label: String(item.label ?? ''),
      score: item.score === null || item.score === undefined ? null : Number(item.score),
      notes: item.notes ? String(item.notes) : '',
    }))
    .filter((item) => item.key && item.label);
  return normalized.length ? normalized : null;
};

const actionPriorities = (structured: unknown): Array<{ rank: number; title: string; score: number | null; why?: string; how?: string }> | null => {
  const raw = getStructuredBlock(structured, 'action_priorities');
  if (!Array.isArray(raw)) return null;
  const normalized = raw
    .filter((item) => item && typeof item === 'object')
    .map((item: any) => ({
      rank: Number(item.rank ?? 0),
      title: String(item.title ?? ''),
      score: item.score === null || item.score === undefined ? null : Number(item.score),
      why: item.why ? String(item.why) : '',
      how: item.how ? String(item.how) : '',
    }))
    .filter((item) => item.title);
  return normalized.length ? normalized : null;
};

// 生成报告
const generateReport = async () => {
  if (!chart.value) {
    uiError.value = '暂无命盘数据，请先填写生辰信息';
    return;
  }
  if (stream.isStreaming.value) return;

  const generationForArchiveId = activeArchiveId.value;
  const generationForChartId = chartId.value;

  uiError.value = '';
  report.value = null;
  stream.reset();

  const payload = {
    chart: normalizeChartForRequest(chart.value),
    focus: []
  };

  try {
    router.push(`/bazi/chart/${route.params.id}/report`);

    await stream.start(payload);

    // 如果用户在生成过程中切换了档案/命盘，就不要把旧结果写进当前档案里
    if (generationForArchiveId !== activeArchiveId.value || generationForChartId !== chartId.value) {
      return;
    }

    if (streamState.analysis) {
      analysis.value = streamState.analysis;
    }

    if (streamState.finalReport) {
      report.value = streamState.finalReport;
      updateActiveArchiveReportState({ updatedAt: Date.now() } satisfies Partial<ArchiveReportState>);
    } else if (!streamState.error && streamHasSections.value) {
      const legacy: LegacyReport = {
        overall_tone: '温和中肯',
        sections: streamSectionsPlan.value.map((sec) => ({
          title: sec.title,
          content: sectionById(sec.sectionId).contentMd || '',
        })),
      };
      report.value = legacy;
      updateActiveArchiveReportState({ updatedAt: Date.now() } satisfies Partial<ArchiveReportState>);
    }

    if (streamState.error) {
      uiError.value = streamState.error;
    }
  } catch (err) {
    if (err instanceof Error && err.name === 'AbortError') {
      // 用户主动取消/切换档案导致的终止：不当作错误展示
      return;
    }
    uiError.value = err instanceof Error ? err.message : '生成报告失败';
  } finally {
    // 这里不主动停止 stream：切换页面时仍应继续生成；stream.isStreaming 会自行收敛
  }
};

const cancelStream = () => {
  stream.abort();
};

// 监听 report / debug 信息变化，写回到当前档案
watch(report, (newReport) => {
  if (newReport) {
    uiError.value = '';
  }
  updateActiveArchiveReportState({ report: newReport } satisfies Partial<ArchiveReportState>);
}, { immediate: true });

watch(debugPrompt, (value) => {
  if (!value) return;
  updateActiveArchiveReportState({ debugPrompt: value } satisfies Partial<ArchiveReportState>);
});

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
