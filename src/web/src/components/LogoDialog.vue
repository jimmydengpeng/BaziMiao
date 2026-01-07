<template>
  <teleport to="body">
    <Transition name="fade">
      <div
        v-if="modelValue"
        class="fixed inset-0 z-[70] flex items-center justify-center px-4"
        :style="{ paddingTop: `calc(env(safe-area-inset-top, 0px) + 12px)`, paddingBottom: `calc(env(safe-area-inset-bottom, 0px) + 12px)` }"
        role="dialog"
        aria-modal="true"
        aria-label="神机喵算菜单"
      >
        <!-- 遮罩 -->
        <button
          class="absolute inset-0 cursor-default bg-black/60"
          type="button"
          aria-label="关闭"
          @click="close"
        />

        <!-- 面板 -->
        <div class="relative w-full max-w-[420px] overflow-hidden rounded-2xl border border-white/10 bg-[rgba(18,22,33,0.92)] shadow-[0_20px_55px_rgba(0,0,0,0.6)] backdrop-blur-xl">
          <div class="flex items-center justify-between gap-3 px-4 py-3">
            <div class="flex items-center gap-2.5">
              <img :src="logoUrl" alt="神机喵算 Logo" class="h-8 w-8 object-contain" />
              <div class="min-w-0">
                <div class="truncate font-['Ma_Shan_Zheng',serif] text-lg tracking-wide text-[var(--accent-2)]">
                  神机喵算
                </div>
                <div class="text-xs text-white/60">想做什么？</div>
              </div>
            </div>

            <button
              class="inline-flex h-9 w-9 items-center justify-center rounded-lg text-white/80 transition hover:bg-white/10"
              type="button"
              aria-label="关闭"
              @click="close"
            >
              <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M18 6 6 18" />
                <path d="M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div class="grid gap-2 px-4 pb-4">
            <button
              class="inline-flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-br from-[var(--accent)] to-[var(--accent-2)] px-4 py-3 text-sm font-semibold text-[#0a0604] shadow-[0_8px_22px_rgba(214,160,96,0.28)] transition hover:-translate-y-[1px] hover:shadow-[0_12px_26px_rgba(214,160,96,0.35)] active:translate-y-0"
              type="button"
              @click="openChat"
            >
              打开神喵大师
            </button>

            <button
              class="inline-flex w-full items-center justify-center rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm font-medium text-white/90 transition hover:bg-white/10"
              type="button"
              @click="goHome"
            >
              回到首页
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </teleport>
</template>

<script setup lang="ts">
import { watch, onUnmounted } from 'vue';
import logoUrl from '../assets/logo-nav.png';

const props = defineProps<{
  modelValue: boolean;
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void;
  (e: 'openChat'): void;
  (e: 'goHome'): void;
}>();

const close = () => emit('update:modelValue', false);

const openChat = () => {
  emit('openChat');
  close();
};

const goHome = () => {
  emit('goHome');
  close();
};

const handleKeydown = (event: KeyboardEvent) => {
  if (event.key === 'Escape') close();
};

watch(
  () => props.modelValue,
  (isOpen) => {
    if (isOpen) {
      window.addEventListener('keydown', handleKeydown);
    } else {
      window.removeEventListener('keydown', handleKeydown);
    }
  },
  { immediate: true }
);

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown);
});
</script>

