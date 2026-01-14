<template>
  <div
    class="[--safe-top:0px] [--safe-top:env(safe-area-inset-top,0px)] [--nav-height:45px] md:[--nav-height:3.5rem] lg:[--nav-height:4rem]"
  >
  <!-- 顶部导航栏 - 毛玻璃效果，固定覆盖层 -->
  <!-- 三档响应式：手机(<768px) h-12 px-3, 平板(768-1023px) h-14 px-4, 桌面(≥1024px) h-16 px-6 -->
  <!-- iOS 添加到主屏幕后，通过 safe-area-inset-top 让导航栏延伸到状态栏区域 -->
  <!-- touch-none: 阻止触摸事件参与 body 的滚动行为链，确保惯性滚动时点击也能立即响应 -->
  <header
    class="fixed left-0 right-0 top-0 z-50 flex flex-col backdrop-blur-xl px-3 md:px-4 lg:px-6 touch-none border-b border-[rgba(255,255,255,0.08)] pt-[var(--safe-top)] min-h-[calc(var(--safe-top)+var(--nav-height))]"
    :class="[navBgClass]"
  >
    <div class="relative flex w-full items-center pt-1 justify-between">
      <!-- 左侧区域：Logo -->
      <div class="flex items-center gap-2 md:gap-3">
        <!-- Logo（点击弹出对话框） -->
        <button
          class="flex items-center gap-1.5 rounded-lg transition hover:opacity-80 md:gap-2.5 lg:gap-3"
          type="button"
          @click="handleLogoClick"
          aria-label="打开神机喵算菜单"
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
      <!-- 移动端：当前模块标题（非首页时显示，可点击展开模块列表） -->
      <button
        v-if="!isHome"
        class="absolute left-1/2 -translate-x-1/2 md:hidden inline-flex items-center gap-1.5 text-lg font-semibold text-white transition-opacity hover:opacity-80"
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
          v-for="item in desktopNavItems"
          :key="item.key"
          :class="[
            'relative rounded-lg py-1.5 font-medium transition',
            // 字体大小：平板 text-sm, 桌面 text-[15px]
            'text-sm md:px-3 md:py-2 lg:text-[15px] lg:px-4',
            isNavActive(item)
              ? 'text-[var(--accent-2)]'
              : 'text-white/70 hover:bg-white/5 hover:text-white',
            !isAuthenticated && item.requiresAuth ? 'opacity-70' : ''
          ]"
          type="button"
          :disabled="!isAuthenticated && item.requiresAuth"
          @click="handleNavClick(item)"
        >
          {{ item.label }}
          <!-- 激活指示器 -->
          <span
            v-if="isNavActive(item)"
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
          class="inline-flex h-9 items-center justify-center rounded-lg border border-white/10 bg-white/5 px-2.5 text-xs text-white/85 transition hover:bg-white/10 md:h-10 md:px-3 md:text-sm"
          type="button"
          @click="$emit('goLogin')"
        >
          登录
        </button>
      </template>

      <!-- 非 Home：登录/个人入口 -->
      <template v-else>
        <button
          v-if="activeModule === 'bazi' && currentPage !== 'chart'"
          class="hidden h-9 w-9 items-center justify-center rounded-lg text-white/80 transition hover:bg-white/10 md:flex md:h-10 md:w-10"
          type="button"
          @click="handleArchiveClick"
          aria-label="切换档案"
        >
          <img :src="switchArchiveIconUrl" alt="切换档案" class="h-5 w-5 object-contain md:h-6 md:w-6" />
        </button>
        <button
          v-if="isAuthenticated"
          :class="[
            'hidden lg:inline-flex items-center justify-center gap-1.5 rounded-lg text-sm transition',
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
          <span class="hidden lg:inline">{{ NAV_LABELS.profile }}</span>
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
    </div>

    <!-- 移动端：模块列表直接展开在顶部导航栏内 -->
    <div
      class="md:hidden grid overflow-hidden transition-[grid-template-rows,opacity] duration-250 ease-out"
      :class="isModuleMenuOpen ? 'grid-rows-[1fr] opacity-100' : 'grid-rows-[0fr] opacity-0 pointer-events-none'"
      :aria-hidden="!isModuleMenuOpen"
    >
      <div class="overflow-hidden">
        <div class="flex flex-col gap-3 p-4">
          <!-- 模块导航（横向可换行、居中排列） -->
          <div class="grid gap-2">
            <div class="flex flex-wrap justify-center gap-3">
              <button
                v-for="item in primaryNavItems"
                :key="item.key"
                :class="[
                  'flex w-[96px] flex-col items-center gap-2 rounded-xl px-1.5 py-2.5 text-center transition',
                  'text-xs font-medium',
                  isNavActive(item)
                    ? 'bg-[rgba(214,160,96,0.18)] text-[var(--accent-2)] border border-[rgba(214,160,96,0.35)]'
                    : 'text-white/85 hover:bg-white/10 border border-transparent',
                  !isAuthenticated && item.requiresAuth ? 'opacity-70' : ''
                ]"
                type="button"
                :disabled="!isAuthenticated && item.requiresAuth"
                @click="handleModuleClickMobile(item)"
              >
                <span
                  class="flex h-12 w-12 items-center justify-center rounded-xl bg-white/5"
                  :class="isNavActive(item) ? 'bg-[rgba(214,160,96,0.2)]' : ''"
                >
                  <img :src="item.icon" :alt="item.label" class="h-8 w-8 object-contain" />
                </span>
                <span class="leading-tight">{{ item.label }}</span>
              </button>
            </div>
          </div>
        </div>
      </div>
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

  <!-- 移动端/平板端：完整下拉菜单（点击汉堡按钮打开） -->
  <Transition name="slide-down">
    <div
      v-if="isHamburgerMenuOpen"
      class="hamburger-menu-panel fixed left-0 right-0 z-50 overflow-y-auto border-b border-[rgba(255,255,255,0.08)] backdrop-blur-xl lg:hidden touch-none"
      :class="[navBgClass]"
    >
      <div class="flex flex-col gap-2 px-4 py-2">
        <button
          class="flex items-center gap-3 rounded-xl px-4 py-3 text-sm text-white/85 transition hover:bg-white/10"
          type="button"
          @click="handleMenuAction('archives')"
        >
          <span class="flex h-9 w-9 items-center justify-center rounded-lg bg-white/5">
            <img :src="archiveListIconUrl" :alt="NAV_LABELS.archives" class="h-5 w-5 object-contain" />
          </span>
          <span class="font-medium">{{ NAV_LABELS.archives }}</span>
        </button>
        <div class="h-px w-full bg-white/5"></div>
        <button
          class="flex items-center gap-3 rounded-xl px-4 py-3 text-sm text-white/85 transition hover:bg-white/10"
          type="button"
          @click="handleMenuAction('profile')"
        >
          <span class="flex h-9 w-9 items-center justify-center rounded-lg bg-white/5">
            <img :src="profileMenuIconUrl" :alt="NAV_LABELS.profile" class="h-5 w-5 object-contain" />
          </span>
          <span class="font-medium">{{ NAV_LABELS.profile }}</span>
        </button>
        <div class="h-px w-full bg-white/5"></div>
        <button
          class="flex items-center gap-3 rounded-xl px-4 py-3 text-sm text-white/85 transition hover:bg-white/10"
          type="button"
          @click="handleMenuAction('about')"
        >
          <span class="flex h-9 w-9 items-center justify-center rounded-lg bg-white/5">
            <img :src="aboutIconUrl" :alt="NAV_LABELS.about" class="h-5 w-5 object-contain" />
          </span>
          <span class="font-medium">{{ NAV_LABELS.about }}</span>
        </button>
      </div>
    </div>
  </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import logoUrl from '../assets/logo-nav.png';
import baziChartIconUrl from '../assets/module-bazi.png';
import compatibilityIconUrl from '../assets/module-compatibility.png';
import encyclopediaIconUrl from '../assets/module-encyclopedia.png';
import archiveListIconUrl from '../assets/menu-archive.png';
import switchArchiveIconUrl from '../assets/change-arch.png';
import profileMenuIconUrl from '../assets/menu-user.png';
import aboutIconUrl from '../assets/menu-about.png';
import { lockBackgroundScroll } from '../utils/scroll-lock';

const router = useRouter();

// Props
const props = defineProps<{
  activeModule: 'bazi' | 'compatibility' | 'profile' | 'master' | 'encyclopedia';
  isHome?: boolean; // 是否在 home 页面
  isAuthenticated?: boolean; // 登录态
  currentPage?: 'chart' | 'report' | 'detail' | 'verification' | 'archive' | 'master-chat' | 'form' | 'home' | 'about'; // 当前页面
  canViewReport?: boolean; // 是否可以查看报告
}>();

// 事件
const emit = defineEmits<{
  (e: 'navigate', module: 'bazi' | 'compatibility' | 'profile' | 'master' | 'encyclopedia'): void;
  (e: 'openLogoDialog'): void;
  (e: 'start'): void;
  (e: 'goLogin'): void;
  (e: 'openArchivePicker'): void;
}>();

// 移动端菜单状态：两个独立的菜单
const isModuleMenuOpen = ref(false); // 中间标题按钮的模块导航菜单
const isHamburgerMenuOpen = ref(false); // 右侧汉堡按钮的完整菜单

let releaseMenuScrollLock: (() => void) | null = null;

// 导航项配置
const NAV_LABELS = {
  bazi: '神机命盘',
  compatibility: '双人合盘',
  encyclopedia: '命理百科',
  archives: '命盘档案',
  profile: '我的',
  about: '关于我们',
  home: '首页',
  newArchive: '新建档案',
  master: '神喵大师'
} as const;

const primaryNavItems = [
  { key: 'bazi' as const, label: NAV_LABELS.bazi, requiresAuth: false, icon: baziChartIconUrl, type: 'module' as const },
  { key: 'compatibility' as const, label: NAV_LABELS.compatibility, requiresAuth: false, icon: compatibilityIconUrl, type: 'module' as const },
  { key: 'encyclopedia' as const, label: NAV_LABELS.encyclopedia, requiresAuth: false, icon: encyclopediaIconUrl, type: 'module' as const }
];

const secondaryDesktopItems = [
  { key: 'archives' as const, label: NAV_LABELS.archives, requiresAuth: false, type: 'route' as const, path: '/bazi/archives' },
  { key: 'about' as const, label: NAV_LABELS.about, requiresAuth: false, type: 'route' as const, path: '/about' }
];

const desktopNavItems = [...primaryNavItems, ...secondaryDesktopItems];


// 是否在 landing 页面（用于品牌名显示）
const isLanding = computed(() => props.isHome);
const navBgClass = computed(() =>
  props.isHome ? 'bg-[rgba(18,22,33,0.15)]' : 'bg-[rgba(18,22,33,0.75)]'
);

// 仅非 home 时显示激活态
const isNavActive = (item: (typeof desktopNavItems)[number]) => {
  if (props.isHome) return false;
  if (item.type === 'module') {
    if (item.key === 'bazi') {
      return (
        props.activeModule === 'bazi' &&
        props.currentPage !== 'archive' &&
        props.currentPage !== 'form'
      );
    }
    return props.activeModule === item.key;
  }
  if (item.key === 'archives') {
    return props.currentPage === 'archive' || props.currentPage === 'form';
  }
  return props.currentPage === 'about';
};


// 切换模块导航菜单（移动端中间标题按钮使用）
const toggleModuleMenu = () => {
  if (!isModuleMenuOpen.value) {
    closeHamburgerMenu();
  }
  isModuleMenuOpen.value = !isModuleMenuOpen.value;
};

// 关闭模块导航菜单
const closeModuleMenu = () => {
  isModuleMenuOpen.value = false;
};

// 切换汉堡菜单（移动端和平板端右侧汉堡按钮使用）
const toggleHamburgerMenu = () => {
  if (!isHamburgerMenuOpen.value) {
    closeModuleMenu();
  }
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
  emit('openLogoDialog');
};

// 处理模块导航点击（桌面端）
const handleNavClick = (item: (typeof desktopNavItems)[number]) => {
  if (item.type === 'module') {
    emit('navigate', item.key);
    return;
  }
  router.push(item.path);
};

// 处理模块导航点击（移动端）
const handleModuleClickMobile = (item: (typeof primaryNavItems)[number]) => {
  closeModuleMenu();
  closeHamburgerMenu();
  emit('navigate', item.key);
};


const handleArchiveClick = () => {
  closeModuleMenu();
  closeHamburgerMenu();
  emit('openArchivePicker');
};

const handleMenuAction = (action: 'archives' | 'profile' | 'about') => {
  closeModuleMenu();
  closeHamburgerMenu();
  switch (action) {
    case 'archives':
      router.push('/bazi/archives');
      break;
    case 'profile':
      router.push('/profile');
      break;
    case 'about':
      router.push('/about');
      break;
  }
};

watch(
  () => isModuleMenuOpen.value || isHamburgerMenuOpen.value,
  (isOpen) => {
    if (isOpen) {
      if (!releaseMenuScrollLock) {
        releaseMenuScrollLock = lockBackgroundScroll();
      }
    } else if (releaseMenuScrollLock) {
      releaseMenuScrollLock();
      releaseMenuScrollLock = null;
    }
  }
);

onUnmounted(() => {
  if (releaseMenuScrollLock) {
    releaseMenuScrollLock();
    releaseMenuScrollLock = null;
  }
});

// 当前模块标题（移动端显示）
const primaryModuleKeys = new Set(['bazi', 'compatibility', 'encyclopedia']);

const currentModuleLabel = computed(() => {
  // 如果是 home 页面，显示"首页"
  if (props.isHome) {
    return NAV_LABELS.home;
  }
  if (props.currentPage === 'form') {
    return NAV_LABELS.newArchive;
  }
  if (props.currentPage === 'archive') {
    return NAV_LABELS.archives;
  }
  if (props.currentPage === 'about') {
    return NAV_LABELS.about;
  }
  if (props.activeModule === 'profile') {
    return NAV_LABELS.profile;
  }
  if (props.activeModule === 'master') {
    return NAV_LABELS.master;
  }
  if (primaryModuleKeys.has(props.activeModule)) {
    return NAV_LABELS[props.activeModule];
  }
  return NAV_LABELS.bazi;
});

</script>

<style scoped>
.hamburger-menu-panel {
  top: calc(var(--safe-top) + var(--nav-height));
  max-height: calc(100vh - (var(--safe-top) + var(--nav-height)));
}
</style>
