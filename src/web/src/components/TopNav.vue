<template>
  <!-- 顶部导航栏 - 毛玻璃效果，固定覆盖层 -->
  <!-- 三档响应式：手机(<768px) h-12 px-3, 平板(768-1023px) h-14 px-4, 桌面(≥1024px) h-16 px-6 -->
  <!-- iOS 添加到主屏幕后，通过 safe-area-inset-top 让导航栏延伸到状态栏区域 -->
  <header
    class="top-nav fixed left-0 right-0 top-0 z-50 flex items-center justify-between border-b border-[rgba(255,255,255,0.08)] backdrop-blur-xl px-3 md:px-4 lg:px-6"
    :class="[
      // 毛玻璃背景：使用主题深蓝色调，半透明
      'bg-[rgba(18,22,33,0.75)]',
      // home 页面可选更透明
      isHome ? 'bg-[rgba(18,22,33,0.15)]' : ''
    ]"
  >
    <!-- 左侧区域：Logo -->
    <div class="flex items-center gap-2 md:gap-3">
      <!-- Logo（可点击回首页） -->
      <button
        class="flex items-center gap-1.5 rounded-lg transition hover:opacity-80 md:gap-2.5 lg:gap-3"
        type="button"
        @click="handleLogoClick"
        aria-label="回到首页"
      >
        <!-- Logo尺寸：手机 h-7 w-7, 平板 h-8 w-8, 桌面 h-9 w-9 -->
        <div class="h-7 w-7 md:h-8 md:w-8 lg:h-9 lg:w-9">
          <img :src="logoUrl" alt="神机喵算 Logo" class="h-full w-full object-contain" />
        </div>
        <!-- 品牌名：手机端仅在首页显示，平板和桌面端始终显示 -->
        <span
          class="font-['Ma_Shan_Zheng',serif] tracking-wide text-[var(--accent-2)]"
          :class="isLanding ? 'text-lg md:text-xl lg:text-2xl' : 'hidden md:block md:text-xl lg:text-2xl'"
        >
          神机喵算
        </span>
      </button>
    </div>

    <!-- 中间区域：移动端显示当前模块标题（首页不显示），平板和桌面端显示导航菜单 -->
    <!-- 移动端：当前模块标题（非首页时显示，可点击打开仅模块导航的下拉菜单） -->
    <button
      v-if="!isHome"
      class="absolute left-1/2 -translate-x-1/2 md:hidden inline-flex items-center gap-1.5 text-sm font-medium text-white transition-opacity hover:opacity-80"
      type="button"
      @click="toggleModuleMenu"
      aria-haspopup="true"
      :aria-expanded="isModuleMenuOpen"
    >
      <span>
        {{ currentModuleLabel }}
      </span>
      <!-- 下拉小箭头 -->
      <svg
        class="w-4 h-4 text-white/70 transition-transform"
        :class="isModuleMenuOpen ? 'rotate-180' : ''"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
        aria-hidden="true"
      >
        <polyline points="6 9 12 15 18 9" />
      </svg>
    </button>

    <!-- 平板和桌面端：主模块导航菜单（命理报告 / 双人合盘等） -->
    <nav class="hidden flex-1 items-center justify-center gap-1 overflow-x-auto md:flex">
      <button
        v-for="item in navItems"
        :key="item.key"
        :class="[
          'relative rounded-lg py-1.5 font-medium transition',
          // 字体大小：平板 text-sm, 桌面 text-[15px]
          'text-sm md:px-3 md:py-2 lg:text-[15px] lg:px-4',
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

    <!-- 右侧区域：用户入口 + 汉堡菜单（移动端/平板端） -->
    <div class="flex items-center gap-1.5 md:gap-2">
      <!-- Home 页：右侧显示 CTA，未登录时附带登录入口 -->
      <template v-if="isHome">
        <button
          class="inline-flex items-center justify-center gap-1.5 rounded-xl bg-gradient-to-br from-[var(--accent)] to-[var(--accent-2)] font-semibold text-[#0a0604] shadow-[0_6px_18px_rgba(214,160,96,0.3)] transition duration-200 hover:-translate-y-[1px] hover:shadow-[0_10px_24px_rgba(214,160,96,0.35)] active:translate-y-0 h-9 px-3 text-xs md:h-10 md:px-4 md:text-sm md:gap-2"
          type="button"
          @click="$emit('start')"
        >
          立即开始
        </button>
        <button
          v-if="!isAuthenticated"
          class="hidden h-9 items-center justify-center rounded-lg border border-white/10 bg-white/5 px-2.5 text-xs text-white/85 transition hover:bg-white/10 md:h-10 md:px-3 md:text-sm lg:inline-flex"
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
            'inline-flex items-center justify-center gap-1.5 rounded-lg text-sm transition',
            // 尺寸：手机 h-9 px-2.5, 平板 h-10 px-3, 桌面 h-10 px-4
            'h-9 px-2.5 md:h-10 md:px-3 lg:px-4',
            activeModule === 'profile'
              ? 'text-[var(--accent-2)]'
              : 'text-white/80 hover:bg-white/10'
          ]"
          type="button"
          @click="$emit('navigate', 'profile')"
        >
          <!-- 用户图标：手机 w-4 h-4, 平板和桌面 w-5 h-5 -->
          <svg class="w-4 h-4 md:w-5 md:h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
            <circle cx="12" cy="8" r="4" />
            <path d="M4 20c0-4 4-6 8-6s8 2 8 6" />
          </svg>
          <span class="hidden lg:inline">我的</span>
        </button>
        <button
          v-else
          class="inline-flex h-9 items-center justify-center gap-1.5 rounded-lg border border-white/10 bg-white/5 px-2.5 text-xs text-white/85 transition hover:bg-white/10 md:h-10 md:px-3 md:text-sm"
          type="button"
          @click="$emit('goLogin')"
        >
          登录
        </button>
      </template>

      <!-- 移动端/平板端汉堡菜单按钮（非首页时显示，放在最右侧，打开完整菜单） -->
      <button
        v-if="!isHome"
        class="flex items-center justify-center rounded-lg text-white/80 transition hover:bg-white/10 lg:hidden h-9 w-9 md:h-10 md:w-10"
        type="button"
        @click="toggleHamburgerMenu"
        aria-label="打开菜单"
        :aria-expanded="isHamburgerMenuOpen"
      >
        <svg
          v-if="!isHamburgerMenuOpen"
          class="w-5 h-5 md:w-6 md:h-6"
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
          class="w-5 h-5 md:w-6 md:h-6"
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
    </div>
  </header>

  <!-- 移动端模块菜单遮罩（仅模块导航） -->
  <Transition name="fade">
    <div
      v-if="isModuleMenuOpen"
      class="fixed inset-0 z-40 bg-black/50 md:hidden"
      @click="closeModuleMenu"
    ></div>
  </Transition>

  <!-- 移动端/平板端汉堡菜单遮罩（完整菜单） -->
  <Transition name="fade">
    <div
      v-if="isHamburgerMenuOpen"
      class="fixed inset-0 z-40 bg-black/50 lg:hidden"
      @click="closeHamburgerMenu"
    ></div>
  </Transition>

  <!-- 移动端：仅模块导航下拉菜单（点击中间标题按钮打开） -->
  <Transition name="slide-down">
    <div
      v-if="isModuleMenuOpen"
      class="fixed left-0 right-0 z-50 overflow-y-auto border-b border-[rgba(255,255,255,0.08)] bg-[rgba(18,22,33,0.95)] backdrop-blur-xl md:hidden"
      :class="[
        'top-12',
        'max-h-[calc(100vh-3rem)]'
      ]"
    >
      <div class="flex flex-col gap-3 p-3">
        <!-- 模块导航（使用完全竖向的列表，样式凸显这是模块基本的切换按钮） -->
        <div class="grid gap-2">
          <div class="text-[10px] uppercase tracking-[0.12em] text-white/60">模块导航</div>
          <div class="flex flex-col gap-1.5">
            <button
              v-for="item in navItems"
              :key="item.key"
              :class="[
                'flex items-center justify-between rounded-lg px-4 py-3 text-left transition',
                'text-sm font-medium',
                isNavActive(item.key)
                  ? 'bg-[rgba(214,160,96,0.15)] text-[var(--accent-2)] border border-[rgba(214,160,96,0.3)]'
                  : 'text-white/90 hover:bg-white/10 border border-transparent',
                !isAuthenticated && item.requiresAuth ? 'opacity-70' : ''
              ]"
              type="button"
              :disabled="!isAuthenticated && item.requiresAuth"
              @click="handleModuleClickMobile(item)"
            >
              <span>{{ item.label }}</span>
              <!-- 激活指示器 -->
              <svg
                v-if="isNavActive(item.key)"
                class="w-5 h-5 text-[var(--accent-2)]"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <polyline points="9 18 15 12 9 6" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  </Transition>

  <!-- 移动端/平板端：完整下拉菜单（点击汉堡按钮打开） -->
  <Transition name="slide-down">
    <div
      v-if="isHamburgerMenuOpen"
      class="fixed left-0 right-0 z-50 overflow-y-auto border-b border-[rgba(255,255,255,0.08)] bg-[rgba(18,22,33,0.95)] backdrop-blur-xl lg:hidden"
      :class="[
        // 根据导航栏高度定位：手机 top-12, 平板 top-14
        'top-12 md:top-14',
        // 最大高度：手机 max-h-[calc(100vh-3rem)], 平板 max-h-[calc(100vh-3.5rem)]
        'max-h-[calc(100vh-3rem)] md:max-h-[calc(100vh-3.5rem)]'
      ]"
    >
      <div class="flex flex-col gap-3 p-3 md:gap-4 md:p-4">
        <!-- 当前模块的侧边导航栏（如果有的话，横向flex布局，尽可能均匀分散填满横向空间） -->
        <div v-if="activeModule === 'bazi'" class="grid gap-2">
          <div class="text-[10px] uppercase tracking-[0.12em] text-white/60 md:text-[11px]">命盘解析 · 核心功能</div>
          <div class="flex gap-2">
            <button
              v-for="item in baziSubNavItems"
              :key="item.key"
              :class="[
                'flex flex-col items-center gap-1.5 rounded-lg px-2 py-2.5 text-center transition flex-1',
                // 字体大小：手机 text-xs, 平板 text-sm
                'text-xs md:text-sm',
                currentPage === item.key
                  ? 'border border-[rgba(255,255,255,0.25)] bg-[rgba(214,160,96,0.22)] text-[var(--accent-2)]'
                  : 'text-white hover:bg-white/5',
                item.disabled ? 'opacity-50 cursor-not-allowed' : ''
              ]"
              type="button"
              :disabled="item.disabled"
              @click="handleSubNavClick(item.key)"
            >
              <span class="flex h-8 w-8 items-center justify-center rounded-lg shrink-0 md:h-9 md:w-9">
                <img :src="item.icon" :alt="item.label" class="h-5 w-5 object-contain md:h-6 md:w-6" />
              </span>
              <span class="font-medium leading-tight">{{ item.label }}</span>
            </button>
          </div>
        </div>

        <!-- 快捷入口 -->
        <div class="grid gap-2">
          <div class="text-[10px] uppercase tracking-[0.12em] text-white/60 md:text-[11px]">快捷入口</div>
          <div class="grid grid-cols-2 gap-2">
            <button
              class="flex items-center justify-center rounded-lg px-3 py-2.5 text-center text-xs text-white transition hover:bg-white/5 md:text-sm"
              type="button"
              @click="handleQuickAction('form')"
            >
              新建排盘
            </button>
            <button
              class="flex items-center justify-center rounded-lg px-3 py-2.5 text-center text-xs text-white transition hover:bg-white/5 md:text-sm"
              type="button"
              @click="handleQuickAction('archive')"
            >
              切换档案
            </button>
          </div>
        </div>

        <!-- 移动端：模块导航（最底部，使用完全竖向的列表） -->
        <div class="grid gap-2 md:hidden">
          <div class="text-[10px] uppercase tracking-[0.12em] text-white/60">模块导航</div>
          <div class="flex flex-col gap-1.5">
            <button
              v-for="item in navItems"
              :key="item.key"
              :class="[
                'flex items-center justify-between rounded-lg px-4 py-3 text-left transition',
                'text-sm font-medium',
                isNavActive(item.key)
                  ? 'bg-[rgba(214,160,96,0.15)] text-[var(--accent-2)] border border-[rgba(214,160,96,0.3)]'
                  : 'text-white/90 hover:bg-white/10 border border-transparent',
                !isAuthenticated && item.requiresAuth ? 'opacity-70' : ''
              ]"
              type="button"
              :disabled="!isAuthenticated && item.requiresAuth"
              @click="handleModuleClickMobile(item)"
            >
              <span>{{ item.label }}</span>
              <!-- 激活指示器 -->
              <svg
                v-if="isNavActive(item.key)"
                class="w-5 h-5 text-[var(--accent-2)]"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <polyline points="9 18 15 12 9 6" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
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
  activeModule: 'bazi' | 'compatibility' | 'profile' | 'master' | 'encyclopedia';
  isHome?: boolean; // 是否在 home 页面
  isAuthenticated?: boolean; // 登录态
  currentPage?: 'chart' | 'report' | 'pro' | 'verification' | 'archive' | 'master-chat' | 'form' | 'home'; // 当前页面
  canViewReport?: boolean; // 是否可以查看报告
}>();

// 事件
const emit = defineEmits<{
  (e: 'navigate', module: 'bazi' | 'compatibility' | 'profile' | 'master' | 'encyclopedia'): void;
  (e: 'goHome'): void;
  (e: 'start'): void;
  (e: 'goLogin'): void;
}>();

// 移动端菜单状态：两个独立的菜单
const isModuleMenuOpen = ref(false); // 中间标题按钮的模块导航菜单
const isHamburgerMenuOpen = ref(false); // 右侧汉堡按钮的完整菜单

// 导航项配置（MVP 阶段移除登录限制，所有功能游客可用）
const navItems = [
  { key: 'bazi' as const, label: '命盘解析', requiresAuth: false },
  { key: 'master' as const, label: '神喵大师', requiresAuth: false },
  { key: 'compatibility' as const, label: '双人合盘', requiresAuth: false },
  { key: 'encyclopedia' as const, label: '命理百科', requiresAuth: false }
];

// 命盘解析模块的子导航项
const baziSubNavItems = computed(() => [
  { key: 'chart' as const, label: '命盘信息', icon: baziChartIconUrl, disabled: false },
  { key: 'report' as const, label: '命理报告', icon: reportIconUrl, disabled: false },
  { key: 'pro' as const, label: '专业细盘', icon: archiveIconUrl, disabled: false },
  { key: 'verification' as const, label: '前事验盘', icon: chatIconUrl, disabled: false }
]);

// 是否在 landing 页面（用于品牌名显示）
const isLanding = computed(() => props.isHome);

// 仅非 home 时显示激活态
const isNavActive = (key: 'bazi' | 'compatibility' | 'master' | 'encyclopedia') =>
  !props.isHome && props.activeModule === key;

// 切换模块导航菜单（移动端中间标题按钮使用）
const toggleModuleMenu = () => {
  isModuleMenuOpen.value = !isModuleMenuOpen.value;
};

// 关闭模块导航菜单
const closeModuleMenu = () => {
  isModuleMenuOpen.value = false;
};

// 切换汉堡菜单（移动端和平板端右侧汉堡按钮使用）
const toggleHamburgerMenu = () => {
  isHamburgerMenuOpen.value = !isHamburgerMenuOpen.value;
};

// 关闭汉堡菜单
const closeHamburgerMenu = () => {
  isHamburgerMenuOpen.value = false;
};

// 处理 Logo 点击
const handleLogoClick = () => {
  closeModuleMenu();
  closeHamburgerMenu();
  emit('goHome');
};

// 处理模块导航点击（桌面端）
const handleModuleClick = (item: (typeof navItems)[number]) => {
  emit('navigate', item.key);
};

// 处理模块导航点击（移动端）
const handleModuleClickMobile = (item: (typeof navItems)[number]) => {
  closeModuleMenu();
  closeHamburgerMenu();
  emit('navigate', item.key);
};

// 处理子导航点击
const handleSubNavClick = (page: 'chart' | 'report' | 'pro' | 'verification' | 'archive' | 'master-chat') => {
  closeHamburgerMenu();
  // 根据页面类型导航到对应路由
  const chartId = (route.params?.id as string | undefined) || activeArchiveId.value || 'temp';
  switch (page) {
    case 'chart': {
      router.push(`/bazi/chart/${chartId}/pillars`);
      break;
    }
    case 'report': {
      router.push(`/bazi/chart/${chartId}/report`);
      break;
    }
    case 'pro': {
      router.push(`/bazi/chart/${chartId}/pro`);
      break;
    }
    case 'verification': {
      router.push(`/bazi/chart/${chartId}/verification`);
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
const handleQuickAction = (action: 'form' | 'archive') => {
  closeHamburgerMenu();
  if (action === 'form') {
    router.push('/bazi/form');
  } else if (action === 'archive') {
    router.push('/bazi/archives');
  }
};

// 当前模块标题（移动端显示）
const currentModuleLabel = computed(() => {
  // 如果是 home 页面，显示"首页"
  if (props.isHome) {
    return '首页';
  }
  const labels: { [key: string]: string } = {
    bazi: '命盘解析',
    compatibility: '双人合盘',
    profile: '我的',
    master: '神喵大师',
    encyclopedia: '命理百科'
  };
  return labels[props.activeModule] || '神机喵算';
});
</script>
