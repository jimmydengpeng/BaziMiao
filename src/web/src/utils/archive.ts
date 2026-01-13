import type { Chart } from '../types';
import type { BirthFormValues } from '../types/forms';
import { lunarMonthLabels } from '../types/forms';
import { chinaRegions, getDefaultRegion, type SelectedRegion } from '../data/china-regions';
import type { ArchiveEntry, ArchivePillar } from './storage';

const elementForStem = (stem: string) => {
  const map: Record<string, string> = {
    甲: '木', 乙: '木', 丙: '火', 丁: '火',
    戊: '土', 己: '土', 庚: '金', 辛: '金',
    壬: '水', 癸: '水'
  };
  return map[stem] ?? '';
};

const elementForBranch = (branch: string) => {
  const map: Record<string, string> = {
    子: '水', 丑: '土', 寅: '木', 卯: '木',
    辰: '土', 巳: '火', 午: '火', 未: '土',
    申: '金', 酉: '金', 戌: '土', 亥: '水'
  };
  return map[branch] ?? '';
};

export const buildPillarsFromChart = (chartData: Chart): ArchivePillar[] => {
  const yearStem = chartData?.year_pillar?.heaven_stem?.name ?? '';
  const yearBranch = chartData?.year_pillar?.earth_branch?.name ?? '';
  const monthStem = chartData?.month_pillar?.heaven_stem?.name ?? '';
  const monthBranch = chartData?.month_pillar?.earth_branch?.name ?? '';
  const dayStem = chartData?.day_pillar?.heaven_stem?.name ?? '';
  const dayBranch = chartData?.day_pillar?.earth_branch?.name ?? '';
  const hourStem = chartData?.hour_pillar?.heaven_stem?.name ?? '';
  const hourBranch = chartData?.hour_pillar?.earth_branch?.name ?? '';

  return [
    {
      stem: yearStem,
      branch: yearBranch,
      stemElement: elementForStem(yearStem),
      branchElement: elementForBranch(yearBranch)
    },
    {
      stem: monthStem,
      branch: monthBranch,
      stemElement: elementForStem(monthStem),
      branchElement: elementForBranch(monthBranch)
    },
    {
      stem: dayStem,
      branch: dayBranch,
      stemElement: elementForStem(dayStem),
      branchElement: elementForBranch(dayBranch)
    },
    {
      stem: hourStem,
      branch: hourBranch,
      stemElement: elementForStem(hourStem),
      branchElement: elementForBranch(hourBranch)
    }
  ];
};

export const buildBirthLabel = (formValues: BirthFormValues): string => {
  const minuteLabel = formValues.minute.toString().padStart(2, '0');
  const hourLabel = formValues.hour.toString().padStart(2, '0');

  if (formValues.calendar === 'lunar') {
    return `农历${formValues.year}年${formValues.isLeapMonth ? '闰' : ''}${
      lunarMonthLabels[formValues.month - 1]
    }${formValues.day}日 ${hourLabel}:${minuteLabel}`;
  }

  return `阳历${formValues.year}年${formValues.month}月${formValues.day}日 ${hourLabel}:${minuteLabel}`;
};

const normalizeText = (text: string) => text.replace(/\s+/g, '');

export const resolveBirthPlace = (birthPlace?: string | null): SelectedRegion => {
  if (!birthPlace || birthPlace === '未知地区') return getDefaultRegion();
  const target = normalizeText(birthPlace);

  for (const province of chinaRegions) {
    for (const city of province.cities) {
      const fullName = `${province.name}${city.name}`;
      if (normalizeText(fullName) === target) {
        return {
          province: province.name,
          city: city.name,
          lng: city.lng,
          lat: city.lat,
          fullName
        };
      }
    }
  }

  return {
    ...getDefaultRegion(),
    fullName: birthPlace
  };
};

export const buildBirthFormValuesFromArchive = (entry: ArchiveEntry): BirthFormValues => {
  const chart = entry.chart;
  const parsedDate = chart?.solar_datetime ? new Date(chart.solar_datetime) : new Date();
  const safeDate = Number.isNaN(parsedDate.getTime()) ? new Date() : parsedDate;
  const gender = chart.gender === 'female' ? 'female' : 'male';

  return {
    name: entry.name || '',
    gender,
    calendar: 'solar',
    year: safeDate.getFullYear(),
    month: safeDate.getMonth() + 1,
    day: safeDate.getDate(),
    hour: safeDate.getHours(),
    minute: safeDate.getMinutes(),
    isLeapMonth: chart.lunar_date?.is_leap_month ?? false,
    birthPlace: resolveBirthPlace(chart.birth_place)
  };
};

export const buildChartRequestBody = (payload: BirthFormValues): Record<string, unknown> => {
  const requestBody: Record<string, unknown> = {
    name: payload.name,
    gender: payload.gender,
    year: payload.year,
    month: payload.month,
    day: payload.day,
    hour: payload.hour,
    minute: payload.minute,
    calendar: payload.calendar,
    is_leap_month: payload.isLeapMonth,
    tz_offset_hours: 0,
    birth_place: payload.birthPlace.fullName
  };

  if (payload.birthPlace.province) {
    requestBody.longitude = payload.birthPlace.lng;
    requestBody.latitude = payload.birthPlace.lat;
  }

  return requestBody;
};
