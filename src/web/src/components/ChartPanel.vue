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
const elementCounts = computed(() => {
  if (!props.chart) return [];
  return elementOrder.map((label) => ({
    label,
    value: props.chart?.five_elements_count[label] ?? 0
  }));
});

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
