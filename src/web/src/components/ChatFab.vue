<template>
  <!-- 全局浮动聊天按钮：支持拖拽定位 -->
  <button
    ref="fabRef"
    :style="fabStyle"
    class="chat-fab fixed z-40 flex h-14 w-14 items-center justify-center rounded-full bg-gradient-to-br from-[var(--accent)] to-[var(--accent-2)] text-sm font-semibold text-[#0a0604] shadow-lg transition hover:-translate-y-1 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--accent-2)] touch-none select-none active:scale-[0.98] lg:w-auto lg:min-w-[120px] lg:justify-start lg:gap-2 lg:px-5 lg:py-3"
    type="button"
    aria-label="喵算大师"
    @pointerdown.prevent="startDrag"
    @click="handleClick"
  >
    <span class="chat-fab__icon" aria-hidden="true">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
      </svg>
    </span>
    <span class="sr-only">喵算大师</span>
    <span class="chat-fab__label hidden lg:inline">喵算大师</span>
  </button>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue';

const emit = defineEmits<{
  (event: 'click'): void;
}>();

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

// 常量配置
const FAB_SIZE = 56;
const MOBILE_SIDE_PADDING = 16;
const DESKTOP_SIDE_PADDING = 24;
const TOP_RESERVED = 76;
const MOBILE_BOTTOM_RESERVED = 100; // 移动端底部预留空间
const DESKTOP_BOTTOM_RESERVED = 48;

// 判断是否为桌面端
const isDesktop = ref(false);

// 事件监听器引用
const fabListeners = ref<{
  onResize?: () => void;
  onPointerMove?: (e: PointerEvent) => void;
  onPointerUp?: (e: PointerEvent) => void;
} | null>(null);

// ========== 辅助函数 ==========
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

// ========== 拖拽逻辑 ==========
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

const handleClick = () => {
  // 拖拽结束后短时间内的点击被忽略，防止误触
  if (fabState.isDragging || fabState.dragMoved) return;
  emit('click');
};

// ========== 样式计算 ==========
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

// ========== 生命周期 ==========
onMounted(() => {
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
</script>

<style scoped>
.chat-fab {
  /* 确保按钮在所有设备上有良好的点击区域 */
  min-height: 56px;
}

/* 桌面端标签形态的过渡 */
@media (min-width: 1024px) {
  .chat-fab {
    border-radius: 28px;
  }
}
</style>
