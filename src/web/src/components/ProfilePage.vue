<template>
  <!-- 我的页面占位 -->
  <div class="flex h-full flex-col items-center justify-center px-6 py-12">
    <div
      class="flex max-w-md flex-col items-center rounded-2xl border border-[rgba(255,255,255,0.1)] bg-[rgba(18,22,33,0.6)] px-8 py-12 text-center backdrop-blur-lg"
    >
      <!-- 用户头像占位 -->
      <div
        class="mb-6 flex h-20 w-20 items-center justify-center rounded-full bg-[rgba(214,160,96,0.15)]"
      >
        <svg
          width="40"
          height="40"
          viewBox="0 0 24 24"
          fill="none"
          stroke="var(--accent)"
          stroke-width="1.5"
        >
          <circle cx="12" cy="8" r="4" />
          <path d="M4 20c0-4 4-6 8-6s8 2 8 6" />
        </svg>
      </div>

      <!-- 标题 -->
      <h2 class="mb-3 text-2xl font-semibold text-white">个人中心</h2>

      <!-- 描述 -->
      <p class="mb-6 text-[15px] leading-relaxed text-white/60">
        管理您的账户信息、历史记录与偏好设置。该功能正在开发中，敬请期待。
      </p>

      <!-- 状态标签 -->
      <div
        class="inline-flex items-center gap-2 rounded-full border border-[rgba(214,160,96,0.3)] bg-[rgba(214,160,96,0.1)] px-4 py-2 text-sm text-[var(--accent)]"
      >
        <span class="h-2 w-2 animate-pulse rounded-full bg-[var(--accent)]"></span>
        <span>即将推出</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// 个人中心占位页面，暂无逻辑
</script>
