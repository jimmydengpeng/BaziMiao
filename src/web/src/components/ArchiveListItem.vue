<template>
  <div
    class="flex items-center gap-3"
    :class="showCheckbox ? 'pr-2' : ''"
  >
    <button
      class="flex w-full items-center justify-between gap-4 overflow-hidden rounded-xl border border-[rgba(255,255,255,0.12)] bg-[rgba(18,20,28,0.55)] px-3 py-2 pr-2 text-left backdrop-blur-xl transition-all duration-200 hover:-translate-y-0.5 hover:border-[rgba(214,160,96,0.55)] hover:shadow-[0_22px_48px_rgba(0,0,0,0.5)]"
      :class="[
        isCurrent
          ? 'border-[0.5px] border-[rgba(214,160,96,0.65)] shadow-[0_22px_50px_rgba(0,0,0,0.15),inset_0_0_0_1px_rgba(214,160,96,0.25)]'
          : '',
        isPending
          ? 'border-[rgba(53,65,81,0.7)] bg-[rgba(40,45,51,0.3)] shadow-[0_12px_32px_rgba(0,0,0,0.35)]'
          : '',
        showCheckbox && checked ? 'border-[rgba(214,160,96,0.55)] bg-[rgba(214,160,96,0.12)]' : ''
      ]"
      type="button"
      @click="$emit('click')"
    >
      <div class="min-w-0 space-y-2">
        <div class="flex items-center gap-2">
          <div class="min-w-0 flex-1 truncate text-md font-semibold text-[var(--accent-2)]">
            {{ entry.displayName }}
            <span
              v-if="genderLabel(entry.gender ?? entry.chart?.gender)"
              class="ml-1 text-sm font-normal text-[var(--muted)]"
            >
              {{ genderLabel(entry.gender ?? entry.chart?.gender) }}
            </span>
          </div>
          <span
            v-if="isCurrent"
            class="inline-flex shrink-0 items-center gap-1 whitespace-nowrap rounded-full border border-[rgba(214,160,96,0.4)] bg-[rgba(214,160,96,0.15)] px-2 py-0.5 text-[11px] text-[var(--accent-2)]"
          >
            <img
              :src="archiveViewIconUrl"
              alt="当前"
              class="h-3.5 w-3.5"
              :style="{ filter: accentIconFilter }"
            />
            当前
          </span>
        </div>
        <div class="min-w-0 truncate whitespace-nowrap text-xs text-[var(--muted)]">
          {{ entry.birthLabel }}
        </div>
      </div>
      <div class="relative flex min-w-[140px] items-center justify-end gap-2">
        <div
          class="grid gap-1.5 text-sm font-semibold tracking-wider transition-opacity duration-200"
          :class="shouldShowActions ? 'pointer-events-none opacity-0' : 'opacity-100'"
        >
          <div class="grid auto-cols-[minmax(14px,1fr)] grid-flow-col gap-1.5">
            <span
              v-for="(pillar, idx) in entry.pillars"
              :key="`stem-${entry.id}-${idx}`"
              :class="['min-w-[16px] text-center', elementClass(pillar.stemElement)]"
            >
              {{ pillar.stem }}
            </span>
          </div>
          <div class="grid auto-cols-[minmax(14px,1fr)] grid-flow-col gap-1.5">
            <span
              v-for="(pillar, idx) in entry.pillars"
              :key="`branch-${entry.id}-${idx}`"
              :class="['min-w-[16px] text-center', elementClass(pillar.branchElement)]"
            >
              {{ pillar.branch }}
            </span>
          </div>
        </div>
        <button
          class="inline-flex h-7 w-4 items-center justify-center text-[var(--accent-2)] transition-all duration-200"
          :class="shouldShowActions ? 'opacity-100' : 'opacity-60 hover:opacity-90'"
          type="button"
          @click.stop="$emit('more')"
        >
          <img
            :src="archiveMoreIconUrl"
            alt="更多"
            class="h-4 w-4 opacity-80 transition-all duration-200"
            :class="shouldShowActions ? 'brightness-110' : ''"
          />
        </button>
        <div
          class="absolute right-8 top-1/2 z-10 flex -translate-y-1/2 items-center gap-4 transition-opacity duration-200"
          :class="shouldShowActions ? 'opacity-100' : 'pointer-events-none opacity-0'"
        >
          <button
            class="inline-flex items-center justify-center p-1 text-[var(--accent-2)] transition-all duration-200"
            :class="shouldShowActions ? 'translate-x-0 opacity-100' : 'translate-x-3 opacity-0'"
            :style="{ transitionDelay: '0ms' }"
            type="button"
            @click.stop="$emit('copy')"
          >
            <img :src="archiveCopyIconUrl" alt="复制八字信息" class="h-4 w-4 opacity-70" />
          </button>
          <button
            class="inline-flex items-center justify-center p-1 text-[var(--accent-2)] transition-all duration-200"
            :class="shouldShowActions ? 'translate-x-0 opacity-100' : 'translate-x-3 opacity-0'"
            :style="{ transitionDelay: '80ms' }"
            type="button"
            @click.stop="$emit('edit')"
          >
            <img :src="archiveEditIconUrl" alt="编辑档案" class="h-4 w-4 opacity-70" />
          </button>
          <button
            class="inline-flex items-center justify-center p-1 text-[var(--accent-2)] transition-all duration-200"
            :class="shouldShowActions ? 'translate-x-0 opacity-100' : 'translate-x-3 opacity-0'"
            :style="{ transitionDelay: '160ms' }"
            type="button"
            @click.stop="$emit('delete')"
          >
            <img :src="archiveDeleteIconUrl" alt="删除档案" class="h-4 w-4 opacity-70" />
          </button>
        </div>
      </div>
    </button>
    <div v-if="showCheckbox" class="flex items-center justify-center">
      <label class="relative inline-flex h-5 w-5 cursor-pointer items-center justify-center">
        <input
          type="checkbox"
          class="peer sr-only"
          :checked="checked"
          @click.stop
          @change="$emit('toggle')"
        />
        <span
          class="h-5 w-5 rounded-md border border-white/25 bg-white/5 transition peer-checked:border-[rgba(214,160,96,0.65)] peer-checked:bg-[rgba(214,160,96,0.35)]"
        ></span>
        <svg
          class="pointer-events-none absolute h-3.5 w-3.5 text-[var(--accent-2)] opacity-0 transition peer-checked:opacity-100"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="3"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <polyline points="20 6 9 17 4 12" />
        </svg>
      </label>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { ArchiveEntry } from '../utils/storage';
import archiveCopyIconUrl from '../assets/archive_copy.png';
import archiveDeleteIconUrl from '../assets/archive_delete.png';
import archiveEditIconUrl from '../assets/archive_edit.png';
import archiveMoreIconUrl from '../assets/archive_more.png';
import archiveViewIconUrl from '../assets/archive_view.png';

const props = defineProps<{
  entry: ArchiveEntry;
  isCurrent?: boolean;
  isPending?: boolean;
  showCheckbox?: boolean;
  checked?: boolean;
  showActions?: boolean;
}>();

defineEmits<{
  (e: 'click'): void;
  (e: 'more'): void;
  (e: 'toggle'): void;
  (e: 'copy'): void;
  (e: 'edit'): void;
  (e: 'delete'): void;
}>();

const elementClass = (element: string) => {
  const map: Record<string, string> = {
    木: 'element-wood',
    火: 'element-fire',
    土: 'element-earth',
    金: 'element-metal',
    水: 'element-water'
  };
  return map[element] ?? 'element-neutral';
};

const genderLabel = (gender?: string) => {
  if (gender === 'male') return '男';
  if (gender === 'female') return '女';
  return '';
};

const accentIconFilter =
  'brightness(0) saturate(100%) invert(78%) sepia(24%) saturate(742%) hue-rotate(350deg) brightness(95%) contrast(88%)';

const shouldShowActions = computed(() => !!props.isPending && props.showActions !== false);
</script>
