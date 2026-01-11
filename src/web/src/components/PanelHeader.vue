<template>
  <div class="panel-header">
    <div class="flex items-center justify-between gap-2 pt-0 pl-2 pr-1 pb-2 mb-0">
      <div class="flex items-center gap-2">
        <slot name="title">
          <h3 class="text-base font-semibold text-(--accent-2)">{{ title }}</h3>
        </slot>
      </div>
      <div class="panel-actions">
        <slot name="actions"></slot>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title: string
}>()
</script>
