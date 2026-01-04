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
          <div class="mode-toggle-switch" @click="toggleGanziMode">
            <div class="mode-toggle-options">
              <span :class="['mode-option', { 'active': !isCurrentMode }]">本命</span>
              <span :class="['mode-option', { 'active': isCurrentMode }]">当前</span>
            </div>
            <div :class="['mode-toggle-pill', { 'right': isCurrentMode }]"></div>
          </div>
        </div>
        
        <div class="ganzi-diagram">
          <!-- SVG 连线层 + 天干地支显示 + 柱标签（统一在 SVG 中绘制） -->
          <div class="ganzi-svg-container">
            <svg class="ganzi-svg" :viewBox="`0 0 ${svgWidth} ${svgHeight}`" :style="{ minHeight: svgHeight + 'px' }" preserveAspectRatio="xMidYMid meet">
              <defs>
                <!-- 天干连线渐变定义 -->
                <linearGradient
                  v-for="conn in stemConnectionLines"
                  :key="conn.gradientId"
                  :id="conn.gradientId"
                  x1="0%"
                  y1="0%"
                  x2="100%"
                  y2="0%"
                >
                  <stop offset="0%" :stop-color="elementColorMap[conn.element1 || '木']" stop-opacity="0.4" />
                  <stop offset="100%" :stop-color="elementColorMap[conn.element2 || '木']" stop-opacity="0.4" />
                </linearGradient>
                
                <!-- 地支连线渐变定义 -->
                <linearGradient
                  v-for="conn in branchConnectionLines"
                  :key="conn.gradientId"
                  :id="conn.gradientId"
                  x1="0%"
                  y1="0%"
                  x2="100%"
                  y2="0%"
                >
                  <stop offset="0%" :stop-color="elementColorMap[conn.element1 || '木']" stop-opacity="0.4" />
                  <stop offset="100%" :stop-color="elementColorMap[conn.element2 || '木']" stop-opacity="0.4" />
                </linearGradient>
                
                <!-- 天干地支连线渐变定义（垂直渐变，从地支到天干） -->
                <!-- 同柱天干-地支相生连线：按地支五行色直接描边（无需渐变） -->
              </defs>
              
              <!-- 柱标签（年柱、月柱、日柱、时柱） -->
              <g class="pillar-labels">
                <text 
                  v-for="(label, idx) in pillarLabels" 
                  :key="`label-${idx}`"
                  :x="getPillarX(idx)" 
                  :y="labelY"
                  text-anchor="middle"
                  dominant-baseline="middle"
                  class="pillar-label-text"
                >{{ label }}</text>
              </g>

              <!-- 天干关系连线（在天干上方绘制） -->
              <g class="stem-connections">
                <template v-for="(conn, idx) in stemConnectionLines" :key="`stem-${idx}`">
                  <path 
                    :d="conn.path" 
                    :stroke="`url(#${conn.gradientId})`"
                    stroke-width="2"
                    stroke-linecap="round"
                    fill="none"
                  />
                  <!-- 使用 foreignObject 放置 pill -->
                  <foreignObject 
                    :x="conn.labelX - 35" 
                    :y="conn.labelY - 11" 
                    width="70" 
                    height="22"
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

              <!-- 天干地支关系连线（垂直，相生为实线，相克为虚线） -->
              <g class="stem-branch-lines">
                <template v-for="(line, idx) in stemBranchLines" :key="`sb-line-${idx}`">
                  <line 
                    :x1="line.x" 
                    :y1="line.y1" 
                    :x2="line.x" 
                    :y2="line.y2"
                    :stroke="elementColorMap[line.element1 || '木']"
                    stroke-opacity="0.55"
                    stroke-width="2"
                    stroke-linecap="round"
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
                  <!-- 主连线（圆角矩形） -->
                  <path
                    :d="conn.path"
                    :stroke="`url(#${conn.gradientId})`"
                    stroke-width="2"
                    stroke-linecap="round"
                    fill="none"
                  />
                  <!-- 三合/三会的中间竖线（如果存在） -->
                  <path
                    v-if="conn.middleLinePath"
                    :d="conn.middleLinePath"
                    :stroke="elementColorMap[conn.middleLineElement || '木']"
                    stroke-opacity="0.4"
                    stroke-width="2"
                    stroke-linecap="round"
                    fill="none"
                  />
                  <!-- 使用 foreignObject 放置 pill -->
                  <foreignObject
                    v-if="conn.label"
                    :x="conn.labelX - 35"
                    :y="conn.labelY - 11"
                    width="70"
                    height="22"
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
          <!-- 本命模式 -->
          <template v-if="!isCurrentMode">
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
          </template>
          
          <!-- 当前模式：显示本命和运势 -->
          <template v-else>
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
            <div v-if="stemFortuneRelationsData.length" class="ganzi-summary-item">
              <span class="summary-label">天干运势</span>
              <div class="summary-pills">
                <span 
                  v-for="(rel, idx) in stemFortuneRelationsData" 
                  :key="`stem-fortune-${idx}`"
                  :class="['relation-pill', `pill-${rel.cssType}`]"
                >{{ rel.description }}</span>
              </div>
            </div>
            <div v-if="branchFortuneRelationsData.length" class="ganzi-summary-item">
              <span class="summary-label">地支运势</span>
              <div class="summary-pills">
                <span 
                  v-for="(rel, idx) in branchFortuneRelationsData" 
                  :key="`branch-fortune-${idx}`"
                  :class="['relation-pill', `pill-${rel.cssType}`]"
                >{{ rel.description }}</span>
              </div>
            </div>
            <div v-if="!stemRelationsData.length && !branchRelationsData.length && !stemFortuneRelationsData.length && !branchFortuneRelationsData.length" class="muted">
              当前无明显刑冲合会关系
            </div>
          </template>
        </div>

        <div class="ganzi-note muted">
          因八字合化论流派繁多且断法各异，故以上仅展示正化结果；实际应用中需考虑是否反化或合而不化的可能，故以上结果仅供基本参考，具体结论以个体判断为准
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import type { Chart, GanZhiRelation, PillarInfo, HeavenStemInfo, EarthBranchInfo } from "../types";
// 导入性别图标
import maleIconUrl from "../assets/gender-male.png";
import femaleIconUrl from "../assets/gender-female.png";

const props = defineProps<{
  chart: Chart | null;
}>();

// 干支关系模式切换：false=本命(4柱), true=当前(6柱，包含大运和流年)
const isCurrentMode = ref(false);

const toggleGanziMode = () => {
  isCurrentMode.value = !isCurrentMode.value;
};

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

// 计算年份对应的天干地支（用于流年）
const getYearGanZhi = (year: number): PillarInfo => {
  const stems = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸'];
  const branches = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥'];
  const stemElements = ['木', '木', '火', '火', '土', '土', '金', '金', '水', '水'];
  const branchElements = ['水', '土', '木', '木', '土', '火', '火', '土', '金', '金', '土', '水'];
  
  // 天干：从甲子年（1984年，年份%10=4对应甲）开始计算
  const stemIndex = (year - 4) % 10;
  // 地支：从甲子年（1984年，年份%12=0对应子）开始计算
  const branchIndex = (year - 4) % 12;
  
  return {
    heaven_stem: {
      name: stems[stemIndex],
      element: stemElements[stemIndex],
      yinyang: stemIndex % 2 === 0 ? '阳' : '阴',
      ten_god: '', // 流年不需要十神
    },
    earth_branch: {
      name: branches[branchIndex],
      element: branchElements[branchIndex],
      yinyang: branchIndex % 2 === 0 ? '阳' : '阴',
      hidden_stems: [], // 简化处理，不计算藏干
    },
  };
};

// 获取当前大运（根据当前日期）
const getCurrentDestinyPillar = computed((): PillarInfo | null => {
  if (!props.chart?.destiny_cycle) return null;
  
  const birthDate = new globalThis.Date(props.chart.solar_datetime);
  const now = new globalThis.Date();
  
  // 计算起运时间
  const startAge = props.chart.destiny_cycle.start_age;
  const qiyunDate = new globalThis.Date(birthDate);
  qiyunDate.setFullYear(birthDate.getFullYear() + startAge.year);
  qiyunDate.setMonth(birthDate.getMonth() + startAge.month);
  qiyunDate.setDate(birthDate.getDate() + startAge.day);
  
  // 如果还未起运，返回null
  if (now < qiyunDate) return null;
  
  // 计算当前年龄（周岁）
  let age = now.getFullYear() - birthDate.getFullYear();
  if (now.getMonth() < birthDate.getMonth() || 
     (now.getMonth() === birthDate.getMonth() && now.getDate() < birthDate.getDate())) {
    age--;
  }
  
  // 计算处于第几步大运（每步10年）
  const yearsAfterQiyun = age - startAge.year;
  const destinyIndex = globalThis.Math.floor(yearsAfterQiyun / 10);
  
  // 获取对应的大运
  const pillars = props.chart.destiny_cycle.destiny_pillars;
  if (destinyIndex < 0 || destinyIndex >= pillars.length) return null;
  
  const destinyPillar = pillars[destinyIndex];
  return {
    heaven_stem: destinyPillar.heaven_stem,
    earth_branch: destinyPillar.earth_branch,
  };
});

// 获取当前流年
const getCurrentYearPillar = computed((): PillarInfo => {
  const currentYear = new globalThis.Date().getFullYear();
  return getYearGanZhi(currentYear);
});

// SVG 尺寸配置（动态根据模式调整）
const pillarCount = computed(() => isCurrentMode.value ? 6 : 4);
const pillarSpacing = computed(() => isCurrentMode.value ? 70 : 90); // 6柱时间距缩小
const svgWidth = computed(() => {
  return pillarSpacing.value * (pillarCount.value - 1) + 100; // 左右各留50px
});
const startX = 50; // 第一个柱的 X 坐标

// 动态计算天干关系区域需要的高度（包括顶部标签空间）
const stemAreaHeight = computed(() => {
  if (!props.chart?.ganzi_relations) return 60;
  const relations = visibleStemRelations.value;
  // 使用行分配算法计算实际需要的行数
  const rowMap = allocateRelationsToRows(relations);
  const rowCount = rowMap.size;
  return rowCount > 0 ? rowCount * 25 + 60 : 60; // 每行25px + 基础空间（包含标签空间）
});

// Y 坐标配置（动态）
const labelY = 20; // 柱标签 Y 坐标（固定在顶部）
const stemLineBaseY = computed(() => stemAreaHeight.value); // 天干连线基准 Y
const stemY = computed(() => stemAreaHeight.value + 40); // 天干 Y 坐标
const branchY = computed(() => stemAreaHeight.value + 110); // 地支 Y 坐标  
const branchLineBaseY = computed(() => stemAreaHeight.value + 160); // 地支连线基准 Y（下方）

// 柱标签文本（动态根据模式）
const pillarLabels = computed(() => {
  if (isCurrentMode.value) {
    return ['流年', '大运', '年柱', '月柱', '日柱', '时柱'];
  }
  return ['年柱', '月柱', '日柱', '时柱'];
});

// 动态计算 SVG 高度：根据关系数量调整
const svgHeight = computed(() => {
  if (!props.chart?.ganzi_relations) return 200;
  
  // 使用行分配算法计算实际需要的行数
  const branchRowMap = allocateRelationsToRows(visibleBranchRelations.value);
  const branchRowCount = branchRowMap.size;
  
  // 天干区域高度（已在 stemAreaHeight 中计算）
  // 字符区域：天干+地支 = 110px
  // 地支关系区域高度：每行24px + 基础空间
  const charAreaHeight = 110;
  const branchAreaHeight = branchRowCount > 0 ? branchRowCount * 24 + 40 : 40;
  
  return stemAreaHeight.value + charAreaHeight + branchAreaHeight;
});

// 获取柱的 X 坐标
const getPillarX = (index: number) => startX + index * pillarSpacing.value;

// 天干信息（动态根据模式：4柱或6柱）
const ganziStems = computed((): HeavenStemInfo[] => {
  if (!props.chart) return [];
  
  // 当前模式：流年、大运、年柱、月柱、日柱、时柱
  if (isCurrentMode.value) {
    const destinyPillar = getCurrentDestinyPillar.value;
    const yearPillar = getCurrentYearPillar.value;
    return [
      yearPillar.heaven_stem, // 流年
      destinyPillar ? destinyPillar.heaven_stem : yearPillar.heaven_stem, // 大运
      props.chart.year_pillar.heaven_stem, // 年柱
      props.chart.month_pillar.heaven_stem, // 月柱
      props.chart.day_pillar.heaven_stem, // 日柱
      props.chart.hour_pillar.heaven_stem, // 时柱
    ];
  }
  
  // 本命模式：年柱、月柱、日柱、时柱
  return [
    props.chart.year_pillar.heaven_stem,
    props.chart.month_pillar.heaven_stem,
    props.chart.day_pillar.heaven_stem,
    props.chart.hour_pillar.heaven_stem,
  ];
});

// 地支信息（动态根据模式：4柱或6柱）
const ganziBranches = computed((): EarthBranchInfo[] => {
  if (!props.chart) return [];
  
  // 当前模式：流年、大运、年柱、月柱、日柱、时柱
  if (isCurrentMode.value) {
    const destinyPillar = getCurrentDestinyPillar.value;
    const yearPillar = getCurrentYearPillar.value;
    return [
      yearPillar.earth_branch, // 流年
      destinyPillar ? destinyPillar.earth_branch : yearPillar.earth_branch, // 大运
      props.chart.year_pillar.earth_branch, // 年柱
      props.chart.month_pillar.earth_branch, // 月柱
      props.chart.day_pillar.earth_branch, // 日柱
      props.chart.hour_pillar.earth_branch, // 时柱
    ];
  }
  
  // 本命模式：年柱、月柱、日柱、时柱
  return [
    props.chart.year_pillar.earth_branch,
    props.chart.month_pillar.earth_branch,
    props.chart.day_pillar.earth_branch,
    props.chart.hour_pillar.earth_branch,
  ];
});

// 柱标识到显示位置的映射（根据模式动态）
const pillarPositionMap = computed(() => {
  if (isCurrentMode.value) {
    // 当前模式：流年、大运、年、月、日、时
    return {
      'year_fortune': 0,
      'destiny': 1,
      'year': 2,
      'month': 3,
      'day': 4,
      'hour': 5
    };
  } else {
    // 本命模式：年、月、日、时
    return {
      'year': 0,
      'month': 1,
      'day': 2,
      'hour': 3
    };
  }
});

// 根据柱标识获取显示位置
const getPillarPosition = (pillarId: string): number | undefined => {
  return pillarPositionMap.value[pillarId as keyof typeof pillarPositionMap.value];
};

// 将关系的柱标识转换为显示位置数组
const getRelationPositions = (relation: GanZhiRelation): number[] => {
  return relation.pillars
    .map(pillarId => getPillarPosition(pillarId))
    .filter((pos): pos is number => pos !== undefined)
    .sort((a, b) => a - b);
};

// 过滤可见的关系
const getVisibleRelations = (relations: GanZhiRelation[]): GanZhiRelation[] => {
  if (!relations) return [];
  if (isCurrentMode.value) {
    // 当前模式：显示所有关系
    return relations;
  } else {
    // 本命模式：只显示不涉及大运流年的关系
    return relations.filter(rel => !rel.involves_fortune);
  }
};

// 可见的天干关系
const visibleStemRelations = computed(() => {
  return getVisibleRelations(props.chart?.ganzi_relations?.stem_relations || []);
});

// 可见的地支关系
const visibleBranchRelations = computed(() => {
  return getVisibleRelations(props.chart?.ganzi_relations?.branch_relations || []);
});

// 连线数据结构
interface ConnectionLine {
  path: string;
  type: string;
  cssType: string;
  label: string;
  labelX: number;
  labelY: number;
  element1?: string; // 连线起点的五行元素
  element2?: string; // 连线终点的五行元素
  gradientId?: string; // 渐变 ID
  // 三合/三会关系的中间竖线（可选）
  middleLinePath?: string;
  middleLineElement?: string;
}

// 圆角半径
const cornerRadius = 10;

// 五行元素颜色映射
const elementColorMap: Record<string, string> = {
  '木': '#7dd56f',
  '火': '#ff6b6b',
  '土': '#a47642',
  '金': '#f2c14e',
  '水': '#5aa9ff',
};

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

// 关系行分配算法：让不重叠的关系共享同一行
// 使用"格子模型"：四柱之间有3个空位 [年-月, 月-日, 日-时]
interface RelationWithSpan {
  relation: GanZhiRelation;
  positions: number[]; // 排序后的位置
  span: number; // 跨度（最大位置 - 最小位置）
  minPos: number;
  maxPos: number;
}

// 计算关系占用的格子（0-based，3个格子：0=年月间，1=月日间，2=日时间）
const getOccupiedSlots = (minPos: number, maxPos: number): number[] => {
  const slots: number[] = [];
  for (let i = minPos; i < maxPos; i++) {
    slots.push(i);
  }
  return slots;
};

// 分配关系到行（使用优化的算法，尝试找到更紧凑的布局）
const allocateRelationsToRows = (relations: GanZhiRelation[]): Map<number, GanZhiRelation[]> => {
  // 1. 计算每个关系的跨度，过滤无效关系
  const relationsWithSpan: RelationWithSpan[] = relations
    .map(rel => {
      const positions = getRelationPositions(rel);
      if (positions.length < 2) return null;

      const minPos = positions[0];
      const maxPos = positions[positions.length - 1];
      return {
        relation: rel,
        positions,
        span: maxPos - minPos,
        minPos,
        maxPos,
      };
    })
    .filter((item): item is RelationWithSpan => item !== null);

  // 2. 使用多重策略排序
  // 主要策略：优先处理占据重要位置（如当前模式的早期位置）的关系
  relationsWithSpan.sort((a, b) => {
    // 优先级1：跨度越小越优先（短关系优先）
    const spanDiff = a.span - b.span;
    if (spanDiff !== 0) return spanDiff;

    // 优先级2：最小位置越靠前越优先（从左到右顺序）
    const minPosDiff = a.minPos - b.minPos;
    if (minPosDiff !== 0) return minPosDiff;

    // 优先级3：最大位置越靠前越优先（避免过长关系被积压）
    return a.maxPos - b.maxPos;
  });

  // 3. 使用优化的行分配算法
  const rows: Map<number, GanZhiRelation[]> = new Map();
  const rowOccupancy: Set<number>[] = []; // 每行的占用格子集合

  // 尝试为每个关系找到最佳行（保持顺序但寻找空隙）
  for (const item of relationsWithSpan) {
    const requiredSlots = getOccupiedSlots(item.minPos, item.maxPos);

    // 寻找可以容纳该关系的最佳行
    let bestRow = -1;
    let bestFitScore = Infinity;

    // 检查所有已存在的行
    for (let row = 0; row < rowOccupancy.length; row++) {
      const occupied = rowOccupancy[row];

      // 计算重叠度（已有关系与当前关系的交集）
      let overlap = 0;
      for (const slot of requiredSlots) {
        if (occupied.has(slot)) {
          overlap++;
        }
      }

      // 如果无重叠，这是一个候选行
      if (overlap === 0) {
        // 计算适配分数：优先考虑靠近已占用区域的行（紧凑布局）
        const occupiedArray = Array.from(occupied).sort((a, b) => a - b);
        const minOccupied = occupiedArray[0] || 0;
        const maxOccupied = occupiedArray[occupiedArray.length - 1] || 0;

        // 计算关系位置与已占用位置的"距离"，越小越好
        const distanceAfter = Math.max(0, item.minPos - maxOccupied);
        const distanceBefore = Math.max(0, minOccupied - item.maxPos);

        // 优先选择可以紧密连接的行
        const fitScore = Math.min(
          distanceAfter === 0 ? 0 : distanceAfter + 100, // 给予紧密连接更高优先级
          distanceBefore === 0 ? 0 : distanceBefore + 100
        );

        if (fitScore < bestFitScore) {
          bestRow = row;
          bestFitScore = fitScore;
        }
      }
    }

    // 如果找到合适的行，使用它；否则创建新行
    if (bestRow >= 0) {
      // 使用最佳行
      if (!rows.has(bestRow)) {
        rows.set(bestRow, []);
      }
      rows.get(bestRow)!.push(item.relation);

      // 标记格子为已占用
      requiredSlots.forEach(slot => rowOccupancy[bestRow].add(slot));
    } else {
      // 创建新行
      const newRow = rowOccupancy.length;

      if (!rows.has(newRow)) {
        rows.set(newRow, []);
      }
      rows.get(newRow)!.push(item.relation);

      // 创建新行的占用集合
      const newOccupied = new Set<number>();
      requiredSlots.forEach(slot => newOccupied.add(slot));
      rowOccupancy.push(newOccupied);
    }
  }

  return rows;
};

// 天干连线数据（使用优化的行分配算法）
const stemConnectionLines = computed<ConnectionLine[]>(() => {
  if (!props.chart?.ganzi_relations) return [];
  
  const relations = visibleStemRelations.value;
  const lines: ConnectionLine[] = [];
  
  // 使用优化算法分配关系到行
  const rowMap = allocateRelationsToRows(relations);
  
  let gradientCounter = 0;
  
  // 遍历每一行，绘制该行的所有关系
  rowMap.forEach((rowRelations, level) => {
    for (const rel of rowRelations) {
      const positions = getRelationPositions(rel);
      if (positions.length < 2) continue;
      
      const p1 = positions[0];
      const p2 = positions[positions.length - 1];
      
      const path = createStemArc(p1, p2, level);
      const midX = (getPillarX(p1) + getPillarX(p2)) / 2;
      const labelY = stemLineBaseY.value - level * 25;
      
      // 显示完整关系描述（简化版）
      let label = '';
      if (rel.type === '合化' && rel.element) {
        label = `合化${rel.element}`;
      } else if (rel.type === '相冲') {
        label = '冲';
      } else if (rel.type === '相克') {
        label = '克';
      }
      
      const cssType = getRelationCssType(rel.type);
      
      // 获取两端天干的五行元素
      const stems = ganziStems.value;
      const element1 = stems[p1]?.element || '木';
      const element2 = stems[p2]?.element || '木';
      const gradientId = `stem-gradient-${gradientCounter++}`;
      
      lines.push({
        path,
        type: rel.type,
        cssType,
        label,
        labelX: midX,
        labelY,
        element1,
        element2,
        gradientId,
      });
    }
  });
  
  return lines;
});

// 地支连线数据（使用优化的行分配算法）
const branchConnectionLines = computed<ConnectionLine[]>(() => {
  if (!props.chart?.ganzi_relations) return [];
  
  const relations = visibleBranchRelations.value;
  const lines: ConnectionLine[] = [];
  
  // 使用优化算法分配关系到行
  const rowMap = allocateRelationsToRows(relations);
  
  let segmentCounter = 0; // 用于生成唯一的渐变 ID
  
  // 遍历每一行，绘制该行的所有关系
  rowMap.forEach((rowRelations, level) => {
    for (const rel of rowRelations) {
      const positions = getRelationPositions(rel);
      if (positions.length < 2) continue;

      // 生成关系标签
      let relationLabel = '';
      if (rel.type === '六合' && rel.element) {
        relationLabel = `合化${rel.element}`;
      } else if (rel.type === '三合') {
        relationLabel = rel.element ? `三合${rel.element}` : '三合';
      } else if (rel.type === '半合') {
        relationLabel = rel.element ? `半合${rel.element}` : '半合';
      } else if (rel.type === '六冲') {
        relationLabel = '冲';
      } else if (rel.type === '相刑') {
        relationLabel = '刑';
      } else if (rel.type === '自刑') {
        relationLabel = '自刑';
      } else if (rel.type === '相害') {
        relationLabel = '害';
      } else if (rel.type === '三会') {
        relationLabel = rel.element ? `会${rel.element}` : '会';
      }

      const cssType = getRelationCssType(rel.type);
      const branches = ganziBranches.value;

      // 对于三合/三会关系（3个位置）：使用新的绘制方式
      if (positions.length === 3 && (rel.type === '三合' || rel.type === '三会')) {
        const p1 = positions[0]; // 左端
        const p2 = positions[1]; // 中间
        const p3 = positions[2]; // 右端

        // 1. 绘制连接两端的圆角矩形连线（p1 -> p3）
        const mainPath = createBranchArc(p1, p3, level);

        // 2. 计算中间竖线的路径（从中间地支连接到横线）
        const x2 = getPillarX(p2);
        const y2 = branchY.value + 25; // 中间地支下方
        const yBottom = branchLineBaseY.value + level * 24; // 横线的 Y 坐标
        const middleLinePath = `M ${x2} ${y2} L ${x2} ${yBottom}`;

        // 3. 标签放在交点上方（交点即为 x2, yBottom）
        const labelX = x2;
        const labelY = yBottom;

        // 4. 获取三个地支的五行元素
        const element1 = branches[p1]?.element || '木';
        const element2 = branches[p2]?.element || '木';
        const element3 = branches[p3]?.element || '木';
        const gradientId = `branch-gradient-${segmentCounter++}`;

        lines.push({
          path: mainPath,
          type: rel.type,
          cssType,
          label: relationLabel,
          labelX,
          labelY,
          element1,
          element2: element3, // 主连线的两端
          gradientId,
          middleLinePath, // 中间竖线路径
          middleLineElement: element2, // 中间元素的五行
        });
      }
      // 对于其他关系（2个位置或其他多位置关系）：使用原有逻辑
      else {
        // 计算整个关系的中央 X 坐标（所有参与位置的平均值）
        const relationCenterX = positions.reduce((sum: number, pos: number) => sum + getPillarX(pos), 0) / positions.length;

        // 对于多位置关系，将标签放在中间段
        const midIndex = Math.floor(positions.length / 2);
        const labelPosIdx = positions.length === 2 ? 0 : midIndex;

        const labelY = branchLineBaseY.value + level * 24;

        // 绘制关系的所有线段
        for (let i = 0; i < positions.length - 1; i++) {
          const p1 = positions[i];
          const p2 = positions[i + 1];

          const path = createBranchArc(p1, p2, level);

          // 标签只在中间段显示，且使用整个关系的中央 X 坐标
          const label = (i === labelPosIdx) ? relationLabel : '';
          const labelX = relationCenterX;

          // 获取两端地支的五行元素
          const element1 = branches[p1]?.element || '木';
          const element2 = branches[p2]?.element || '木';
          const gradientId = `branch-gradient-${segmentCounter++}`;

          lines.push({
            path,
            type: rel.type,
            cssType,
            label,
            labelX,
            labelY,
            element1,
            element2,
            gradientId,
          });
        }
      }
    }
  });
  
  return lines;
});

// 天干地支连线（替代原来的箭头）
interface StemBranchLine {
  x: number;
  y1: number;
  y2: number;
  element1: string; // 起点五行（地支）
}

const stemBranchLines = computed<StemBranchLine[]>(() => {
  if (!props.chart?.ganzi_relations) return [];
  
  // 过滤可见的关系
  const allRelations = props.chart.ganzi_relations.stem_branch_relations || [];
  const relations = getVisibleRelations(allRelations);
  
  const lines: StemBranchLine[] = [];
  
  for (const rel of relations) {
    if (rel.pillars.length !== 1) continue;
    
    const pos = getPillarPosition(rel.pillars[0]);
    if (pos === undefined) continue;
    
    // 获取地支和天干的五行
    const branch = ganziBranches.value[pos];
    const branchElement = branch?.element || '木';

    // 仅展示"地支生天干"的相生关系（后端也只会返回这一类）
    if (rel.type !== '相生') continue;
    
    lines.push({
      x: getPillarX(pos),
      y1: branchY.value - 30, // 从地支上方开始
      y2: stemY.value + 30, // 到天干下方结束
      element1: branchElement, // 起点（地支）
    });
  }
  
  return lines;
});

// 根据关系类型获取 CSS 类型
const getRelationCssType = (type: string): string => {
  if (['合化', '六合', '三合', '半合', '三会'].includes(type)) {
    return 'combine';
  } else if (['相冲', '六冲'].includes(type)) {
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

// 天干关系数据（本命，带 CSS 类型）
const stemRelationsData = computed(() => {
  if (!props.chart?.ganzi_relations) return [];
  return props.chart.ganzi_relations.stem_relations
    .filter(rel => !rel.involves_fortune)
    .map(rel => ({
      description: rel.description,
      cssType: getRelationCssType(rel.type),
    }));
});

// 地支关系数据（本命，带 CSS 类型）
const branchRelationsData = computed(() => {
  if (!props.chart?.ganzi_relations) return [];
  return props.chart.ganzi_relations.branch_relations
    .filter(rel => !rel.involves_fortune)
    .map(rel => ({
      description: rel.description,
      cssType: getRelationCssType(rel.type),
    }));
});

// 天干运势关系数据（涉及大运或流年天干的关系）
const stemFortuneRelationsData = computed(() => {
  if (!props.chart?.ganzi_relations || !isCurrentMode.value) return [];
  return props.chart.ganzi_relations.stem_relations
    .filter(rel => rel.involves_fortune)
    .map(rel => ({
      description: rel.description,
      cssType: getRelationCssType(rel.type),
    }));
});

// 地支运势关系数据（涉及大运或流年地支的关系）
const branchFortuneRelationsData = computed(() => {
  if (!props.chart?.ganzi_relations || !isCurrentMode.value) return [];
  return props.chart.ganzi_relations.branch_relations
    .filter(rel => rel.involves_fortune)
    .map(rel => ({
      description: rel.description,
      cssType: getRelationCssType(rel.type),
    }));
});
</script>
