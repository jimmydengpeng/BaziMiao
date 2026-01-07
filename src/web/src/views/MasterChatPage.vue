<template>
  <!-- 神喵大师聊天页面（旧路由 /bazi/chat 兼容） -->
  <div class="master-chat-page-wrapper mx-auto max-w-[900px] px-3 pb-6 md:px-4 md:pb-8 lg:px-6 lg:pb-10">
    <section class="master-chat-page h-[calc(100vh-120px)] md:h-[calc(100vh-140px)] lg:h-[calc(100vh-160px)]">
      <keep-alive>
        <UnifiedChat mode="modal" />
      </keep-alive>
    </section>
  </div>
</template>

<script setup lang="ts">
import UnifiedChat from '../components/UnifiedChat.vue';
</script>
