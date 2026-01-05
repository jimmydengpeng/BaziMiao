<template>
  <!-- 顶部导航栏 - 毛玻璃效果，固定覆盖层 -->
  <header
    class="top-nav fixed left-0 right-0 top-0 z-50 flex h-14 items-center justify-between border-b border-[rgba(255,255,255,0.08)] px-4 backdrop-blur-xl lg:h-16 lg:px-6"
    :class="[
      // 毛玻璃背景：使用主题深蓝色调，半透明
      'bg-[rgba(18,22,33,0.72)]',
      // home 页面可选更透明
      isHome ? 'bg-[rgba(18,22,33,0.15)]' : ''
    ]"
  >
    <!-- 左侧区域 -->
    <div class="flex items-center gap-3">
      <!-- 移动端汉堡菜单按钮（非首页时显示） -->
      <button
        v-if="!isHome"
        class="flex h-10 w-10 items-center justify-center rounded-lg text-white/80 transition hover:bg-white/10 lg:hidden"
        type="button"
        @click="toggleMobileMenu"
        aria-label="打开菜单"
      >
        <svg
          v-if="!isMobileMenuOpen"
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <line x1="3" y1="6" x2="21" y2="6" />
          <line x1="3" y1="12" x2="21" y2="12" />
          <line x1="3" y1="18" x2="21" y2="18" />
        </svg>
        <svg
          v-else
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <line x1="18" y1="6" x2="6" y2="18" />
          <line x1="6" y1="6" x2="18" y2="18" />
        </svg>
      </button>

      <!-- Logo（可点击回首页） -->
      <button
        class="flex items-center gap-2.5 rounded-lg transition hover:opacity-80 lg:gap-3"
        type="button"
        @click="handleLogoClick"
        aria-label="回到首页"
      >
        <div class="h-8 w-8 lg:h-9 lg:w-9">
          <img :src="logoUrl" alt="神机喵算 Logo" class="h-full w-full object-contain" />
        </div>
        <!-- 桌面端始终显示品牌名；移动端仅在首页显示 -->
        <span
          class="font-['Ma_Shan_Zheng',serif] tracking-wide text-[var(--accent-2)]"
          :class="isLanding ? 'text-xl lg:text-2xl' : 'hidden lg:inline lg:text-2xl'"
        >
          神机喵算
        </span>
      </button>
    </div>

    <!-- 中间区域：移动端显示当前模块标题（首页不显示），桌面端显示导航菜单 -->
    <!-- 移动端：当前模块标题（非首页时显示） -->
    <div v-if="!isHome" class="absolute left-1/2 -translate-x-1/2 lg:hidden">
      <span class="text-base font-medium text-white">
        {{ currentModuleLabel }}
      </span>
    </div>

    <!-- 桌面端：主模块导航菜单（命理报告 / 双人合盘等） -->
    <nav class="hidden flex-1 items-center justify-center gap-1 lg:flex">
      <button
        v-for="item in navItems"
        :key="item.key"
        :class="[
          'relative rounded-lg px-4 py-2 text-[15px] font-medium transition',
          isNavActive(item.key)
            ? 'text-[var(--accent-2)]'
            : 'text-white/70 hover:bg-white/5 hover:text-white',
          !isAuthenticated && item.requiresAuth ? 'opacity-70' : ''
        ]"
        type="button"
        :disabled="!isAuthenticated && item.requiresAuth"
        @click="handleModuleClick(item)"
      >
        {{ item.label }}
        <!-- 激活指示器 -->
        <span
          v-if="isNavActive(item.key)"
          class="absolute bottom-0 left-1/2 h-0.5 w-6 -translate-x-1/2 rounded-full bg-[var(--accent)]"
        ></span>
      </button>
    </nav>

    <!-- 右侧区域：用户入口 + 汉堡菜单（移动端） -->
    <div class="flex items-center gap-2">
      <!-- Home 页：右侧显示 CTA，未登录时附带登录入口 -->
      <template v-if="isHome">
        <button
          class="inline-flex h-10 items-center justify-center gap-2 rounded-xl bg-gradient-to-br from-[var(--accent)] to-[var(--accent-2)] px-4 text-sm font-semibold text-[#0a0604] shadow-[0_6px_18px_rgba(214,160,96,0.3)] transition duration-200 hover:-translate-y-[1px] hover:shadow-[0_10px_24px_rgba(214,160,96,0.35)] active:translate-y-0"
          type="button"
          @click="$emit('start')"
        >
          立即开始
        </button>
        <button
          v-if="!isAuthenticated"
          class="hidden h-10 items-center justify-center rounded-lg border border-white/10 bg-white/5 px-3 text-sm text-white/85 transition hover:bg-white/10 lg:inline-flex"
          type="button"
          @click="$emit('goLogin')"
        >
          登录
        </button>
      </template>

      <!-- 非 Home：登录/个人入口 -->
      <template v-else>
        <button
          v-if="isAuthenticated"
          :class="[
            'inline-flex h-10 items-center justify-center gap-2 rounded-lg px-3 text-sm transition lg:px-4',
            activeModule === 'profile'
              ? 'text-[var(--accent-2)]'
              : 'text-white/80 hover:bg-white/10'
          ]"
          type="button"
          @click="$emit('navigate', 'profile')"
        >
          <!-- 用户图标 -->
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
            <circle cx="12" cy="8" r="4" />
            <path d="M4 20c0-4 4-6 8-6s8 2 8 6" />
          </svg>
          <span class="hidden lg:inline">我的</span>
        </button>
        <button
          v-else
          class="inline-flex h-10 items-center justify-center gap-2 rounded-lg border border-white/10 bg-white/5 px-3 text-sm text-white/85 transition hover:bg-white/10"
          type="button"
          @click="$emit('goLogin')"
        >
          登录
        </button>
      </template>
    </div>
  </header>

  <!-- 移动端菜单遮罩 -->
  <Transition name="fade">
    <div
      v-if="isMobileMenuOpen"
      class="fixed inset-0 z-40 bg-black/50 lg:hidden"
      @click="closeMobileMenu"
    ></div>
  </Transition>

  <!-- 移动端抽屉菜单 -->
  <Transition name="slide-left">
    <aside
      v-if="isMobileMenuOpen"
      class="fixed top-14 bottom-0 left-0 z-50 w-72 overflow-y-auto border-r border-[rgba(255,255,255,0.08)] bg-[rgba(18,22,33,0.95)] backdrop-blur-xl lg:hidden"
    >
      <div class="flex flex-col gap-4 p-4">
        <!-- 当前模块的子导航（如果在 bazi 模块内） -->
        <div v-if="activeModule === 'bazi'" class="grid gap-2">
          <div class="text-[11px] uppercase tracking-[0.12em] text-white/60">命理报告</div>
          <button
            v-for="item in baziSubNavItems"
            :key="item.key"
            :class="[
              'flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left text-[15px] transition',
              currentPage === item.key
                ? 'border border-[rgba(255,255,255,0.25)] bg-[rgba(214,160,96,0.22)] text-[var(--accent-2)]'
                : 'text-white hover:bg-white/5',
              item.disabled ? 'opacity-50 cursor-not-allowed' : ''
            ]"
            type="button"
            :disabled="item.disabled"
            @click="handleSubNavClick(item.key)"
          >
            <span class="flex h-9 w-9 items-center justify-center rounded-lg shrink-0">
              <img :src="item.icon" :alt="item.label" class="h-6 w-6 object-contain" />
            </span>
            <span class="font-medium">{{ item.label }}</span>
          </button>
        </div>

        <!-- 分隔线（仅在 bazi 模块内显示） -->
        <div v-if="activeModule === 'bazi'" class="border-t border-white/10"></div>

        <!-- 主模块导航 -->
        <div class="grid gap-2">
          <div class="text-[11px] uppercase tracking-[0.12em] text-white/60">模块导航</div>
          <button
            v-for="item in navItems"
            :key="item.key"
            :class="[
              'flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left text-[15px] transition',
              isNavActive(item.key)
                ? 'border border-[rgba(255,255,255,0.25)] bg-[rgba(214,160,96,0.22)] text-[var(--accent-2)]'
                : 'text-white hover:bg-white/5'
            ]"
            type="button"
            @click="handleModuleClickMobile(item)"
          >
            <span class="font-medium">{{ item.label }}</span>
          </button>
        </div>

        <!-- 快捷入口 -->
        <div class="grid gap-2">
          <div class="text-[11px] uppercase tracking-[0.12em] text-white/60">快捷入口</div>
          <button
            class="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left text-[15px] text-white transition hover:bg-white/5"
            type="button"
            @click="handleQuickAction('form')"
          >
            新建排盘
          </button>
          <button
            class="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left text-[15px] text-white transition hover:bg-white/5"
            type="button"
            @click="handleQuickAction('home')"
          >
            回到首页
          </button>
        </div>
      </div>
    </aside>
  </Transition>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import logoUrl from '../assets/logo-nav.png';
import baziChartIconUrl from '../assets/bazi-chart.png';
import reportIconUrl from '../assets/report.png';
import archiveIconUrl from '../assets/archive.png';
import chatIconUrl from '../assets/chat-dot-square.png';
import { useStore } from '../composables/useStore';

const router = useRouter();
const route = useRoute();
const { activeArchiveId } = useStore();

// Props
const props = defineProps<{
  activeModule: 'bazi' | 'compatibility' | 'profile';
  isHome?: boolean; // 是否在 home 页面
  isAuthenticated?: boolean; // 登录态
  currentPage?: 'chart' | 'report' | 'archive' | 'master-chat' | 'form' | 'home'; // 当前页面
  canViewReport?: boolean; // 是否可以查看报告
}>();

// 事件
const emit = defineEmits<{
  (e: 'navigate', module: 'bazi' | 'compatibility' | 'profile'): void;
  (e: 'goHome'): void;
  (e: 'start'): void;
  (e: 'goLogin'): void;
}>();

// 移动端菜单状态
const isMobileMenuOpen = ref(false);

// 导航项配置（MVP 阶段移除登录限制，所有功能游客可用）
const navItems = [
  { key: 'bazi' as const, label: '命理报告', requiresAuth: false },
  { key: 'compatibility' as const, label: '双人合盘', requiresAuth: false }
];

// 命理报告模块的子导航项
const baziSubNavItems = computed(() => [
  { key: 'chart' as const, label: '八字命盘', icon: baziChartIconUrl, disabled: false },
  { key: 'report' as const, label: '命理报告', icon: reportIconUrl, disabled: !props.canViewReport },
  { key: 'archive' as const, label: '档案列表', icon: archiveIconUrl, disabled: false },
  { key: 'master-chat' as const, label: '神喵大师', icon: chatIconUrl, disabled: false }
]);

// 是否在 landing 页面（用于品牌名显示）
const isLanding = computed(() => props.isHome);

// 仅非 home 时显示激活态
const isNavActive = (key: 'bazi' | 'compatibility') => !props.isHome && props.activeModule === key;

// 切换移动端菜单
const toggleMobileMenu = () => {
  isMobileMenuOpen.value = !isMobileMenuOpen.value;
};

// 关闭移动端菜单
const closeMobileMenu = () => {
  isMobileMenuOpen.value = false;
};

// 处理 Logo 点击
const handleLogoClick = () => {
  closeMobileMenu();
  emit('goHome');
};

// 处理模块导航点击（桌面端）
const handleModuleClick = (item: (typeof navItems)[number]) => {
  emit('navigate', item.key);
};

// 处理模块导航点击（移动端）
const handleModuleClickMobile = (item: (typeof navItems)[number]) => {
  closeMobileMenu();
  emit('navigate', item.key);
};

// 处理子导航点击
const handleSubNavClick = (page: 'chart' | 'report' | 'archive' | 'master-chat') => {
  closeMobileMenu();
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
    case 'archive':
      router.push('/bazi/archives');
      break;
    case 'master-chat':
      router.push('/bazi/chat');
      break;
  }
};

// 处理快捷入口点击
const handleQuickAction = (action: 'form' | 'home') => {
  closeMobileMenu();
  if (action === 'form') {
    router.push('/bazi/form');
  } else {
    router.push('/');
  }
};

// 当前模块标题（移动端显示）
const currentModuleLabel = computed(() => {
  // 如果是 home 页面，显示"首页"
  if (props.isHome) {
    return '首页';
  }
  const labels: Record<string, string> = {
    bazi: '命理报告',
    compatibility: '双人合盘',
    profile: '我的'
  };
  return labels[props.activeModule] || '神机喵算';
});
</script>

<style scoped>
/* 遮罩淡入淡出动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 抽屉滑入滑出动画 */
.slide-left-enter-active,
.slide-left-leave-active {
  transition: transform 0.25s ease;
}

.slide-left-enter-from,
.slide-left-leave-from {
  transform: translateX(-100%);
}

.slide-left-enter-to,
.slide-left-leave-to {
  transform: translateX(0);
}

.slide-left-leave-to {
  transform: translateX(-100%);
}
</style>
