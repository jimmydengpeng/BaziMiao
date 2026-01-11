<template>
  <div class="app-root h-[100dvh] overflow-hidden relative">
    <!-- 云朵装饰背景 -->
    <CloudDecoration />

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
        ref="chatFabRef"
        v-show="showChatFab && !chatModalOpen"
        :hint-text="chatFabHintText"
        :hint-visible="chatFabHintVisible"
        :hint-typing="true"
        :nudge-key="chatFabNudgeKey"
        :nudge-kind="chatFabNudgeKind"
        :sparkle-visible="chatFabSparkleVisible"
        @click="handleChatFabClick"
      />

      <!-- Logo 弹窗（点击左上角 Logo 打开） -->
      <LogoDialog
        v-model="logoDialogOpen"
        @open-chat="openMasterChat"
        @go-home="goHome"
      />

      <!-- 桌面端聊天弹窗 -->
      <div
        v-if="chatModalOpen && isDesktop"
        class="fixed inset-y-4 right-4 z-50 flex w-[420px] max-w-[calc(100vw-32px)] flex-col"
      >
        <UnifiedChat mode="modal" @close="closeChatModal" />
      </div>

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
import CloudDecoration from './components/CloudDecoration.vue';
import ChatFab from './components/ChatFab.vue';
import UnifiedChat from './components/UnifiedChat.vue';
import LogoDialog from './components/LogoDialog.vue';
import { useStore } from './composables/useStore';
import { useUnifiedChatStore } from './composables/useUnifiedChatStore';
import { loadBaziViewState, saveBaziViewState } from './utils/storage';

const router = useRouter();
const route = useRoute();
const { isAuthenticated, activeArchiveId, report, chart } = useStore();
const { isStreamingActive } = useUnifiedChatStore();
const scrollEl = ref<HTMLElement | null>(null);
const chatFabRef = ref<InstanceType<typeof ChatFab> | null>(null);

// ========== ChatFab：提示气泡/动效/提醒 ==========
// 调试开关：先强制显示气泡，方便你肉眼确认样式/位置是否正常
const FORCE_CHAT_FAB_HINT = false;
const FORCE_CHAT_FAB_HINT_TEXT = '要不要，我帮你看看？';

// 命盘页提示策略（可按体感微调）
const CHART_ENTRY_HINT_DELAY_MS = 5000; // 从其他页面进入命盘解析后，5s 后提示
const CHART_ENTRY_HINT_DURATION_MS = 5000; // 气泡持续显示 5s

const chatFabHintText = ref<string | null>(null);
const chatFabHintVisible = ref(false);
const chatFabNudgeKey = ref(0);
const chatFabNudgeKind = ref<'pop' | 'wiggle'>('pop');
const chatFabSparkleVisible = ref(false);

let chatFabIntroTimer: number | null = null;
let chatFabHideHintTimer: number | null = null;
let chatFabSparkleTimer: number | null = null;

const hideChatFabHint = () => {
  chatFabHintVisible.value = false;
  if (chatFabHideHintTimer) {
    clearTimeout(chatFabHideHintTimer);
    chatFabHideHintTimer = null;
  }
};

const showChatFabHint = (text: string, durationMs = 2500) => {
  chatFabHintText.value = text;
  chatFabHintVisible.value = true;
  if (chatFabHideHintTimer) clearTimeout(chatFabHideHintTimer);
  chatFabHideHintTimer = window.setTimeout(() => {
    chatFabHintVisible.value = false;
    chatFabHideHintTimer = null;
  }, durationMs);
};

const nudgeChatFab = (kind: 'pop' | 'wiggle') => {
  chatFabNudgeKind.value = kind;
  chatFabNudgeKey.value += 1;
};

const pickOne = (items: string[]) => items[Math.floor(Math.random() * items.length)];

const INTRO_HINTS = [
  '要不要我帮你看看？',
  '可以直接问我哦喵~',
  '看不懂的地方，直接问我就好',
  '想知道重点在哪？我来帮你抓',
  '我在这儿，随时可以问',
  // 严肃派
  '我先帮你抓重点',
  '先从格局下手？',
  '要我按时间线讲？',
  '想先看事业还是感情？',
  '先讲用神与忌神？',
  // 娱乐派
  '喵算上线，开盘！',
  '这盘有点东西',
  '来个一句话总结？',
  '我给你“人话版”',
  '要不要先听个重点？',
  // 江湖派
  '此盘刀光剑影',
  '你这命，有门道',
  '且听我一言',
  '我给你拆招',
  '江湖规矩：先看财官',
  '先问一句：你想算啥？',
];

const isChartPage = computed(() => layoutRoute.value.path.startsWith('/bazi/chart/'));

const clearChatFabTimers = () => {
  if (chatFabIntroTimer) {
    clearTimeout(chatFabIntroTimer);
    chatFabIntroTimer = null;
  }
  if (chatFabHideHintTimer) {
    clearTimeout(chatFabHideHintTimer);
    chatFabHideHintTimer = null;
  }
  if (chatFabSparkleTimer) {
    clearTimeout(chatFabSparkleTimer);
    chatFabSparkleTimer = null;
  }
};

const scheduleChartHints = () => {
  if (FORCE_CHAT_FAB_HINT) return;
  clearChatFabTimers();
  hideChatFabHint();

  // 不在命盘页不触发
  if (!isChartPage.value) return;

  // 从其他页面进入命盘解析后：5s 弹出气泡 + 轻微晃动，持续 3s 后消失
  chatFabIntroTimer = window.setTimeout(() => {
    if (!isChartPage.value) return;
    if (chatModalOpen.value) return;
    nudgeChatFab('wiggle');
    showChatFabHint(pickOne(INTRO_HINTS), CHART_ENTRY_HINT_DURATION_MS);
    chatFabIntroTimer = null;
  }, CHART_ENTRY_HINT_DELAY_MS);
};

// 聊天弹窗状态
const chatModalOpen = ref(false);
const isDesktop = ref(false);
const logoDialogOpen = ref(false);

// 聊天“后台回复完成提醒”：
// - 如果用户在等待/回复过程中退出聊天（route 退出或关闭 modal），当流结束后在 ChatFab 右上角点亮微光两点；
// - 用户重新打开聊天后自动清除。
const leftChatWhileStreaming = ref(false);
const isChatUiVisible = computed(() => chatModalOpen.value || route.path === '/chat' || route.path === '/bazi/chat');

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
  // 注意：overlay(/chat) 打开时，route.path 是 /chat，但布局背景页是 layoutRoute
  // 我们希望“浮动对话按钮”只在主要模块出现：命盘解析(/bazi/chart/*)、双人合盘(/compatibility)、命理百科(/encyclopedia)
  // 其他页面（首页、填写生辰信息、档案管理、个人中心等）不显示

  // 聊天页面本身不显示
  if (route.path === '/chat' || route.path === '/bazi/chat') return false;

  const path = layoutRoute.value.path;
  if (path.startsWith('/bazi/chart/')) return true;
  if (path.startsWith('/compatibility')) return true;
  if (path.startsWith('/encyclopedia')) return true;
  return false;
});

// 命盘页提示策略：从其他页面进入命盘页时安排提示；离开时清理定时器
watch(
  () => layoutRoute.value.path,
  (path, prevPath) => {
    if (FORCE_CHAT_FAB_HINT) return;

    const isNowChart = path.startsWith('/bazi/chart/');
    const wasChart = (prevPath ?? '').startsWith('/bazi/chart/');

    // 只在“从非命盘页进入命盘页”时触发（切 tab 不重复）
    if (isNowChart && !wasChart && showChatFab.value && !chatModalOpen.value) {
      scheduleChartHints();
      return;
    }

    // 离开命盘页：清理
    if (!isNowChart) {
      clearChatFabTimers();
      hideChatFabHint();
    }
  },
  { immediate: true }
);

watch(chatModalOpen, (open) => {
  if (FORCE_CHAT_FAB_HINT) return;
  if (open) {
    clearChatFabTimers();
    hideChatFabHint();
  }
});

watch(
  () => showChatFab.value && !chatModalOpen.value,
  (visible) => {
    if (!FORCE_CHAT_FAB_HINT) return;
    if (visible) {
      chatFabHintText.value = FORCE_CHAT_FAB_HINT_TEXT;
      chatFabHintVisible.value = true;
    } else {
      chatFabHintVisible.value = false;
    }
  },
  { immediate: true }
);

watch(isChatUiVisible, (visible) => {
  // 只要回到聊天界面，就清除提醒
  if (visible) {
    leftChatWhileStreaming.value = false;
    chatFabSparkleVisible.value = false;
    if (chatFabSparkleTimer) {
      clearTimeout(chatFabSparkleTimer);
      chatFabSparkleTimer = null;
    }
    return;
  }

  // 聊天界面不可见 + 仍在流式：标记“后台生成中”
  if (isStreamingActive.value) {
    leftChatWhileStreaming.value = true;
  }
});

watch(isStreamingActive, (active, prev) => {
  // 流开始：清除旧提醒
  if (active && !prev) {
    chatFabSparkleVisible.value = false;
    if (chatFabSparkleTimer) {
      clearTimeout(chatFabSparkleTimer);
      chatFabSparkleTimer = null;
    }
    leftChatWhileStreaming.value = false;
    return;
  }

  // 流结束：如果用户曾"中途退出聊天"，且当前不在聊天界面，则点亮提醒
  if (!active && prev) {
    if (leftChatWhileStreaming.value && !isChatUiVisible.value) {
      chatFabSparkleVisible.value = true;
      chatFabRef.value?.showCompletionBubble();  // 显示回复完毕气泡
      
      // 10秒后自动隐藏光晕
      if (chatFabSparkleTimer) clearTimeout(chatFabSparkleTimer);
      chatFabSparkleTimer = window.setTimeout(() => {
        chatFabSparkleVisible.value = false;
        chatFabSparkleTimer = null;
      }, 10000);  // 10秒
    }
    leftChatWhileStreaming.value = false;
  }
});

// 当前页面类型（用于侧边导航/移动端菜单高亮）
const currentPage = computed(() => {
  const path = layoutRoute.value.path;
  if (path.includes('/report')) return 'report';
  if (path.includes('/detail') || path.includes('/pro')) return 'detail';
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
  if (!FORCE_CHAT_FAB_HINT) hideChatFabHint();
  chatFabSparkleVisible.value = false;
  if (chatFabSparkleTimer) {
    clearTimeout(chatFabSparkleTimer);
    chatFabSparkleTimer = null;
  }
  leftChatWhileStreaming.value = false;

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
      const page = currentPage.value as 'chart' | 'report' | 'detail' | 'verification';

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
      const page = currentPage.value as 'chart' | 'report' | 'detail' | 'verification';

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
  clearChatFabTimers();
});
</script>

<style>
/* 样式已移除 - 不再使用动画效果 */
</style>
