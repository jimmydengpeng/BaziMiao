<template>
  <!-- 侧边导航栏（命理报告模块专用） -->
  <!-- 桌面端：固定侧边栏；移动端：抽屉式（从 TopNav 下方开始） -->
  <aside
    :class="[
      'side-nav z-40 flex flex-col gap-3 border border-[rgba(255,255,255,0.14)] bg-[rgba(18,22,33,0.62)] px-4 py-4 shadow-[0_18px_40px_rgba(0,0,0,0.35)] backdrop-blur-xl',
      // 桌面端样式
      'lg:sticky lg:top-20 lg:max-h-[calc(100vh-96px)] lg:w-[clamp(180px,18vw,240px)] lg:translate-x-0 lg:rounded-2xl lg:p-4 lg:overflow-y-auto',
      // 移动端样式：抽屉（top-14 为 TopNav 高度）
      open
        ? 'fixed top-14 bottom-0 left-0 w-[78%] max-w-[320px] translate-x-0 rounded-br-2xl'
        : 'fixed top-14 bottom-0 left-0 w-[78%] max-w-[320px] -translate-x-full',
      'transition-transform duration-300 ease-in-out overflow-y-auto'
    ]"
  >
    <!-- 核心功能导航 -->
    <div class="grid gap-3">
      <div class="grid gap-2">
        <div class="text-[11px] uppercase tracking-[0.12em] text-white/60">核心功能</div>
        <button
          :class="[navBtnBase, { [navBtnActive]: currentPage === 'chart' }]"
          type="button"
          @click="handleNav('chart')"
        >
          <span :class="navIconClass">
            <img :src="baziChartIconUrl" alt="八字命盘" class="h-6 w-6 object-contain" />
          </span>
          <span class="flex-1 font-medium">八字命盘</span>
        </button>
        <button
          :class="[navBtnBase, { [navBtnActive]: currentPage === 'report' }]"
          type="button"
          :disabled="!canViewReport"
          @click="handleNav('report')"
        >
          <span :class="navIconClass">
            <img :src="reportIconUrl" alt="命理报告" class="h-6 w-6 object-contain" />
          </span>
          <span class="flex-1 font-medium">命理报告</span>
        </button>
        <button
          :class="[navBtnBase, { [navBtnActive]: currentPage === 'archive' }]"
          type="button"
          @click="handleNav('archive')"
        >
          <span :class="navIconClass">
            <img :src="archiveIconUrl" alt="档案列表" class="h-6 w-6 object-contain" />
          </span>
          <span class="flex-1 font-medium">档案列表</span>
        </button>
        <button
          :class="[navBtnBase, { [navBtnActive]: currentPage === 'master-chat' }]"
          type="button"
          @click="handleNav('master-chat')"
        >
          <span :class="navIconClass">
            <img :src="chatIconUrl" alt="神喵大师" class="h-6 w-6 object-contain" />
          </span>
          <span class="flex-1 font-medium">神喵大师</span>
        </button>
      </div>

      <!-- 更多模块（禁用状态） -->
      <div class="grid gap-2 opacity-80">
        <div class="text-[11px] uppercase tracking-[0.12em] text-white/60">更多模块</div>
        <button
          class="flex w-full items-center gap-2 rounded-xl px-3 py-2 text-left text-[15px] text-white/60"
          type="button"
          disabled
        >
          运势测算
        </button>
        <button
          class="flex w-full items-center gap-2 rounded-xl px-3 py-2 text-left text-[15px] text-white/60"
          type="button"
          disabled
        >
          今日运势
        </button>
        <button
          class="flex w-full items-center gap-2 rounded-xl px-3 py-2 text-left text-[15px] text-white/60"
          type="button"
          disabled
        >
          命理百科
        </button>
      </div>

      <!-- 快捷入口 -->
      <div class="grid gap-2">
        <div class="text-[11px] uppercase tracking-[0.12em] text-white/60">快捷入口</div>
        <button
          class="flex w-full items-center gap-2 rounded-xl border border-transparent px-3 py-2 text-left text-[15px] text-white transition hover:bg-white/5"
          type="button"
          @click="handleNav('form')"
        >
          新建排盘
        </button>
        <button
          class="flex w-full items-center gap-2 rounded-xl border border-transparent px-3 py-2 text-left text-[15px] text-white transition hover:bg-white/5"
          type="button"
          @click="handleNav('home')"
        >
          回到首页
        </button>
      </div>
    </div>
  </aside>

  <!-- 抽屉遮罩（仅移动端，从 TopNav 下方开始） -->
  <div
    v-if="open"
    class="fixed top-14 bottom-0 left-0 right-0 z-30 bg-black/50 backdrop-blur-[2px] lg:hidden"
    @click="$emit('close')"
  ></div>
</template>

<script setup lang="ts">
import baziChartIconUrl from '../assets/bazi-chart.png';
import reportIconUrl from '../assets/report.png';
import archiveIconUrl from '../assets/archive.png';
import chatIconUrl from '../assets/chat-dot-square.png';

// Props
defineProps<{
  open: boolean; // 移动端抽屉是否打开
  currentPage: 'chart' | 'report' | 'archive' | 'master-chat' | 'form' | 'home';
  canViewReport: boolean; // 是否可以查看报告（需要已生成报告）
}>();

// 事件
const emit = defineEmits<{
  (e: 'navigate', page: 'chart' | 'report' | 'archive' | 'master-chat' | 'form' | 'home'): void;
  (e: 'close'): void;
}>();

// 导航按钮基础样式
const navBtnBase =
  'flex w-full items-center gap-0 rounded-xl border border-transparent px-3 py-2 text-left text-[15px] text-white transition hover:bg-white/5 disabled:opacity-50 disabled:cursor-not-allowed';
const navBtnActive =
  'border-[rgba(255,255,255,0.25)] bg-[rgba(214,160,96,0.22)] text-[var(--accent-2)]';
const navIconClass = 'flex h-10 w-10 items-center justify-center rounded-lg shrink-0';

// 处理导航点击
const handleNav = (page: 'chart' | 'report' | 'archive' | 'master-chat' | 'form' | 'home') => {
  emit('navigate', page);
  emit('close'); // 移动端点击后自动关闭抽屉
};
</script>
