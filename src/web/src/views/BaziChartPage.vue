<template>
  <!-- 命盘主页面：
       - 手机端：底部有固定 Tab Bar，预留更大底部内边距避免内容被遮挡
       - 平板 / 桌面端：正常内边距，由顶部导航 + 悬浮 Tab Bar 协同控制 -->
  <div class="bazi-chart-page-wrapper mx-auto max-w-[1600px] px-1.5 pb-20 md:px-4 md:pb-8 lg:px-6 lg:pb-10">
    <section class="main-shell grid grid-cols-1 items-start gap-3 md:gap-4 lg:gap-5 lg:grid-cols-[auto_minmax(0,1fr)]">
      <!-- 模块级侧边导航（使用 SideNav 组件，桌面端显示） -->
      <SideNav
        :current-page="currentPage"
        :can-view-report="canViewReport"
      />

      <div class="workspace flex min-w-0 gap-3 md:gap-4 lg:gap-5 lg:items-start" :class="{ 'chat-open': chatOpen }">
        <!-- main-content：
             - 手机端：轻微上内边距，和底部 Tab Bar 形成平衡
             - 平板端：增加顶部内边距，避免被顶部悬浮 Tab Bar 遮挡
             - 桌面端：保持原样 -->
        <main
          class="main-content relative w-full min-w-0 max-w-[900px] space-y-3 pt-1 md:space-y-4 md:pt-9 lg:space-y-5 lg:pt-0"
        >
          <!-- 子路由内容 -->
          <router-view />
        </main>

        <!-- 侧边聊天面板 - 桌面端：侧边栏；移动端：全屏模态框 -->
        <aside
          v-if="chatOpen"
          :class="[
            // 移动端：全屏模态框
            'fixed inset-0 z-50 bg-[rgba(18,22,33,0.98)] backdrop-blur-lg lg:relative lg:inset-auto lg:z-auto lg:bg-transparent lg:backdrop-blur-none',
            // 桌面端：侧边栏
            'chat-column lg:block',
            { open: chatOpen }
          ]"
          :aria-hidden="!chatOpen"
        >
          <SideChat :open="chatOpen" @close="closeChat" />
        </aside>
      </div>

      <!-- 浮动聊天按钮（聊天未打开时显示） -->
      <button
        v-if="!chatOpen"
        class="chat-fab fixed bottom-20 right-4 z-40 flex h-14 items-center gap-2 rounded-full bg-gradient-to-br from-[var(--accent)] to-[var(--accent-2)] px-5 py-3 text-sm font-semibold text-[#0a0604] shadow-lg transition hover:-translate-y-1 lg:bottom-6"
        type="button"
        aria-label="智能解析"
        @click="openChat"
      >
        <span class="chat-fab__icon" aria-hidden="true">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
          </svg>
        </span>
        <span class="chat-fab__label">智能解析</span>
      </button>

      <!-- 移动端 / 平板端 Tab Bar（最多 4 个 Tab，对应侧边栏核心功能） -->
      <!-- 说明：
           - 手机端和平板端：统一固定在屏幕底部上方，参考 iOS 风格的悬浮 Tab Bar，背景使用毛玻璃效果
           - 平板端：宽度略更大，使用更“弹性”的宽度以适配不同尺寸的平板
           - 桌面端：由左侧 SideNav 负责导航，隐藏此 Tab Bar -->
      <TabBar :items="tabItems" />
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRoute } from 'vue-router';
import SideNav from '../components/SideNav.vue';
import SideChat from '../components/SideChat.vue';
import TabBar from '../components/TabBar.vue';
import { useStore } from '../composables/useStore';
// 与侧边栏保持一致的核心功能图标
import baziChartIconUrl from '../assets/bazi-chart.png';
import reportIconUrl from '../assets/report.png';
import detailChartIconUrl from '../assets/pages.png';
import verifyChartIconUrl from  '../assets/check-list-1.png';

const route = useRoute();
const { report } = useStore();

const chatOpen = ref(false);

// 当前命盘 ID
const chartId = computed(() => route.params.id as string);

// 根据当前路由计算当前页面（用于 SideNav 高亮）
const currentPage = computed(() => {
  const path = route.path;
  if (path.includes('/pillars')) return 'chart';
  if (path.includes('/report')) return 'report';
  if (path.includes('/pro')) return 'pro';
  if (path.includes('/verification')) return 'verification';
  return 'chart';
});

// 底部 Tab Bar 配置，复用统一的样式
const tabItems = computed(() => {
  const id = chartId.value;
  return [
    {
      key: 'chart',
      label: '命盘信息',
      icon: baziChartIconUrl,
      to: `/bazi/chart/${id}/pillars`,
      active: currentPage.value === 'chart'
    },
    {
      key: 'report',
      label: '命理报告',
      icon: reportIconUrl,
      to: `/bazi/chart/${id}/report`,
      active: currentPage.value === 'report'
    },
    {
      key: 'pro',
      label: '专业细盘',
      icon: detailChartIconUrl,
      to: `/bazi/chart/${id}/pro`,
      active: currentPage.value === 'pro'
    },
    {
      key: 'verification',
      label: '前事验盘',
      icon: verifyChartIconUrl,
      to: `/bazi/chart/${id}/verification`,
      active: currentPage.value === 'verification'
    }
  ];
});

// 是否可以查看报告
const canViewReport = computed(() => !!report.value);

const openChat = () => {
  chatOpen.value = true;
};

const closeChat = () => {
  chatOpen.value = false;
};

// 设置页面样式类
onMounted(() => {
  document.documentElement.classList.add('page-main');
  document.documentElement.classList.remove('page-home');
});

onUnmounted(() => {
  document.documentElement.classList.remove('page-main');
});
</script>
