/**
 * localStorage 数据持久化工具
 * 用于保存用户的档案、当前命盘等数据
 */

import type { Chart, Analysis, Report } from '../types';

// 存储键名
const STORAGE_KEYS = {
  ARCHIVES: 'bazi_archives',
  CURRENT_CHART: 'bazi_current_chart',
  CURRENT_ANALYSIS: 'bazi_current_analysis',
  CURRENT_REPORT: 'bazi_current_report',
  ARCHIVE_COUNTER: 'bazi_archive_counter',
  ACTIVE_ARCHIVE_ID: 'bazi_active_archive_id',
  BAZI_VIEW_STATE: 'bazi_view_state', // 命盘解析模块的浏览状态
} as const;

// 档案条目类型定义
export type ArchivePillar = {
  stem: string;
  branch: string;
  stemElement: string;
  branchElement: string;
};

export type ArchiveEntry = {
  id: number;
  name: string;
  displayName: string;
  birthLabel: string;
  pillars: ArchivePillar[];
  chart: Chart;
};

/**
 * 保存档案列表到 localStorage
 */
export const saveArchives = (archives: ArchiveEntry[]): void => {
  try {
    localStorage.setItem(STORAGE_KEYS.ARCHIVES, JSON.stringify(archives));
  } catch (error) {
    console.error('保存档案失败:', error);
  }
};

/**
 * 从 localStorage 加载档案列表
 */
export const loadArchives = (): ArchiveEntry[] => {
  try {
    const data = localStorage.getItem(STORAGE_KEYS.ARCHIVES);
    return data ? JSON.parse(data) : [];
  } catch (error) {
    console.error('加载档案失败:', error);
    return [];
  }
};

/**
 * 保存当前命盘到 localStorage（用于刷新后恢复）
 */
export const saveCurrentChart = (chart: Chart | null): void => {
  try {
    if (chart) {
      localStorage.setItem(STORAGE_KEYS.CURRENT_CHART, JSON.stringify(chart));
    } else {
      localStorage.removeItem(STORAGE_KEYS.CURRENT_CHART);
    }
  } catch (error) {
    console.error('保存当前命盘失败:', error);
  }
};

/**
 * 从 localStorage 加载当前命盘
 */
export const loadCurrentChart = (): Chart | null => {
  try {
    const data = localStorage.getItem(STORAGE_KEYS.CURRENT_CHART);
    return data ? JSON.parse(data) : null;
  } catch (error) {
    console.error('加载当前命盘失败:', error);
    return null;
  }
};

/**
 * 保存当前分析结果
 */
export const saveCurrentAnalysis = (analysis: Analysis | null): void => {
  try {
    if (analysis) {
      localStorage.setItem(STORAGE_KEYS.CURRENT_ANALYSIS, JSON.stringify(analysis));
    } else {
      localStorage.removeItem(STORAGE_KEYS.CURRENT_ANALYSIS);
    }
  } catch (error) {
    console.error('保存当前分析失败:', error);
  }
};

/**
 * 加载当前分析结果
 */
export const loadCurrentAnalysis = (): Analysis | null => {
  try {
    const data = localStorage.getItem(STORAGE_KEYS.CURRENT_ANALYSIS);
    return data ? JSON.parse(data) : null;
  } catch (error) {
    console.error('加载当前分析失败:', error);
    return null;
  }
};

/**
 * 保存当前报告
 */
export const saveCurrentReport = (report: Report | null): void => {
  try {
    if (report) {
      localStorage.setItem(STORAGE_KEYS.CURRENT_REPORT, JSON.stringify(report));
    } else {
      localStorage.removeItem(STORAGE_KEYS.CURRENT_REPORT);
    }
  } catch (error) {
    console.error('保存当前报告失败:', error);
  }
};

/**
 * 加载当前报告
 */
export const loadCurrentReport = (): Report | null => {
  try {
    const data = localStorage.getItem(STORAGE_KEYS.CURRENT_REPORT);
    return data ? JSON.parse(data) : null;
  } catch (error) {
    console.error('加载当前报告失败:', error);
    return null;
  }
};

/**
 * 保存档案计数器
 */
export const saveArchiveCounter = (counter: number): void => {
  try {
    localStorage.setItem(STORAGE_KEYS.ARCHIVE_COUNTER, counter.toString());
  } catch (error) {
    console.error('保存档案计数器失败:', error);
  }
};

/**
 * 加载档案计数器
 */
export const loadArchiveCounter = (): number => {
  try {
    const data = localStorage.getItem(STORAGE_KEYS.ARCHIVE_COUNTER);
    return data ? parseInt(data, 10) : 0;
  } catch (error) {
    console.error('加载档案计数器失败:', error);
    return 0;
  }
};

/**
 * 保存当前激活的档案 ID
 */
export const saveActiveArchiveId = (id: number | null): void => {
  try {
    if (id !== null) {
      localStorage.setItem(STORAGE_KEYS.ACTIVE_ARCHIVE_ID, id.toString());
    } else {
      localStorage.removeItem(STORAGE_KEYS.ACTIVE_ARCHIVE_ID);
    }
  } catch (error) {
    console.error('保存激活档案ID失败:', error);
  }
};

/**
 * 加载当前激活的档案 ID
 */
export const loadActiveArchiveId = (): number | null => {
  try {
    const data = localStorage.getItem(STORAGE_KEYS.ACTIVE_ARCHIVE_ID);
    return data ? parseInt(data, 10) : null;
  } catch (error) {
    console.error('加载激活档案ID失败:', error);
    return null;
  }
};

/**
 * 命盘解析模块的浏览状态
 */
export type BaziViewPage = 'chart' | 'report' | 'detail' | 'verification';

export type BaziViewState = {
  page: BaziViewPage; // 当前浏览的页面
  scrollPosition: number; // 滚动位置
  chartId: string | number; // 命盘ID
};

/**
 * 保存命盘解析模块的浏览状态
 */
export const saveBaziViewState = (state: BaziViewState | null): void => {
  try {
    if (state) {
      localStorage.setItem(STORAGE_KEYS.BAZI_VIEW_STATE, JSON.stringify(state));
    } else {
      localStorage.removeItem(STORAGE_KEYS.BAZI_VIEW_STATE);
    }
  } catch (error) {
    console.error('保存浏览状态失败:', error);
  }
};

/**
 * 加载命盘解析模块的浏览状态
 */
export const loadBaziViewState = (): BaziViewState | null => {
  try {
    const data = localStorage.getItem(STORAGE_KEYS.BAZI_VIEW_STATE);
    if (!data) return null;

    const raw = JSON.parse(data) as unknown;
    if (!raw || typeof raw !== 'object') return null;

    const record = raw as { [key: string]: unknown };
    const rawPage = record.page;
    // 兼容旧值 pro -> detail
    const page: BaziViewPage | null = (() => {
      if (rawPage === 'pro') return 'detail';
      if (rawPage === 'chart') return 'chart';
      if (rawPage === 'report') return 'report';
      if (rawPage === 'detail') return 'detail';
      if (rawPage === 'verification') return 'verification';
      return null;
    })();

    const chartId = record.chartId;
    const scrollPosition = record.scrollPosition;

    if (!page) return null;
    if (typeof chartId !== 'string' && typeof chartId !== 'number') return null;

    const normalizedScrollPosition =
      typeof scrollPosition === 'number' && Number.isFinite(scrollPosition) ? scrollPosition : 0;

    return { page, chartId, scrollPosition: normalizedScrollPosition };
  } catch (error) {
    console.error('加载浏览状态失败:', error);
    return null;
  }
};

/**
 * 清除所有数据（用于登出或重置）
 */
export const clearAllData = (): void => {
  try {
    Object.values(STORAGE_KEYS).forEach(key => {
      localStorage.removeItem(key);
    });
  } catch (error) {
    console.error('清除数据失败:', error);
  }
};
