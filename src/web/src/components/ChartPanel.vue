<template>
  <div class="chart-panel-wrapper">
    <div v-if="!chart" class="muted panel">生成后会显示命盘信息。</div>
    <div v-else class="chart-cards">
      <!-- 基本信息卡片 -->
      <div class="panel info-card">
        <!-- 标题栏：姓名 + 农历生日 + 排盘设置 -->
        <div class="info-header">
          <div class="info-header-left">
            <span class="info-name">{{ chart.name || "命主" }}</span>
            <span class="info-lunar-birth">{{ lunarBirthText }}</span>
          </div>
          <button class="info-header-action" type="button">
            排盘设置
            <span class="chevron-icon">›</span>
          </button>
        </div>

        <!-- 第一模块：时间地点信息 -->
        <div class="info-section">
          <div class="info-entry">
            <span class="entry-label">阳历</span>
            <span class="entry-value">{{ solarText }}</span>
          </div>
          <div class="info-entry">
            <span class="entry-label">真太阳时</span>
            <span class="entry-value">{{ trueSolarText }}</span>
          </div>
          <div class="info-entry full-width">
            <span class="entry-label">出生地区</span>
            <span class="entry-value">
              <template v-if="!chart.birth_place || chart.birth_place === '未知地区'">
                未知区域<span class="muted">（不使用真太阳时）</span>
              </template>
              <template v-else>{{ chart.birth_place }}</template>
            </span>
          </div>
          <div class="info-entry full-width">
            <span class="entry-label">出生节气</span>
            <span class="entry-value">{{ jieqiText }}</span>
          </div>
        </div>

        <!-- 第二模块：个人属性信息 -->
        <div class="info-section">
          <div class="info-entry">
            <span class="entry-label">性别</span>
            <span class="entry-value gender-value">
              <span>{{ genderText }}</span>
              <img
                v-if="chart.gender === 'male'"
                :src="maleIconUrl"
                alt="男"
                class="gender-icon"
              />
              <img
                v-else-if="chart.gender === 'female'"
                :src="femaleIconUrl"
                alt="女"
                class="gender-icon"
              />
              <span class="gender-type">{{ genderType }}</span>
            </span>
          </div>
          <div class="info-entry">
            <span class="entry-label">属相</span>
            <span class="entry-value">{{ chart.zodiac_animal || "未知" }}</span>
          </div>
          <div class="info-entry">
            <span class="entry-label">星座</span>
            <span class="entry-value">{{ chart.zodiac_sign || "未知" }}</span>
          </div>
          <div class="info-entry">
            <span class="entry-label">星宿</span>
            <span class="entry-value">{{ chart.star_mansion || "未知" }}</span>
          </div>
          <div class="info-entry">
            <span class="entry-label">命主五行</span>
            <span class="entry-value">
              <span :class="elementClass(chart.day_master.element)">
                {{ chart.day_master_display || dayMasterDisplay }}
              </span>
            </span>
          </div>
          <div class="info-entry">
            <span class="entry-label">天运五行</span>
            <span class="entry-value">{{ chart.fortune_element || "未知" }}</span>
          </div>
        </div>

        <!-- 第三模块：命理要素 -->
        <div class="info-section">
          <div class="info-entry">
            <span class="entry-label">胎元</span>
            <span class="entry-value">
              {{ taiYuanText }}
            </span>
          </div>
          <div class="info-entry">
            <span class="entry-label">胎息</span>
            <span class="entry-value">
              {{ taiXiText }}
            </span>
          </div>
          <div class="info-entry">
            <span class="entry-label">身宫</span>
            <span class="entry-value">
              {{ shenGongText }}
            </span>
          </div>
          <div class="info-entry">
            <span class="entry-label">命宫</span>
            <span class="entry-value">
              {{ mingGongText }}
            </span>
          </div>
          <div class="info-entry">
            <span class="entry-label">人元司令分野</span>
            <span class="entry-value">{{ chart.ren_yuan_si_ling || "未知" }}</span>
          </div>
          <div class="info-entry">
            <span class="entry-label">空亡</span>
            <span class="entry-value">{{ chart.kong_wang || "未知" }}</span>
          </div>
        </div>
      </div>

      <!-- 八字命盘卡片 -->
      <div class="panel bazi-card">
        <div class="card-header">
          <div class="card-title">八字命盘</div>
          <span class="badge">四柱八字</span>
        </div>
        <div class="bazi-table">
          <div class="bazi-row header">
            <div class="bazi-cell label"></div>
            <div class="bazi-cell">年柱</div>
            <div class="bazi-cell">月柱</div>
            <div class="bazi-cell">日柱</div>
            <div class="bazi-cell">时柱</div>
          </div>
          <div class="bazi-row">
            <div class="bazi-cell label">主星</div>
            <div class="bazi-cell star">{{ chart.year_pillar.heaven_stem.ten_god }}</div>
            <div class="bazi-cell star">{{ chart.month_pillar.heaven_stem.ten_god }}</div>
            <div class="bazi-cell star">{{ chart.day_pillar.heaven_stem.ten_god }}</div>
            <div class="bazi-cell star">{{ chart.hour_pillar.heaven_stem.ten_god }}</div>
          </div>
          <div class="bazi-row">
            <div class="bazi-cell label">天干</div>
            <div class="bazi-cell stem">
              <span :class="['pillar-char', elementClass(chart.year_pillar.heaven_stem.element)]">
                {{ chart.year_pillar.heaven_stem.name }}
              </span>
              <span class="pillar-icon">{{ elementIcon(chart.year_pillar.heaven_stem.element) }}</span>
            </div>
            <div class="bazi-cell stem">
              <span :class="['pillar-char', elementClass(chart.month_pillar.heaven_stem.element)]">
                {{ chart.month_pillar.heaven_stem.name }}
              </span>
              <span class="pillar-icon">{{ elementIcon(chart.month_pillar.heaven_stem.element) }}</span>
            </div>
            <div class="bazi-cell stem">
              <span :class="['pillar-char', elementClass(chart.day_pillar.heaven_stem.element)]">
                {{ chart.day_pillar.heaven_stem.name }}
              </span>
              <span class="pillar-icon">{{ elementIcon(chart.day_pillar.heaven_stem.element) }}</span>
            </div>
            <div class="bazi-cell stem">
              <span :class="['pillar-char', elementClass(chart.hour_pillar.heaven_stem.element)]">
                {{ chart.hour_pillar.heaven_stem.name }}
              </span>
              <span class="pillar-icon">{{ elementIcon(chart.hour_pillar.heaven_stem.element) }}</span>
            </div>
          </div>
          <div class="bazi-row">
            <div class="bazi-cell label">地支</div>
            <div class="bazi-cell branch">
              <span :class="['pillar-char', elementClass(chart.year_pillar.earth_branch.element)]">
                {{ chart.year_pillar.earth_branch.name }}
              </span>
              <span class="pillar-icon">{{ elementIcon(chart.year_pillar.earth_branch.element) }}</span>
            </div>
            <div class="bazi-cell branch">
              <span :class="['pillar-char', elementClass(chart.month_pillar.earth_branch.element)]">
                {{ chart.month_pillar.earth_branch.name }}
              </span>
              <span class="pillar-icon">{{ elementIcon(chart.month_pillar.earth_branch.element) }}</span>
            </div>
            <div class="bazi-cell branch">
              <span :class="['pillar-char', elementClass(chart.day_pillar.earth_branch.element)]">
                {{ chart.day_pillar.earth_branch.name }}
              </span>
              <span class="pillar-icon">{{ elementIcon(chart.day_pillar.earth_branch.element) }}</span>
            </div>
            <div class="bazi-cell branch">
              <span :class="['pillar-char', elementClass(chart.hour_pillar.earth_branch.element)]">
                {{ chart.hour_pillar.earth_branch.name }}
              </span>
              <span class="pillar-icon">{{ elementIcon(chart.hour_pillar.earth_branch.element) }}</span>
            </div>
          </div>
          <div class="bazi-row">
            <div class="bazi-cell label">藏干</div>
            <div class="bazi-cell hidden">
              <div class="hidden-stems">
                <span
                  v-for="stem in chart.year_pillar.earth_branch.hidden_stems"
                  :key="stem.name"
                  :class="elementClass(stem.element)"
                >
                  {{ stem.name }}
                </span>
              </div>
            </div>
            <div class="bazi-cell hidden">
              <div class="hidden-stems">
                <span
                  v-for="stem in chart.month_pillar.earth_branch.hidden_stems"
                  :key="stem.name"
                  :class="elementClass(stem.element)"
                >
                  {{ stem.name }}
                </span>
              </div>
            </div>
            <div class="bazi-cell hidden">
              <div class="hidden-stems">
                <span
                  v-for="stem in chart.day_pillar.earth_branch.hidden_stems"
                  :key="stem.name"
                  :class="elementClass(stem.element)"
                >
                  {{ stem.name }}
                </span>
              </div>
            </div>
            <div class="bazi-cell hidden">
              <div class="hidden-stems">
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
          <div class="bazi-row">
            <div class="bazi-cell label">副星</div>
            <div class="bazi-cell sub-star">
              <div class="sub-star-list">
                <span v-for="stem in chart.year_pillar.earth_branch.hidden_stems" :key="stem.name">
                  {{ stem.ten_god }}
                </span>
              </div>
            </div>
            <div class="bazi-cell sub-star">
              <div class="sub-star-list">
                <span v-for="stem in chart.month_pillar.earth_branch.hidden_stems" :key="stem.name">
                  {{ stem.ten_god }}
                </span>
              </div>
            </div>
            <div class="bazi-cell sub-star">
              <div class="sub-star-list">
                <span v-for="stem in chart.day_pillar.earth_branch.hidden_stems" :key="stem.name">
                  {{ stem.ten_god }}
                </span>
              </div>
            </div>
            <div class="bazi-cell sub-star">
              <div class="sub-star-list">
                <span v-for="stem in chart.hour_pillar.earth_branch.hidden_stems" :key="stem.name">
                  {{ stem.ten_god }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- 五行统计摘要 -->
        <div class="elements-summary">
          <div v-for="item in elementCounts" :key="item.label" class="element-badge">
            <span :class="['element-dot', elementClass(item.label)]"></span>
            <span :class="elementClass(item.label)">{{ item.label }}</span>
            <span class="element-count">{{ item.value }}</span>
          </div>
        </div>
      </div>

      <!-- 五行能量卡片 -->
      <div class="panel energy-card">
        <div class="card-header">
          <div class="card-title">五行能量</div>
          <span class="badge">命理分析</span>
        </div>
        <div class="energy-content">
          <!-- 雷达图 -->
          <div class="energy-radar">
            <div class="radar-title">
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

          <!-- 五行占比 -->
          <div class="energy-breakdown">
            <div class="breakdown-title">
              <strong>五行占比</strong>
              <span class="muted">基于天干与藏干统计</span>
            </div>
            <div class="energy-bars">
              <div v-for="item in energyItems" :key="item.element" class="energy-bar-item">
                <div class="bar-header">
                  <div class="bar-left">
                    <span :class="['bar-dot', elementClass(item.element)]"></span>
                    <span class="bar-name">{{ item.element }}</span>
                    <span class="bar-relation">{{ item.relation }}</span>
                  </div>
                  <div class="bar-right">
                    <span class="bar-percent">{{ formatPercent(item.ratio) }}</span>
                    <span class="bar-count">{{ item.count }}个</span>
                  </div>
                </div>
                <div class="bar-track">
                  <div
                    class="bar-fill"
                    :class="elementClass(item.element)"
                    :style="{ width: `${(item.ratio / maxEnergyRatio) * 100}%` }"
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 大运卡片 -->
      <div class="panel destiny-card">
        <div class="card-header">
          <div class="card-title">大运</div>
          <span v-if="destinyMeta" class="badge">{{ destinyMeta }}</span>
        </div>
        <div v-if="!destinyPillars.length" class="muted">暂无大运数据。</div>
        <div v-else class="destiny-grid">
          <div v-for="pillar in destinyPillarsWithAge" :key="pillar.year" class="destiny-item">
            <div class="destiny-year">{{ pillar.year }}年 · {{ pillar.age }}岁</div>
            <div class="destiny-pillar">
              <div class="destiny-row">
                <span :class="['destiny-char', elementClass(pillar.heaven_stem.element)]">
                  {{ pillar.heaven_stem.name }}
                </span>
                <span class="destiny-god">{{ pillar.heaven_stem.ten_god }}</span>
              </div>
              <div class="destiny-row">
                <span :class="['destiny-char', elementClass(pillar.earth_branch.element)]">
                  {{ pillar.earth_branch.name }}
                </span>
                <span class="destiny-god">{{ pillar.earth_branch_ten_god }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 干支关系卡片 -->
      <div class="panel ganzi-card">
        <div class="card-header">
          <div class="card-title">干支关系</div>
          <span class="badge">本命</span>
        </div>
        
        <div class="ganzi-diagram">
          <!-- 柱标签行 -->
          <div class="ganzi-labels">
            <div class="ganzi-label">年柱</div>
            <div class="ganzi-label">月柱</div>
            <div class="ganzi-label">日柱</div>
            <div class="ganzi-label">时柱</div>
          </div>

          <!-- SVG 连线层 + 天干地支显示 -->
          <div class="ganzi-svg-container">
            <svg class="ganzi-svg" :viewBox="`0 0 ${svgWidth} ${svgHeight}`" :style="{ minHeight: svgHeight + 'px' }" preserveAspectRatio="xMidYMid meet">
              <defs>
                <!-- 箭头标记定义 -->
                <marker id="arrow-up" markerWidth="8" markerHeight="8" refX="4" refY="8" orient="auto">
                  <path d="M0,8 L4,0 L8,8" fill="none" stroke="currentColor" stroke-width="1.5"/>
                </marker>
              </defs>
              
              <!-- 天干关系连线（在天干上方绘制） -->
              <g class="stem-connections">
                <template v-for="(conn, idx) in stemConnectionLines" :key="`stem-${idx}`">
                  <path 
                    :d="conn.path" 
                    :class="['ganzi-line', `line-${conn.cssType}`]"
                    fill="none"
                  />
                  <!-- 使用 foreignObject 放置 pill -->
                  <foreignObject 
                    :x="conn.labelX - 35" 
                    :y="conn.labelY - 9" 
                    width="70" 
                    height="18"
                  >
                    <div class="relation-pill-container">
                      <span :class="['relation-pill', 'pill-sm', `pill-${conn.cssType}`]">
                        {{ conn.label }}
                      </span>
                    </div>
                  </foreignObject>
                </template>
              </g>

              <!-- 天干字符 -->
              <g class="stem-chars">
                <text 
                  v-for="(stem, idx) in ganziStems" 
                  :key="`stem-char-${idx}`"
                  :x="getPillarX(idx)" 
                  :y="stemY"
                  text-anchor="middle"
                  dominant-baseline="middle"
                  :class="['ganzi-char', 'stem-char', elementClass(stem.element)]"
                >{{ stem.name }}</text>
              </g>

              <!-- 天干地支相生箭头（垂直） -->
              <g class="stem-branch-arrows">
                <template v-for="(arrow, idx) in stemBranchArrows" :key="`arrow-${idx}`">
                  <line 
                    :x1="arrow.x" 
                    :y1="arrow.y1" 
                    :x2="arrow.x" 
                    :y2="arrow.y2"
                    class="ganzi-arrow"
                    marker-end="url(#arrow-up)"
                  />
                </template>
              </g>

              <!-- 地支字符 -->
              <g class="branch-chars">
                <text 
                  v-for="(branch, idx) in ganziBranches" 
                  :key="`branch-char-${idx}`"
                  :x="getPillarX(idx)" 
                  :y="branchY"
                  text-anchor="middle"
                  dominant-baseline="middle"
                  :class="['ganzi-char', 'branch-char', elementClass(branch.element)]"
                >{{ branch.name }}</text>
              </g>

              <!-- 地支关系连线（在地支下方绘制） -->
              <g class="branch-connections">
                <template v-for="(conn, idx) in branchConnectionLines" :key="`branch-${idx}`">
                  <path 
                    :d="conn.path" 
                    :class="['ganzi-line', `line-${conn.cssType}`]"
                    fill="none"
                  />
                  <!-- 使用 foreignObject 放置 pill，垂直居中在水平线上 -->
                  <foreignObject 
                    :x="conn.labelX - 35" 
                    :y="conn.labelY - 9" 
                    width="70" 
                    height="18"
                  >
                    <div class="relation-pill-container">
                      <span :class="['relation-pill', 'pill-sm', `pill-${conn.cssType}`]">
                        {{ conn.label }}
                      </span>
                    </div>
                  </foreignObject>
                </template>
              </g>
            </svg>
          </div>
        </div>

        <!-- 关系说明区域 -->
        <div class="ganzi-summary">
          <div v-if="stemRelationsData.length" class="ganzi-summary-item">
            <span class="summary-label">天干本命</span>
            <div class="summary-pills">
              <span 
                v-for="(rel, idx) in stemRelationsData" 
                :key="`stem-rel-${idx}`"
                :class="['relation-pill', `pill-${rel.cssType}`]"
              >{{ rel.description }}</span>
            </div>
          </div>
          <div v-if="branchRelationsData.length" class="ganzi-summary-item">
            <span class="summary-label">地支本命</span>
            <div class="summary-pills">
              <span 
                v-for="(rel, idx) in branchRelationsData" 
                :key="`branch-rel-${idx}`"
                :class="['relation-pill', `pill-${rel.cssType}`]"
              >{{ rel.description }}</span>
            </div>
          </div>
          <div v-if="!stemRelationsData.length && !branchRelationsData.length" class="muted">
            本命四柱无明显刑冲合会关系
          </div>
        </div>

        <div class="ganzi-note muted">
          因八字合化论流派繁多且断法各异，故以上仅展示正化结果；实际应用中需考虑是否反化或合而不化的可能，故以上结果仅供基本参考，具体结论以个体判断为准
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import type { Chart } from "../types";
// 导入性别图标
import maleIconUrl from "../assets/male-icon.png";
import femaleIconUrl from "../assets/female-icon.png";

const props = defineProps<{
  chart: Chart | null;
}>();

// 农历数字转中文
const lunarMonthNames = [
  "正月", "二月", "三月", "四月", "五月", "六月",
  "七月", "八月", "九月", "十月", "冬月", "腊月"
];
const lunarDayNames = [
  "初一", "初二", "初三", "初四", "初五", "初六", "初七", "初八", "初九", "初十",
  "十一", "十二", "十三", "十四", "十五", "十六", "十七", "十八", "十九", "二十",
  "廿一", "廿二", "廿三", "廿四", "廿五", "廿六", "廿七", "廿八", "廿九", "三十"
];
const chineseNumerals = ["〇", "一", "二", "三", "四", "五", "六", "七", "八", "九"];

// 将年份数字转换为中文
const yearToChinese = (year: number): string => {
  return year.toString().split("").map(d => chineseNumerals[parseInt(d)]).join("");
};

// 时辰对应表
const hourToBranch = (hour: number): string => {
  const branches = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"];
  const index = Math.floor((hour + 1) / 2) % 12;
  return branches[index] + "时";
};

// 性别文字
const genderText = computed(() => {
  if (!props.chart) return "";
  if (props.chart.gender === "male") return "男";
  if (props.chart.gender === "female") return "女";
  return "其他";
});

// 性别类型（乾造/坤造）
const genderType = computed(() => {
  if (!props.chart) return "";
  return props.chart.gender === "male" ? "乾造" : "坤造";
});

// 农历出生日期（标题栏使用，中文格式）
const lunarBirthText = computed(() => {
  if (!props.chart) return "";
  const lunar = props.chart.lunar_date;
  const yearStr = yearToChinese(lunar.year);
  const monthStr = lunar.is_leap_month ? "闰" + lunarMonthNames[lunar.month - 1] : lunarMonthNames[lunar.month - 1];
  const dayStr = lunarDayNames[lunar.day - 1] || `${lunar.day}日`;
  // 从阳历时间提取小时来推算时辰
  const solarHour = props.chart.solar_datetime ? new Date(props.chart.solar_datetime).getHours() : 0;
  const hourStr = hourToBranch(solarHour);
  return `${yearStr}年${monthStr}${dayStr} ${hourStr}`;
});

// 阳历文本
const solarText = computed(() => {
  if (!props.chart) return "";
  const raw = props.chart.solar_datetime.replace("T", " ");
  return raw.length >= 16 ? raw.slice(0, 16) : raw;
});

// 真太阳时文本
const trueSolarText = computed(() => {
  if (!props.chart || !props.chart.true_solar_datetime) return solarText.value;
  const raw = props.chart.true_solar_datetime.replace("T", " ");
  return raw.length >= 16 ? raw.slice(0, 16) : raw;
});

// 节气信息文本
const jieqiText = computed(() => {
  if (!props.chart || !props.chart.birth_jieqi) return "未知";
  const jieqi = props.chart.birth_jieqi;
  return `${jieqi.prev_distance}，${jieqi.next_distance}`;
});

// 命主五行展示（备用）
const dayMasterDisplay = computed(() => {
  if (!props.chart) return "";
  const dm = props.chart.day_master;
  return `${dm.name}${dm.yinyang}${dm.element}`;
});

// 纳音信息格式化
const formatNaYin = (info: { gan_zhi: string; na_yin: string } | null | undefined): string => {
  if (!info) return "未知";
  return `${info.gan_zhi}（${info.na_yin}）`;
};

const taiYuanText = computed(() => formatNaYin(props.chart?.tai_yuan));
const taiXiText = computed(() => formatNaYin(props.chart?.tai_xi));
const shenGongText = computed(() => formatNaYin(props.chart?.shen_gong));
const mingGongText = computed(() => formatNaYin(props.chart?.ming_gong));

// 五行元素顺序和配置
const elementOrder = ["木", "火", "土", "金", "水"];
const radarSize = 400;
const radarCenter = radarSize / 2;
const radarRadius = 140;
const radarLevels = [1, 2, 3, 4, 5];
const radarAngleStep = (Math.PI * 2) / elementOrder.length;
const radarStartAngle = -Math.PI / 2;

// 五行关系映射表
const elementRelationMap: Record<string, Record<string, string>> = {
  木: { 木: "比劫", 火: "食伤", 土: "财才", 金: "官杀", 水: "印枭" },
  火: { 木: "印枭", 火: "比劫", 土: "食伤", 金: "财才", 水: "官杀" },
  土: { 木: "官杀", 火: "印枭", 土: "比劫", 金: "食伤", 水: "财才" },
  金: { 木: "财才", 火: "官杀", 土: "印枭", 金: "比劫", 水: "食伤" },
  水: { 木: "食伤", 火: "财才", 土: "官杀", 金: "印枭", 水: "比劫" }
};

// 五行计数
const elementCounts = computed(() => {
  if (!props.chart) return [];
  return elementOrder.map((label) => ({
    label,
    value: props.chart?.five_elements_count[label] ?? 0
  }));
});

// 五行能量条目
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

// 最大能量比率（用于归一化）
const maxEnergyRatio = computed(() => {
  const maxValue = Math.max(...energyItems.value.map((item) => item.ratio), 0);
  return maxValue > 0 ? maxValue : 1;
});

// 雷达图轴线坐标
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

// 雷达图数据点坐标
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

// 雷达图形状点（用于绘制多边形）
const radarShapePoints = computed(() =>
  radarPoints.value.map((point) => `${point.x.toFixed(1)},${point.y.toFixed(1)}`).join(" ")
);

// 生成雷达图网格点
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

// 格式化百分比
const formatPercent = (value: number) => `${(Number.isFinite(value) ? value : 0).toFixed(1)}%`;

// 大运数据
const destinyPillars = computed(() => {
  if (!props.chart) return [];
  return props.chart.destiny_cycle?.destiny_pillars ?? [];
});

// 大运数据（带年龄和地支十神）
const destinyPillarsWithAge = computed(() => {
  if (!props.chart || !destinyPillars.value.length) return [];
  
  // 从阳历时间提取出生年份
  const birthYear = new Date(props.chart.solar_datetime).getFullYear();
  
  return destinyPillars.value.map((pillar) => ({
    ...pillar,
    // 计算命主在该大运年份的年龄（虚岁）
    age: pillar.year - birthYear + 1,
    // 地支的十神取藏干的第一个（本气）的十神
    earth_branch_ten_god: pillar.earth_branch.hidden_stems[0]?.ten_god ?? "未知"
  }));
});

// 大运元信息（起运时间等）
const destinyMeta = computed(() => {
  if (!props.chart) return "";
  const startAge = props.chart.destiny_cycle?.start_age;
  if (!startAge) return "";
  const direction = props.chart.destiny_cycle.is_forward ? "顺行" : "逆行";
  return `起运 ${startAge.year}岁${startAge.month}月${startAge.day}天 · ${direction}`;
});

// 五行对应的 CSS 类名
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

// 五行对应的图标（emoji）
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

// ========== 干支关系卡片相关 ==========

// SVG 尺寸配置
const svgWidth = 400;
const pillarSpacing = 90; // 柱之间的间距
const startX = 50; // 第一个柱的 X 坐标

// 动态计算天干关系区域需要的高度
const stemAreaHeight = computed(() => {
  if (!props.chart?.ganzi_relations) return 40;
  const stemCount = props.chart.ganzi_relations.stem_relations.length;
  return stemCount > 0 ? stemCount * 25 + 40 : 40; // 每行25px + 基础空间
});

// Y 坐标配置（动态）
const stemLineBaseY = computed(() => stemAreaHeight.value); // 天干连线基准 Y
const stemY = computed(() => stemAreaHeight.value + 40); // 天干 Y 坐标
const branchY = computed(() => stemAreaHeight.value + 110); // 地支 Y 坐标  
const branchLineBaseY = computed(() => stemAreaHeight.value + 160); // 地支连线基准 Y（下方）

// 动态计算 SVG 高度：根据关系数量调整
const svgHeight = computed(() => {
  if (!props.chart?.ganzi_relations) return 200;
  // 每个关系占一行，统计总行数
  const branchCount = props.chart.ganzi_relations.branch_relations.length;
  
  // 天干区域高度（已在 stemAreaHeight 中计算）
  // 字符区域：天干+地支 = 110px
  // 地支关系区域高度：每行24px + 基础空间
  const charAreaHeight = 110;
  const branchAreaHeight = branchCount > 0 ? branchCount * 24 + 40 : 40;
  
  return stemAreaHeight.value + charAreaHeight + branchAreaHeight;
});

// 获取柱的 X 坐标（0=时,1=日,2=月,3=年）
const getPillarX = (index: number) => startX + index * pillarSpacing;

// 四柱天干信息（按年月日时顺序，从左到右）
const ganziStems = computed(() => {
  if (!props.chart) return [];
  return [
    props.chart.year_pillar.heaven_stem,
    props.chart.month_pillar.heaven_stem,
    props.chart.day_pillar.heaven_stem,
    props.chart.hour_pillar.heaven_stem,
  ];
});

// 四柱地支信息（按年月日时顺序，从左到右）
const ganziBranches = computed(() => {
  if (!props.chart) return [];
  return [
    props.chart.year_pillar.earth_branch,
    props.chart.month_pillar.earth_branch,
    props.chart.day_pillar.earth_branch,
    props.chart.hour_pillar.earth_branch,
  ];
});

// 位置索引映射：后端返回的位置索引（0=年,1=月,2=日,3=时）与前端显示顺序一致
const mapPosition = (backendPos: number): number => {
  // 后端和前端顺序一致: 0=年, 1=月, 2=日, 3=时
  return backendPos;
};

// 连线数据结构
interface ConnectionLine {
  path: string;
  type: string;
  cssType: string;
  label: string;
  labelX: number;
  labelY: number;
}

// 圆角半径
const cornerRadius = 6;

// 生成连接两个柱位置的折线路径（用于天干，在上方），带圆角
const createStemArc = (pos1: number, pos2: number, level: number): string => {
  const x1 = getPillarX(pos1);
  const x2 = getPillarX(pos2);
  const y1 = stemY.value - 25; // 起点 Y（天干下方）
  const yTop = stemLineBaseY.value - level * 25; // 折线顶部 Y，每行间距25px
  const r = Math.min(cornerRadius, Math.abs(x2 - x1) / 4, Math.abs(y1 - yTop) / 2);
  
  // 路径：从 x1 向上 -> 水平到 x2 -> 向下到 y1
  // 使用圆弧来实现圆角
  return `M ${x1} ${y1} 
          L ${x1} ${yTop + r} 
          Q ${x1} ${yTop} ${x1 + r} ${yTop}
          L ${x2 - r} ${yTop}
          Q ${x2} ${yTop} ${x2} ${yTop + r}
          L ${x2} ${y1}`;
};

// 生成连接两个柱位置的折线路径（用于地支，在下方），带圆角
const createBranchArc = (pos1: number, pos2: number, level: number): string => {
  const x1 = getPillarX(pos1);
  const x2 = getPillarX(pos2);
  const y1 = branchY.value + 25; // 起点 Y（地支下方）
  const yBottom = branchLineBaseY.value + level * 24; // 折线底部 Y，每层间距24px
  const r = Math.min(cornerRadius, Math.abs(x2 - x1) / 4, Math.abs(yBottom - y1) / 2);
  
  // 路径：从 x1 向下 -> 水平到 x2 -> 向上到 y1
  return `M ${x1} ${y1} 
          L ${x1} ${yBottom - r} 
          Q ${x1} ${yBottom} ${x1 + r} ${yBottom}
          L ${x2 - r} ${yBottom}
          Q ${x2} ${yBottom} ${x2} ${yBottom - r}
          L ${x2} ${y1}`;
};

// 天干连线数据（每个关系独立占一行）
const stemConnectionLines = computed<ConnectionLine[]>(() => {
  if (!props.chart?.ganzi_relations) return [];
  const relations = props.chart.ganzi_relations.stem_relations;
  const lines: ConnectionLine[] = [];
  
  // 每个关系独立分配一个 level（行号）
  for (let idx = 0; idx < relations.length; idx++) {
    const rel = relations[idx];
    if (rel.positions.length < 2) continue;
    
    const level = idx; // 每个关系独立占一行
    const pos1 = mapPosition(rel.positions[0]);
    const pos2 = mapPosition(rel.positions[1]);
    const [p1, p2] = pos1 < pos2 ? [pos1, pos2] : [pos2, pos1];
    
    const path = createStemArc(p1, p2, level);
    const midX = (getPillarX(p1) + getPillarX(p2)) / 2;
    const labelY = stemLineBaseY.value - level * 25; // pill在折线顶部
    
    // 显示完整关系描述（简化版）
    let label = '';
    if (rel.type === '合化' && rel.element) {
      label = `合化${rel.element}`;
    } else if (rel.type === '相克') {
      label = '克';
    }
    
    const cssType = getRelationCssType(rel.type);
    
    lines.push({
      path,
      type: rel.type,
      cssType,
      label,
      labelX: midX,
      labelY,
    });
  }
  
  return lines;
});

// 地支连线数据（每个关系独立占一行）
const branchConnectionLines = computed<ConnectionLine[]>(() => {
  if (!props.chart?.ganzi_relations) return [];
  const relations = props.chart.ganzi_relations.branch_relations;
  const lines: ConnectionLine[] = [];
  
  // 每个关系独立分配一个 level（行号）
  for (let idx = 0; idx < relations.length; idx++) {
    const rel = relations[idx];
    if (rel.positions.length < 2) continue;
    
    const level = idx; // 每个关系独立占一行
    
    // 对于多位置关系（如三合），连接所有相邻对
    const positions = rel.positions.map(mapPosition).sort((a, b) => a - b);
    
    // 计算中间位置用于放置标签
    const midIndex = Math.floor(positions.length / 2);
    const labelPosIdx = positions.length === 2 ? 0 : midIndex;
    
    for (let i = 0; i < positions.length - 1; i++) {
      const p1 = positions[i];
      const p2 = positions[i + 1];
      
      const path = createBranchArc(p1, p2, level);
      const midX = (getPillarX(p1) + getPillarX(p2)) / 2;
      const labelY = branchLineBaseY.value + level * 24; // pill在折线中央（水平线上）
      
      // 标签只在中间段显示
      let label = '';
      if (i === labelPosIdx) {
        if (rel.type === '六合' && rel.element) {
          label = `合化${rel.element}`;
        } else if (rel.type === '三合') {
          label = rel.element ? `三合${rel.element}` : '三合';
        } else if (rel.type === '半合') {
          label = rel.element ? `半合${rel.element}` : '半合';
        } else if (rel.type === '六冲') {
          label = '冲';
        } else if (rel.type === '相刑') {
          label = '刑';
        } else if (rel.type === '自刑') {
          label = '自刑';
        } else if (rel.type === '相害') {
          label = '害';
        } else if (rel.type === '三会') {
          label = rel.element ? `会${rel.element}` : '会';
        }
      }
      
      const cssType = getRelationCssType(rel.type);
      
      lines.push({
        path,
        type: rel.type,
        cssType,
        label,
        labelX: midX,
        labelY,
      });
    }
  }
  
  return lines;
});

// 天干地支相生箭头
const stemBranchArrows = computed(() => {
  if (!props.chart?.ganzi_relations) return [];
  const relations = props.chart.ganzi_relations.stem_branch_relations;
  const arrows: { x: number; y1: number; y2: number }[] = [];
  
  for (const rel of relations) {
    if (rel.positions.length !== 1) continue;
    const pos = mapPosition(rel.positions[0]);
    arrows.push({
      x: getPillarX(pos),
      y1: branchY.value - 30, // 从地支上方开始
      y2: stemY.value + 30, // 到天干下方结束
    });
  }
  
  return arrows;
});

// 根据关系类型获取 CSS 类型
const getRelationCssType = (type: string): string => {
  if (['合化', '六合', '三合', '半合', '三会'].includes(type)) {
    return 'combine';
  } else if (type === '六冲') {
    return 'clash';
  } else if (['相刑', '自刑'].includes(type)) {
    return 'punish';
  } else if (type === '相害') {
    return 'harm';
  } else if (type === '相克') {
    return 'clash';
  }
  return 'neutral';
};

// 天干关系数据（带 CSS 类型）
const stemRelationsData = computed(() => {
  if (!props.chart?.ganzi_relations) return [];
  return props.chart.ganzi_relations.stem_relations.map(rel => ({
    description: rel.description,
    cssType: getRelationCssType(rel.type),
  }));
});

// 地支关系数据（带 CSS 类型）
const branchRelationsData = computed(() => {
  if (!props.chart?.ganzi_relations) return [];
  return props.chart.ganzi_relations.branch_relations.map(rel => ({
    description: rel.description,
    cssType: getRelationCssType(rel.type),
  }));
});
</script>
