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
}

export interface PillarInfo {
  heaven_stem: HeavenStemInfo;
  earth_branch: EarthBranchInfo;
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

// 干支关系（单个）
export interface GanZhiRelation {
  type: string; // 关系类型：合化、相克、六合、三合、三会、六冲、相刑、相害、相生
  positions: number[]; // 涉及的柱位置索引 [0=年,1=月,2=日,3=时]
  description: string; // 描述，如"癸戊合化火"
  element?: string | null; // 合化后的五行（如有）
}

// 干支关系汇总
export interface GanZhiRelations {
  stem_relations: GanZhiRelation[]; // 天干关系
  branch_relations: GanZhiRelation[]; // 地支关系
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
  kong_wang?: string; // 空亡
  ganzi_relations?: GanZhiRelations | null; // 干支关系
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

export interface Report {
  overall_tone: string;
  sections: { title: string; content: string }[];
  raw_prompt?: unknown;
  energy_chart?: string;
  facts_ref?: string[];
}

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

export interface ChartResponse {
  chart: Chart;
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
