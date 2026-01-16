<template>
  <button
    class="inline-flex h-9 w-9 items-center justify-center rounded-full border border-white/10 bg-white/5 text-white/70 transition hover:bg-white/10 hover:text-white"
    type="button"
    :aria-label="ariaLabel"
  >
    <svg
      class="h-4 w-4"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      stroke-width="2.2"
      stroke-linecap="round"
      stroke-linejoin="round"
      aria-hidden="true"
    >
      <path d="M12 5v14M5 12h14" />
    </svg>
  </button>
</template>

<script setup lang="ts">
withDefaults(defineProps<{ ariaLabel?: string }>(), {
  ariaLabel: '新建档案'
});
</script>
