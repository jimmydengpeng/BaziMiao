<template>
  <div class="mx-auto max-w-[1600px] px-3 pb-6 md:px-4 md:pb-8 lg:px-6 lg:pb-10">
    <ArchiveListPanel
      mode="page"
      :profiles="archives"
      :current-id="activeArchiveId"
      :pending-id="pendingEntryId"
      @select="openArchive"
      @create="goToNewForm"
      @delete="deleteArchives"
      @request-delete="handleRequestDelete"
      @request-delete-bulk="handleRequestDeleteBulk"
      @copy="copyArchiveInfo"
      @edit="handleEditArchive"
    />
    <div
      v-if="showCopyModal"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 px-4 py-6 backdrop-blur-sm"
    >
      <div class="w-full max-w-sm rounded-2xl border border-white/10 bg-[rgba(18,22,33,0.95)] p-5 text-center shadow-[0_30px_80px_rgba(0,0,0,0.55)]">
        <div class="mx-auto flex h-12 w-12 items-center justify-center">
          <img
            :src="successIconUrl"
            alt="复制成功"
            class="h-12 w-12"
            :style="{ filter: successIconFilter }"
          />
        </div>
        <h2 class="mt-3 text-lg font-semibold text-white">复制成功</h2>
        <p class="mt-2 text-sm text-[var(--muted)]">可直接修改内容后再次复制。</p>
        <textarea
          v-model="copyText"
          class="mt-4 h-32 w-full resize-none rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-left text-xs text-white/85 outline-none focus:border-[rgba(214,160,96,0.55)]"
          @focus="isCopyMode = true"
          @input="isCopyMode = true"
        ></textarea>
        <button class="btn-primary mt-4 w-full" type="button" @click="handleModalAction">
          {{ isCopyMode ? '复制' : '好的' }}
        </button>
      </div>
    </div>
    <div
      v-if="showDeleteModal"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 px-4 py-6 backdrop-blur-sm"
    >
      <div
        class="w-full max-w-sm rounded-2xl border bg-[rgba(22,16,18,0.95)] p-5 text-center shadow-[0_30px_80px_rgba(0,0,0,0.55)]"
        :style="{ borderColor: deleteAccent }"
      >
        <div class="mx-auto flex h-12 w-12 items-center justify-center">
          <img
            :src="deleteIconUrl"
            alt="删除档案"
            class="h-10 w-10"
            :style="{ filter: deleteIconFilter }"
          />
        </div>
        <h2 class="mt-3 text-lg font-semibold text-white">确认删除</h2>
        <p class="mt-2 text-sm text-[var(--muted)]">
          将删除 {{ deleteTargetLabel }} 的档案，且无法恢复。
        </p>
        <div class="mt-4 flex gap-3">
          <button class="btn-ghost flex-1" type="button" @click="closeDeleteModal">
            取消
          </button>
          <button
            class="btn-primary flex-1 border text-white"
            type="button"
            :style="{
              background: deleteAccent,
              borderColor: deleteBorderAccent,
              boxShadow: '0 12px 24px rgba(90, 37, 37, 0.35)'
            }"
            @click="confirmDelete"
          >
            删除
          </button>
        </div>
      </div>
    </div>
    <div
      v-if="showBulkDeleteModal"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 px-4 py-6 backdrop-blur-sm"
    >
      <div
        class="w-full max-w-sm rounded-2xl border bg-[rgba(22,16,18,0.95)] p-5 text-center shadow-[0_30px_80px_rgba(0,0,0,0.55)]"
        :style="{ borderColor: deleteAccent }"
      >
        <div class="mx-auto flex h-12 w-12 items-center justify-center">
          <img
            :src="deleteIconUrl"
            alt="删除档案"
            class="h-10 w-10"
            :style="{ filter: deleteIconFilter }"
          />
        </div>
        <h2 class="mt-3 text-lg font-semibold text-white">确认删除</h2>
        <p class="mt-2 text-sm text-[var(--muted)]">
          将删除选中的 {{ bulkDeleteCount }} 份档案，且无法恢复。
        </p>
        <div class="mt-4 flex gap-3">
          <button class="btn-ghost flex-1" type="button" @click="closeBulkDeleteModal">
            取消
          </button>
          <button
            class="btn-primary flex-1 border text-white"
            type="button"
            :style="{
              background: deleteAccent,
              borderColor: deleteBorderAccent,
              boxShadow: '0 12px 24px rgba(90, 37, 37, 0.35)'
            }"
            @click="confirmBulkDelete"
          >
            删除
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useStore } from '../composables/useStore';
import type { ArchiveEntry } from '../utils/storage';
import ArchiveListPanel from '../components/ArchiveListPanel.vue';
import successIconUrl from '../assets/success.png';
import deleteIconUrl from '../assets/archive_delete.png';

const router = useRouter();
const route = useRoute();
const { archives, activeArchiveId, chart, analysis, report } = useStore();
const showCopyModal = ref(false);
const copyText = ref('');
const isCopyMode = ref(false);
const showDeleteModal = ref(false);
const showBulkDeleteModal = ref(false);
const deleteTargetEntry = ref<ArchiveEntry | null>(null);
const bulkDeleteIds = ref<number[]>([]);
const deleteAccent = '#5a2525';
const deleteBorderAccent = '#8a4a4a';
const successIconFilter =
  'brightness(0) saturate(100%) invert(78%) sepia(24%) saturate(742%) hue-rotate(350deg) brightness(95%) contrast(88%)';
const deleteIconFilter =
  'brightness(0) saturate(100%) invert(22%) sepia(24%) saturate(1948%) hue-rotate(327deg) brightness(94%) contrast(98%)';
const deleteTargetLabel = computed(() => {
  const entry = deleteTargetEntry.value;
  if (!entry) return '该档案';
  return entry.displayName || entry.name || `档案 #${entry.id}`;
});
const bulkDeleteCount = computed(() => bulkDeleteIds.value.length);
const pendingEntryId = computed(() => {
  const raw = route.query.pendingId;
  if (typeof raw !== 'string') return null;
  const parsed = Number(raw);
  return Number.isFinite(parsed) ? parsed : null;
});

// 打开档案，加载命盘数据并跳转到详情页
const openArchive = (entry: ArchiveEntry) => {
  activeArchiveId.value = entry.id;
  chart.value = entry.chart;

  // 清空分析和报告（需要重新生成）
  analysis.value = null;
  report.value = null;

  // 跳转到命盘详情页
  router.push(`/bazi/chart/${entry.id}/pillars`);
};

// 跳转到新建表单
const goToNewForm = () => {
  router.push('/bazi/form');
};

const handleEditArchive = (entry: ArchiveEntry) => {
  router.push({
    path: `/bazi/archives/${entry.id}/edit`,
    query: { pendingId: entry.id.toString() }
  });
};

const deleteArchives = (ids: number[]) => {
  if (ids.length === 0) return;
  const remaining = archives.value.filter((entry) => !ids.includes(entry.id));
  archives.value = remaining;

  if (activeArchiveId.value !== null && ids.includes(activeArchiveId.value)) {
    const next = remaining[0] ?? null;
    activeArchiveId.value = next ? next.id : null;
    chart.value = next ? next.chart : null;
    analysis.value = null;
    report.value = null;
  }
};

const handleRequestDelete = (entry: ArchiveEntry) => {
  deleteTargetEntry.value = entry;
  showDeleteModal.value = true;
};

const closeDeleteModal = () => {
  showDeleteModal.value = false;
  deleteTargetEntry.value = null;
};

const confirmDelete = () => {
  if (!deleteTargetEntry.value) return;
  deleteArchives([deleteTargetEntry.value.id]);
  closeDeleteModal();
};

const handleRequestDeleteBulk = (ids: number[]) => {
  if (ids.length === 0) return;
  bulkDeleteIds.value = ids;
  showBulkDeleteModal.value = true;
};

const closeBulkDeleteModal = () => {
  showBulkDeleteModal.value = false;
  bulkDeleteIds.value = [];
};

const confirmBulkDelete = () => {
  if (bulkDeleteIds.value.length === 0) return;
  deleteArchives([...bulkDeleteIds.value]);
  closeBulkDeleteModal();
};

const formatGender = (gender?: string | null) => {
  if (gender === 'male') return '男';
  if (gender === 'female') return '女';
  return gender ? '其他' : '未知';
};

const writeClipboard = async (text: string) => {
  if (navigator.clipboard?.writeText) {
    await navigator.clipboard.writeText(text);
    return;
  }
  const textarea = document.createElement('textarea');
  textarea.value = text;
  textarea.style.position = 'fixed';
  textarea.style.left = '-9999px';
  document.body.appendChild(textarea);
  textarea.select();
  document.execCommand('copy');
  document.body.removeChild(textarea);
};

const copyArchiveInfo = async (entry: ArchiveEntry) => {
  const destiny = entry.chart?.destiny_cycle?.destiny_pillars ?? [];
  const destinyText = destiny
    .slice(0, 6)
    .map((pillar) => `${pillar.heaven_stem.name}${pillar.earth_branch.name}`)
    .join('、');
  const pillarsText = entry.pillars
    .map((pillar) => `${pillar.stem}${pillar.branch}`)
    .join('、');
  const text = [
    `姓名：${entry.displayName || entry.name || '未命名'}`,
    `性别：${formatGender(entry.chart?.gender ?? null)}`,
    `四柱：${pillarsText || '未知'}`,
    `大运：${destinyText || '未知'}`
  ].join('\n');

  try {
    await writeClipboard(text);
    copyText.value = text;
    isCopyMode.value = false;
    showCopyModal.value = true;
  } catch (error) {
    console.error('复制失败:', error);
    window.alert('复制失败，请稍后重试。');
  }
};

const handleModalAction = async () => {
  if (!isCopyMode.value) {
    showCopyModal.value = false;
    return;
  }
  try {
    await writeClipboard(copyText.value);
    showCopyModal.value = false;
  } catch (error) {
    console.error('复制失败:', error);
    window.alert('复制失败，请稍后重试。');
  }
};
</script>
