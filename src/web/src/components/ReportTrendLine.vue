<template>
  <div class="flex flex-col gap-3">
    <div class="flex flex-wrap items-center justify-between gap-2 text-xs text-[var(--muted)]">
      <span class="rounded-full border border-white/10 bg-white/5 px-2 py-0.5">未来趋势折线</span>
      <span v-if="trend.dayunContext" class="text-[10px] text-white/50">{{ trend.dayunContext }}</span>
    </div>

    <div class="w-full overflow-x-auto">
      <div class="flex min-w-[320px] justify-center">
        <svg :viewBox="`0 0 ${viewWidth} ${viewHeight}`" class="h-40 w-full max-w-[360px]">
          <g class="stroke-white/10">
            <line
              v-for="(tick, idx) in gridTicks"
              :key="`grid-${idx}`"
              :x1="paddingX"
              :y1="tick"
              :x2="viewWidth - paddingX"
              :y2="tick"
              stroke-width="1"
            />
          </g>

          <g v-for="(series, idx) in trend.series" :key="series.key">
            <path
              v-if="series.path"
              :d="series.path"
              fill="none"
              :stroke="series.color"
              stroke-width="2.5"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
            <circle
              v-for="(point, pIdx) in series.points"
              :key="`${series.key}-${pIdx}`"
              :cx="point.x"
              :cy="point.y"
              r="3.5"
              :fill="series.color"
            />
          </g>

          <g class="fill-white/60 text-[10px]">
            <text
              v-for="(year, idx) in trend.years"
              :key="`year-${idx}`"
              :x="pointX(idx)"
              :y="viewHeight - 6"
              text-anchor="middle"
            >
              {{ year }}
            </text>
          </g>
        </svg>
      </div>
    </div>

    <div v-if="trend.notes.length" class="rounded-lg border border-white/5 bg-white/5 px-2 py-1 text-[10px] leading-relaxed text-[var(--muted)]">
      {{ trend.notes.join('；') }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

type TrendSeriesInput = { key: string; label: string; values: Array<number | null> };

const props = defineProps<{
  years: number[];
  series: TrendSeriesInput[];
  dayunContext?: string;
  notes?: string[];
}>();

const viewWidth = 360;
const viewHeight = 160;
const paddingX = 24;
const paddingTop = 14;
const paddingBottom = 26;
const plotHeight = viewHeight - paddingTop - paddingBottom;
const plotWidth = viewWidth - paddingX * 2;

const clampScore = (value: number) => Math.max(0, Math.min(100, value));

const normalizeScore = (value: unknown) => {
  if (value === null || value === undefined) return null;
  const num = Number(value);
  return Number.isFinite(num) ? clampScore(num) : null;
};

const normalizedYears = computed(() =>
  props.years.map((item) => Number(item)).filter((item) => Number.isFinite(item))
);

const pointX = (idx: number) => {
  const count = normalizedYears.value.length;
  const step = count > 1 ? plotWidth / (count - 1) : 0;
  return paddingX + step * idx;
};

const pointY = (score: number) => paddingTop + (1 - score / 100) * plotHeight;

const gridTicks = computed(() => {
  const levels = 4;
  const ticks: number[] = [];
  for (let i = 0; i <= levels; i += 1) {
    ticks.push(paddingTop + (plotHeight / levels) * i);
  }
  return ticks;
});

const colorPalette = ['rgba(214,160,96,0.9)', 'rgba(92,184,92,0.9)', 'rgba(90,169,255,0.9)'];

const buildPath = (values: Array<number | null>) => {
  let started = false;
  let path = '';

  values.forEach((value, idx) => {
    if (value === null) {
      started = false;
      return;
    }
    const x = pointX(idx);
    const y = pointY(value);
    if (!started) {
      path += `M ${x} ${y}`;
      started = true;
    } else {
      path += ` L ${x} ${y}`;
    }
  });

  return path;
};

const trend = computed(() => {
  const years = normalizedYears.value;
  const notes = props.notes?.filter((item) => item) ?? [];
  const series = props.series.map((item, idx) => {
    const rawValues = item.values ?? [];
    const values = years.map((_, i) => normalizeScore(rawValues[i]));
    const points = values
      .map((value, i) => (value === null ? null : { x: pointX(i), y: pointY(value) }))
      .filter((value): value is { x: number; y: number } => !!value);
    return {
      key: item.key,
      label: item.label,
      values,
      points,
      path: buildPath(values),
      color: colorPalette[idx % colorPalette.length],
    };
  });

  return {
    years,
    series,
    notes,
    dayunContext: props.dayunContext || '',
  };
});
</script>
