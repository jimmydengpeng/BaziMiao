<template>
  <div class="grid gap-3">
    <ReportTalentRadar
      v-if="sectionId === 'talent_radar' && radarDimensions(structured)"
      :dimensions="radarDimensions(structured)!"
    />
    <ReportStrengthGauge
      v-if="sectionId === 'chart_basic' && strengthGauge(structured)"
      v-bind="strengthGauge(structured)!"
    />
    <ReportTrendLine
      v-if="sectionId === 'recent_trend' && trendLines(structured)"
      v-bind="trendLines(structured)!"
    />
    <ReportWealthSources
      v-if="sectionId === 'wealth_career' && wealthSources(structured)"
      :sources="wealthSources(structured)!"
    />
    <ReportActionPriorities
      v-if="sectionId === 'summary' && actionPriorities(structured)"
      :items="actionPriorities(structured)!"
    />
    <div
      class="markdown-body report-section-content text-xs leading-relaxed break-words"
      :class="compact ? 'max-h-[7.5rem] overflow-hidden' : ''"
      v-html="renderMarkdown(contentMd)"
    ></div>
  </div>
</template>

<script setup lang="ts">
import ReportTalentRadar from './ReportTalentRadar.vue';
import ReportStrengthGauge from './ReportStrengthGauge.vue';
import ReportTrendLine from './ReportTrendLine.vue';
import ReportWealthSources from './ReportWealthSources.vue';
import ReportActionPriorities from './ReportActionPriorities.vue';
import { renderMarkdown } from '../utils/markdown';

withDefaults(defineProps<{
  sectionId?: string;
  contentMd: string;
  structured?: unknown;
  compact?: boolean;
}>(), {
  sectionId: undefined,
  structured: undefined,
  compact: false,
});

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
</script>
