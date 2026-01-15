<template>
  <section class="flex flex-col gap-3">
    <header
      v-if="mode === 'page'"
      class="sticky top-0 z-20 -mx-3 -mt-px relative before:content-[''] before:absolute before:inset-x-0 before:top-0 before:h-px before:bg-[rgba(18,22,33,0.75)] flex flex-col gap-3 border-b border-[rgba(255,255,255,0.08)] bg-[rgba(18,22,33,0.75)] px-3 py-3 backdrop-blur-xl md:-mx-4 md:px-4 lg:-mx-6 lg:px-6"
    >
      <div class="flex flex-wrap items-center justify-between gap-3">
        <div class="relative flex min-w-[200px] flex-1 items-center">
          <img
            :src="archiveSearchIconUrl"
            alt="搜索"
            class="pointer-events-none absolute left-3 h-3.5 w-3.5 object-contain opacity-70"
          />
          <input
            v-model="queryModel"
            type="text"
            class="h-9 w-full rounded-full border border-white/10 bg-white/5 pl-9 pr-2 text-sm text-white/85 placeholder-white/35 outline-none focus:border-[rgba(214,160,96,0.55)]"
            :placeholder="`搜索共 ${profiles.length} 份命盘档案...`"
          />
        </div>
        <div class="flex flex-wrap items-center gap-2">
          <button class="btn-ghost gap-1.5 px-3 py-2 text-xs" type="button" @click="$emit('create')">
            <img :src="archiveAddIconUrl" alt="新建" class="h-3.5 w-3.5 object-contain" />
            新建
          </button>
          <button
            class="btn-ghost gap-1.5 px-3 py-2 text-xs"
            type="button"
            :disabled="profiles.length === 0"
            :class="isDeleteMode ? `${activeActionClass} bg-white/10` : 'bg-transparent'"
            @click="handleDeleteClick"
          >
            <img
              :src="archiveManageIconUrl"
              alt="管理"
              class="h-3.5 w-3.5 object-contain"
              :style="{ filter: isDeleteMode ? activeIconFilter : 'none' }"
            />
            管理
          </button>
        </div>
      </div>
      <div v-if="isDeleteMode" class="flex w-full items-center justify-between gap-3">
        <button class="btn-ghost gap-1.5 px-3 py-2 text-xs" type="button" @click="exitDeleteMode">
          <img :src="archiveManageExitIconUrl" alt="退出" class="h-3.5 w-3.5 object-contain" />
          退出
        </button>
        <div class="flex items-center gap-2">
          <button
            class="btn-ghost px-3 py-2 text-xs"
            :class="isAllSelected ? 'bg-white/10' : 'bg-transparent'"
            type="button"
            @click="toggleSelectAll"
          >
            {{ selectAllLabel }}
          </button>
          <button
            class="btn-ghost border px-3 py-2 text-xs"
            type="button"
            :disabled="selectedIds.length === 0"
            :style="{ borderColor: deleteBorderAccent, color: deleteBorderAccent }"
            @click="confirmDelete"
          >
            删除选中档案
          </button>
        </div>
      </div>
    </header>

    <header
      v-else-if="showModalSearch"
      class="sticky top-0 z-20 -mx-4 relative before:content-[''] before:absolute before:inset-x-0 before:top-0 before:h-px before:bg-[rgba(18,20,28,0.96)] border-b border-[rgba(255,255,255,0.08)] bg-[rgba(18,20,28,0.96)] px-4 py-3 backdrop-blur-xl md:-mx-5 md:px-5"
    >
      <input
        v-model="queryModel"
        type="text"
        class="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white/85 placeholder-white/35 outline-none focus:border-[rgba(214,160,96,0.55)]"
        placeholder="搜索档案名称..."
      />
    </header>

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
          :show-actions="pendingEntry?.id === entry.id ? pendingActions : false"
          :show-more="mode === 'page'"
          :show-checkbox="isDeleteMode"
          :checked="selectedIds.includes(entry.id)"
          @click="handleItemClick(entry)"
          @more="handleMoreClick(entry)"
          @delete="handleQuickDelete(entry)"
          @toggle="toggleSelect(entry.id)"
          @copy="handleCopy(entry)"
          @edit="handleEdit(entry)"
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
import archiveManageIconUrl from '../assets/archive_manage.png';
import archiveManageExitIconUrl from '../assets/archive_manage_exit.png';

const props = withDefaults(defineProps<{
  mode: 'page' | 'modal';
  profiles: ArchiveEntry[];
  currentId: number | null;
  pendingId?: number | null;
  searchQuery?: string;
  showModalSearch?: boolean;
}>(), {
  showModalSearch: true
});

const emit = defineEmits<{
  (e: 'select', entry: ArchiveEntry): void;
  (e: 'create'): void;
  (e: 'delete', ids: number[]): void;
  (e: 'copy', entry: ArchiveEntry): void;
  (e: 'edit', entry: ArchiveEntry): void;
  (e: 'request-delete', entry: ArchiveEntry): void;
  (e: 'request-delete-bulk', ids: number[]): void;
  (e: 'update:searchQuery', value: string): void;
}>();

const localQuery = ref('');
const queryModel = computed<string>({
  get: () => props.searchQuery ?? localQuery.value,
  set: (next) => {
    if (props.searchQuery !== undefined) {
      emit('update:searchQuery', next);
      return;
    }
    localQuery.value = next;
  }
});
const showModalSearch = computed(() => props.showModalSearch);
const isDeleteMode = ref(false);
const selectedIds = ref<number[]>([]);
const pendingEntry = ref<ArchiveEntry | null>(null);
const pendingActions = ref(false);
const manageBorderAccent = '#8a4a4a';
const deleteBorderAccent = '#e36b6b';
const activeActionClass = 'border-[rgba(214,160,96,0.7)] text-[var(--accent-2)]';
const activeIconFilter =
  'brightness(0) saturate(100%) invert(78%) sepia(24%) saturate(742%) hue-rotate(350deg) brightness(95%) contrast(88%)';

const isAllSelected = computed(() => {
  if (filteredProfiles.value.length === 0) return false;
  return filteredProfiles.value.every((entry) => selectedIds.value.includes(entry.id));
});

const selectAllLabel = computed(() => (isAllSelected.value ? '取消全选' : '全选'));

const filteredProfiles = computed(() => {
  const keyword = queryModel.value.trim().toLowerCase();
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

const toggleSelectAll = () => {
  if (!isDeleteMode.value) return;
  const allIds = filteredProfiles.value.map((entry) => entry.id);
  const allSelected = allIds.length > 0 && allIds.every((id) => selectedIds.value.includes(id));
  selectedIds.value = allSelected ? [] : allIds;
};

const handleItemClick = (entry: ArchiveEntry) => {
  if (isDeleteMode.value) {
    toggleSelect(entry.id);
    return;
  }
  pendingEntry.value = null;
  pendingActions.value = false;
  emit('select', entry);
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
  emit('request-delete-bulk', [...selectedIds.value]);
};

const handleMoreClick = (entry: ArchiveEntry) => {
  if (isDeleteMode.value) return;
  if (pendingEntry.value?.id === entry.id) {
    if (pendingActions.value) {
      pendingEntry.value = null;
      pendingActions.value = false;
      return;
    }
    pendingActions.value = true;
    return;
  }
  pendingEntry.value = entry;
  pendingActions.value = true;
};

const handleQuickDelete = (entry: ArchiveEntry) => {
  pendingEntry.value = null;
  pendingActions.value = false;
  emit('request-delete', entry);
};

const handleEdit = (entry?: ArchiveEntry) => {
  const target = entry ?? pendingEntry.value;
  if (!target) return;
  pendingEntry.value = null;
  pendingActions.value = false;
  emit('edit', target);
};

const handleDeleteClick = () => {
  if (!isDeleteMode.value) {
    enterDeleteMode();
    pendingEntry.value = null;
    pendingActions.value = false;
    return;
  }
  exitDeleteMode();
};

const handleCopy = (entry?: ArchiveEntry) => {
  const target = entry ?? pendingEntry.value;
  if (!target) return;
  pendingEntry.value = null;
  pendingActions.value = false;
  emit('copy', target);
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
    if (!next) {
      pendingActions.value = false;
    }
  },
  { deep: true }
);

watch(
  () => props.currentId,
  () => {
    if (isDeleteMode.value) return;
    pendingEntry.value = null;
    pendingActions.value = false;
  }
);

watch(
  () => props.pendingId,
  (nextId) => {
    if (!nextId || isDeleteMode.value) return;
    const target = props.profiles.find((entry) => entry.id === nextId) ?? null;
    if (!target) return;
    pendingEntry.value = target;
    pendingActions.value = false;
  },
  { immediate: true }
);
</script>
