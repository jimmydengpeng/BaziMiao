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
    class="h-14 w-14 md:h-16 md:w-16 lg:h-20 lg:w-20"
    type="button"
    aria-label="喵算大师"
    @pointerdown.prevent="startDrag"
    @click="handleClick"
    @mouseenter="handleMouseEnter"
    @mouseleave="handleMouseLeave"
  >
    <!-- 气泡提示 -->
    <Transition
      appear
      enter-active-class="[transition:opacity_180ms_ease,transform_220ms_cubic-bezier(0.2,0.9,0.2,1)]"
      enter-from-class="opacity-0 translate-y-1.5 scale-[0.98]"
      enter-to-class="opacity-100 translate-y-0 scale-100"
      leave-active-class="[transition:opacity_180ms_ease,transform_220ms_cubic-bezier(0.2,0.9,0.2,1)]"
      leave-from-class="opacity-100 translate-y-0 scale-100"
      leave-to-class="opacity-0 translate-y-1.5 scale-[0.98]"
    >
      <div
        v-if="hintVisible && hintText && !fabState.isDragging"
        ref="hintBubbleRef"
        class="
          absolute bottom-[calc(100%+10px)] z-20 max-w-[min(240px,calc(100vw-48px))] pointer-events-none
          rounded-2xl border border-[var(--accent-2)] bg-[rgba(240,192,122,0.35)] px-3 py-2
          text-[13px] leading-5 text-[rgba(255,255,255,0.92)] shadow-[0_16px_34px_rgba(0,0,0,0.35),0_0_8px_rgba(240,192,122,0.3)]
          backdrop-blur-lg
        "
        :class="fabState.side === 'right' ? 'right-0 rounded-br-[6px]' : 'left-0 rounded-bl-[6px]'"
        role="status"
        aria-live="polite"
      >
        <div class="whitespace-nowrap">{{ props.hintTyping ? typedHintText : hintText }}</div>
      </div>
    </Transition>

    <!-- 回复完成气泡 -->
    <Transition
      appear
      enter-active-class="[transition:opacity_180ms_ease,transform_220ms_cubic-bezier(0.2,0.9,0.2,1)]"
      enter-from-class="opacity-0 translate-y-1.5 scale-[0.98]"
      enter-to-class="opacity-100 translate-y-0 scale-100"
      leave-active-class="[transition:opacity_180ms_ease,transform_220ms_cubic-bezier(0.2,0.9,0.2,1)]"
      leave-from-class="opacity-100 translate-y-0 scale-100"
      leave-to-class="opacity-0 translate-y-1.5 scale-[0.98]"
    >
      <div
        v-if="completionBubbleVisible && !fabState.isDragging"
        ref="completionBubbleRef"
        class="
          absolute bottom-[calc(100%+10px)] z-20 max-w-[min(240px,calc(100vw-48px))] pointer-events-none
          rounded-2xl border border-[var(--accent-2)] bg-[rgba(240,192,122,0.35)] px-3 py-2
          text-[13px] leading-5 text-[rgba(255,255,255,0.92)] shadow-[0_16px_34px_rgba(0,0,0,0.35),0_0_8px_rgba(240,192,122,0.3)]
          backdrop-blur-lg
        "
        :class="fabState.side === 'right' ? 'right-0 rounded-br-[6px]' : 'left-0 rounded-bl-[6px]'"
        role="status"
        aria-live="polite"
      >
        <div class="whitespace-nowrap">{{ completionBubbleText }}</div>
      </div>
    </Transition>

    <!-- 呼吸动效层（外）+ 触发动效层（内） -->
    <div class="fab-breathe" :class="{ 'is-paused': fabState.isDragging || isHovering, 'is-enhanced': sparkleVisible }">
      <div class="fab-nudge" :class="nudgeClass">
        <div class="fab-glow-layer" aria-hidden="true"></div>

        <img :src="chatFabIconUrl" alt="" class="fab-icon" draggable="false" aria-hidden="true" />

        <!-- 回复完成提醒：右上角单个微光 -->
        <div v-if="sparkleVisible" class="fab-sparkle" aria-hidden="true">
          <span class="fab-sparkle__dot fab-sparkle__dot--a"></span>
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
  hintTyping?: boolean;
  hintTypingSpeedMs?: number;
  nudgeKey?: number;
  nudgeKind?: 'pop' | 'wiggle';
  sparkleVisible?: boolean;
}>(), {
  hintText: null,
  hintVisible: false,
  hintTyping: false,
  hintTypingSpeedMs: 70,
  nudgeKey: 0,
  nudgeKind: 'pop',
  sparkleVisible: false,
});

const { hintText, hintVisible, sparkleVisible } = toRefs(props);

const emit = defineEmits<{
  (event: 'click'): void;
}>();

const fabRef = ref<HTMLElement | null>(null);
const hintBubbleRef = ref<HTMLElement | null>(null);
const completionBubbleRef = ref<HTMLElement | null>(null);

// ========== 拖动相关常量 ==========
const DRAG_DELAY_MS = 150;  // 拖动延迟阈值（150ms 内且移动距离小于阈值才算点击）
const DRAG_DISTANCE_THRESHOLD = 5;  // 拖动距离阈值（像素）

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
  // 新增：用于区分点击和拖动
  pointerDownTime: 0,          // 按下时间戳
  pointerDownX: 0,             // 按下时的 X 坐标
  pointerDownY: 0,             // 按下时的 Y 坐标
  dragDelayTimer: null as number | null,  // 延迟触发拖动模式的定时器
});

// ========== 动画状态（外部触发） ==========
const isHovering = ref(false);
const nudgeClass = ref<string>('');
let nudgeTimer: number | null = null;

// ========== 回复完成气泡状态 ==========
const completionBubbleVisible = ref(false);
const completionBubbleText = ref('');
let completionBubbleTimer: number | null = null;

const COMPLETION_MESSAGES = [
  '算完啦~',
  '搞定！',
  '解读完成喵~',
  '都给你讲清楚啦',
  '看看有没有帮到你',
  '这就是全部咯',
  '批完收工~',
  '就这样，明白了吗',
  '算卦完毕！',
  '给你整明白了',
];

const pickRandomCompletion = () =>
  COMPLETION_MESSAGES[Math.floor(Math.random() * COMPLETION_MESSAGES.length)];

// ========== 气泡文本：打字机效果 ==========
const typedHintText = ref('');
let typingTimer: number | null = null;

const stopTyping = () => {
  if (typingTimer) {
    clearInterval(typingTimer);
    typingTimer = null;
  }
};

const showCompletionBubble = () => {
  completionBubbleText.value = pickRandomCompletion();
  completionBubbleVisible.value = true;

  if (completionBubbleTimer) clearTimeout(completionBubbleTimer);
  completionBubbleTimer = window.setTimeout(() => {
    completionBubbleVisible.value = false;
    completionBubbleTimer = null;
  }, 5000);
};

const hideCompletionBubble = () => {
  completionBubbleVisible.value = false;
  if (completionBubbleTimer) {
    clearTimeout(completionBubbleTimer);
    completionBubbleTimer = null;
  }
};

const startTyping = () => {
  stopTyping();

  const fullText = props.hintText ?? '';
  if (!fullText) {
    typedHintText.value = '';
    return;
  }

  if (!props.hintTyping) {
    typedHintText.value = fullText;
    return;
  }

  typedHintText.value = '';
  let index = 0;
  typingTimer = window.setInterval(() => {
    index += 1;
    typedHintText.value = fullText.slice(0, index);
    if (index >= fullText.length) {
      stopTyping();
    }
  }, Math.max(16, props.hintTypingSpeedMs));
};

watch(
  () => [props.hintVisible, props.hintText, props.nudgeKey] as const,
  ([visible]) => {
    if (!visible) {
      stopTyping();
      typedHintText.value = '';
      return;
    }
    startTyping();
  },
  { immediate: true }
);

// ========== 常量配置 ==========
const MOBILE_SIDE_PADDING = 16;
const DESKTOP_SIDE_PADDING = 24;
const TOPNAV_HEIGHT_MOBILE = 48;
const TOPNAV_HEIGHT_TABLET = 56;
const TOPNAV_HEIGHT_DESKTOP = 64;
const TOPNAV_BUFFER = 12;
const TABBAR_HEIGHT = 70;
const TABBAR_BOTTOM_OFFSET = 24;
const TABBAR_BUFFER = 12;
const BUBBLE_HEIGHT_ESTIMATE = 45;
const BUBBLE_GAP = 10;
const BUBBLE_RESERVED_HEIGHT = 55;  // 固定预留气泡高度（45px 气泡 + 10px 间隙）
const STORAGE_KEY = 'chatFabPosition';

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

const getTopNavHeight = () => {
  if (window.matchMedia('(min-width: 1024px)').matches) return TOPNAV_HEIGHT_DESKTOP;
  if (window.matchMedia('(min-width: 768px)').matches) return TOPNAV_HEIGHT_TABLET;
  return TOPNAV_HEIGHT_MOBILE;
};

const getTopReserved = () => getTopNavHeight() + TOPNAV_BUFFER + BUBBLE_RESERVED_HEIGHT;

const getBottomReserved = () => {
  if (isDesktop.value) return TABBAR_BUFFER;
  return TABBAR_HEIGHT + TABBAR_BOTTOM_OFFSET + TABBAR_BUFFER;
};

const getFabSize = () => {
  const rect = fabRef.value?.getBoundingClientRect();
  const width = rect?.width ?? 0;
  // 与模板的 Tailwind 尺寸保持一致：移动端 56，平板 64，桌面端 80
  if (width > 0) return width;
  if (window.matchMedia('(min-width: 1024px)').matches) return 80;  // lg: h-20 w-20
  if (window.matchMedia('(min-width: 768px)').matches) return 64;   // md: h-16 w-16
  return 56;  // h-14 w-14
};

const clampY = (y: number) => {
  const topLimit = getTopReserved();  // 已包含固定气泡预留高度
  const bottomLimit = getBottomReserved();
  const maxY = window.innerHeight - bottomLimit - getFabSize();
  return Math.min(Math.max(y, topLimit), Math.max(topLimit, maxY));
};

const clampX = (x: number) => {
  const padding = getSidePadding();
  const maxX = window.innerWidth - getFabSize() - padding;
  return Math.min(Math.max(x, padding), Math.max(padding, maxX));
};

const saveFabPosition = () => {
  if (!fabState.hasCustom) return;

  const data = {
    side: fabState.side,
    y: fabState.y,
    timestamp: Date.now(),
  };

  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
  } catch (e) {
    console.warn('Failed to save ChatFab position:', e);
  }
};

const loadFabPosition = () => {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;

    const data = JSON.parse(raw);
    if (!data || typeof data.side !== 'string' || typeof data.y !== 'number') {
      return null;
    }

    return data;
  } catch (e) {
    console.warn('Failed to load ChatFab position:', e);
    return null;
  }
};

const getDefaultY = () => {
  if (typeof window === 'undefined') return 0;
  const bottom = getBottomReserved();
  return clampY(window.innerHeight - bottom - getFabSize());
};

const setupFabDefault = () => {
  const saved = loadFabPosition();

  if (saved) {
    fabState.side = saved.side as 'left' | 'right';
    fabState.y = clampY(saved.y);
    fabState.hasCustom = true;
  } else {
    fabState.y = getDefaultY();
    fabState.side = 'right';
    fabState.hasCustom = false;
  }
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

// 监听气泡显示变化，动态调整位置
watch(
  () => hintVisible.value,
  () => {
    if (fabState.hasCustom) {
      fabState.y = clampY(fabState.y);
    }
  }
);

// ========== 拖拽逻辑 ==========
const startDrag = (event: PointerEvent) => {
  // 清除之前的重置定时器
  if (fabState.resetTimer) {
    clearTimeout(fabState.resetTimer);
    fabState.resetTimer = null;
  }

  // 记录按下时间和位置（用于区分点击和拖动）
  fabState.pointerDownTime = Date.now();
  fabState.pointerDownX = event.clientX;
  fabState.pointerDownY = event.clientY;
  fabState.dragMoved = false;

  // 延迟 150ms 后才进入拖动模式（允许快速点击）
  fabState.dragDelayTimer = window.setTimeout(() => {
    fabState.isDragging = true;
    fabState.dragDelayTimer = null;
  }, DRAG_DELAY_MS);

  const target = fabRef.value || (event.currentTarget as HTMLElement);

  // 捕获指针，确保拖动过程中事件不被其他元素干扰
  if (target.setPointerCapture) {
    target.setPointerCapture(event.pointerId);
  }

  const onPointerMove = (e: PointerEvent) => {
    // 计算移动距离
    const dx = e.clientX - fabState.pointerDownX;
    const dy = e.clientY - fabState.pointerDownY;
    const distance = Math.sqrt(dx * dx + dy * dy);

    // 只有移动距离超过阈值才算拖动
    if (distance > DRAG_DISTANCE_THRESHOLD) {
      // 取消延迟定时器，立即进入拖动模式
      if (fabState.dragDelayTimer) {
        clearTimeout(fabState.dragDelayTimer);
        fabState.dragDelayTimer = null;
      }
      fabState.isDragging = true;
      fabState.dragMoved = true;
    }

    // 只有在拖动模式下才更新位置
    if (fabState.isDragging) {
      const size = getFabSize();
      fabState.dragX = clampX(e.clientX - size / 2);
      fabState.dragY = clampY(e.clientY - size / 2);
    }
  };

  const onPointerUp = (e: PointerEvent) => {
    // 清除延迟定时器
    if (fabState.dragDelayTimer) {
      clearTimeout(fabState.dragDelayTimer);
      fabState.dragDelayTimer = null;
    }

    // 计算按压时长和移动距离
    const pressDuration = Date.now() - fabState.pointerDownTime;
    const dx = e.clientX - fabState.pointerDownX;
    const dy = e.clientY - fabState.pointerDownY;
    const distance = Math.sqrt(dx * dx + dy * dy);

    // 快速点击判定：时间短 + 距离小
    const isQuickTap = pressDuration < DRAG_DELAY_MS && distance < DRAG_DISTANCE_THRESHOLD;

    if (isQuickTap) {
      // 快速点击：不保存位置，直接清理状态
      fabState.isDragging = false;
      fabState.dragMoved = false;

      // 释放指针捕获
      if (fabRef.value?.releasePointerCapture) {
        try {
          fabRef.value.releasePointerCapture(e.pointerId);
        } catch (err) {
          // ignore
        }
      }

      // 移除事件监听
      window.removeEventListener('pointermove', onPointerMove);
      window.removeEventListener('pointerup', onPointerUp);
      fabListeners.value = { ...fabListeners.value, onPointerMove: undefined, onPointerUp: undefined };

      return;  // 立即返回，不执行后续拖动逻辑
    }

    // 拖动逻辑：保存位置
    if (fabState.isDragging && fabState.dragMoved) {
      const targetSide = e.clientX < window.innerWidth / 2 ? 'left' : 'right';
      fabState.side = targetSide;
      const size = getFabSize();
      fabState.y = clampY(e.clientY - size / 2);
      fabState.hasCustom = true;
      saveFabPosition();  // 保存位置到 localStorage
    }

    fabState.isDragging = false;

    // 释放指针捕获
    if (fabRef.value?.releasePointerCapture) {
      try {
        fabRef.value.releasePointerCapture(e.pointerId);
      } catch (err) {
        // ignore
      }
    }

    // 120ms 后重置 dragMoved，避免拖动完成后的误触发点击
    fabState.resetTimer = window.setTimeout(() => {
      fabState.dragMoved = false;
      fabState.resetTimer = null;
    }, 120);

    // 移除事件监听
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
    saveFabPosition();  // 保存调整后的位置
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
  if (completionBubbleTimer) {
    clearTimeout(completionBubbleTimer);
    completionBubbleTimer = null;
  }
  stopTyping();
});

// 暴露方法供父组件调用
defineExpose({
  showCompletionBubble,
  hideCompletionBubble,
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

/* ========== 呼吸动画（按钮图标的上下浮动效果） ========== */
.fab-breathe {
  position: absolute;
  inset: 0;
  pointer-events: none;
  animation: chatfab-breathe 5.2s ease-in-out infinite;  /* 5.2秒一轮，轻微浮动 */
  transform-origin: 50% 100%;  /* 变换原点：底部中心，让摇晃动画以底部为轴 */
  will-change: transform;     /* 性能优化：预告浏览器将进行transform变换 */
}

/* 拖拽或悬停时暂停呼吸动画 */
.fab-breathe.is-paused {
  animation: none;
}

/* 回复完成时增强呼吸幅度（sparkleVisible为true时触发） */
.fab-breathe.is-enhanced {
  animation: chatfab-breathe-enhanced 2.5s ease-in-out infinite;  /* 加快速度到2.5秒 */
}

/* 默认呼吸动画：轻微上下浮动 */
@keyframes chatfab-breathe {
  0%,
  100% {
    transform: translateY(0);     /* 初始位置 */
  }
  50% {
    transform: translateY(-2px);  /* 向上移动2px（调整此值可改变浮动幅度） */
  }
}

/* 增强呼吸动画：更大幅度的上下浮动 */
@keyframes chatfab-breathe-enhanced {
  0%,
  100% {
    transform: translateY(0);     /* 初始位置 */
  }
  50% {
    transform: translateY(-8px);  /* 向上移动8px，幅度是默认的4倍 */
  }
}

/* ========== 触发动效（一次） ========== */
.fab-nudge {
  position: absolute;
  inset: 0;
  pointer-events: none;
  transform-origin: 50% 100%;  /* 底部中心为轴心，让 wiggle 摇晃以底部为支点 */
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
  cursor: grabbing;
}

.chat-fab.is-dragging .fab-icon {
  filter: brightness(1.06) drop-shadow(0 10px 18px rgba(0, 0, 0, 0.22));
}

/* ========== 回复完成光晕 ========== */
.fab-sparkle {
  position: absolute;
  top: 12px;        /* 距离按钮顶部12px（调整此值可改变光晕垂直位置） */
  right: 12px;      /* 距离按钮右侧12px（调整此值可改变光晕水平位置） */
  z-index: 1;       /* 确保光晕显示在图标上方 */
  width: 32px;      /* 光晕容器宽度（增大此值可放大光晕） */
  height: 32px;     /* 光晕容器高度（增大此值可放大光晕） */
  pointer-events: none;  /* 不响应鼠标事件，避免影响按钮点击 */
}

.fab-sparkle__dot {
  position: absolute;
  inset: 0;         /* 填满父容器 */
  border-radius: 999px;  /* 圆形 */

  /* 径向渐变：从左上角10%,10%位置向外扩散的金色光晕 */
  background: radial-gradient(
    circle at 10% 10%,                /* 光源位置（改为50% 50%可居中） */
    rgba(240, 192, 122, 0.4) 0%,      /* 中心：金色，40%不透明度 */
    rgba(240, 192, 122, 0.2) 30%,     /* 30%半径：金色，20%不透明度 */
    rgba(240, 192, 122, 0.1) 50%,     /* 50%半径：金色，10%不透明度 */
    rgba(240, 192, 122, 0) 70%        /* 70%半径：完全透明，形成柔和过渡 */
  );

  animation: chatfab-sparkle 1.8s ease-in-out infinite;  /* 1.8秒循环呼吸动画 */
  opacity: 0.95;    /* 整体不透明度95% */

  /* 双层发光阴影：内圈16px + 外圈32px，营造光晕效果 */
  box-shadow:
    0 0 12px rgba(240, 192, 122, 0.5),   /* 内圈光晕：16px扩散半径 */
    0 0 32px rgba(240, 192, 122, 0.3);   /* 外圈光晕：32px扩散半径 */
}

/* 光晕呼吸动画：缩放 + 透明度变化 */
@keyframes chatfab-sparkle {
  0%,
  100% {
    transform: scale(0.95);  /* 缩小到85%（减小此值可增大呼吸幅度） */
    opacity: 0.5;            /* 半透明（减小此值可增大明暗对比） */
  }
  50% {
    transform: scale(1.55);  /* 放大到115%（增大此值可增大呼吸幅度） */
    opacity: 1;              /* 完全不透明 */
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
