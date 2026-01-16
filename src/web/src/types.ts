export type Gender = "male" | "female" | "other";

export interface LunarDate {
  year: number;
  month: number;
  day: number;
  is_leap_month?: boolean;
}

export interface HeavenStemInfo {
  name: string;
  element: string;
  yinyang: string;
  ten_god: string;
}

export interface EarthBranchInfo {
  name: string;
  element: string;
  yinyang: string;
  hidden_stems: HeavenStemInfo[];
  star_fortune?: string;
}

export interface PillarInfo {
  heaven_stem: HeavenStemInfo;
  earth_branch: EarthBranchInfo;
  na_yin?: string;
  na_yin_trait?: string;
}

export interface StartAge {
  year: number;
  month: number;
  day: number;
}

export interface DestinyPillarInfo {
  heaven_stem: HeavenStemInfo;
  earth_branch: EarthBranchInfo;
  year: number;
  is_current?: boolean;
}

export interface DestinyCycleInfo {
  destiny_pillars: DestinyPillarInfo[];
  start_age: StartAge;
  qiyun_date_solar: LunarDate;
  qiyun_date_lunar: LunarDate;
  is_forward: boolean;
}

// 纳音信息
export interface NaYinInfo {
  gan_zhi: string; // 干支，如"己亥"
  na_yin: string; // 纳音，如"平地木"
}

// 节气信息
export interface JieQiInfo {
  prev_jieqi: string; // 前一个节气
  prev_distance: string; // 距前一节气的时间
  next_jieqi: string; // 后一个节气
  next_distance: string; // 距后一节气的时间
}

export interface KongWangInfo {
  year: string; // 年柱空亡
  month: string; // 月柱空亡
  day: string; // 日柱空亡
  hour: string; // 时柱空亡
}

// 干支关系（单个）
export interface GanZhiRelation {
  type: string; // 关系类型：合化、相克、六合、三合、三会、六冲、相刑、相害、相生
  pillars: string[]; // 涉及的柱标识：year, month, day, hour, destiny, year_fortune
  ganzi_items: string[]; // 涉及的干支名称
  description: string; // 描述，如"癸戊合化火"
  element?: string | null; // 合化后的五行（如有）
  category: string; // 关系类别: stem(天干), branch(地支), stem_branch(天干地支)
  involves_fortune: boolean; // 是否涉及大运或流年
}

// 干支关系汇总
export interface GanZhiRelations {
  stem_relations: GanZhiRelation[]; // 天干关系（包含所有）
  branch_relations: GanZhiRelation[]; // 地支关系（包含所有）
  stem_branch_relations: GanZhiRelation[]; // 天干地支相生关系
}

export interface Chart {
  name?: string | null;
  gender: Gender;
  solar_datetime: string;
  lunar_date: LunarDate;
  year_pillar: PillarInfo;
  month_pillar: PillarInfo;
  day_pillar: PillarInfo;
  hour_pillar: PillarInfo;
  day_master: HeavenStemInfo;
  five_elements_count: Record<string, number>;
  five_elements_ratio: Record<string, number>;
  destiny_cycle: DestinyCycleInfo;
  zodiac_animal: string; // 生肖属相
  // 新增字段
  true_solar_datetime?: string | null; // 真太阳时
  birth_place?: string; // 出生地点
  birth_jieqi?: JieQiInfo | null; // 出生节气信息
  zodiac_sign?: string; // 星座
  star_mansion?: string; // 星宿
  day_master_display?: string; // 命主五行展示，如"癸阴水"
  fortune_element?: string; // 天运五行（年柱纳音）
  tai_yuan?: NaYinInfo | null; // 胎元
  tai_xi?: NaYinInfo | null; // 胎息
  shen_gong?: NaYinInfo | null; // 身宫
  ming_gong?: NaYinInfo | null; // 命宫
  ren_yuan_si_ling?: string; // 人元司令分野
  kong_wang?: KongWangInfo | string | null; // 空亡
  current_year_pillar?: PillarInfo | null; // 当前流年柱（以立春为界）
  ganzi_relations?: GanZhiRelations | null; // 干支关系
  destiny_relations_map?: Record<string, GanZhiRelations>; // 大运关系缓存
}

export interface Analysis {
  pattern?: string | null;
  strength_score?: number | null;
  yi_yong_shen: string[];
  ji_shen: string[];
  pattern_tags: string[];
  key_conclusions: string[];
  risk_points: string[];
  luck_highlights: {
    start_age: number;
    year: number;
    pillar: string;
    element_tendency?: string;
    summary?: string;
  }[];
}

export interface LegacyReport {
  overall_tone: string;
  sections: { title: string; content: string }[];
  raw_prompt?: unknown;
  energy_chart?: string;
  facts_ref?: string[];
}

export interface BaziReportMetaV1 {
  version: string;
  generated_at: string;
  language: string;
  tone: string;
  disclaimer: string;
}

export interface BaziReportInputRefsV1 {
  solar_date: string;
  lunar_date: string;
  birth_time: string;
  bazi_str: string;
  gender: string;
  cur_dayun: string;
  cur_liunian: string;
  day_master: string;
  five_elements_count: string;
  pattern_tags: string[];
  yong_shen: string[];
  ji_shen: string[];
}

export interface BaziReportSectionV1 {
  id: string;
  title: string;
  summary?: string;
  content_md: string;
  structured?: unknown;
}

export interface BaziReportV1 {
  meta: BaziReportMetaV1;
  input_refs: BaziReportInputRefsV1;
  sections: BaziReportSectionV1[];
}

export type Report = LegacyReport | BaziReportV1;

export interface ReportResponse {
  chart: Chart;
  analysis: Analysis;
  knowledge: Array<{ source: string; topic: string; summary: string }>;
  prompt: unknown;
  report: Report;
}

export type ReportStreamEvent =
  | {
      type: "meta";
      chart: Chart;
      analysis: Analysis;
      knowledge: Array<{ source: string; topic: string; summary: string }>;
      prompt: unknown;
    }
  | { type: "thinking"; text: string }
  | { type: "delta"; text: string }
  | { type: "done"; report: Report; analysis?: Analysis; thinking?: string }
  | { type: "error"; message: string };

export type ReportSseEvent =
  | {
      type: "report_start";
      report_id: string;
      schema_version: string;
      sections: Array<{ section_id: string; title: string }>;
    }
  | {
      type: "meta";
      report_id: string;
      chart: Chart;
      analysis: Analysis;
      knowledge: Array<{ source: string; topic: string; summary: string }>;
      prompt: unknown;
    }
  | { type: "thinking_delta"; report_id: string; text: string }
  | { type: "section_start"; report_id: string; section_id: string; title?: string }
  | {
      type: "section_delta";
      report_id: string;
      section_id: string;
      seq: number;
      delta: string;
      title?: string;
    }
  | { type: "section_patch"; report_id: string; section_id: string; patch: Record<string, unknown> }
  | { type: "section_done"; report_id: string; section_id: string }
  | { type: "report_done"; report_id: string; report?: Report; thinking?: string; dev_info?: DevInfo }
  | { type: "error"; report_id?: string; message: string; recoverable?: boolean };

export interface ChartResponse {
  chart: Chart;
  destiny_relations_map?: Record<string, GanZhiRelations>;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  thinking?: string;
  thinkingCollapsed?: boolean;
}

export interface ChatResponse {
  reply: { overall_tone?: string; sections?: { title: string; content: string }[]; raw_prompt?: unknown };
  prompt: unknown;
}

export type ChatStreamEvent =
  | { type: "thinking"; text: string }
  | { type: "delta"; text: string }
  | { type: "done"; reply: string; thinking?: string }
  | { type: "error"; message: string };

// 四柱反查相关类型
export interface PillarSearchRequest {
  year_pillar: string;
  month_pillar: string;
  day_pillar: string;
  hour_pillar: string;
  start_year: number;
  end_year: number;
}

export interface MatchedDate {
  year: number;
  month: number;
  day: number;
  hour: number;
  minute: number;
  lunar_display: string;
}

export interface PillarSearchResponse {
  matched_dates: MatchedDate[];
  total_count: number;
}

// 五行能量智能分析结果
export interface SmartEnergyElement {
  score: number;
  description: string;
}

export interface DevInfo {
  elapsed_ms: number;
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
}

export interface SmartEnergyResult {
  elements: {
    木: SmartEnergyElement;
    火: SmartEnergyElement;
    土: SmartEnergyElement;
    金: SmartEnergyElement;
    水: SmartEnergyElement;
  };
  summary?: string;
  overall?: string;
  temperament?: string;
  health?: string;
  dev_info?: DevInfo;
}

export interface DestinyAnalysisResult {
  summary: string;
  tips: string;
}

export interface DestinyAnalysisItem extends DestinyAnalysisResult {
  year: number;
}

export interface DestinyAnalysisBatchResult {
  items: DestinyAnalysisItem[];
  dev_info?: DevInfo;
}
