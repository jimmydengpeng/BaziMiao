<template>
  <!-- 我的页面占位 -->
  <div class="flex h-full flex-col items-center justify-center px-6 py-12">
    <div
      class="flex w-full max-w-md flex-col items-center rounded-2xl border border-[rgba(255,255,255,0.1)] bg-[rgba(18,22,33,0.6)] px-6 py-10 text-center backdrop-blur-lg"
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
      <h2 class="mb-3 text-2xl font-semibold text-white">我的</h2>

      <!-- 描述 -->
      <p class="mb-6 text-[15px] leading-relaxed text-white/60">
        个人中心与设置入口合并在同一块区域，统一管理账号与偏好。
      </p>

      <!-- 合并区块 -->
      <div class="w-full rounded-2xl border border-[rgba(255,255,255,0.08)] bg-[rgba(14,16,24,0.6)] px-5 py-5 text-left">
        <div class="mb-2 flex items-center gap-2 text-xs uppercase tracking-[0.25em] text-[var(--accent)]">
          <span class="h-1.5 w-1.5 rounded-full bg-[var(--accent)]"></span>
          <span>个人中心 / 设置</span>
        </div>
        <p class="text-sm text-white/60">
          账号信息、历史记录、登录安全与偏好配置将统一放在这里管理。
        </p>
        <div class="mt-4 flex flex-wrap gap-2 text-xs text-white/70">
          <span class="rounded-full border border-white/10 bg-white/5 px-3 py-1">账号资料</span>
          <span class="rounded-full border border-white/10 bg-white/5 px-3 py-1">历史记录</span>
          <span class="rounded-full border border-white/10 bg-white/5 px-3 py-1">安全设置</span>
          <span class="rounded-full border border-white/10 bg-white/5 px-3 py-1">偏好配置</span>
        </div>
      </div>

      <!-- 状态标签 -->
      <div
        class="mt-6 inline-flex items-center gap-2 rounded-full border border-[rgba(214,160,96,0.3)] bg-[rgba(214,160,96,0.1)] px-4 py-2 text-sm text-[var(--accent)]"
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
