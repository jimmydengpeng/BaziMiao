/**
 * 全局状态管理 Composable
 * 用于在各页面组件间共享数据（命盘、报告、档案等）
 */

import { ref, computed, watch } from 'vue';
import type { Chart, Analysis, Report } from '../types';
import {
  type ArchiveEntry,
  type ArchiveReportState,
  loadArchives,
  saveArchives,
  loadCurrentChart,
  saveCurrentChart,
  loadCurrentAnalysis,
  saveCurrentAnalysis,
  loadArchiveCounter,
  saveArchiveCounter,
  loadActiveArchiveId,
  saveActiveArchiveId,
} from '../utils/storage';

// 全局状态（使用单例模式，确保所有组件共享同一份数据）
const chart = ref<Chart | null>(null);
const analysis = ref<Analysis | null>(null);
const report = ref<Report | null>(null);
const archives = ref<ArchiveEntry[]>([]);
const archiveCounter = ref(0);
const activeArchiveId = ref<number | null>(null);
const isAuthenticated = ref(false);

// 是否已初始化（避免重复加载）
let initialized = false;

/**
 * 初始化全局状态（从 localStorage 加载数据）
 */
const initializeStore = () => {
  if (initialized) return;

  chart.value = loadCurrentChart();
  analysis.value = loadCurrentAnalysis();
  archives.value = loadArchives();
  archiveCounter.value = loadArchiveCounter();
  activeArchiveId.value = loadActiveArchiveId();
  if (activeArchiveId.value !== null) {
    const entry = archives.value.find((item) => item.id === activeArchiveId.value) ?? null;
    report.value = entry?.reportState.report ?? null;
  } else {
    report.value = null;
  }

  initialized = true;
};

/**
 * 全局状态管理 Hook
 */
export const useStore = () => {
  // 确保初始化
  if (!initialized) {
    initializeStore();
  }

  // 监听数据变化，自动保存到 localStorage
  watch(chart, (newChart) => {
    saveCurrentChart(newChart);
  }, { deep: true });

  watch(analysis, (newAnalysis) => {
    saveCurrentAnalysis(newAnalysis);
  }, { deep: true });

  watch(archives, (newArchives) => {
    saveArchives(newArchives);
  }, { deep: true });

  watch(archiveCounter, (newCounter) => {
    saveArchiveCounter(newCounter);
  });

  watch(activeArchiveId, (newId) => {
    saveActiveArchiveId(newId);
  });

  // 计算属性
  const canChat = computed(() => !!chart.value && !!analysis.value);
  const updateActiveArchiveReportState = (partial: Partial<ArchiveReportState>) => {
    const activeId = activeArchiveId.value;
    if (activeId === null) return;

    const index = archives.value.findIndex((entry) => entry.id === activeId);
    if (index < 0) return;

    const current = archives.value[index];
    const currentState = current.reportState ?? { status: 'idle', report: null };

    const nextReport =
      Object.prototype.hasOwnProperty.call(partial, 'report') ? partial.report ?? null : currentState.report;
    const nextState: ArchiveReportState = {
      ...currentState,
      ...partial,
      report: nextReport,
      status: nextReport ? 'generated' : 'idle',
    };

    if (
      nextState.report === currentState.report &&
      nextState.status === currentState.status &&
      nextState.debugPrompt === currentState.debugPrompt &&
      nextState.updatedAt === currentState.updatedAt
    ) {
      return;
    }

    archives.value = [
      ...archives.value.slice(0, index),
      { ...current, reportState: nextState },
      ...archives.value.slice(index + 1),
    ];
  };

  const canViewReport = computed(() => !!activeArchiveId.value || !!report.value);

  watch(activeArchiveId, (newId) => {
    if (newId === null) {
      report.value = null;
      return;
    }
    const entry = archives.value.find((item) => item.id === newId) ?? null;
    report.value = entry?.reportState.report ?? null;
  });

  watch(report, (newReport) => {
    updateActiveArchiveReportState({ report: newReport ?? null });
  }, { deep: true });

  return {
    // 状态
    chart,
    analysis,
    report,
    archives,
    archiveCounter,
    activeArchiveId,
    isAuthenticated,

    // 计算属性
    canChat,
    canViewReport,
    updateActiveArchiveReportState,
  };
};
