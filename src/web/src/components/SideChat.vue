<template>
  <div class="chat-window" :class="{ open }">
    <div class="chat-window-header">
      <div class="chat-window-title">
        <span>智能对话</span>
        <span class="chat-window-status">在线</span>
      </div>
      <button class="chat-close-btn" type="button" @click="emit('close')" aria-label="关闭对话">
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
