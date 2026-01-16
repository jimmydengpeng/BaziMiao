<template>
  <div class="flex flex-col gap-3">
    <div class="flex flex-wrap items-center gap-2 text-xs text-[var(--muted)]">
      <span class="rounded-full border border-white/10 bg-white/5 px-2 py-0.5">行动优先级 Top5</span>
      <span class="text-[10px] text-white/40">分数 0-100</span>
    </div>

    <div class="grid gap-3">
      <div v-for="item in normalized" :key="item.rank" class="flex gap-3 rounded-lg border border-white/5 bg-white/5 px-2 py-2">
        <div class="flex h-7 w-7 shrink-0 items-center justify-center rounded-full border border-white/10 text-xs font-semibold text-[var(--accent-2)]">
          {{ item.rank }}
        </div>
        <div class="flex-1">
          <div class="flex items-center justify-between gap-2 text-xs">
            <span class="font-semibold text-white/85">{{ item.title }}</span>
            <span class="text-[var(--accent-2)] font-semibold">{{ item.scoreText }}</span>
          </div>
          <div class="mt-1 h-1.5 w-full overflow-hidden rounded-full bg-white/10">
            <div class="h-full rounded-full bg-[var(--accent-2)]" :style="{ width: `${item.score}%` }"></div>
          </div>
          <div v-if="item.detail" class="mt-1 text-[10px] leading-relaxed text-[var(--muted)]">
            {{ item.detail }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

type ActionPriority = { rank: number; title: string; score: number | null; why?: string; how?: string };

const props = defineProps<{
  items: ActionPriority[];
}>();

const clampScore = (value: number) => Math.max(0, Math.min(100, value));

const normalized = computed(() => {
  const items = props.items
    .filter((item) => item && item.title)
    .map((item) => {
      const num = item.score === null || item.score === undefined ? null : Number(item.score);
      const score = num === null || !Number.isFinite(num) ? 0 : clampScore(num);
      const detailParts = [item.why, item.how].filter((part) => part);
      return {
        ...item,
        rank: Number.isFinite(item.rank) ? item.rank : 0,
        score,
        scoreText: num === null || !Number.isFinite(num) ? '暂无' : Math.round(score).toString(),
        detail: detailParts.join('；'),
      };
    });

  return items.sort((a, b) => (a.rank || 0) - (b.rank || 0)).slice(0, 5);
});
</script>
