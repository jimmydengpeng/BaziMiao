<template>
  <div class="not-found-page flex min-h-[60vh] flex-col items-center justify-center px-4 text-center">
    <div class="mb-6 text-8xl opacity-30">404</div>
    <h1 class="mb-4 text-2xl font-semibold text-white">页面未找到</h1>
    <p class="mb-8 text-white/60">抱歉，您访问的页面不存在。</p>
    <router-link
      to="/"
      class="inline-flex items-center gap-2 rounded-xl bg-gradient-to-br from-[var(--accent)] to-[var(--accent-2)] px-6 py-3 font-semibold text-[#0a0604] shadow-lg transition hover:-translate-y-0.5"
    >
      返回首页
    </router-link>
  </div>
</template>

<script setup lang="ts">
//
</script>
