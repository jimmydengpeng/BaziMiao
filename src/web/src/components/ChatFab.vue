<template>
  <!-- 全局浮动聊天按钮：支持拖拽定位 + 角色化动效/提示气泡 -->
  <button
    ref="fabRef"
    :style="fabStyle"
    :class="[
      'chat-fab fixed z-40 touch-none select-none bg-transparent p-0 overflow-visible',
      {
        'is-dragging': fabState.isDragging,
      },
    ]"
    class="h-12 w-12 md:h-14 md:w-14 lg:h-16 lg:w-16"
    type="button"
    aria-label="喵算大师"
    @pointerdown.prevent="startDrag"
    @click="handleClick"
    @mouseenter="handleMouseEnter"
    @mouseleave="handleMouseLeave"
  >
    <!-- 气泡提示 -->
    <Transition name="fab-bubble" appear>
      <div
        v-if="hintVisible && hintText && !fabState.isDragging"
        class="fab-bubble"
        :class="fabState.side === 'right' ? 'is-right' : 'is-left'"
        role="status"
        aria-live="polite"
      >
        <div class="fab-bubble__text">{{ hintText }}</div>
        <div class="fab-bubble__arrow" aria-hidden="true"></div>
      </div>
    </Transition>

    <!-- 呼吸动效层（外）+ 触发动效层（内） -->
    <div class="fab-breathe" :class="{ 'is-paused': fabState.isDragging || isHovering }">
      <div class="fab-nudge" :class="nudgeClass">
        <div class="fab-glow-layer" aria-hidden="true"></div>

        <img :src="chatFabIconUrl" alt="" class="fab-icon" draggable="false" aria-hidden="true" />

        <!-- 回复完成提醒：右上角两点微光 -->
        <div v-if="sparkleVisible" class="fab-sparkle" aria-hidden="true">
          <span class="fab-sparkle__dot fab-sparkle__dot--a"></span>
          <span class="fab-sparkle__dot fab-sparkle__dot--b"></span>
        </div>
      </div>
    </div>

    <span class="sr-only">喵算大师</span>
  </button>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted, watch, toRefs } from 'vue';
import chatFabIconUrl from '../assets/chat_fab.png';

const props = withDefaults(defineProps<{
  hintText?: string | null;
  hintVisible?: boolean;
  nudgeKey?: number;
  nudgeKind?: 'pop' | 'wiggle';
  sparkleVisible?: boolean;
}>(), {
  hintText: null,
  hintVisible: false,
  nudgeKey: 0,
  nudgeKind: 'pop',
  sparkleVisible: false,
});

const { hintText, hintVisible, sparkleVisible } = toRefs(props);

const emit = defineEmits<{
  (event: 'click'): void;
}>();

const fabRef = ref<HTMLElement | null>(null);

// ========== 浮动按钮拖拽状态 ==========
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

// ========== 动画状态（外部触发） ==========
const isHovering = ref(false);
const nudgeClass = ref<string>('');
let nudgeTimer: number | null = null;

// ========== 常量配置 ==========
const MOBILE_SIDE_PADDING = 16;
const DESKTOP_SIDE_PADDING = 24;
const TOP_RESERVED = 76;
const MOBILE_BOTTOM_RESERVED = 100;
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

const getFabSize = () => {
  const rect = fabRef.value?.getBoundingClientRect();
  const width = rect?.width ?? 0;
  // 与模板的 Tailwind 尺寸保持一致：移动端 48，桌面端 64（中间档 56）
  if (width > 0) return width;
  if (window.matchMedia('(min-width: 1024px)').matches) return 64;
  if (window.matchMedia('(min-width: 768px)').matches) return 56;
  return 48;
};

const clampY = (y: number) => {
  const topLimit = TOP_RESERVED;
  const bottomLimit = getBottomReserved();
  const maxY = window.innerHeight - bottomLimit - getFabSize();
  return Math.min(Math.max(y, topLimit), Math.max(topLimit, maxY));
};

const clampX = (x: number) => {
  const padding = getSidePadding();
  const maxX = window.innerWidth - getFabSize() - padding;
  return Math.min(Math.max(x, padding), Math.max(padding, maxX));
};

const getDefaultY = () => {
  if (typeof window === 'undefined') return 0;
  const bottom = getBottomReserved();
  return clampY(window.innerHeight - bottom - getFabSize());
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

watch(
  () => props.nudgeKey,
  () => {
    if (nudgeTimer) {
      clearTimeout(nudgeTimer);
      nudgeTimer = null;
    }

    nudgeClass.value = props.nudgeKind === 'wiggle' ? 'is-wiggle' : 'is-pop';
    nudgeTimer = window.setTimeout(() => {
      nudgeClass.value = '';
      nudgeTimer = null;
    }, 900);
  }
);

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
    const size = getFabSize();
    fabState.dragX = clampX(e.clientX - size / 2);
    fabState.dragY = clampY(e.clientY - size / 2);
  };

  const onPointerUp = (e: PointerEvent) => {
    const targetSide = e.clientX < window.innerWidth / 2 ? 'left' : 'right';
    fabState.side = targetSide;
    const size = getFabSize();
    fabState.y = clampY(e.clientY - size / 2);
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

  // 移动端触觉反馈
  if ('vibrate' in navigator) {
    navigator.vibrate(50);
  }

  emit('click');
};

// ========== 悬停处理 ==========
const handleMouseEnter = () => {
  isHovering.value = true;
};

const handleMouseLeave = () => {
  isHovering.value = false;
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
  if (nudgeTimer) {
    clearTimeout(nudgeTimer);
    nudgeTimer = null;
  }
});
</script>

<style scoped>
/* ========== 基础样式 ========== */
.chat-fab {
  /* position: fixed 由 Tailwind class 提供，不要在这里覆盖 */
  border: none;
  cursor: pointer;
  outline: none;
  opacity: 1;
}

/* 键盘可访问：只在 focus-visible 时出现描边（不影响“角色感”） */
.chat-fab:focus-visible {
  outline: 2px solid var(--accent-2, #f0c07a);
  outline-offset: 5px;
}

/* ========== 呼吸（4~6s 一轮，轻） ========== */
.fab-breathe {
  position: absolute;
  inset: 0;
  pointer-events: none;
  animation: chatfab-breathe 5.2s ease-in-out infinite;
  transform-origin: 50% 60%;
  will-change: transform;
}

.fab-breathe.is-paused {
  animation: none;
}

@keyframes chatfab-breathe {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-2px);
  }
}

/* ========== 触发动效（一次） ========== */
.fab-nudge {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.fab-nudge.is-pop {
  animation: chatfab-pop 0.75s cubic-bezier(0.2, 0.9, 0.2, 1) both;
}

@keyframes chatfab-pop {
  0% {
    transform: translateY(0) scale(1);
  }
  35% {
    transform: translateY(-7px) scale(1.05);
  }
  100% {
    transform: translateY(0) scale(1);
  }
}

.fab-nudge.is-wiggle {
  animation: chatfab-wiggle 0.7s ease-in-out both;
}

@keyframes chatfab-wiggle {
  0%,
  100% {
    transform: rotate(0deg);
  }
  25% {
    transform: rotate(-7deg);
  }
  50% {
    transform: rotate(0deg);
  }
  75% {
    transform: rotate(7deg);
  }
}

/* ========== 光晕层（轻，不像按钮） ========== */
.fab-glow-layer {
  position: absolute;
  inset: -10px;
  border-radius: 999px;
  pointer-events: none;
  background: radial-gradient(circle at 50% 55%, rgba(240, 192, 122, 0.22) 0%, rgba(240, 192, 122, 0) 65%);
  filter: blur(6px);
  opacity: 0.55;
  animation: chatfab-glow 5.2s ease-in-out infinite;
  will-change: opacity, transform;
}

@keyframes chatfab-glow {
  0%,
  100% {
    opacity: 0.45;
    transform: scale(0.98);
  }
  50% {
    opacity: 0.65;
    transform: scale(1.02);
  }
}

/* ========== 主图片样式 ========== */
.fab-icon {
  position: relative;
  z-index: 2;
  display: block;
  width: 100%;
  height: 100%;
  filter: drop-shadow(0 8px 14px rgba(0, 0, 0, 0.18));
  transition:
    filter 0.3s ease,
    transform 0.3s ease;
  will-change: filter, transform;
}

/* ========== 悬停效果（轻） ========== */
.chat-fab:hover {
  transform: translateY(-3px);
}

.chat-fab:hover .fab-icon {
  filter: brightness(1.06) drop-shadow(0 10px 18px rgba(0, 0, 0, 0.22));
}

/* ========== 点击效果 ========== */
.chat-fab:active {
  transform: translateY(-1px) scale(0.98);
  transition: transform 0.1s ease;
}

/* ========== 拖拽状态 ========== */
.chat-fab.is-dragging {
  transform: scale(1.04);
  cursor: grabbing;
  transition: none;
}

.chat-fab.is-dragging .fab-icon {
  filter: brightness(1.06) drop-shadow(0 10px 18px rgba(0, 0, 0, 0.22));
}

/* ========== 气泡提示 ========== */
.fab-bubble {
  position: absolute;
  bottom: calc(100% + 10px);
  max-width: min(240px, calc(100vw - 48px));
  pointer-events: none;
  z-index: 20;
  border-radius: 14px;
  padding: 10px 12px;
  background: rgba(18, 20, 28, 0.86);
  backdrop-filter: blur(16px);
  box-shadow: 0 16px 34px rgba(0, 0, 0, 0.35);
  color: rgba(255, 255, 255, 0.92);
  font-size: 13px;
  line-height: 1.25rem;
}

.fab-bubble.is-right {
  right: 0;
}

.fab-bubble.is-left {
  left: 0;
}

.fab-bubble__text {
  white-space: nowrap;
}

.fab-bubble__arrow {
  position: absolute;
  bottom: -7px;
  width: 0;
  height: 0;
  border-left: 7px solid transparent;
  border-right: 7px solid transparent;
  border-top: 8px solid rgba(18, 20, 28, 0.86);
  filter: drop-shadow(0 8px 10px rgba(0, 0, 0, 0.25));
}

.fab-bubble.is-right .fab-bubble__arrow {
  right: 16px;
}

.fab-bubble.is-left .fab-bubble__arrow {
  left: 16px;
}

.fab-bubble-enter-active,
.fab-bubble-leave-active {
  transition: opacity 180ms ease, transform 220ms cubic-bezier(0.2, 0.9, 0.2, 1);
}

.fab-bubble-enter-from,
.fab-bubble-leave-to {
  opacity: 0;
  transform: translateY(6px) scale(0.98);
}

.fab-bubble-enter-to,
.fab-bubble-leave-from {
  opacity: 1;
  transform: translateY(0) scale(1);
}

/* ========== 回复完成微光（两点） ========== */
.fab-sparkle {
  position: absolute;
  top: 6px;
  right: 6px;
  z-index: 3;
  width: 14px;
  height: 14px;
  pointer-events: none;
}

.fab-sparkle__dot {
  position: absolute;
  border-radius: 999px;
  background: radial-gradient(circle, rgba(240, 192, 122, 1) 0%, rgba(214, 160, 96, 0.75) 45%, rgba(240, 192, 122, 0) 70%);
  animation: chatfab-sparkle 1.35s ease-in-out infinite;
  opacity: 0.9;
}

.fab-sparkle__dot--a {
  width: 8px;
  height: 8px;
  top: 0;
  left: 4px;
}

.fab-sparkle__dot--b {
  width: 5px;
  height: 5px;
  top: 7px;
  left: 0;
  animation-delay: 0.25s;
  opacity: 0.75;
}

@keyframes chatfab-sparkle {
  0%,
  100% {
    transform: scale(0.85);
    filter: blur(0px);
    opacity: 0.55;
  }
  50% {
    transform: scale(1.05);
    filter: blur(0.2px);
    opacity: 0.95;
  }
}

/* ========== 减弱动画（尊重用户偏好） ========== */
@media (prefers-reduced-motion: reduce) {
  .fab-breathe,
  .fab-glow-layer,
  .fab-nudge.is-pop,
  .fab-nudge.is-wiggle,
  .fab-sparkle__dot {
    animation: none !important;
  }

  .chat-fab:hover {
    transform: translateY(-2px);
  }
}
</style>
