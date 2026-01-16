<template>
  <ReportSectionCard :title="title">
    <template v-if="showToggle" #actions>
      <button
        class="btn-ghost rounded-full px-2.5 py-1 text-xs"
        type="button"
        @click="$emit('toggle-sample')"
      >
        {{ showSample ? '查看占位' : '查看示例' }}
      </button>
    </template>

    <div class="py-2 text-xs leading-relaxed text-[var(--muted)]">
      <span v-if="state === 'queued'" class="mr-2 inline-flex items-center gap-1 text-[11px] text-white/50">
        <span class="h-1.5 w-1.5 rounded-full bg-white/30"></span>
        {{ queuedText }}
      </span>
      <span v-else-if="state === 'generating'" class="mr-2 inline-flex items-center gap-1 text-[11px] text-white/60">
        <span class="h-1.5 w-1.5 rounded-full bg-[var(--accent-2)]/70"></span>
        {{ generatingText }}
      </span>
      {{ description }}
    </div>

    <div v-if="showSample && state === 'idle'" class="space-y-2 pb-3">
      <slot name="sample" />
    </div>
    <div v-else class="space-y-2 pb-3">
      <div
        v-for="(bar, idx) in placeholderBarsResolved"
        :key="`placeholder-${idx}`"
        class="h-2 rounded"
        :class="placeholderBarClass"
        :style="{ width: `${bar}%` }"
      ></div>
    </div>
  </ReportSectionCard>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import ReportSectionCard from './ReportSectionCard.vue';

const props = withDefaults(defineProps<{
  title: string;
  description: string;
  state?: 'idle' | 'queued' | 'generating';
  showToggle?: boolean;
  showSample?: boolean;
  placeholderBars?: number[];
  queuedText?: string;
  generatingText?: string;
}>(), {
  state: 'idle',
  showToggle: false,
  showSample: false,
  placeholderBars: () => [],
  queuedText: '即将生成',
  generatingText: '生成中',
});

defineEmits<{
  (e: 'toggle-sample'): void;
}>();

const placeholderBarsResolved = computed(() => (
  props.placeholderBars?.length ? props.placeholderBars : [68, 100, 82]
));
const placeholderBarClass = computed(() => {
  if (props.state === 'generating' || props.state === 'queued') {
    return 'animate-pulse bg-[rgba(255,255,255,0.14)]';
  }
  return 'bg-white/10';
});
</script>
