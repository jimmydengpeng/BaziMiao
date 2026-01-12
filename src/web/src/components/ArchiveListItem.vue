<template>
  <div
    class="flex items-center gap-3"
    :class="showCheckbox ? 'pr-2' : ''"
  >
    <button
      class="flex w-full items-center justify-between gap-4 overflow-hidden rounded-2xl border border-[rgba(255,255,255,0.12)] bg-[rgba(18,20,28,0.25)] px-3 py-3 text-left backdrop-blur-lg transition-all duration-200 hover:-translate-y-0.5 hover:border-[rgba(214,160,96,0.55)] hover:shadow-[0_22px_48px_rgba(0,0,0,0.5)]"
      :class="[
        isCurrent
          ? 'border-[rgba(214,160,96,0.85)] shadow-[0_22px_50px_rgba(0,0,0,0.55),inset_0_0_0_1px_rgba(214,160,96,0.35)]'
          : '',
        isPending
          ? 'border-[rgba(88,160,255,0.7)] bg-[rgba(88,160,255,0.12)]'
          : '',
        showCheckbox && checked ? 'border-[rgba(214,160,96,0.55)] bg-[rgba(214,160,96,0.12)]' : ''
      ]"
      type="button"
      @click="$emit('click')"
    >
      <div class="min-w-0 space-y-1">
        <div class="flex items-center gap-2">
          <div class="truncate text-lg font-semibold text-[var(--accent-2)]">
            {{ entry.displayName }}
            <span v-if="genderLabel(entry.gender)" class="ml-1 text-sm font-normal text-[var(--muted)]">
              · {{ genderLabel(entry.gender) }}
            </span>
          </div>
          <span
            v-if="isCurrent"
            class="rounded-full border border-[rgba(214,160,96,0.4)] bg-[rgba(214,160,96,0.15)] px-2 py-0.5 text-[11px] text-[var(--accent-2)]"
          >
            当前
          </span>
          <button
            v-if="isPending"
            class="inline-flex items-center rounded-full border border-[rgba(88,160,255,0.5)] bg-[rgba(88,160,255,0.18)] px-2 py-0.5 text-[11px] font-semibold text-[#8fc0ff] transition hover:bg-[rgba(88,160,255,0.3)]"
            type="button"
            @click.stop="$emit('switch')"
          >
            切换
          </button>
        </div>
        <div class="text-sm text-[var(--muted)]">
          {{ entry.birthLabel }}
        </div>
      </div>
      <div class="flex items-center gap-3">
        <div class="grid gap-1.5 text-sm font-semibold tracking-wider">
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
        <div class="text-2xl text-[var(--accent-2)] opacity-80">›</div>
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
import type { ArchiveEntry } from '../utils/storage';

defineProps<{
  entry: ArchiveEntry;
  isCurrent?: boolean;
  isPending?: boolean;
  showCheckbox?: boolean;
  checked?: boolean;
}>();

defineEmits<{
  (e: 'click'): void;
  (e: 'switch'): void;
  (e: 'toggle'): void;
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
</script>
