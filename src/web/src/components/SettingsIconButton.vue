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
      <circle cx="12" cy="12" r="3.4" />
      <path
        d="M19.4 15a1.8 1.8 0 0 0 .36 1.98l.02.02a2 2 0 1 1-2.83 2.83l-.02-.02A1.8 1.8 0 0 0 15 19.4a1.8 1.8 0 0 0-1 .33 1.8 1.8 0 0 0-.54 1.65V21a2 2 0 1 1-4 0v-.02a1.8 1.8 0 0 0-.54-1.65 1.8 1.8 0 0 0-1-.33 1.8 1.8 0 0 0-1.98.36l-.02.02a2 2 0 1 1-2.83-2.83l.02-.02A1.8 1.8 0 0 0 4.6 15a1.8 1.8 0 0 0-.33-1 1.8 1.8 0 0 0-1.65-.54H2a2 2 0 1 1 0-4h.02a1.8 1.8 0 0 0 1.65-.54 1.8 1.8 0 0 0 .33-1 1.8 1.8 0 0 0-.36-1.98l-.02-.02A2 2 0 1 1 6.38 3.1l.02.02A1.8 1.8 0 0 0 8 4.6a1.8 1.8 0 0 0 1-.33 1.8 1.8 0 0 0 .54-1.65V2a2 2 0 1 1 4 0v.02a1.8 1.8 0 0 0 .54 1.65 1.8 1.8 0 0 0 1 .33 1.8 1.8 0 0 0 1.98-.36l.02-.02a2 2 0 1 1 2.83 2.83l-.02.02A1.8 1.8 0 0 0 19.4 9c0 .35.12.69.33 1 .35.5.93.78 1.54.76H22a2 2 0 1 1 0 4h-.02a1.8 1.8 0 0 0-1.65.54 1.8 1.8 0 0 0-.33 1Z"
      />
    </svg>
  </button>
</template>

<script setup lang="ts">
withDefaults(defineProps<{ ariaLabel?: string }>(), {
  ariaLabel: '命盘档案'
});
</script>
