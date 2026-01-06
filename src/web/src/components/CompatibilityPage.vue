<template>
  <!-- 双人合盘占位页面 -->
  <div class="flex h-full flex-col items-center justify-center px-6 py-12">
    <div
      class="panel-card flex max-w-md flex-col items-center px-8 py-12 text-center"
    >
      <!-- 图标 -->
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
          <!-- 双心图标 -->
          <path
            d="M12 6.5C9.5 3.5 5 3.5 3 6.5C1 9.5 3 13.5 12 20C21 13.5 23 9.5 21 6.5C19 3.5 14.5 3.5 12 6.5Z"
          />
        </svg>
      </div>

      <!-- 标题 -->
      <h2 class="mb-3 text-2xl font-semibold text-white">双人合盘</h2>

      <!-- 描述 -->
      <p class="mb-6 text-[15px] leading-relaxed text-white/60">
        通过分析两人八字，解读感情缘分、性格互补与相处之道。该功能正在开发中，敬请期待。
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
// 双人合盘占位页面，暂无逻辑
</script>
