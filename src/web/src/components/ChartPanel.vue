<template>
  <div class="panel stack">
    <div class="status-line">
      <strong>八字命盘</strong>
      <span class="badge">真实排盘</span>
    </div>
    <div v-if="!chart" class="muted">生成后会显示命盘信息。</div>
    <div v-else class="stack">
      <div class="chart-meta">
        <div class="meta-row">
          <span class="meta-label">姓名</span>
          <span>{{ chart.name || "未填写" }}</span>
          <span class="meta-label">性别</span>
          <span>{{ genderLabel }}</span>
        </div>
        <div class="meta-row">
          <span class="meta-label">阴历</span>
          <span>{{ lunarText }}</span>
        </div>
        <div class="meta-row">
          <span class="meta-label">阳历</span>
          <span>{{ solarText }}</span>
        </div>
      </div>

      <div class="elements-row">
        <div v-for="item in elementCounts" :key="item.label" class="element-chip">
          <span :class="elementClass(item.label)">{{ item.label }}</span>
          <span class="muted">{{ item.value }}</span>
        </div>
      </div>

      <div class="chart-table">
        <div class="chart-row header">
          <div class="chart-cell label">时间</div>
          <div class="chart-cell">年柱</div>
          <div class="chart-cell">月柱</div>
          <div class="chart-cell">日柱</div>
          <div class="chart-cell">时柱</div>
        </div>
        <div class="chart-row">
          <div class="chart-cell label">主星</div>
          <div class="chart-cell">{{ chart.year_pillar.heaven_stem.ten_god }}</div>
          <div class="chart-cell">{{ chart.month_pillar.heaven_stem.ten_god }}</div>
          <div class="chart-cell">{{ chart.day_pillar.heaven_stem.ten_god }}</div>
          <div class="chart-cell">{{ chart.hour_pillar.heaven_stem.ten_god }}</div>
        </div>
        <div class="chart-row">
          <div class="chart-cell label">天干</div>
          <div class="chart-cell">
            <span :class="['pillar-main', elementClass(chart.year_pillar.heaven_stem.element)]">
              {{ chart.year_pillar.heaven_stem.name }}
            </span>
            <span class="pillar-icon">{{ elementIcon(chart.year_pillar.heaven_stem.element) }}</span>
          </div>
          <div class="chart-cell">
            <span :class="['pillar-main', elementClass(chart.month_pillar.heaven_stem.element)]">
              {{ chart.month_pillar.heaven_stem.name }}
            </span>
            <span class="pillar-icon">{{ elementIcon(chart.month_pillar.heaven_stem.element) }}</span>
          </div>
          <div class="chart-cell">
            <span :class="['pillar-main', elementClass(chart.day_pillar.heaven_stem.element)]">
              {{ chart.day_pillar.heaven_stem.name }}
            </span>
            <span class="pillar-icon">{{ elementIcon(chart.day_pillar.heaven_stem.element) }}</span>
          </div>
          <div class="chart-cell">
            <span :class="['pillar-main', elementClass(chart.hour_pillar.heaven_stem.element)]">
              {{ chart.hour_pillar.heaven_stem.name }}
            </span>
            <span class="pillar-icon">{{ elementIcon(chart.hour_pillar.heaven_stem.element) }}</span>
          </div>
        </div>
        <div class="chart-row">
          <div class="chart-cell label">地支</div>
          <div class="chart-cell">
            <span :class="['pillar-main', elementClass(chart.year_pillar.earth_branch.element)]">
              {{ chart.year_pillar.earth_branch.name }}
            </span>
            <span class="pillar-icon">{{ elementIcon(chart.year_pillar.earth_branch.element) }}</span>
          </div>
          <div class="chart-cell">
            <span :class="['pillar-main', elementClass(chart.month_pillar.earth_branch.element)]">
              {{ chart.month_pillar.earth_branch.name }}
            </span>
            <span class="pillar-icon">{{ elementIcon(chart.month_pillar.earth_branch.element) }}</span>
          </div>
          <div class="chart-cell">
            <span :class="['pillar-main', elementClass(chart.day_pillar.earth_branch.element)]">
              {{ chart.day_pillar.earth_branch.name }}
            </span>
            <span class="pillar-icon">{{ elementIcon(chart.day_pillar.earth_branch.element) }}</span>
          </div>
          <div class="chart-cell">
            <span :class="['pillar-main', elementClass(chart.hour_pillar.earth_branch.element)]">
              {{ chart.hour_pillar.earth_branch.name }}
            </span>
            <span class="pillar-icon">{{ elementIcon(chart.hour_pillar.earth_branch.element) }}</span>
          </div>
        </div>
        <div class="chart-row">
          <div class="chart-cell label">藏干</div>
          <div class="chart-cell">
            <div class="chart-stack">
              <span
                v-for="stem in chart.year_pillar.earth_branch.hidden_stems"
                :key="stem.name"
                :class="elementClass(stem.element)"
              >
                {{ stem.name }}
              </span>
            </div>
          </div>
          <div class="chart-cell">
            <div class="chart-stack">
              <span
                v-for="stem in chart.month_pillar.earth_branch.hidden_stems"
                :key="stem.name"
                :class="elementClass(stem.element)"
              >
                {{ stem.name }}
              </span>
            </div>
          </div>
          <div class="chart-cell">
            <div class="chart-stack">
              <span
                v-for="stem in chart.day_pillar.earth_branch.hidden_stems"
                :key="stem.name"
                :class="elementClass(stem.element)"
              >
                {{ stem.name }}
              </span>
            </div>
          </div>
          <div class="chart-cell">
            <div class="chart-stack">
              <span
                v-for="stem in chart.hour_pillar.earth_branch.hidden_stems"
                :key="stem.name"
                :class="elementClass(stem.element)"
              >
                {{ stem.name }}
              </span>
            </div>
          </div>
        </div>
        <div class="chart-row">
          <div class="chart-cell label">副星</div>
          <div class="chart-cell">
            <div class="chart-stack">
              <span v-for="stem in chart.year_pillar.earth_branch.hidden_stems" :key="stem.name">
                {{ stem.ten_god }}
              </span>
            </div>
          </div>
          <div class="chart-cell">
            <div class="chart-stack">
              <span v-for="stem in chart.month_pillar.earth_branch.hidden_stems" :key="stem.name">
                {{ stem.ten_god }}
              </span>
            </div>
          </div>
          <div class="chart-cell">
            <div class="chart-stack">
              <span v-for="stem in chart.day_pillar.earth_branch.hidden_stems" :key="stem.name">
                {{ stem.ten_god }}
              </span>
            </div>
          </div>
          <div class="chart-cell">
            <div class="chart-stack">
              <span v-for="stem in chart.hour_pillar.earth_branch.hidden_stems" :key="stem.name">
                {{ stem.ten_god }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div class="panel energy-card">
        <div class="energy-shell">
          <div class="energy-radar">
            <div class="status-line">
              <strong>五行雷达图</strong>
              <span class="muted">最高占比为满格</span>
            </div>
            <div class="radar-stage">
              <svg class="radar-svg" viewBox="0 0 400 400" role="img" aria-label="五行雷达图">
                <g class="radar-grid">
                  <polygon
                    v-for="level in radarLevels"
                    :key="`grid-${level}`"
                    :points="gridPoints(level)"
                  />
                  <line
                    v-for="(axis, idx) in radarAxes"
                    :key="`axis-${idx}`"
                    :x1="axis.cx"
                    :y1="axis.cy"
                    :x2="axis.x"
                    :y2="axis.y"
                  />
                </g>
                <polygon class="radar-shape" :points="radarShapePoints" />
                <g class="radar-dots">
                  <circle
                    v-for="(point, idx) in radarPoints"
                    :key="`dot-${idx}`"
                    :cx="point.x"
                    :cy="point.y"
                    r="7"
                    :class="['radar-dot', elementClass(point.element)]"
                  />
                </g>
                <g class="radar-labels">
                  <text
                    v-for="(axis, idx) in radarAxes"
                    :key="`label-${idx}`"
                    :x="axis.labelX"
                    :y="axis.labelY"
                    text-anchor="middle"
                    :class="['radar-label', elementClass(axis.element)]"
                  >
                    {{ axis.element }}
                  </text>
                </g>
              </svg>
            </div>
          </div>
          <div class="energy-aside">
            <div class="status-line">
              <strong>五行占比</strong>
              <span class="muted">基于天干与藏干统计</span>
            </div>
            <div class="energy-list">
              <div v-for="item in energyItems" :key="item.element" class="energy-item">
                <div class="energy-left">
                  <span :class="['energy-dot', elementClass(item.element)]"></span>
                  <div>
                    <div class="energy-name">{{ item.element }}</div>
                    <div class="energy-meta">代表{{ item.relation }}</div>
                  </div>
                </div>
                <div class="energy-right">
                  <div class="energy-value">{{ formatPercent(item.ratio) }}</div>
                  <div class="energy-count">{{ item.count }}个</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="destiny-panel">
        <div class="status-line">
          <strong>大运</strong>
          <span v-if="destinyMeta" class="muted">{{ destinyMeta }}</span>
        </div>
        <div v-if="!destinyPillars.length" class="muted">暂无大运数据。</div>
        <div v-else class="destiny-grid">
          <div v-for="pillar in destinyPillars" :key="pillar.year" class="destiny-card">
            <div class="destiny-year">{{ pillar.year }}年</div>
            <div class="destiny-pillar">
              <span :class="['destiny-char', elementClass(pillar.heaven_stem.element)]">
                {{ pillar.heaven_stem.name }}
              </span>
              <span :class="['destiny-char', elementClass(pillar.earth_branch.element)]">
                {{ pillar.earth_branch.name }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import type { Chart } from "../types";

const props = defineProps<{
  chart: Chart | null;
}>();

const genderLabel = computed(() => {
  if (!props.chart) return "";
  if (props.chart.gender === "male") return "男";
  if (props.chart.gender === "female") return "女";
  return "其他";
});

const lunarText = computed(() => {
  if (!props.chart) return "";
  const lunar = props.chart.lunar_date;
  const leap = lunar.is_leap_month ? "闰" : "";
  return `${lunar.year}年${leap}${lunar.month}月${lunar.day}日`;
});

const solarText = computed(() => {
  if (!props.chart) return "";
  const raw = props.chart.solar_datetime.replace("T", " ");
  return raw.length >= 16 ? raw.slice(0, 19) : raw;
});

const elementOrder = ["木", "火", "土", "金", "水"];
const radarSize = 400;
const radarCenter = radarSize / 2;
const radarRadius = 140;
const radarLevels = [1, 2, 3, 4, 5];
const radarAngleStep = (Math.PI * 2) / elementOrder.length;
const radarStartAngle = -Math.PI / 2;
const elementRelationMap: Record<string, Record<string, string>> = {
  木: { 木: "比劫", 火: "食伤", 土: "财才", 金: "官杀", 水: "印枭" },
  火: { 木: "印枭", 火: "比劫", 土: "食伤", 金: "财才", 水: "官杀" },
  土: { 木: "官杀", 火: "印枭", 土: "比劫", 金: "食伤", 水: "财才" },
  金: { 木: "财才", 火: "官杀", 土: "印枭", 金: "比劫", 水: "食伤" },
  水: { 木: "食伤", 火: "财才", 土: "官杀", 金: "印枭", 水: "比劫" }
};
const elementCounts = computed(() => {
  if (!props.chart) return [];
  return elementOrder.map((label) => ({
    label,
    value: props.chart?.five_elements_count[label] ?? 0
  }));
});

const energyItems = computed(() => {
  if (!props.chart) {
    return elementOrder.map((element) => ({
      element,
      count: 0,
      ratio: 0,
      relation: "未知"
    }));
  }
  const counts = props.chart.five_elements_count ?? {};
  const ratios = props.chart.five_elements_ratio ?? {};
  const dayElement = props.chart.day_master?.element ?? "";
  return elementOrder.map((element) => ({
    element,
    count: counts[element] ?? 0,
    ratio: ratios[element] ?? 0,
    relation: elementRelationMap[dayElement]?.[element] ?? "未知"
  }));
});

const maxEnergyRatio = computed(() => {
  const maxValue = Math.max(...energyItems.value.map((item) => item.ratio), 0);
  return maxValue > 0 ? maxValue : 1;
});

const radarAxes = computed(() =>
  elementOrder.map((element, idx) => {
    const angle = radarStartAngle + radarAngleStep * idx;
    const axisX = radarCenter + radarRadius * Math.cos(angle);
    const axisY = radarCenter + radarRadius * Math.sin(angle);
    const labelOffset = 28;
    return {
      element,
      cx: radarCenter,
      cy: radarCenter,
      x: axisX,
      y: axisY,
      labelX: radarCenter + (radarRadius + labelOffset) * Math.cos(angle),
      labelY: radarCenter + (radarRadius + labelOffset) * Math.sin(angle)
    };
  })
);

const radarPoints = computed(() =>
  energyItems.value.map((item, idx) => {
    const angle = radarStartAngle + radarAngleStep * idx;
    const ratio = item.ratio / maxEnergyRatio.value;
    const radius = radarRadius * ratio;
    return {
      element: item.element,
      x: radarCenter + radius * Math.cos(angle),
      y: radarCenter + radius * Math.sin(angle)
    };
  })
);

const radarShapePoints = computed(() =>
  radarPoints.value.map((point) => `${point.x.toFixed(1)},${point.y.toFixed(1)}`).join(" ")
);

const gridPoints = (level: number) => {
  const scale = level / radarLevels.length;
  return elementOrder
    .map((_, idx) => {
      const angle = radarStartAngle + radarAngleStep * idx;
      const radius = radarRadius * scale;
      const x = radarCenter + radius * Math.cos(angle);
      const y = radarCenter + radius * Math.sin(angle);
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(" ");
};

const formatPercent = (value: number) => `${(Number.isFinite(value) ? value : 0).toFixed(1)}%`;

const destinyPillars = computed(() => {
  if (!props.chart) return [];
  return props.chart.destiny_cycle?.destiny_pillars ?? [];
});

const destinyMeta = computed(() => {
  if (!props.chart) return "";
  const startAge = props.chart.destiny_cycle?.start_age;
  if (!startAge) return "";
  const direction = props.chart.destiny_cycle.is_forward ? "顺行" : "逆行";
  return `起运 ${startAge.year}岁${startAge.month}月${startAge.day}天 · ${direction}`;
});

const elementClass = (element: string) => {
  const map: Record<string, string> = {
    木: "element-wood",
    火: "element-fire",
    土: "element-earth",
    金: "element-metal",
    水: "element-water"
  };
  return map[element] ?? "element-neutral";
};

const elementIcon = (element: string) => {
  const map: Record<string, string> = {
    木: "🍃",
    火: "🔥",
    土: "⛰️",
    金: "✨",
    水: "💧"
  };
  return map[element] ?? "";
};
</script>
