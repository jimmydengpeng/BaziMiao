<template>
  <div class="app-root h-[100dvh] overflow-hidden">
    <!-- 顶部导航栏（所有页面都显示，聊天全屏页面除外） -->
    <TopNav
      v-if="!isLayoutChatPage"
      :active-module="activeModule"
      :is-home="isHomePage"
      :is-authenticated="isAuthenticated"
      :current-page="currentPage"
      :can-view-report="canViewReport"
      @navigate="handleNavigate"
      @open-logo-dialog="openLogoDialog"
      @start="goToForm"
      @go-login="goToLogin"
    />

    <!-- 主内容区域：路由视图（滚动由 app-scroll 容器接管） -->
    <div class="app-content h-full pt-0 md:pt-0 lg:pt-0">
      <div
        ref="scrollEl"
        class="app-scroll h-full overflow-y-auto overscroll-contain"
        :class="
          isHomePage || isLayoutChatPage
            ? ''
            : 'pt-[calc(48px+env(safe-area-inset-top,0px))] md:pt-[calc(56px+env(safe-area-inset-top,0px))] lg:pt-[calc(64px+env(safe-area-inset-top,0px))]'
        "
      >
        <router-view v-if="!isOverlayRoute" />
        <router-view v-else-if="backgroundRoute" :route="backgroundRoute" />
      </div>
    </div>

    <!-- 全局浮动聊天按钮和弹窗（Teleport 到 body） -->
    <teleport to="body">
      <!-- 浮动聊天按钮：非聊天页面且弹窗未打开时显示 -->
      <ChatFab
        v-if="showChatFab && !chatModalOpen"
        @click="handleChatFabClick"
      />

      <!-- Logo 弹窗（点击左上角 Logo 打开） -->
      <LogoDialog
        v-model="logoDialogOpen"
        @open-chat="openMasterChat"
        @go-home="goHome"
      />

      <!-- 桌面端聊天弹窗 -->
      <Transition name="chat-modal">
        <div
          v-if="chatModalOpen && isDesktop"
          class="fixed inset-y-4 right-4 z-50 flex w-[420px] max-w-[calc(100vw-32px)] flex-col"
        >
          <UnifiedChat mode="modal" @close="closeChatModal" />
        </div>
      </Transition>

      <!-- 移动端全屏聊天（overlay 路由）：渲染在 body 上层，退出时可露出背景页 -->
      <router-view v-if="isOverlayRoute" v-slot="{ Component }">
        <component :is="Component" />
      </router-view>
    </teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue';
import { useRouter, useRoute, type RouteLocationNormalizedLoaded } from 'vue-router';
import TopNav from './components/TopNav.vue';
import ChatFab from './components/ChatFab.vue';
import UnifiedChat from './components/UnifiedChat.vue';
import LogoDialog from './components/LogoDialog.vue';
import { useStore } from './composables/useStore';
import { loadBaziViewState, saveBaziViewState } from './utils/storage';

const router = useRouter();
const route = useRoute();
const { isAuthenticated, activeArchiveId, report, chart } = useStore();
const scrollEl = ref<HTMLElement | null>(null);

// 聊天弹窗状态
const chatModalOpen = ref(false);
const isDesktop = ref(false);
const logoDialogOpen = ref(false);

// overlay 路由：例如 /chat 作为覆盖层叠在上一页之上
const backgroundRoute = ref<RouteLocationNormalizedLoaded | null>(null);
const isOverlayRoute = computed(() => route.meta?.overlay === true);
const layoutRoute = computed(() => (isOverlayRoute.value && backgroundRoute.value ? backgroundRoute.value : route));
const isLayoutChatPage = computed(() => layoutRoute.value.path === '/chat');
const skipNextScrollRestore = ref(false);
let removeAfterEachHook: (() => void) | null = null;

// 根据当前路由计算激活的模块
const activeModule = computed(() => {
  const path = layoutRoute.value.path;
  if (path.startsWith('/bazi/chat') || path === '/chat') return 'master';
  if (path.startsWith('/bazi')) return 'bazi';
  if (path.startsWith('/compatibility')) return 'compatibility';
  if (path.startsWith('/profile')) return 'profile';
  if (path.startsWith('/encyclopedia')) return 'encyclopedia';
  return 'bazi';
});

// 是否在首页
const isHomePage = computed(() => layoutRoute.value.path === '/');

// 是否显示浮动聊天按钮（排除聊天页面和首页）
const showChatFab = computed(() => {
  const path = route.path;
  // 聊天页面不显示
  if (path === '/chat' || path === '/bazi/chat') return false;
  // 首页不显示
  if (path === '/') return false;
  return true;
});

// 当前页面类型（用于侧边导航/移动端菜单高亮）
const currentPage = computed(() => {
  const path = layoutRoute.value.path;
  if (path.includes('/report')) return 'report';
  if (path.includes('/pro')) return 'pro';
  if (path.includes('/verification')) return 'verification';
  if (path.includes('/pillars')) return 'chart';
  if (path.includes('/chart')) return 'chart';
  if (path.includes('/archives')) return 'archive';
  if (path.includes('/chat')) return 'master-chat';
  if (path.includes('/form')) return 'form';
  if (path === '/') return 'home';
  return 'chart';
});

// 是否可以查看报告（需要已生成报告）
const canViewReport = computed(() => {
  return !!report.value || !!activeArchiveId.value;
});

// 处理浮动按钮点击
const handleChatFabClick = () => {
  if (isDesktop.value) {
    // 桌面端：打开弹窗
    chatModalOpen.value = true;
  } else {
    // 移动端：跳转到聊天页面
    router.push('/chat');
  }
};

// 关闭聊天弹窗
const closeChatModal = () => {
  chatModalOpen.value = false;
};

// 处理模块导航
const handleNavigate = (module: 'bazi' | 'compatibility' | 'profile' | 'master' | 'encyclopedia') => {
  switch (module) {
    case 'bazi':
      // 智能导航：如果有活跃的命盘，恢复到之前的浏览状态；否则显示表单页
      const viewState = loadBaziViewState();
      const hasActiveChart = chart.value && (activeArchiveId.value !== null || route.params.id);

      if (hasActiveChart) {
        // 有活跃命盘，恢复到之前的浏览状态或默认页面
        const chartId = activeArchiveId.value || route.params.id || viewState?.chartId;
        if (chartId) {
          if (viewState && viewState.chartId === chartId) {
            // 有保存的状态，恢复到之前的页面和滚动位置
            const pagePath = viewState.page === 'chart' ? 'pillars' : viewState.page;
            router.push(`/bazi/chart/${chartId}/${pagePath}`);
          } else {
            // 没有保存的状态，跳转到默认页面（命盘信息）
            router.push(`/bazi/chart/${chartId}/pillars`);
          }
        } else {
          // 没有有效的 chartId，跳转到表单页
          router.push('/bazi/form');
        }
      } else {
        // 没有活跃命盘，跳转到表单页（表单页会显示新建和从档案选择两个选项）
        router.push('/bazi/form');
      }
      break;
    case 'compatibility':
      router.push('/compatibility');
      break;
    case 'profile':
      router.push('/profile');
      break;
    case 'master':
      // 导航到聊天：根据设备类型处理
      if (isDesktop.value) {
        chatModalOpen.value = true;
      } else {
        router.push('/chat');
      }
      break;
    case 'encyclopedia':
      router.push('/encyclopedia');
      break;
  }
};

const openLogoDialog = () => {
  logoDialogOpen.value = true;
};

const openMasterChat = () => {
  if (isDesktop.value) {
    chatModalOpen.value = true;
  } else {
    router.push('/chat');
  }
};

// 回到首页
const goHome = () => {
  router.push('/');
};

// 跳转到表单页
const goToForm = () => {
  router.push('/bazi/form');
};

// 跳转到登录页
const goToLogin = () => {
  router.push('/profile');
};

const getScrollTop = () => scrollEl.value?.scrollTop ?? 0;
const setScrollTop = (top: number, behavior: ScrollBehavior = 'auto') => {
  scrollEl.value?.scrollTo({ top, behavior });
};

// 更新桌面端状态
const updateDesktop = () => {
  isDesktop.value = window.matchMedia('(min-width: 1024px)').matches;
};

// 根据路由更新 body 类名（用于样式）
watch(
  () => layoutRoute.value.path,
  (path) => {
    const classList = document.documentElement.classList;
    classList.remove('page-home', 'page-main');

    if (path === '/') {
      classList.add('page-home');
    } else {
      classList.add('page-main');
    }
  },
  { immediate: true }
);

// 保存命盘解析模块的浏览状态（当在命盘相关页面时）
watch(
  () => route.path,
  (path) => {
    // 如果当前在命盘解析模块的页面
    if (path.startsWith('/bazi/chart/')) {
      const chartId = route.params.id as string;
      const page = currentPage.value as 'chart' | 'report' | 'pro' | 'verification';

      // 保存浏览状态（包括当前页面和滚动位置）
      if (chartId && page) {
        saveBaziViewState({
          page,
          scrollPosition: getScrollTop(),
          chartId,
        });
      }
    }
  }
);

// 监听滚动，实时更新滚动位置（节流处理）
let scrollTimer: number | null = null;
const handleScroll = () => {
  if (scrollTimer) {
    clearTimeout(scrollTimer);
  }
  scrollTimer = window.setTimeout(() => {
    if (route.path.startsWith('/bazi/chart/')) {
      const chartId = route.params.id as string;
      const page = currentPage.value as 'chart' | 'report' | 'pro' | 'verification';

      if (chartId && page) {
        saveBaziViewState({
          page,
          scrollPosition: getScrollTop(),
          chartId,
        });
      }
    }
  }, 200); // 200ms 节流
};

// 路由切换后，恢复滚动位置（由 App 内的滚动容器接管）
watch(
  () => route.fullPath,
  async () => {
    // 路由变化时收起弹窗，避免遮挡
    logoDialogOpen.value = false;

    // overlay 打开/关闭时，不改动背景页滚动；关闭 overlay 后跳过一次滚动恢复
    if (route.meta?.overlay === true) return;
    if (skipNextScrollRestore.value) {
      skipNextScrollRestore.value = false;
      return;
    }

    await nextTick();
    if (!scrollEl.value) return;

    if (route.path.startsWith('/bazi/chart/')) {
      const viewState = loadBaziViewState();
      const chartId = route.params.id as string;
      if (viewState && viewState.chartId === chartId) {
        setScrollTop(viewState.scrollPosition, 'auto');
        return;
      }
    }
    setScrollTop(0, 'auto');
  },
  { immediate: true }
);

onMounted(() => {
  updateDesktop();
  window.addEventListener('resize', updateDesktop, { passive: true });

  if (scrollEl.value) {
    scrollEl.value.addEventListener('scroll', handleScroll, { passive: true });
  }

  // 记录 overlay 的背景路由：用于 /chat 退出动画露出上一页
  removeAfterEachHook = router.afterEach((to, from) => {
    if (to.meta?.overlay === true) {
      // 进入 overlay：记录上一页（非 overlay）
      if (from.meta?.overlay !== true) {
        backgroundRoute.value = from;
      }
      return;
    }

    // 退出 overlay：下一次 route.fullPath watch 不要改滚动位置
    if (from.meta?.overlay === true) {
      skipNextScrollRestore.value = true;
      backgroundRoute.value = null;
      return;
    }

    backgroundRoute.value = null;
  });
});

// 组件卸载时清理
onUnmounted(() => {
  window.removeEventListener('resize', updateDesktop);
  if (removeAfterEachHook) {
    removeAfterEachHook();
    removeAfterEachHook = null;
  }
  if (scrollEl.value) {
    scrollEl.value.removeEventListener('scroll', handleScroll);
  }
  if (scrollTimer) {
    clearTimeout(scrollTimer);
  }
});
</script>

<style>
/* 聊天弹窗动画 */
.chat-modal-enter-active,
.chat-modal-leave-active {
  transition: all 0.3s ease;
}

.chat-modal-enter-from {
  opacity: 0;
  transform: translateX(20px);
}

.chat-modal-leave-to {
  opacity: 0;
  transform: translateX(20px);
}
</style>
