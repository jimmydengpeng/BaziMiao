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
  REPORT_CACHE_V1: 'bazi_report_cache_v1',
  ARCHIVE_COUNTER: 'bazi_archive_counter',
  ACTIVE_ARCHIVE_ID: 'bazi_active_archive_id',
  BAZI_VIEW_STATE: 'bazi_view_state', // 命盘解析模块的浏览状态
} as const;

type ReportCacheItemV1 = {
  savedAt: number;
  report: Report;
};

type ReportCacheStoreV1 = {
  version: 1;
  order: string[];
  items: Record<string, ReportCacheItemV1>;
};

const MAX_REPORT_CACHE_ITEMS = 12;

const normalizeChartId = (chartId: string | number) => String(chartId);

const loadReportCacheStoreV1 = (): ReportCacheStoreV1 => {
  try {
    const raw = localStorage.getItem(STORAGE_KEYS.REPORT_CACHE_V1);
    if (!raw) return { version: 1, order: [], items: {} };

    const parsed = JSON.parse(raw) as unknown;
    if (!parsed || typeof parsed !== 'object') return { version: 1, order: [], items: {} };

    const record = parsed as Partial<ReportCacheStoreV1>;
    if (record.version !== 1) return { version: 1, order: [], items: {} };

    const order = Array.isArray(record.order) ? record.order.filter((id) => typeof id === 'string') : [];
    const items = record.items && typeof record.items === 'object' ? (record.items as ReportCacheStoreV1['items']) : {};

    return { version: 1, order, items };
  } catch (error) {
    console.error('加载报告缓存失败:', error);
    return { version: 1, order: [], items: {} };
  }
};

const saveReportCacheStoreV1 = (store: ReportCacheStoreV1): void => {
  try {
    localStorage.setItem(STORAGE_KEYS.REPORT_CACHE_V1, JSON.stringify(store));
  } catch (error) {
    console.error('保存报告缓存失败:', error);
  }
};

/**
 * 保存某个 chartId 对应的报告（用于多档案切换/刷新恢复）
 */
export const saveReportForChartId = (chartId: string | number, report: Report | null): void => {
  try {
    const key = normalizeChartId(chartId);
    const store = loadReportCacheStoreV1();

    if (!report) {
      delete store.items[key];
      store.order = store.order.filter((id) => id !== key);
      saveReportCacheStoreV1(store);
      return;
    }

    store.items[key] = { savedAt: Date.now(), report };
    store.order = [key, ...store.order.filter((id) => id !== key)];

    // 简单 LRU：只保留最近 N 份报告
    while (store.order.length > MAX_REPORT_CACHE_ITEMS) {
      const tail = store.order.pop();
      if (!tail) break;
      delete store.items[tail];
    }

    saveReportCacheStoreV1(store);
  } catch (error) {
    console.error('保存报告缓存失败:', error);
  }
};

/**
 * 加载某个 chartId 对应的报告
 */
export const loadReportForChartId = (chartId: string | number): Report | null => {
  try {
    const key = normalizeChartId(chartId);
    const store = loadReportCacheStoreV1();
    const hit = store.items[key];
    return hit?.report ?? null;
  } catch (error) {
    console.error('加载报告缓存失败:', error);
    return null;
  }
};

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
  gender?: string;
  birthLabel: string;
  pillars: ArchivePillar[];
  chart: Chart;
  reportState: ArchiveReportState;
};

export type ArchiveReportState = {
  status: 'idle' | 'generated';
  report: Report | null;
  debugPrompt?: unknown;
  updatedAt?: number;
};

const normalizeArchiveReportState = (
  value: unknown,
  fallbackReport: Report | null
): ArchiveReportState => {
  if (!value || typeof value !== 'object') {
    return {
      status: fallbackReport ? 'generated' : 'idle',
      report: fallbackReport ?? null,
      updatedAt: fallbackReport ? Date.now() : undefined,
    };
  }

  const record = value as Partial<ArchiveReportState>;
  const report = record.report ?? fallbackReport ?? null;

  return {
    status: report ? 'generated' : 'idle',
    report,
    debugPrompt: record.debugPrompt,
    updatedAt: record.updatedAt,
  };
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
    const parsed = data ? (JSON.parse(data) as unknown) : [];
    if (!Array.isArray(parsed)) return [];

    return parsed.map((entry) => {
      const record = entry as ArchiveEntry;
      const cachedReport = record?.id ? loadReportForChartId(record.id) : null;
      return {
        ...record,
        reportState: normalizeArchiveReportState(record.reportState, cachedReport),
      };
    });
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
export type BaziViewPage = 'basic' | 'report' | 'detail' | 'verification';

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
      // 兼容旧值 chart -> basic
      if (rawPage === 'chart') return 'basic';
      if (rawPage === 'basic') return 'basic';
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
