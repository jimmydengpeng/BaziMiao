<template>
  <section class="flex flex-col gap-3">
    <header
      v-if="mode === 'page'"
      class="sticky top-0 z-20 -mx-3 flex flex-col gap-3 border-b border-[rgba(255,255,255,0.08)] bg-[rgba(18,22,33,0.75)] px-3 py-3 backdrop-blur-xl md:-mx-4 md:px-4 lg:-mx-6 lg:px-6"
    >
      <div class="flex flex-wrap items-center justify-between gap-3">
        <div class="flex flex-wrap items-center gap-2">
          <button class="btn-ghost gap-1.5 px-3 py-2 text-xs" type="button" @click="$emit('create')">
            <img :src="archiveAddIconUrl" alt="新建" class="h-3.5 w-3.5 object-contain" />
            新建
          </button>
          <button
            class="btn-ghost gap-1.5 px-3 py-2 text-xs"
            :class="searchOpen ? activeActionClass : ''"
            type="button"
            @click="toggleSearch"
          >
            <img :src="archiveSearchIconUrl" alt="搜索" class="h-3.5 w-3.5 object-contain" />
            搜索
          </button>
          <button
            class="btn-ghost gap-1.5 px-3 py-2 text-xs"
            :class="isDeleteMode ? activeActionClass : ''"
            type="button"
            :disabled="profiles.length === 0"
            @click="handleDeleteClick"
          >
            <img :src="archiveDeleteIconUrl" alt="删除" class="h-3.5 w-3.5 object-contain" />
            {{ deleteButtonLabel }}
          </button>
          <button
            class="btn-ghost gap-1.5 px-3 py-2 text-xs"
            type="button"
            :disabled="pendingEntry === null"
            @click="handleCopy"
          >
            <img :src="archiveCopyIconUrl" alt="复制给AI" class="h-3.5 w-3.5 object-contain" />
            复制给AI
          </button>
        </div>
      </div>
      <div class="text-sm text-[var(--muted)]">已保存 {{ profiles.length }} 份命盘档案</div>
      <div v-if="searchOpen" class="flex flex-col gap-2 md:flex-row md:items-center">
        <input
          v-model="query"
          type="text"
          class="w-full min-w-[200px] rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white/85 placeholder-white/35 outline-none focus:border-[rgba(214,160,96,0.55)] md:w-[320px]"
          placeholder="搜索档案名称..."
        />
        <div class="text-xs text-white/50">支持姓名、出生信息或编号搜索</div>
      </div>
    </header>

    <div v-else class="px-1">
      <input
        v-model="query"
        type="text"
        class="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white/85 placeholder-white/35 outline-none focus:border-[rgba(214,160,96,0.55)]"
        placeholder="搜索档案名称..."
      />
    </div>

    <div v-if="profiles.length === 0" class="panel-card flex flex-col gap-2.5 text-center bg-[rgba(16,12,10,0.7)]">
      <h2 class="text-lg font-semibold text-white">还没有档案</h2>
      <p class="text-sm text-[var(--muted)]">先填写姓名与生日信息，再保存到这里。</p>
      <button
        v-if="mode === 'page'"
        class="btn-primary mx-auto mt-2"
        type="button"
        @click="$emit('create')"
      >
        去填写
      </button>
    </div>

    <div v-else class="flex flex-1 flex-col gap-3">
      <div v-if="filteredProfiles.length === 0" class="panel-card text-center text-sm text-white/60">
        没有匹配的档案
      </div>
      <div class="grid gap-3 pb-6 md:grid-cols-2">
        <ArchiveListItem
          v-for="entry in filteredProfiles"
          :key="entry.id"
          :entry="entry"
          :is-current="entry.id === currentId"
          :is-pending="entry.id === pendingEntry?.id"
          :show-checkbox="isDeleteMode"
          :checked="selectedIds.includes(entry.id)"
          @click="handleItemClick(entry)"
          @switch="handleSwitch(entry)"
          @toggle="toggleSelect(entry.id)"
        />
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import ArchiveListItem from './ArchiveListItem.vue';
import type { ArchiveEntry } from '../utils/storage';
import archiveAddIconUrl from '../assets/archive_add.png';
import archiveSearchIconUrl from '../assets/archive_search.png';
import archiveDeleteIconUrl from '../assets/archive_delete.png';
import archiveCopyIconUrl from '../assets/archive_copy.png';

const props = defineProps<{
  mode: 'page' | 'modal';
  profiles: ArchiveEntry[];
  currentId: number | null;
}>();

const emit = defineEmits<{
  (e: 'select', entry: ArchiveEntry): void;
  (e: 'create'): void;
  (e: 'delete', ids: number[]): void;
  (e: 'copy', entry: ArchiveEntry): void;
}>();

const query = ref('');
const isDeleteMode = ref(false);
const selectedIds = ref<number[]>([]);
const pendingEntry = ref<ArchiveEntry | null>(null);
const searchOpen = ref(false);
const activeActionClass = 'border-[rgba(214,160,96,0.7)] text-[var(--accent-2)]';

const deleteButtonLabel = computed(() => {
  if (!isDeleteMode.value) return '删除';
  if (selectedIds.value.length === 0) return '删除(取消)';
  return `删除(${selectedIds.value.length})`;
});

const filteredProfiles = computed(() => {
  const keyword = query.value.trim().toLowerCase();
  if (!keyword) return props.profiles;
  return props.profiles.filter((entry) => {
    const haystack = `${entry.displayName} ${entry.birthLabel} #${entry.id}`.toLowerCase();
    return haystack.includes(keyword);
  });
});

const toggleSelect = (id: number) => {
  if (!isDeleteMode.value) return;
  if (selectedIds.value.includes(id)) {
    selectedIds.value = selectedIds.value.filter((item) => item !== id);
    return;
  }
  selectedIds.value = [...selectedIds.value, id];
};

const handleItemClick = (entry: ArchiveEntry) => {
  if (isDeleteMode.value) {
    toggleSelect(entry.id);
    return;
  }
  if (props.mode === 'modal') {
    emit('select', entry);
    return;
  }
  if (pendingEntry.value?.id === entry.id) {
    emit('select', entry);
    return;
  }
  pendingEntry.value = entry;
};

const enterDeleteMode = () => {
  isDeleteMode.value = true;
  selectedIds.value = [];
};

const exitDeleteMode = () => {
  isDeleteMode.value = false;
  selectedIds.value = [];
};

const confirmDelete = () => {
  if (selectedIds.value.length === 0) return;
  const confirmed = window.confirm(`确定要删除 ${selectedIds.value.length} 份档案吗？此操作不可恢复。`);
  if (!confirmed) return;
  emit('delete', [...selectedIds.value]);
  exitDeleteMode();
};

const handleSwitch = (entry: ArchiveEntry) => {
  emit('select', entry);
};

const toggleSearch = () => {
  searchOpen.value = !searchOpen.value;
  if (!searchOpen.value) {
    query.value = '';
  }
};

const handleDeleteClick = () => {
  if (!isDeleteMode.value) {
    enterDeleteMode();
    pendingEntry.value = null;
    return;
  }
  if (selectedIds.value.length === 0) {
    exitDeleteMode();
    return;
  }
  confirmDelete();
};

const handleCopy = () => {
  if (!pendingEntry.value) return;
  emit('copy', pendingEntry.value);
};

watch(
  () => props.profiles,
  (nextProfiles) => {
    if (!isDeleteMode.value || selectedIds.value.length === 0) return;
    const idSet = new Set(nextProfiles.map((entry) => entry.id));
    selectedIds.value = selectedIds.value.filter((id) => idSet.has(id));
  },
  { deep: true }
);

watch(
  () => props.profiles,
  (nextProfiles) => {
    if (!pendingEntry.value) return;
    const next = nextProfiles.find((entry) => entry.id === pendingEntry.value?.id) ?? null;
    pendingEntry.value = next;
  },
  { deep: true }
);

watch(
  () => props.currentId,
  () => {
    if (isDeleteMode.value) return;
    pendingEntry.value = null;
  }
);
</script>
