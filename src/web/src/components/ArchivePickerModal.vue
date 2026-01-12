<template>
  <teleport to="body">
    <Transition name="fade">
      <div v-if="modelValue" class="fixed inset-0 z-[500]">
        <div class="absolute inset-0 bg-black/50" @click="close"></div>
        <div class="absolute inset-x-0 bottom-0 pb-[env(safe-area-inset-bottom,0px)] md:inset-0 md:flex md:items-center md:justify-center md:pb-0">
          <div
            class="mx-auto w-full max-w-[920px] rounded-t-2xl border border-white/10 bg-[rgba(18,20,28,0.96)] shadow-[0_-18px_50px_rgba(0,0,0,0.55)] backdrop-blur-xl md:rounded-2xl"
          >
            <div class="flex items-center justify-between gap-3 px-4 py-3 md:px-5">
              <div class="min-w-0">
                <div class="text-sm font-semibold text-white/90">
                  {{ title }}
                </div>
                <div v-if="description" class="text-[11px] text-white/55">
                  {{ description }}
                </div>
              </div>
              <button
                class="flex h-9 w-9 items-center justify-center rounded-lg text-white/70 transition hover:bg-white/10 hover:text-white"
                type="button"
                @click="close"
                aria-label="关闭"
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M18 6L6 18M6 6l12 12"/>
                </svg>
              </button>
            </div>

            <div class="max-h-[70vh] overflow-y-auto px-4 pb-5 md:px-5 overscroll-contain">
              <ArchiveListPanel
                mode="modal"
                :profiles="profiles"
                :current-id="currentId"
                @select="handleSelect"
              />
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </teleport>
</template>

<script setup lang="ts">
import ArchiveListPanel from './ArchiveListPanel.vue';
import type { ArchiveEntry } from '../utils/storage';

const props = withDefaults(defineProps<{
  modelValue: boolean;
  profiles: ArchiveEntry[];
  currentId: number | null;
  title?: string;
  description?: string;
}>(), {
  title: '选择命主档案',
  description: '点击档案即可切换'
});

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void;
  (e: 'select', entry: ArchiveEntry): void;
}>();

const close = () => {
  emit('update:modelValue', false);
};

const handleSelect = (entry: ArchiveEntry) => {
  emit('select', entry);
  close();
};
</script>
