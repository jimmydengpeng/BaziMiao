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
  destiny_cycle: DestinyCycleInfo;
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
  | { type: "delta"; text: string }
  | { type: "done"; report: Report; analysis?: Analysis }
  | { type: "error"; message: string };

export interface ChartResponse {
  chart: Chart;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface ChatResponse {
  reply: { overall_tone?: string; sections?: { title: string; content: string }[]; raw_prompt?: unknown };
  prompt: unknown;
}

export type ChatStreamEvent =
  | { type: "delta"; text: string }
  | { type: "done"; reply: string }
  | { type: "error"; message: string };
