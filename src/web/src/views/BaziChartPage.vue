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
             - 平板端和桌面端：顶部间距已由 App.vue 的 app-content 统一处理 -->
        <main
          class="main-content relative w-full min-w-0 max-w-[900px] space-y-3 pt-1 md:space-y-4 lg:space-y-5"
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

      <!-- 固定层 UI（浮动按钮 + Tab Bar）从滚动容器中 Teleport 到 body，避免 iOS 惯性滚动吞点击 -->
      <teleport to="body">
        <!-- 浮动聊天按钮（聊天未打开时显示） -->
        <button
          v-if="!chatOpen"
          :style="fabStyle"
          ref="fabRef"
          class="chat-fab fixed z-40 flex h-14 w-14 items-center justify-center rounded-full bg-gradient-to-br from-[var(--accent)] to-[var(--accent-2)] text-sm font-semibold text-[#0a0604] shadow-lg transition hover:-translate-y-1 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--accent-2)] touch-none select-none active:scale-[0.98] lg:w-auto lg:min-w-[120px] lg:justify-start lg:gap-2 lg:px-5 lg:py-3"
          type="button"
          aria-label="智能解析"
          @pointerdown.prevent="startDrag"
          @click="openChat"
        >
          <span class="chat-fab__icon" aria-hidden="true">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
            </svg>
          </span>
          <span class="sr-only">神喵大师</span>
          <span class="chat-fab__label hidden lg:inline">神喵大师</span>
        </button>

        <!-- 移动端 / 平板端 Tab Bar（最多 4 个 Tab，对应侧边栏核心功能） -->
        <!-- 说明：
             - 手机端和平板端：统一固定在屏幕底部上方，参考 iOS 风格的悬浮 Tab Bar，背景使用毛玻璃效果
             - 平板端：宽度略更大，使用更“弹性”的宽度以适配不同尺寸的平板
             - 桌面端：由左侧 SideNav 负责导航，隐藏此 Tab Bar -->
        <TabBar :items="tabItems" />
      </teleport>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue';
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
const isDesktop = ref(false);
const fabRef = ref<HTMLElement | null>(null);

// 浮动按钮拖拽状态
const fabState = reactive({
  isDragging: false,
  dragMoved: false,
  dragX: 0,
  dragY: 0,
  side: 'right' as 'left' | 'right',
  y: 0,
  hasCustom: false,
  resetTimer: null as number | null,
});

const FAB_SIZE = 56; // 按钮直径（px）
const MOBILE_SIDE_PADDING = 16;
const DESKTOP_SIDE_PADDING = 24;
const TOP_RESERVED = 76; // 预留顶部导航区域
const MOBILE_BOTTOM_RESERVED = 150; // 预留底部 Tab Bar 区域
const DESKTOP_BOTTOM_RESERVED = 48;

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
  // 拖拽结束后短时间内的点击被忽略，防止误触
  if (fabState.isDragging || fabState.dragMoved) return;
  chatOpen.value = true;
};

const closeChat = () => {
  chatOpen.value = false;
};

// 设置页面样式类
onMounted(() => {
  document.documentElement.classList.add('page-main');
  document.documentElement.classList.remove('page-home');

  const updateDesktop = () => {
    isDesktop.value = window.matchMedia('(min-width: 1024px)').matches;
  };
  updateDesktop();

  const onResize = () => {
    updateDesktop();
    resetFabToDefault();
  };

  window.addEventListener('resize', onResize, { passive: true });
  setupFabDefault();
  fabListeners.value = { onResize };
});

onUnmounted(() => {
  document.documentElement.classList.remove('page-main');
  if (fabListeners.value?.onResize) {
    window.removeEventListener('resize', fabListeners.value.onResize);
  }
  if (fabListeners.value?.onPointerMove) {
    window.removeEventListener('pointermove', fabListeners.value.onPointerMove);
  }
  if (fabListeners.value?.onPointerUp) {
    window.removeEventListener('pointerup', fabListeners.value.onPointerUp);
  }
  if (fabState.resetTimer) {
    clearTimeout(fabState.resetTimer);
  }
});

// --- 浮动按钮拖拽逻辑 ---
const fabListeners = ref<{
  onResize?: () => void;
  onPointerMove?: (e: PointerEvent) => void;
  onPointerUp?: (e: PointerEvent) => void;
} | null>(null);

const getSidePadding = () => (isDesktop.value ? DESKTOP_SIDE_PADDING : MOBILE_SIDE_PADDING);
const getBottomReserved = () => (isDesktop.value ? DESKTOP_BOTTOM_RESERVED : MOBILE_BOTTOM_RESERVED);

const clampY = (y: number) => {
  const topLimit = TOP_RESERVED;
  const bottomLimit = getBottomReserved();
  const maxY = window.innerHeight - bottomLimit - FAB_SIZE;
  return Math.min(Math.max(y, topLimit), Math.max(topLimit, maxY));
};

const clampX = (x: number) => {
  const padding = getSidePadding();
  const maxX = window.innerWidth - FAB_SIZE - padding;
  return Math.min(Math.max(x, padding), Math.max(padding, maxX));
};

const getDefaultY = () => {
  if (typeof window === 'undefined') return 0;
  const bottom = getBottomReserved();
  return clampY(window.innerHeight - bottom - FAB_SIZE);
};

const setupFabDefault = () => {
  fabState.y = getDefaultY();
  fabState.side = 'right';
  fabState.hasCustom = false;
};

const resetFabToDefault = () => {
  if (!fabState.hasCustom) {
    fabState.y = getDefaultY();
  } else {
    fabState.y = clampY(fabState.y);
  }
};

const startDrag = (event: PointerEvent) => {
  if (fabState.resetTimer) {
    clearTimeout(fabState.resetTimer);
    fabState.resetTimer = null;
  }
  fabState.isDragging = true;
  fabState.dragMoved = false;

  const target = fabRef.value || (event.currentTarget as HTMLElement);
  const rect = target.getBoundingClientRect();
  fabState.dragX = clampX(event.clientX - rect.width / 2);
  fabState.dragY = clampY(event.clientY - rect.height / 2);
  if (target.setPointerCapture) {
    target.setPointerCapture(event.pointerId);
  }

  const onPointerMove = (e: PointerEvent) => {
    fabState.isDragging = true;
    fabState.dragMoved = true;
    fabState.dragX = clampX(e.clientX - FAB_SIZE / 2);
    fabState.dragY = clampY(e.clientY - FAB_SIZE / 2);
  };

  const onPointerUp = (e: PointerEvent) => {
    const targetSide = e.clientX < window.innerWidth / 2 ? 'left' : 'right';
    fabState.side = targetSide;
    fabState.y = clampY(e.clientY - FAB_SIZE / 2);
    fabState.hasCustom = true;
    fabState.isDragging = false;
    if (fabRef.value?.releasePointerCapture) {
      try {
        fabRef.value.releasePointerCapture(e.pointerId);
      } catch (err) {
        // ignore
      }
    }

    fabState.resetTimer = window.setTimeout(() => {
      fabState.dragMoved = false;
      fabState.resetTimer = null;
    }, 120);

    window.removeEventListener('pointermove', onPointerMove);
    window.removeEventListener('pointerup', onPointerUp);
    fabListeners.value = { ...fabListeners.value, onPointerMove: undefined, onPointerUp: undefined };
  };

  window.addEventListener('pointermove', onPointerMove);
  window.addEventListener('pointerup', onPointerUp);
  fabListeners.value = { ...fabListeners.value, onPointerMove, onPointerUp };
};

const fabStyle = computed(() => {
  const sidePadding = getSidePadding();
  const y = fabState.hasCustom ? clampY(fabState.y) : getDefaultY();

  if (fabState.isDragging) {
    return {
      top: `${fabState.dragY}px`,
      left: `${fabState.dragX}px`,
      right: 'auto',
      transition: 'none',
    };
  }

  const base = {
    top: `${y}px`,
    right: 'auto',
    left: 'auto',
  } as Record<string, string>;

  if (fabState.side === 'left') {
    base.left = `${sidePadding}px`;
  } else {
    base.right = `${sidePadding}px`;
  }
  return base;
});
</script>
