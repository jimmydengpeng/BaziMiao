<template>
  <div class="report-section-card" :class="variantClass">
    <PanelHeader :title="title">
      <template #actions>
        <slot name="actions"></slot>
        <span v-if="meta" class="text-xs text-[var(--muted)]">{{ meta }}</span>
      </template>
    </PanelHeader>
    <div class="px-3">
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import PanelHeader from './PanelHeader.vue';

const props = withDefaults(defineProps<{
  title: string;
  meta?: string;
  variant?: 'default' | 'accent' | 'danger';
}>(), {
  meta: '',
  variant: 'default',
});

const variantClass = computed(() => {
  if (props.variant === 'accent') {
    return 'border-dashed border-[rgba(255,255,255,0.08)] bg-[rgba(214,160,96,0.08)]';
  }
  if (props.variant === 'danger') {
    return 'border border-[rgba(255,80,80,0.24)] bg-[rgba(255,80,80,0.08)]';
  }
  return '';
});
</script>
