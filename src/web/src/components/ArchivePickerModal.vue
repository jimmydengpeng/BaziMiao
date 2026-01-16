<template>
  <teleport to="body">
    <Transition name="fade">
      <div v-if="modelValue" class="fixed inset-0 z-[500] overscroll-contain">
        <div class="absolute inset-0 bg-black/55" @click="close"></div>

        <div class="absolute inset-x-0 bottom-0 md:inset-0 md:flex md:items-center md:justify-center">
          <Transition name="sheet">
            <div
              class="mx-auto w-full max-w-[920px] rounded-t-2xl border border-white/10 bg-[rgba(18,20,28,0.96)] shadow-[0_-18px_50px_rgba(0,0,0,0.55)] backdrop-blur-xl md:rounded-2xl"
            >
              <div class="border-b border-[rgba(255,255,255,0.08)]">
                <div class="flex items-center justify-between gap-3 px-4 py-3 md:px-5">
                  <div class="min-w-0">
                    <div class="truncate text-lg font-semibold text-white/90 md:text-xl">
                      {{ title }}
                    </div>
                    <div v-if="description" class="truncate text-[11px] text-white/55">
                      {{ description }}
                    </div>
                  </div>

                  <div class="flex items-center gap-2">
                    <div
                      class="relative h-9 overflow-hidden rounded-full border border-white/10 bg-white/5 text-white/70 transition-[width,background-color,color] duration-250 ease-out"
                      :class="
                        searchOpen
                          ? 'w-[min(42vw,260px)] bg-white/10 text-white'
                          : searchQuery.trim().length > 0
                            ? 'w-9 bg-white/10 text-white'
                            : 'w-9 hover:bg-white/10 hover:text-white'
                      "
                    >
                      <button
                        v-if="!searchOpen"
                        class="absolute inset-0 inline-flex items-center justify-center"
                        type="button"
                        aria-label="搜索档案"
                        @click="openSearch"
                      >
                        <svg
                          class="h-4 w-4"
                          viewBox="0 0 24 24"
                          fill="none"
                          stroke="currentColor"
                          stroke-width="2.2"
                          stroke-linecap="round"
                          stroke-linejoin="round"
                          aria-hidden="true"
                        >
                          <circle cx="11" cy="11" r="7" />
                          <path d="M20 20l-3.5-3.5" />
                        </svg>
                      </button>

                      <div v-else class="absolute inset-0 flex items-center px-3">
                        <input
                          ref="searchInputRef"
                          v-model="searchQuery"
                          type="text"
                          class="h-9 w-full bg-transparent text-xs text-white/85 placeholder-white/35 outline-none"
                          :placeholder="`搜索共 ${profiles.length} 份档案...`"
                          @keydown.esc.prevent="closeSearch"
                          @blur="closeSearch"
                        />
                      </div>
                    </div>
                    <SettingsIconButton aria-label="命盘档案" @click="goToArchives" />
                    <CloseIconButton @click="close" />
                  </div>
                </div>
              </div>

              <div
                class="max-h-[70vh] overflow-y-auto px-4 pb-[calc(env(safe-area-inset-bottom,0px)+20px)] md:px-5 overscroll-contain [-webkit-overflow-scrolling:touch]"
              >
                <ArchiveListPanel
                  mode="modal"
                  :profiles="profiles"
                  :current-id="currentId"
                  :search-query="searchQuery"
                  :show-modal-search="false"
                  @select="handleSelect"
                />
              </div>
            </div>
          </Transition>
        </div>
      </div>
    </Transition>
  </teleport>
</template>

<script setup lang="ts">
import { nextTick, onUnmounted, ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import ArchiveListPanel from './ArchiveListPanel.vue';
import CloseIconButton from './CloseIconButton.vue';
import SettingsIconButton from './SettingsIconButton.vue';
import type { ArchiveEntry } from '../utils/storage';
import { lockBackgroundScroll } from '../utils/scroll-lock';

const router = useRouter();

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

let releaseScrollLock: (() => void) | null = null;
const searchOpen = ref(false);
const searchQuery = ref('');
const searchInputRef = ref<HTMLInputElement | null>(null);

const close = () => {
  searchOpen.value = false;
  searchQuery.value = '';
  emit('update:modelValue', false);
};

const goToArchives = () => {
  close();
  router.push({ name: 'Archives' });
};

const handleSelect = (entry: ArchiveEntry) => {
  emit('select', entry);
  close();
};

const openSearch = async () => {
  searchOpen.value = true;
  await nextTick();
  searchInputRef.value?.focus();
};

const closeSearch = () => {
  searchOpen.value = false;
  searchQuery.value = '';
};

watch(
  () => props.modelValue,
  (open) => {
    if (open) {
      if (!releaseScrollLock) releaseScrollLock = lockBackgroundScroll();
      return;
    }
    searchOpen.value = false;
    searchQuery.value = '';
    if (releaseScrollLock) {
      releaseScrollLock();
      releaseScrollLock = null;
    }
  },
  { immediate: true }
);

onUnmounted(() => {
  if (releaseScrollLock) {
    releaseScrollLock();
    releaseScrollLock = null;
  }
});
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 160ms ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.sheet-enter-active,
.sheet-leave-active {
  transition: transform 350ms ease, opacity 350ms ease;
}
.sheet-enter-from,
.sheet-leave-to {
  transform: translateY(14px) scale(0.98);
  opacity: 0;
}
</style>
