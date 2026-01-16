<template>
  <div class="mx-auto max-w-[1100px] px-5 pb-16 pt-5">
    <div class="mb-4 flex items-center gap-3">
      <button
        class="flex h-8 w-8 items-center justify-center rounded-lg border border-[rgba(255,255,255,0.08)] bg-[rgba(15,24,40,0.9)] text-white transition hover:bg-white/10"
        type="button"
        @click="handleBack"
      >
        <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M19 12H5M12 19l-7-7 7-7" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
      <div class="min-w-0">
        <h2 class="text-lg font-semibold text-[var(--accent-2)]">编辑档案</h2>
        <p class="text-sm text-[var(--muted)]">修改后会重新排盘并覆盖原档案</p>
      </div>
    </div>

    <div v-if="!currentEntry" class="panel-card flex flex-col gap-2 text-center">
      <h2 class="text-lg font-semibold text-white">档案不存在</h2>
      <p class="text-sm text-[var(--muted)]">可能已被删除，请返回档案列表。</p>
      <button class="btn-primary mx-auto mt-2" type="button" @click="handleBack">
        返回档案管理
      </button>
    </div>

    <BirthFormCard
      v-else
      :loading="loading"
      :error="error"
      :initial-values="initialValues"
      :show-intro="false"
      submit-label="保存修改"
      submit-loading-label="保存中..."
      @submit="handleSubmit"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import BirthFormCard from '../components/BirthFormCard.vue';
import { useStore } from '../composables/useStore';
import type { BirthFormValues } from '../types/forms';
import type { ChartResponse } from '../types';
import { buildBirthFormValuesFromArchive, buildBirthLabel, buildChartRequestBody, buildPillarsFromChart } from '../utils/archive';

const router = useRouter();
const route = useRoute();
const { archives, activeArchiveId, chart, analysis, report } = useStore();

const loading = ref(false);
const error = ref('');

const archiveId = computed(() => Number(route.params.id));
const pendingEntryId = computed(() => {
  const raw = route.query.pendingId;
  if (typeof raw !== 'string') return null;
  const parsed = Number(raw);
  return Number.isFinite(parsed) ? parsed.toString() : null;
});
const currentEntry = computed(() => archives.value.find((entry) => entry.id === archiveId.value) ?? null);
const initialValues = computed(() => {
  if (!currentEntry.value) return undefined;
  return buildBirthFormValuesFromArchive(currentEntry.value);
});

const handleBack = () => {
  router.push({
    path: '/bazi/archives',
    query: pendingEntryId.value ? { pendingId: pendingEntryId.value } : undefined
  });
};

const normalizeText = (text: string) => text.replace(/\s+/g, '');

const getSolarParts = (value?: string | null) => {
  if (!value) return null;
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return null;
  return {
    year: date.getFullYear(),
    month: date.getMonth() + 1,
    day: date.getDate(),
    hour: date.getHours(),
    minute: date.getMinutes()
  };
};

const hasBirthDateChanged = (payload: BirthFormValues, entry: typeof currentEntry.value) => {
  if (!entry || payload.calendar !== 'solar') return true;
  const original = getSolarParts(entry.chart.solar_datetime);
  if (!original) return true;
  return !(
    payload.year === original.year &&
    payload.month === original.month &&
    payload.day === original.day &&
    payload.hour === original.hour &&
    payload.minute === original.minute
  );
};

const hasBirthPlaceChanged = (payload: BirthFormValues, entry: typeof currentEntry.value) => {
  if (!entry) return true;
  const original = entry.chart.birth_place || '未知地区';
  return normalizeText(payload.birthPlace.fullName) !== normalizeText(original);
};

const handleSubmit = async (payload: BirthFormValues) => {
  if (!currentEntry.value) return;
  error.value = '';
  loading.value = true;

  try {
    const entry = currentEntry.value;
    const name = payload.name.trim();
    const displayName = name || entry.displayName || entry.name || `命主${entry.id}`;
    const shouldRechart =
      hasBirthDateChanged(payload, entry) || hasBirthPlaceChanged(payload, entry);

    let updatedEntry = {
      ...entry,
      name,
      displayName,
    };

    if (shouldRechart) {
      const requestBody = buildChartRequestBody(payload);
      const chartRes = await fetch('/api/bazi/chart', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody)
      });

      if (!chartRes.ok) throw new Error(await chartRes.text());

      const chartData = (await chartRes.json()) as ChartResponse;
      const updatedChart = {
        ...chartData.chart,
        name: payload.name.trim() || null,
        destiny_relations_map: chartData.destiny_relations_map ?? {}
      };
      updatedEntry = {
        ...updatedEntry,
        gender: chartData.chart.gender,
        birthLabel: buildBirthLabel(payload),
        pillars: buildPillarsFromChart(chartData.chart),
        chart: updatedChart,
        reportState: {
          status: 'idle',
          report: null,
        },
      };
    } else {
      const nextChart = {
        ...entry.chart,
        gender: payload.gender,
        name: payload.name.trim() || null
      };
      updatedEntry = {
        ...updatedEntry,
        gender: payload.gender,
        chart: nextChart,
        reportState: entry.reportState,
      };
    }

    archives.value = archives.value.map((item) => (item.id === entry.id ? updatedEntry : item));

    if (activeArchiveId.value === entry.id) {
      chart.value = updatedEntry.chart;
      if (shouldRechart) {
        analysis.value = null;
        report.value = null;
      }
    }

    handleBack();
  } catch (err) {
    error.value = err instanceof Error ? err.message : String(err);
  } finally {
    loading.value = false;
  }
};
</script>
