<template>
  <div class="bazi-chart-page-wrapper mx-auto max-w-[1600px] px-4 pb-10 lg:px-6">
    <section class="main-shell grid grid-cols-1 items-start gap-5 lg:grid-cols-[auto_minmax(0,1fr)]">
      <!-- 模块级侧边导航（使用 SideNav 组件，桌面端显示） -->
      <SideNav
        :current-page="currentPage"
        :can-view-report="canViewReport"
      />

      <div class="workspace flex min-w-0 gap-5 lg:items-start" :class="{ 'chat-open': chatOpen }">
        <main class="main-content relative w-full min-w-0 max-w-[900px] space-y-5">
          <!-- 移动端 Tab 栏 -->
          <div class="mobile-tabs flex gap-2 border-b border-white/10 pb-3 lg:hidden">
            <router-link
              :to="`/bazi/chart/${chartId}/pillars`"
              :class="[
                'flex-1 rounded-lg px-4 py-2.5 text-center text-sm font-medium transition',
                currentPage === 'chart'
                  ? 'bg-[rgba(214,160,96,0.2)] text-[var(--accent-2)]'
                  : 'text-white/70 hover:bg-white/5'
              ]"
            >
              八字命盘
            </router-link>
            <router-link
              :to="`/bazi/chart/${chartId}/report`"
              :class="[
                'flex-1 rounded-lg px-4 py-2.5 text-center text-sm font-medium transition',
                currentPage === 'report'
                  ? 'bg-[rgba(214,160,96,0.2)] text-[var(--accent-2)]'
                  : 'text-white/70 hover:bg-white/5',
                !canViewReport ? 'opacity-50 pointer-events-none' : ''
              ]"
            >
              命理报告
            </router-link>
          </div>

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
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRoute } from 'vue-router';
import SideNav from '../components/SideNav.vue';
import SideChat from '../components/SideChat.vue';
import { useStore } from '../composables/useStore';

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
