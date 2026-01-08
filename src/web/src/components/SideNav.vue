<template>
  <!-- 侧边导航栏（命盘解析模块专用） -->
  <!-- 桌面端：固定侧边栏；移动端：使用底部导航，侧边栏隐藏 -->
  <aside
    :class="[
      'side-nav z-40 hidden flex-col gap-3 border border-[rgba(255,255,255,0.14)] bg-[rgba(18,22,33,0.62)] px-4 py-4 shadow-[0_18px_40px_rgba(0,0,0,0.35)] backdrop-blur-xl',
      // 桌面端样式：显示侧边栏
      'lg:flex lg:sticky lg:top-[calc(64px+env(safe-area-inset-top,0px))] lg:max-h-[calc(100vh-96px)] lg:w-[clamp(180px,18vw,240px)] lg:rounded-2xl lg:overflow-y-auto'
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
            <img :src="baziChartIconUrl" alt="命盘信息" class="h-6 w-6 object-contain" />
          </span>
          <span class="flex-1 font-medium">命盘信息</span>
        </button>
        <button
          :class="[navBtnBase, { [navBtnActive]: currentPage === 'report' }]"
          type="button"
          @click="handleNav('report')"
        >
          <span :class="navIconClass">
            <img :src="reportIconUrl" alt="命理报告" class="h-6 w-6 object-contain" />
          </span>
          <span class="flex-1 font-medium">命理报告</span>
        </button>
        <button
          :class="[navBtnBase, { [navBtnActive]: currentPage === 'detail' }]"
          type="button"
          @click="handleNav('detail')"
        >
          <span :class="navIconClass">
            <img :src="archiveIconUrl" alt="专业细盘" class="h-6 w-6 object-contain" />
          </span>
          <span class="flex-1 font-medium">专业细盘</span>
        </button>
        <button
          :class="[navBtnBase, { [navBtnActive]: currentPage === 'verification' }]"
          type="button"
          @click="handleNav('verification')"
        >
          <span :class="navIconClass">
            <img :src="chatIconUrl" alt="前事验盘" class="h-6 w-6 object-contain" />
          </span>
          <span class="flex-1 font-medium">前事验盘</span>
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
          @click="handleNav('archive')"
        >
          切换档案
        </button>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { useRouter, useRoute } from 'vue-router';
import baziChartIconUrl from '../assets/bazi-chart.png';
import reportIconUrl from '../assets/report.png';
import archiveIconUrl from '../assets/archive.png';
import chatIconUrl from '../assets/chat-dot-square.png';
import { useStore } from '../composables/useStore';

const router = useRouter();
const route = useRoute();
const { activeArchiveId } = useStore();

// Props
defineProps<{
  currentPage: 'chart' | 'report' | 'detail' | 'verification' | 'archive' | 'form';
  canViewReport: boolean; // 是否可以查看报告（需要已生成报告）
}>();

// 导航按钮基础样式
const navBtnBase =
  'flex w-full items-center gap-0 rounded-xl border border-transparent px-3 py-2 text-left text-[15px] text-white transition hover:bg-white/5 disabled:opacity-50 disabled:cursor-not-allowed';
const navBtnActive =
  'border-[rgba(255,255,255,0.25)] bg-[rgba(214,160,96,0.22)] text-[var(--accent-2)]';
const navIconClass = 'flex h-10 w-10 items-center justify-center rounded-lg shrink-0';

// 处理导航点击
const handleNav = (page: 'chart' | 'report' | 'detail' | 'verification' | 'archive' | 'form') => {
  // 根据页面类型导航到对应路由
  switch (page) {
    case 'chart': {
      const chartId = route.params.id || activeArchiveId.value || 'temp';
      router.push(`/bazi/chart/${chartId}/pillars`);
      break;
    }
    case 'report': {
      const chartId = route.params.id || activeArchiveId.value || 'temp';
      router.push(`/bazi/chart/${chartId}/report`);
      break;
    }
    case 'detail': {
      const chartId = route.params.id || activeArchiveId.value || 'temp';
      router.push(`/bazi/chart/${chartId}/detail`);
      break;
    }
    case 'verification': {
      const chartId = route.params.id || activeArchiveId.value || 'temp';
      router.push(`/bazi/chart/${chartId}/verification`);
      break;
    }
    case 'archive':
      router.push('/bazi/archives');
      break;
    case 'form':
      router.push('/bazi/form');
      break;
  }
};
</script>
