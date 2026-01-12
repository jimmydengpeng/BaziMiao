<template>
  <div class="mx-auto max-w-[1600px] px-3 pb-6 md:px-4 md:pb-8 lg:px-6 lg:pb-10">
    <ArchiveListPanel
      mode="page"
      :profiles="archives"
      :current-id="activeArchiveId"
      @select="openArchive"
      @create="goToNewForm"
      @delete="deleteArchives"
      @copy="copyArchiveInfo"
    />
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import { useStore } from '../composables/useStore';
import type { ArchiveEntry } from '../utils/storage';
import ArchiveListPanel from '../components/ArchiveListPanel.vue';

const router = useRouter();
const { archives, activeArchiveId, chart, analysis, report } = useStore();

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

const formatGender = (gender?: string | null) => {
  if (gender === 'male') return '男';
  if (gender === 'female') return '女';
  return gender ? '其他' : '未知';
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
    `前6个大运：${destinyText || '未知'}`
  ].join('\n');

  try {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(text);
    } else {
      const textarea = document.createElement('textarea');
      textarea.value = text;
      textarea.style.position = 'fixed';
      textarea.style.left = '-9999px';
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand('copy');
      document.body.removeChild(textarea);
    }
    window.alert('已复制档案信息到剪切板。');
  } catch (error) {
    console.error('复制失败:', error);
    window.alert('复制失败，请稍后重试。');
  }
};
</script>
