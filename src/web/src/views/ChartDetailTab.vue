<template>
  <div class="grid gap-4">
    <div class="panel-card">
      <div class="flex items-center justify-between gap-3">
        <div class="flex items-center gap-2 text-sm">
          <strong class="text-white">专业细盘</strong>
          <span class="rounded-[10px] border border-[rgba(255,255,255,0.08)] bg-[rgba(255,255,255,0.06)] px-2 py-1 text-xs text-[var(--muted)]">开发中</span>
        </div>
        <span class="text-xs text-[var(--muted)]">高级排盘细节即将上线</span>
      </div>
      <div class="mt-3 grid gap-2 text-sm text-[var(--muted)]">
        <p>这里将展示更精细的命盘拆解，包括十神、格局、用神等深入分析。</p>
        <p>当前版本为占位页面，功能完善后会自动展示对应命盘的专业解析。</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineOptions({ name: 'ChartDetailTab' });

// 占位页面，无需逻辑
</script>
