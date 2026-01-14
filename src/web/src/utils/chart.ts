import type { Chart, KongWangInfo } from '../types';

const buildKongWangInfo = (value: string): KongWangInfo => ({
  year: value,
  month: value,
  day: value,
  hour: value,
});

export const normalizeChartForRequest = (chart: Chart): Chart => {
  if (!chart.kong_wang || typeof chart.kong_wang !== 'string') return chart;
  return {
    ...chart,
    kong_wang: buildKongWangInfo(chart.kong_wang),
  };
};
