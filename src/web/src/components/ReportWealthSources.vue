<template>
  <div class="flex flex-col gap-3">
    <div class="flex flex-wrap items-center gap-2 text-xs text-[var(--muted)]">
      <span class="rounded-full border border-white/10 bg-white/5 px-2 py-0.5">财富来源结构</span>
      <span class="text-[10px] text-white/40">0-100 相对强弱</span>
    </div>

    <div v-if="totalScore > 0" class="h-2 w-full overflow-hidden rounded-full bg-white/10">
      <div class="flex h-full w-full">
        <div
          v-for="item in normalized"
          :key="item.key"
          class="h-full"
          :style="{ width: `${item.ratio}%`, backgroundColor: item.color }"
        ></div>
      </div>
    </div>
    <div v-else class="rounded-lg border border-white/5 bg-white/5 px-2 py-1 text-[10px] text-[var(--muted)]">
      暂无可展示的结构分数
    </div>

    <div class="grid gap-2">
      <div v-for="item in normalized" :key="item.key" class="flex flex-col gap-1 rounded-lg border border-white/5 bg-white/5 px-2 py-1">
        <div class="flex items-center gap-2 text-xs">
          <span class="h-2 w-2 rounded-full" :style="{ backgroundColor: item.color }"></span>
          <span class="font-semibold text-white/80">{{ item.label }}</span>
          <span class="ml-auto text-[var(--accent-2)] font-semibold">{{ item.scoreText }}</span>
        </div>
        <div class="h-1.5 w-full overflow-hidden rounded-full bg-white/10">
          <div class="h-full rounded-full" :style="{ width: `${item.score}%`, backgroundColor: item.color }"></div>
        </div>
        <div v-if="item.notes" class="text-[10px] leading-relaxed text-[var(--muted)]">
          {{ item.notes }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

type WealthSource = { key: string; label: string; score: number | null; notes?: string };

const props = defineProps<{
  sources: WealthSource[];
}>();

const clampScore = (value: number) => Math.max(0, Math.min(100, value));

const colorMap: Record<string, string> = {
  zhengcai: 'rgba(92,184,92,0.8)',
  piancai: 'rgba(255,107,107,0.8)',
  skill: 'rgba(90,169,255,0.8)',
  resource: 'rgba(242,193,78,0.8)',
  investment: 'rgba(214,160,96,0.8)',
  accumulation: 'rgba(189,140,255,0.8)',
};

const normalized = computed(() => {
  const base = props.sources
    .filter((item) => item && item.label)
    .map((item) => {
      if (item.score === null || item.score === undefined) {
        return {
          ...item,
          score: 0,
          scoreText: '暂无',
          notes: item.notes || '',
          color: colorMap[item.key] || 'rgba(255,255,255,0.4)',
          ratio: 0,
        };
      }
      const num = Number(item.score);
      const score = Number.isFinite(num) ? clampScore(num) : 0;
      return {
        ...item,
        score,
        scoreText: Number.isFinite(num) ? Math.round(score).toString() : '暂无',
        notes: item.notes || '',
        color: colorMap[item.key] || 'rgba(255,255,255,0.4)',
        ratio: 0,
      };
    });

  const total = base.reduce((sum, item) => sum + item.score, 0);
  return base.map((item) => ({
    ...item,
    ratio: total > 0 ? (item.score / total) * 100 : 0,
  }));
});

const totalScore = computed(() => normalized.value.reduce((sum, item) => sum + item.score, 0));
</script>
