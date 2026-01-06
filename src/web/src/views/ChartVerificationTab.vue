<template>
  <div class="grid gap-4">
    <div class="rounded-2xl border border-[rgba(255,255,255,0.08)] bg-[var(--panel)] p-5 shadow-[0_12px_40px_rgba(0,0,0,0.35)]">
      <div class="flex items-center justify-between gap-3">
        <div class="flex items-center gap-2 text-sm">
          <strong class="text-white">前事验盘</strong>
          <span class="rounded-[10px] border border-[rgba(255,255,255,0.08)] bg-[rgba(255,255,255,0.06)] px-2 py-1 text-xs text-[var(--muted)]">占位</span>
        </div>
        <span class="text-xs text-[var(--muted)]">验证过往事件，校准推演</span>
      </div>
      <div class="mt-3 grid gap-2 text-sm text-[var(--muted)]">
        <p>后续将支持填写已发生的关键事件，校验命盘推演的准确性。</p>
        <p>在此期间，可返回命盘信息或命理报告继续查看已有内容。</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// 占位页面，无逻辑
</script>
