import { reactive, ref } from 'vue';
import type { Analysis, BaziReportInputRefsV1, BaziReportV1, ReportSseEvent } from '../types';

export type SectionStatus = 'idle' | 'generating' | 'done' | 'error';

export interface SectionState {
  sectionId: string;
  title: string;
  status: SectionStatus;
  contentMd: string;
  structured?: unknown;
  error?: string;
}

export interface ReportStreamState {
  reportId: string;
  schemaVersion: string;
  sectionsPlan: Array<{ sectionId: string; title: string }>;
  sections: Record<string, SectionState>;
  thinking: string;
  prompt: unknown | null;
  done: boolean;
  error: string;
  finalReport: BaziReportV1 | null;
  analysis: Analysis | null;
}

const isBaziReportV1 = (value: unknown): value is BaziReportV1 => {
  if (!value || typeof value !== 'object') return false;
  return 'meta' in value && 'input_refs' in value && 'sections' in value;
};

const normalizeStringArray = (value: unknown) => {
  if (!Array.isArray(value)) return [];
  return value.map((item) => String(item ?? '')).filter((item) => item);
};

const buildInputRefsFromPrompt = (prompt: unknown): BaziReportInputRefsV1 | null => {
  const input = (prompt as any)?.user?.input_refs_backend;
  if (!input || typeof input !== 'object') return null;

  return {
    solar_date: String((input as any).solar_date ?? ''),
    lunar_date: String((input as any).lunar_date ?? ''),
    birth_time: String((input as any).birth_time ?? ''),
    bazi_str: String((input as any).bazi_str ?? ''),
    gender: String((input as any).gender ?? ''),
    cur_dayun: String((input as any).cur_dayun ?? ''),
    cur_liunian: String((input as any).cur_liunian ?? ''),
    day_master: String((input as any).day_master ?? ''),
    five_elements_count: String((input as any).five_elements_count ?? ''),
    pattern_tags: normalizeStringArray((input as any).pattern_tags),
    yong_shen: normalizeStringArray((input as any).yong_shen),
    ji_shen: normalizeStringArray((input as any).ji_shen),
  };
};

const buildFinalReportFromSections = (): BaziReportV1 => {
  const inputRefs =
    buildInputRefsFromPrompt(state.prompt) ??
    ({
      solar_date: '',
      lunar_date: '',
      birth_time: '',
      bazi_str: '',
      gender: '',
      cur_dayun: '',
      cur_liunian: '',
      day_master: '',
      five_elements_count: '',
      pattern_tags: [],
      yong_shen: [],
      ji_shen: [],
    } satisfies BaziReportInputRefsV1);

  return {
    meta: {
      version: state.schemaVersion || 'bazi_report_v1',
      generated_at: new Date().toISOString(),
      language: 'zh-CN',
      tone: '温和中肯',
      disclaimer: '本报告仅基于已提供事实进行解读，不构成确定性承诺或医疗/投资建议。',
    },
    input_refs: inputRefs,
    sections: state.sectionsPlan.map((sec) => {
      const sectionState = state.sections[sec.sectionId];
      return {
        id: sec.sectionId,
        title: sec.title,
        content_md: sectionState?.contentMd ?? '',
        structured: sectionState?.structured,
      };
    }),
  };
};

const deepMerge = (target: any, patch: any) => {
  if (!patch || typeof patch !== 'object') return target;
  if (!target || typeof target !== 'object') return patch;

  for (const [key, value] of Object.entries(patch)) {
    const prev = (target as any)[key];
    if (Array.isArray(value)) {
      (target as any)[key] = value;
    } else if (value && typeof value === 'object') {
      (target as any)[key] = deepMerge(prev ?? {}, value);
    } else {
      (target as any)[key] = value;
    }
  }
  return target;
};

const extractSseData = (rawEventBlock: string) => {
  // SSE 事件块通常是多行，真正的数据行以 'data:' 开头（可能有多行 data: 需要拼接）
  const lines = rawEventBlock.split(/\r?\n/);
  const dataLines = lines
    .filter((line) => line.startsWith('data:'))
    .map((line) => line.slice(5).trimStart());
  return dataLines.join('\n').trim();
};

// 单例（切换路由/Tab 时不丢状态、不打断请求）
const state = reactive<ReportStreamState>({
  reportId: '',
  schemaVersion: '',
  sectionsPlan: [],
  sections: {},
  thinking: '',
  prompt: null,
  done: false,
  error: '',
  finalReport: null,
  analysis: null,
});

const isStreaming = ref(false);
let abortController: AbortController | null = null;

const reset = () => {
  state.reportId = '';
  state.schemaVersion = '';
  state.sectionsPlan = [];
  state.sections = {};
  state.thinking = '';
  state.prompt = null;
  state.done = false;
  state.error = '';
  state.finalReport = null;
  state.analysis = null;
};

const abort = () => {
  abortController?.abort();
  abortController = null;
  isStreaming.value = false;
};

const ensureSection = (sectionId: string, title?: string) => {
  const existing = state.sections[sectionId];
  if (existing) {
    if (title && !existing.title) existing.title = title;
    return existing;
  }
  const next: SectionState = {
    sectionId,
    title: title || sectionId,
    status: 'idle',
    contentMd: '',
  };
  state.sections[sectionId] = next;
  return next;
};

const handleEvent = (event: ReportSseEvent) => {
  if (event.type === 'report_start') {
    state.reportId = event.report_id;
    state.schemaVersion = event.schema_version;
    state.sectionsPlan = event.sections.map((item) => ({
      sectionId: item.section_id,
      title: item.title,
    }));

    for (const sec of state.sectionsPlan) {
      ensureSection(sec.sectionId, sec.title);
    }
    return;
  }

  if (event.type === 'meta') {
    state.analysis = event.analysis;
    state.prompt = (event as any).prompt ?? null;
    return;
  }

  if (event.type === 'thinking_delta') {
    state.thinking += event.text ?? '';
    return;
  }

  if (event.type === 'section_start') {
    const sec = ensureSection(event.section_id, event.title);
    sec.status = 'generating';
    return;
  }

  if (event.type === 'section_delta') {
    const sec = ensureSection(event.section_id, event.title);
    sec.status = 'generating';
    sec.contentMd += event.delta ?? '';
    return;
  }

  if (event.type === 'section_patch') {
    const sec = ensureSection(event.section_id);
    const patch = event.patch ?? {};
    if (typeof patch === 'object' && patch) {
      if ('structured' in patch) {
        sec.structured = deepMerge(sec.structured ?? {}, (patch as any).structured);
      } else {
        sec.structured = deepMerge(sec.structured ?? {}, patch);
      }
    }
    return;
  }

  if (event.type === 'section_done') {
    const sec = ensureSection(event.section_id);
    if (sec.status !== 'error') sec.status = 'done';
    return;
  }

  if (event.type === 'report_done') {
    state.done = true;
    if (event.thinking) state.thinking = event.thinking;
    if (event.report && isBaziReportV1(event.report)) {
      state.finalReport = event.report;
      return;
    }
    // 新协议：report_done 不再附带完整报告 JSON，由前端用已收到的分段内容拼装。
    state.finalReport = buildFinalReportFromSections();
    return;
  }

  if (event.type === 'error') {
    state.error = event.message || '生成报告失败';
    state.done = false;
  }
};

const start = async (payload: unknown) => {
  if (isStreaming.value) return;
  reset();
  isStreaming.value = true;
  abortController = new AbortController();

  try {
    const response = await fetch('/api/bazi/report/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      signal: abortController.signal,
    });

    if (!response.ok) throw new Error(await response.text());
    if (!response.body) throw new Error('浏览器不支持流式响应');

    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let buffer = '';
    let didReceiveDone = false;

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const blocks = buffer.split(/\r?\n\r?\n/);
      buffer = blocks.pop() ?? '';

      for (const rawBlock of blocks) {
        const dataText = extractSseData(rawBlock);
        if (!dataText) continue;

        try {
          const event = JSON.parse(dataText) as ReportSseEvent;
          handleEvent(event);
          if (event.type === 'report_done') {
            didReceiveDone = true;
            break;
          }
          if (event.type === 'error') {
            didReceiveDone = false;
            break;
          }
        } catch (err) {
          state.error = err instanceof Error ? err.message : String(err);
          break;
        }
      }

      if (didReceiveDone || state.error) break;
    }

    if (didReceiveDone) {
      try {
        await reader.cancel();
      } catch {
        // ignore
      }
    }

    if (!didReceiveDone && !state.error) state.error = '流式响应未返回 report_done';
  } finally {
    isStreaming.value = false;
    abortController = null;
  }
};

export const useBaziReportStream = () => ({
  state,
  isStreaming,
  start,
  abort,
  reset,
});
