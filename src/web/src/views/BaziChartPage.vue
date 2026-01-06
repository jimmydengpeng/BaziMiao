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
      <div class="mobile-tabs fixed inset-x-0 bottom-6 z-40 flex justify-center lg:hidden">
        <div
          class="inline-flex w-[calc(100%-32px)] max-w-[420px] items-stretch rounded-full border border-[rgba(255,255,255,0.16)] bg-[rgba(18,22,33,0.3)] px-1.5 py-1.5 shadow-[0_18px_48px_rgba(0,0,0,0.7)] backdrop-blur-2xl md:w-[calc(100%-96px)] md:max-w-[560px] md:bg-[rgba(18,22,33,0.65)]"
        >
          <!-- 命盘信息 -->
          <router-link
            :to="`/bazi/chart/${chartId}/pillars`"
            :class="[
              'flex flex-1 flex-col items-center justify-center gap-0.5 rounded-full px-3 py-2 text-[10px] font-medium transition md:px-4 md:text-[11px]',
              currentPage === 'chart'
                ? 'bg-[rgba(214,160,96,0.3)] text-[var(--accent-2)]'
                : 'text-white/75 hover:bg-white/5'
            ]"
          >
            <span class="flex h-6 w-6 items-center justify-center md:h-7 md:w-7">
              <img :src="baziChartIconUrl" alt="命盘信息" class="h-5 w-5 md:h-6 md:w-6 object-contain" />
            </span>
            <span class="font-medium" style="font-family: 'Noto Sans SC','Microsoft YaHei','PingFang SC',sans-serif;">命盘信息</span>
          </router-link>

          <!-- 命理报告（不可用时降权显示并禁用点击） -->
          <router-link
            :to="`/bazi/chart/${chartId}/report`"
            :class="[
              'flex flex-1 flex-col items-center justify-center gap-0.5 rounded-full px-3 py-2 text-[10px] font-medium transition md:px-4 md:text-[11px]',
              currentPage === 'report'
                ? 'bg-[rgba(214,160,96,0.3)] text-[var(--accent-2)]'
                : 'text-white/75 hover:bg-white/5'
            ]"
          >
            <span class="flex h-6 w-6 items-center justify-center md:h-7 md:w-7">
              <img :src="reportIconUrl" alt="命理报告" class="h-5 w-5 md:h-6 md:w-6 object-contain" />
            </span>
            <span class="font-medium" style="font-family: 'Noto Sans SC','Microsoft YaHei','PingFang SC',sans-serif;">命理报告</span>
          </router-link>

          <!-- 专业细盘 -->
          <router-link
            :to="`/bazi/chart/${chartId}/pro`"
            :class="[
              'flex flex-1 flex-col items-center justify-center gap-0.5 rounded-full px-3 py-2 text-[10px] font-medium transition md:px-4 md:text-[11px]',
              currentPage === 'pro'
                ? 'bg-[rgba(214,160,96,0.3)] text-[var(--accent-2)]'
                : 'text-white/75 hover:bg-white/5'
            ]"
          >
            <span class="flex h-6 w-6 items-center justify-center md:h-7 md:w-7">
              <img :src="archiveIconUrl" alt="专业细盘" class="h-5 w-5 md:h-6 md:w-6 object-contain" />
            </span>
            <span class="font-medium" style="font-family: 'Noto Sans SC','Microsoft YaHei','PingFang SC',sans-serif;">专业细盘</span>
          </router-link>

          <!-- 前事验盘 -->
          <router-link
            :to="`/bazi/chart/${chartId}/verification`"
            :class="[
              'flex flex-1 flex-col items-center justify-center gap-0.5 rounded-full px-3 py-2 text-[10px] font-medium transition md:px-4 md:text-[11px]',
              currentPage === 'verification'
                ? 'bg-[rgba(214,160,96,0.3)] text-[var(--accent-2)]'
                : 'text-white/75 hover:bg-white/5'
            ]"
          >
            <span class="flex h-6 w-6 items-center justify-center md:h-7 md:w-7">
              <img :src="chatIconUrl" alt="前事验盘" class="h-5 w-5 md:h-6 md:w-6 object-contain" />
            </span>
            <span class="font-medium" style="font-family: 'Noto Sans SC','Microsoft YaHei','PingFang SC',sans-serif;">前事验盘</span>
          </router-link>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRoute } from 'vue-router';
import SideNav from '../components/SideNav.vue';
import SideChat from '../components/SideChat.vue';
import { useStore } from '../composables/useStore';
// 与侧边栏保持一致的核心功能图标
import baziChartIconUrl from '../assets/bazi-chart.png';
import reportIconUrl from '../assets/report.png';
import archiveIconUrl from '../assets/archive.png';
import chatIconUrl from '../assets/chat-dot-square.png';

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
