import type { SelectedRegion } from "../data/china-regions";

export type CalendarType = "solar" | "lunar" | "pillar";

export type BirthFormValues = {
  name: string;
  gender: "male" | "female";
  calendar: CalendarType;
  year: number;
  month: number;
  day: number;
  hour: number;
  minute: number;
  isLeapMonth: boolean;
  birthPlace: SelectedRegion;
};

export type PillarMatchedDate = {
  year: number;
  month: number;
  day: number;
  hour: number;
  minute: number;
  lunar_display: string;
};

export const lunarMonthLabels = [
  "正月",
  "二月",
  "三月",
  "四月",
  "五月",
  "六月",
  "七月",
  "八月",
  "九月",
  "十月",
  "冬月",
  "腊月"
];
