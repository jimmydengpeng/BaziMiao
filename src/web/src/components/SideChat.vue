<template>
  <div
    :class="[
      'flex h-full w-full flex-col overflow-hidden rounded-[20px] border border-[rgba(255,255,255,0.12)] bg-gradient-to-br from-[rgba(18,16,24,0.92)] to-[rgba(10,12,18,0.88)] shadow-[0_24px_60px_rgba(0,0,0,0.45)] backdrop-blur-[14px] transition-all duration-250',
      open ? 'opacity-100 translate-y-0 pointer-events-auto' : 'opacity-0 translate-y-3 pointer-events-none'
    ]"
  >
    <div class="relative z-10 flex items-center justify-between border-b border-[rgba(255,255,255,0.15)] bg-[rgba(14,13,19,0.85)] px-5 py-4 backdrop-blur-[32px] backdrop-saturate-[180%] before:absolute before:inset-0 before:bg-gradient-to-br before:from-[rgba(214,160,96,0.05)] before:to-[rgba(240,192,122,0.03)] before:pointer-events-none rounded-t-[20px]">
      <div class="relative z-[1] flex items-center gap-3 text-base font-semibold text-[var(--text)]">
        <span>智能对话</span>
        <span class="text-xs font-normal text-[#7dd56f]">在线</span>
      </div>
      <button
        class="relative z-[1] flex h-8 w-8 items-center justify-center rounded-lg border border-[rgba(255,255,255,0.1)] bg-[rgba(255,255,255,0.06)] text-[var(--muted)] transition-all duration-200 hover:bg-[rgba(255,255,255,0.1)] hover:text-[var(--text)] hover:-translate-y-[1px]"
        type="button"
        @click="emit('close')"
        aria-label="关闭对话"
      >
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="4" y1="4" x2="16" y2="16" />
          <line x1="16" y1="4" x2="4" y2="16" />
        </svg>
      </button>
    </div>
    <keep-alive>
      <MasterChat v-if="open" />
    </keep-alive>
  </div>
</template>

<script setup lang="ts">
import MasterChat from "./MasterChat.vue";

defineProps<{ open: boolean }>();

const emit = defineEmits<{
  (event: "close"): void;
}>();
</script>
