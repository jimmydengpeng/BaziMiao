<template>
  <!-- 顶部导航栏 - 毛玻璃效果，固定覆盖层 -->
  <header
    class="top-nav fixed left-0 right-0 top-0 z-50 flex h-14 items-center justify-between border-b border-[rgba(255,255,255,0.08)] px-4 backdrop-blur-xl lg:h-16 lg:px-6"
    :class="[
      // 毛玻璃背景：使用主题深蓝色调，半透明
      'bg-[rgba(18,22,33,0.72)]',
      // landing 页面可选更透明
      isLanding ? 'bg-[rgba(18,22,33,0.55)]' : ''
    ]"
  >
    <!-- 左侧区域 -->
    <div class="flex items-center gap-3">
      <!-- Logo（可点击回首页） -->
      <button
        class="flex items-center gap-2.5 rounded-lg transition hover:opacity-80 lg:gap-3"
        type="button"
        @click="$emit('goHome')"
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
    <div v-if="!isLanding" class="absolute left-1/2 -translate-x-1/2 lg:hidden">
      <span class="text-base font-medium text-white">
        {{ currentModuleLabel }}
      </span>
    </div>

    <!-- 桌面端：导航菜单 -->
    <nav class="hidden flex-1 items-center justify-center gap-1 lg:flex">
      <button
        v-for="item in navItems"
        :key="item.key"
        :class="[
          'relative rounded-lg px-4 py-2 text-[15px] font-medium transition',
          isNavActive(item.key)
            ? 'text-[var(--accent-2)]'
            : 'text-white/70 hover:bg-white/5 hover:text-white'
        ]"
        type="button"
        @click="$emit('navigate', item.key)"
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
      <!-- 用户入口 -->
      <button
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

      <!-- 移动端：汉堡菜单按钮（仅在命理报告模块显示） -->
      <button
        v-if="activeModule === 'bazi'"
        class="inline-flex h-10 w-10 items-center justify-center rounded-lg text-white/80 transition hover:bg-white/10 lg:hidden"
        type="button"
        @click="$emit('toggleSideNav')"
        aria-label="打开菜单"
      >
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="4" y1="7" x2="20" y2="7" />
          <line x1="4" y1="12" x2="20" y2="12" />
          <line x1="4" y1="17" x2="20" y2="17" />
        </svg>
      </button>
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import logoUrl from '../assets/logo-bazi_meow.png';

// Props
const props = defineProps<{
  activeModule: 'bazi' | 'compatibility' | 'profile';
  isLanding?: boolean; // 是否在 landing 页面
}>();

// 事件
defineEmits<{
  (e: 'navigate', module: 'bazi' | 'compatibility' | 'profile'): void;
  (e: 'toggleSideNav'): void;
  (e: 'goHome'): void;
}>();

// 导航项配置
const navItems = [
  { key: 'bazi' as const, label: '命理报告' },
  { key: 'compatibility' as const, label: '双人合盘' }
];

// 仅非 landing 时显示激活态
const isNavActive = (key: 'bazi' | 'compatibility') => !props.isLanding && props.activeModule === key;

// 当前模块标题（移动端显示）
const currentModuleLabel = computed(() => {
  // 如果是 landing 页面，显示"首页"
  if (props.isLanding) {
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
