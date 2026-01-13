<template>
  <div class="mx-auto max-w-[1100px] px-5 pb-16 pt-5">
    <!-- 选择模式：新建排盘 或 从档案选择 -->
    <div v-if="!showForm && !showArchiveList" class="flex flex-col gap-4 mb-6">
      <div class="panel-card flex flex-col gap-3">
        <h2 class="text-lg font-semibold text-[var(--accent-2)] mb-2">选择排盘方式</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
          <button
            class="panel-tile flex flex-col items-center gap-3 py-5 text-left transition-all duration-200 hover:-translate-y-0.5 hover:border-[rgba(214,160,96,0.4)] hover:shadow-lg"
            type="button"
            @click="showForm = true"
          >
            <div class="flex items-center justify-center w-12 h-12 rounded-lg bg-gradient-to-br from-[var(--accent)] to-[var(--accent-2)]">
              <svg class="w-6 h-6 text-[#0c0f15]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 5v14M5 12h14" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <div class="flex flex-col gap-1 text-center">
              <span class="text-base font-semibold text-white">新建排盘</span>
              <span class="text-sm text-[var(--muted)]">填写生辰信息进行排盘</span>
            </div>
          </button>
          <button
            class="panel-tile flex flex-col items-center gap-3 py-5 text-left transition-all duration-200 hover:-translate-y-0.5 hover:border-[rgba(214,160,96,0.4)] hover:shadow-lg"
            type="button"
            @click="showArchiveList = true"
            :disabled="archives.length === 0"
            :class="archives.length === 0 ? 'opacity-50 cursor-not-allowed' : ''"
          >
            <div class="flex items-center justify-center w-12 h-12 rounded-lg bg-gradient-to-br from-[var(--accent)] to-[var(--accent-2)]">
              <svg class="w-6 h-6 text-[#0c0f15]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M4 7h16M4 12h16M4 17h16" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <div class="flex flex-col gap-1 text-center">
              <span class="text-base font-semibold text-white">从档案选择</span>
              <span class="text-sm text-[var(--muted)]">
                {{ archives.length > 0 ? `已有 ${archives.length} 份档案` : '暂无档案' }}
              </span>
            </div>
          </button>
        </div>
      </div>
    </div>

    <!-- 档案列表 -->
    <div v-if="showArchiveList" class="flex flex-col gap-4 mb-6">
      <div class="panel-card flex items-center justify-between gap-4">
        <div class="flex items-center gap-3">
          <button
            class="flex items-center justify-center w-8 h-8 rounded-lg border border-[rgba(255,255,255,0.08)] bg-[rgba(15,24,40,0.9)] text-white transition hover:bg-white/10"
            type="button"
            @click="showArchiveList = false; showForm = false"
          >
            <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M19 12H5M12 19l-7-7 7-7" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
          <div>
            <h2 class="text-lg font-semibold text-[var(--accent-2)]">选择档案</h2>
            <p class="text-sm text-[var(--muted)]">已保存 {{ archives.length }} 份命盘档案</p>
          </div>
        </div>
      </div>

      <div class="flex flex-col gap-3">
        <button
          v-for="entry in archives"
          :key="entry.id"
          :class="[
            'panel-tile flex items-center justify-between gap-4 px-5 py-4 text-left transition-all duration-200 hover:border-[rgba(214,160,96,0.4)] hover:-translate-y-0.5 hover:shadow-lg',
            entry.id === activeArchiveId
              ? 'border-[rgba(214,160,96,0.85)] shadow-lg'
              : ''
          ]"
          type="button"
          @click="selectArchive(entry)"
        >
          <div class="flex flex-col gap-1.5 flex-1 min-w-0">
            <div class="text-lg font-semibold text-[var(--accent-2)]">{{ entry.displayName }}</div>
            <div class="text-sm text-[var(--muted)]">{{ entry.birthLabel }}</div>
          </div>
          <div class="flex items-center gap-2 text-2xl text-[var(--accent-2)] opacity-80">
            <span>›</span>
          </div>
        </button>
      </div>
    </div>

    <!-- 新建排盘表单 -->
    <div v-if="showForm">
      <div class="flex items-center gap-3 mb-4">
        <button
          class="flex items-center justify-center w-8 h-8 rounded-lg border border-[rgba(255,255,255,0.08)] bg-[rgba(15,24,40,0.9)] text-white transition hover:bg-white/10"
          type="button"
          @click="showForm = false"
        >
          <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M19 12H5M12 19l-7-7 7-7" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
        <h2 class="text-lg font-semibold text-[var(--accent-2)]">新建排盘</h2>
      </div>
      <BirthFormCard
        :loading="loading"
        :error="error"
        @submit="handleSubmit"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import BirthFormCard from '../components/BirthFormCard.vue';
import { useStore } from '../composables/useStore';
import type { BirthFormValues } from '../types/forms';
import type { ChartResponse } from '../types';
import type { ArchiveEntry } from '../utils/storage';
import { buildBirthLabel, buildChartRequestBody, buildPillarsFromChart } from '../utils/archive';

const router = useRouter();
const { chart, analysis, report, archives, archiveCounter, activeArchiveId } = useStore();

const loading = ref(false);
const error = ref('');
const showForm = ref(false);
const showArchiveList = ref(false);

// 如果用户有档案，默认显示选择页面；否则直接显示表单
const hasArchives = computed(() => archives.value.length > 0);

// 初始化：如果有档案，显示选择页面；否则直接显示表单
if (!hasArchives.value) {
  showForm.value = true;
}

// 提交表单，调用排盘 API
const handleSubmit = async (payload: BirthFormValues) => {
  error.value = '';
  loading.value = true;

  try {
    // 构建请求体，包含出生地点信息
    const requestBody = buildChartRequestBody(payload);

    const chartRes = await fetch('/api/bazi/chart', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestBody)
    });

    if (!chartRes.ok) throw new Error(await chartRes.text());

    const chartData = (await chartRes.json()) as ChartResponse;

    // 保存到全局状态
    chart.value = chartData.chart;

    // 保存到档案
    saveArchive(payload, chartData.chart);

    // 清空报告和分析（新的命盘）
    analysis.value = null;
    report.value = null;

    // 生成临时 ID 或使用档案 ID
    const chartId = activeArchiveId.value || 'temp-' + Date.now();

    // 跳转到命盘详情页
    router.push(`/bazi/chart/${chartId}/pillars`);
  } catch (err) {
    error.value = err instanceof Error ? err.message : String(err);
  } finally {
    loading.value = false;
  }
};

// 选择档案
const selectArchive = (entry: ArchiveEntry) => {
  activeArchiveId.value = entry.id;
  chart.value = entry.chart;

  // 清空分析和报告（需要重新生成）
  analysis.value = null;
  report.value = null;

  // 跳转到命盘详情页
  router.push(`/bazi/chart/${entry.id}/pillars`);
};

// 保存档案
const saveArchive = (formValues: BirthFormValues, chartData: any) => {
  const name = formValues.name.trim();
  const displayName = name || `命主${archiveCounter.value + 1}`;
  archiveCounter.value += 1;

  const birthLabel = buildBirthLabel(formValues);
  const pillars = buildPillarsFromChart(chartData);

  const entry = {
    id: archiveCounter.value,
    name,
    displayName,
    gender: chartData.gender,
    birthLabel,
    pillars,
    chart: chartData
  };

  archives.value.unshift(entry);
  activeArchiveId.value = entry.id;
};

// 从 Chart 数据构建四柱信息（用于档案显示）
</script>
