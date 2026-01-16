<template>
  <div class="flex flex-col gap-3">
    <div class="flex flex-col items-start justify-between gap-2 sm:flex-row sm:items-center">
      <div class="text-xs text-[var(--muted)]">
        分数范围 0-100，仅用于相对强弱对比。
      </div>
      <div class="flex flex-wrap gap-2">
        <span
          v-for="dim in dimensions"
          :key="dim.key"
          class="rounded-full border border-[rgba(255,255,255,0.08)] bg-[rgba(255,255,255,0.04)] px-2 py-1 text-[11px] text-[var(--muted)]"
        >
          <span class="text-[var(--accent-2)]">{{ dim.label }}</span>
          <span class="ml-1">{{ dim.score }}</span>
        </span>
      </div>
    </div>

    <div class="w-full overflow-x-auto">
      <div class="flex justify-center">
        <svg
          class="w-full max-w-[260px] min-w-[260px] lg:max-w-[300px]"
          viewBox="0 0 400 400"
          role="img"
          aria-label="天赋特长雷达图"
        >
        <g class="radar-grid">
          <polygon
            v-for="level in levels"
            :key="level"
            :points="gridPoints(level)"
          />
          <line
            v-for="(axis, idx) in axes"
            :key="idx"
            :x1="center"
            :y1="center"
            :x2="axis.x"
            :y2="axis.y"
          />
        </g>

        <polygon
          class="radar-shape-muted"
          :points="gridPoints(levels.length)"
        />

        <polygon
          class="radar-shape"
          :points="shapePoints"
        />

        <g class="radar-dots">
          <circle
            v-for="(pt, idx) in shapeDots"
            :key="idx"
            class="radar-dot text-[var(--accent-2)]"
            :cx="pt.x"
            :cy="pt.y"
            r="7"
          />
        </g>

        <g class="radar-labels">
          <text
            v-for="(axis, idx) in axes"
            :key="idx"
            class="radar-label text-white/75"
            :x="axis.labelX"
            :y="axis.labelY"
            text-anchor="middle"
            dominant-baseline="middle"
          >
            {{ axis.label }}
          </text>
        </g>
        </svg>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

type Dimension = { key: string; label: string; score: number };

const props = defineProps<{
  dimensions: Dimension[];
}>();

const size = 400;
const center = size / 2;
const radius = 150;
const levels = [1, 2, 3, 4, 5];
const startAngle = -Math.PI / 2;

const axes = computed(() => {
  const n = Math.max(props.dimensions.length, 1);
  const step = (Math.PI * 2) / n;
  const labelOffset = 28;

  return props.dimensions.map((dim, idx) => {
    const angle = startAngle + step * idx;
    const x = center + radius * Math.cos(angle);
    const y = center + radius * Math.sin(angle);
    return {
      key: dim.key,
      label: dim.label,
      x,
      y,
      labelX: center + (radius + labelOffset) * Math.cos(angle),
      labelY: center + (radius + labelOffset) * Math.sin(angle),
      angle,
    };
  });
});

const clampScore = (score: number) => {
  if (!Number.isFinite(score)) return 0;
  return Math.max(0, Math.min(100, score));
};

const gridPoints = (level: number) => {
  const n = Math.max(props.dimensions.length, 1);
  const step = (Math.PI * 2) / n;
  const scale = level / levels.length;
  const pts: string[] = [];
  for (let i = 0; i < n; i += 1) {
    const angle = startAngle + step * i;
    const x = center + radius * scale * Math.cos(angle);
    const y = center + radius * scale * Math.sin(angle);
    pts.push(`${x.toFixed(1)},${y.toFixed(1)}`);
  }
  return pts.join(" ");
};

const shapeDots = computed(() => {
  if (!props.dimensions.length) return [];
  return props.dimensions.map((dim, idx) => {
    const axis = axes.value[idx];
    const ratio = clampScore(dim.score) / 100;
    const x = center + radius * ratio * Math.cos(axis.angle);
    const y = center + radius * ratio * Math.sin(axis.angle);
    return { x, y };
  });
});

const shapePoints = computed(() =>
  shapeDots.value.map((pt) => `${pt.x.toFixed(1)},${pt.y.toFixed(1)}`).join(' ')
);
</script>
