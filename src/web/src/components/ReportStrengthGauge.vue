<template>
  <div class="flex flex-col gap-3">
    <div class="flex flex-wrap items-center gap-2 text-xs text-[var(--muted)]">
      <span class="rounded-full border border-white/10 bg-white/5 px-2 py-0.5">身强弱指数</span>
      <span class="text-[var(--accent-2)] font-semibold">{{ scoreLabel }}</span>
      <span class="text-[var(--accent-2)] font-semibold">{{ scoreText }}</span>
      <span v-if="confidenceText" class="text-[10px] text-white/40">可信度 {{ confidenceText }}</span>
    </div>

    <div class="relative">
      <div class="h-2 w-full rounded-full bg-white/10"></div>
      <div
        class="absolute left-0 top-0 h-2 rounded-full bg-gradient-to-r from-[rgba(92,184,92,0.55)] to-[rgba(214,160,96,0.9)]"
        :style="{ width: `${clampedScore}%` }"
      ></div>
      <div
        class="absolute top-1/2 h-3.5 w-3.5 -translate-y-1/2 rounded-full border border-black/40 bg-[var(--accent-2)] shadow-[0_0_8px_rgba(214,160,96,0.6)]"
        :style="{ left: markerLeft }"
      ></div>
    </div>

    <div class="flex items-center justify-between text-[10px] text-white/40">
      <span>偏弱</span>
      <span>中和</span>
      <span>偏强</span>
    </div>

    <div v-if="notesText" class="rounded-lg border border-white/5 bg-white/5 px-2 py-1 text-[10px] leading-relaxed text-[var(--muted)]">
      {{ notesText }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps<{
  score: number | null;
  label?: string;
  confidence?: number | null;
  notes?: string[];
}>();

const clampScore = (value: number) => Math.max(0, Math.min(100, value));

const scoreValue = computed(() => {
  if (props.score === null || props.score === undefined) return null;
  const num = Number(props.score);
  return Number.isFinite(num) ? clampScore(num) : null;
});

const clampedScore = computed(() => scoreValue.value ?? 0);

const scoreText = computed(() => (scoreValue.value === null ? '暂无' : `${Math.round(scoreValue.value)}`));

const scoreLabel = computed(() => props.label || '身强/身弱');

const confidenceText = computed(() => {
  if (props.confidence === null || props.confidence === undefined) return '';
  const num = Number(props.confidence);
  if (!Number.isFinite(num)) return '';
  const ratio = num <= 1 ? num * 100 : num;
  return `${Math.round(ratio)}%`;
});

const markerLeft = computed(() => {
  if (scoreValue.value === null) return '0%';
  const offset = clampedScore.value <= 0 ? 0 : 7;
  return `calc(${clampedScore.value}% - ${offset}px)`;
});

const notesText = computed(() => (props.notes && props.notes.length ? props.notes.join('；') : ''));
</script>
