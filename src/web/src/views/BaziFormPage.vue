<template>
  <div class="mx-auto max-w-[1100px] px-5 pb-16 pt-5">
    <BirthFormCard :loading="loading" :error="error" :show-intro="false" @submit="handleSubmit" />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import BirthFormCard from '../components/BirthFormCard.vue';
import { useStore } from '../composables/useStore';
import type { BirthFormValues } from '../types/forms';
import type { ChartResponse } from '../types';
import { buildBirthLabel, buildChartRequestBody, buildPillarsFromChart } from '../utils/archive';

const router = useRouter();
const { chart, analysis, report, archives, archiveCounter, activeArchiveId } = useStore();

const loading = ref(false);
const error = ref('');

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
    chart.value = {
      ...chartData.chart,
      destiny_relations_map: chartData.destiny_relations_map ?? {}
    };

    // 保存到档案
    saveArchive(payload, {
      ...chartData.chart,
      destiny_relations_map: chartData.destiny_relations_map ?? {}
    });

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
