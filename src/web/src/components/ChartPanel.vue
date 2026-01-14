<template>
  <div class="flex flex-col gap-4">
    <div v-if="!chart" class="rounded-2xl border border-[rgba(255,255,255,0.08)] bg-[var(--panel)] p-5 text-[var(--muted)]">
      生成后会显示命盘信息。
    </div>
    <div v-else class="flex flex-col gap-2 mt-0.5">
      <!-- 基本信息卡片 -->
      <div class="overflow-hidden rounded-2xl border border-[rgba(255,255,255,0.12)] bg-[rgba(18,20,28,0.65)] backdrop-blur-[16px]">
        <!-- 标题栏：姓名 + 农历生日 + 基础/专业切换 -->
        <div class="flex items-center justify-between gap-1 border-[rgba(255,255,255,0.08)] bg-[rgba(255,255,255,0.03)] px-4 pr-2 py-3 pb-2">
          <div class="flex flex-1 flex-wrap items-baseline gap-x-3 gap-y-1 min-w-0 text-left">
            <span class="text-lg font-bold tracking-wide text-(--accent-2) truncate whitespace-nowrap">{{ chart.name || "命主" }}</span>
            <span class="text-sm text-(--white) whitespace-nowrap">{{ lunarBirthText }}</span>
          </div>
          <!-- 右侧功能区：切换档案 + 展开/收起详细 -->
          <div class="ml-auto inline-flex shrink-0 items-center gap-2">
            <button
              v-if="infoMode === 'pro'"
              class="group flex h-8 w-8 items-center justify-center rounded-lg bg-transparent text-white/50 transition hover:text-white/70"
              type="button"
              @click="handleArchivePickerOpen"
              aria-label="切换档案"
            >
              <img :src="switchArchiveIconUrl" alt="" class="h-4 w-4 object-contain opacity-60 transition group-hover:opacity-80" />
            </button>
            <button
              class="flex h-8 w-8 items-center justify-center rounded-lg bg-transparent text-white/50 transition hover:text-white/70"
              type="button"
              @click="toggleInfoMode"
              :aria-expanded="infoMode === 'pro'"
              :aria-label="infoMode === 'pro' ? '收起详细信息' : '展开详细信息'"
              :title="infoMode === 'pro' ? '收起详细信息' : '展开详细信息'"
            >
              <svg
                class="h-4 w-4 transition-transform duration-200"
                :class="infoMode === 'pro' ? 'rotate-180' : ''"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                aria-hidden="true"
              >
                <polyline points="6 9 12 15 18 9" />
              </svg>
            </button>
          </div>
        </div>

        <!-- 基础信息模块（始终显示） -->
        <div class="flex flex-col">
          <div :class="infoGridClass" ref="infoGridRef">
            <div
              v-for="item in basicInfoItems"
              :key="item.key"
              :class="[infoItemClass, item.spanClass]"
            >
              <span :class="infoLabelClass">{{ item.label }}</span>
              <span v-if="item.type === 'gender'" :class="infoValueInlineClass">
                <span>{{ item.value }}</span>
                <img
                  v-if="chart.gender === 'male'"
                  :src="maleIconUrl"
                  alt="男"
                  class="h-3.5 w-3.5 object-contain"
                />
                <img
                  v-else-if="chart.gender === 'female'"
                  :src="femaleIconUrl"
                  alt="女"
                  class="h-3.5 w-3.5 object-contain"
                />
              </span>
              <span v-else-if="item.type === 'element'" :class="[infoValueClass, item.noWrap ? infoValueNoWrapClass : '']">
                <span :class="elementClass(item.element || '')">
                  {{ item.display }}
                </span>
              </span>
              <span v-else-if="item.type === 'birthPlace'" :class="[infoValueClass, item.noWrap ? infoValueNoWrapClass : '']">
                <template v-if="item.isUnknown">
                  未知区域<span class="ml-0.5 text-[11px] text-[var(--muted)]">（不使用真太阳时）</span>
                </template>
                <template v-else>{{ item.value }}</template>
              </span>
              <span v-else :class="[infoValueClass, item.noWrap ? infoValueNoWrapClass : '']">{{ item.value }}</span>
            </div>
          </div>
        </div>

        <!-- 专业信息模块（专业模式下额外显示） -->
        <div v-show="infoMode === 'pro'" class="flex flex-col">
          <!-- 分隔线 -->
          <div class="border-t border-[rgba(255,255,255,0.08)] my-1 mx-4"></div>
          <div :class="infoGridClass">
            <div
              v-for="item in proInfoItems"
              :key="item.key"
              :class="[infoItemClass, item.spanClass]"
            >
              <span :class="infoLabelClass">{{ item.label }}</span>
              <span v-if="item.type === 'element'" :class="[infoValueClass, item.noWrap ? infoValueNoWrapClass : '']">
                <span :class="elementClass(item.element || '')">
                  {{ item.display }}
                </span>
              </span>
              <span v-else :class="[infoValueClass, item.noWrap ? infoValueNoWrapClass : '']">{{ item.value }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 五行能量卡片 -->
      <div class="panel-card">
        <PanelHeader title="五行能量">
          <template #actions>
            <div class="relative inline-flex shrink-0 cursor-pointer items-center rounded-3xl border border-[rgba(255,255,255,0.1)] bg-[rgba(15,17,24,0.9)] p-0.5">
              <span
                :class="[
                  'relative z-[1] w-[80px] rounded-3xl px-2 py-1.5 text-center text-[12px] font-medium transition-colors duration-200',
                  energyMode === 'default' ? 'text-white' : 'text-white/65'
                ]"
                @click="setEnergyMode('default')"
              >
                干支个数
              </span>
              <span
                :class="[
                  'relative z-[1] flex w-[80px] items-center justify-center gap-1 rounded-3xl px-2 py-1.5 text-[12px] font-medium transition-colors duration-200',
                  energyMode === 'smart' ? 'text-[var(--accent-2)]' : 'text-white/65'
                ]"
                @click="setEnergyMode('smart')"
              >
                神机秘算
                <span
                  class="icon-mask h-3 w-3 align-middle"
                  :style="{ maskImage: `url(${thinkingDoubleIconUrl})`, WebkitMaskImage: `url(${thinkingDoubleIconUrl})` }"
                  aria-hidden="true"
                ></span>
              </span>
              <div
                :class="[
                  'absolute left-0.5 top-0.5 z-0 h-[calc(100%-4px)] w-[80px] rounded-3xl shadow-[0_2px_8px_rgba(0,0,0,0.25)] transition-transform duration-300 ease-[cubic-bezier(0.4,0,0.2,1)]',
                  energyMode === 'smart' ? 'bg-[rgba(214,160,96,0.18)]' : 'bg-[rgba(176,184,210,0.1)]',
                  energyMode === 'smart' ? 'translate-x-[80px]' : ''
                ]"
              ></div>
            </div>
          </template>
        </PanelHeader>
        <div class="grid grid-cols-1 gap-0 lg:grid-cols-2">
          <!-- 雷达图 -->
          <div class="flex flex-col gap-1">
            <div class="flex justify-center">
              <!-- 智能解析加载状态 -->
              <div v-if="energyMode === 'smart' && smartEnergyLoading" class="flex flex-col items-center justify-center h-[280px] w-[260px] lg:w-[300px]">
                <div class="relative">
                  <div class="h-16 w-16 animate-spin rounded-full border-4 border-[rgba(255,255,255,0.1)] border-t-[var(--accent-2)]"></div>
                  <img :src="sparkleIconUrl" class="absolute left-1/2 top-1/2 h-8 w-8 -translate-x-1/2 -translate-y-1/2 transform opacity-80" alt="加载中" />
                </div>
                <p class="mt-4 text-sm text-[var(--muted)]">{{ loadingMessage }}</p>
                <div class="mt-3 w-[200px]">
                  <div class="h-1.5 overflow-hidden rounded-full bg-[rgba(255,255,255,0.08)]">
                    <div
                      class="h-full rounded-full bg-[var(--accent-2)] transition-[width] duration-300"
                      :style="{ width: `${loadingProgress}%` }"
                    ></div>
                  </div>
                </div>
              </div>

              <!-- 雷达图 SVG -->
              <svg v-else class="w-full max-w-[260px] lg:max-w-[300px]" viewBox="0 0 400 400" role="img" aria-label="五行雷达图">
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
                <!-- 智能解析模式叠加显示默认与AI雷达图 -->
                <template v-if="energyMode === 'smart'">
                  <polygon
                    class="radar-shape-muted"
                    :points="radarShapePoints"
                  />
                  <polygon
                    class="radar-shape"
                    :points="smartRadarShapePoints"
                  />
                </template>
                <polygon
                  v-else
                  class="radar-shape-muted"
                  :points="radarShapePoints"
                />
                <g class="radar-dots">
                  <circle
                    v-for="(point, idx) in energyMode === 'smart' ? smartRadarPoints : radarPoints"
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
          <div class="flex flex-col gap-2 md:gap-3">
            <div class="mb-1.5 flex items-end justify-between gap-2 text-xs md:mb-2 md:text-[13px] px-3">
              <div class="flex flex-col items-start gap-1 pt-5">
                <strong>五行占比</strong>
              </div>
              <span v-if="energyMode === 'smart'" class="flex items-center gap-2">
                <button
                  class="flex items-center gap-1.5 rounded-xl border-1 py-2 border-[rgba(255,255,255,0.16)] bg-[rgba(255,255,255,0.04)] px-3 py-1 text-[12px] font-medium text-white/70 transition-all duration-200 hover:bg-[rgba(255,255,255,0.08)] active:bg-[rgba(255,255,255,0.16)] active:translate-y-[1px] disabled:cursor-not-allowed disabled:opacity-60"
                  :disabled="smartEnergyLoading"
                  @click="openSmartEnergyConfirm"
                >
                  再行秘算
                  <span
                    class="icon-mask h-3 w-3 align-middle"
                    :style="{ maskImage: `url(${thinkingDoubleIconUrl})`, WebkitMaskImage: `url(${thinkingDoubleIconUrl})` }"
                    aria-hidden="true"
                  ></span>
                </button>
              </span>
            </div>
            <div class="flex flex-col gap-2 px-3 md:gap-3">
              <div v-for="item in energyItems" :key="item.element" class="flex flex-col">
                <div class="flex flex-wrap items-start gap-x-2 gap-y-1 text-xs md:text-[13px]">
                  <div class="flex items-center gap-1.5 md:gap-2 shrink-0">
                    <!-- 五行标识圆点：使用对应颜色 -->
                    <span
                      class="h-2.5 w-2.5 shrink-0 rounded-full shadow-[0_0_8px_currentColor]"
                      :style="{
                        backgroundColor: elementColorMap[item.element],
                        color: elementColorMap[item.element],
                        boxShadow: `0 0 8px ${elementColorMap[item.element]}40`
                      }"
                    ></span>
                    <!-- 五行名称：使用对应颜色 -->
                    <span
                      class="font-semibold shrink-0"
                      :style="{ color: elementColorMap[item.element] }"
                    >{{ item.element }}</span>
                    <span class="text-[10px] text-[var(--muted)] md:text-[11px] shrink-0">{{ item.relation }}</span>
                  </div>
                  <!-- 智能解析的解释文本 -->
                  <div v-if="energyMode === 'smart'" class="flex min-w-0 items-start text-[10px] text-[var(--muted)] md:text-[11px] leading-snug break-words">
                    <span class="text-white/40">「</span>
                    <span class="min-w-0">{{ item.description }}</span>
                    <span class="text-white/40">」</span>
                  </div>
                </div>
                <div class="flex items-center gap-2">
                  <!-- 百分比条 -->
                  <div class="h-1.5 flex-1 overflow-hidden rounded-full bg-[rgba(255,255,255,0.08)] md:h-2">
                    <div
                      class="h-full rounded-full transition-[width] duration-500"
                      :style="{
                        width: `${(item.ratio / (energyMode === 'smart' ? maxSmartScore : maxEnergyRatio)) * 100}%`,
                        background: `linear-gradient(90deg, ${elementColorMap[item.element]}dd, ${elementColorMap[item.element]})`
                      }"
                    ></div>
                  </div>
                  <div class="flex items-center gap-1 md:gap-2.5 shrink-0">
                    <!-- 百分比：使用对应颜色 -->
                    <span
                      class="min-w-[42px] text-right text-xs font-semibold md:min-w-[48px] md:text-[13px]"
                      :style="{ color: elementColorMap[item.element] }"
                    >{{ formatPercent(item.ratio) }}</span>
                    <!-- 普通模式显示个数 -->
                    <span v-if="energyMode !== 'smart'" class="min-w-[24px] text-right text-[10px] text-[var(--muted)] md:min-w-[28px] md:text-[11px]">{{ item.count }}个</span>
                  </div>
                </div>
              </div>
            </div>
            <!-- 神机秘算三段式内容区 -->
            <div v-if="energyMode === 'smart'" class="mt-3 px-3">
              <div class="flex flex-col gap-2 text-xs md:gap-3">
                <div class="border-[rgba(255,255,255,0.08)] pt-2">
                  <button
                    class="flex w-full items-center justify-between text-left text-xs font-semibold text-[var(--text)]"
                    type="button"
                    @click="toggleEnergySection('overall')"
                  >
                    五行总势
                    <svg
                      class="h-4 w-4 text-white/50 transition-transform duration-200"
                      :class="energySectionOpen.overall ? 'rotate-180' : ''"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="2"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      aria-hidden="true"
                    >
                      <polyline points="6 9 12 15 18 9" />
                    </svg>
                  </button>
                  <div v-show="energySectionOpen.overall" class="mt-2 text-xs leading-relaxed text-[var(--muted)]">
                    <span
                      v-if="smartEnergyOverall"
                      class="summary-markdown"
                      v-html="renderEnergySummary(smartEnergyOverall)"
                    ></span>
                    <span v-else>暂无秘算提示</span>
                  </div>
                </div>
                <div class="border-[rgba(255,255,255,0.08)] pt-2">
                  <button
                    class="flex w-full items-center justify-between text-left text-xs font-semibold text-[var(--text)]"
                    type="button"
                    @click="toggleEnergySection('temperament')"
                  >
                    性情底色
                    <svg
                      class="h-4 w-4 text-white/50 transition-transform duration-200"
                      :class="energySectionOpen.temperament ? 'rotate-180' : ''"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="2"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      aria-hidden="true"
                    >
                      <polyline points="6 9 12 15 18 9" />
                    </svg>
                  </button>
                  <div v-show="energySectionOpen.temperament" class="mt-2 text-xs leading-relaxed text-[var(--muted)]">
                    <span
                      v-if="smartEnergyTemperament"
                      class="summary-markdown"
                      v-html="renderEnergySummary(smartEnergyTemperament)"
                    ></span>
                    <span v-else>暂无秘算提示</span>
                  </div>
                </div>
                <div class="border-[rgba(255,255,255,0.08)] pt-2">
                  <button
                    class="flex w-full items-center justify-between text-left text-xs font-semibold text-[var(--text)]"
                    type="button"
                    @click="toggleEnergySection('health')"
                  >
                    身心气机
                    <svg
                      class="h-4 w-4 text-white/50 transition-transform duration-200"
                      :class="energySectionOpen.health ? 'rotate-180' : ''"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="2"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      aria-hidden="true"
                    >
                      <polyline points="6 9 12 15 18 9" />
                    </svg>
                  </button>
                  <div v-show="energySectionOpen.health" class="mt-2 text-xs leading-relaxed text-[var(--muted)]">
                    <span
                      v-if="smartEnergyHealth"
                      class="summary-markdown"
                      v-html="renderEnergySummary(smartEnergyHealth)"
                    ></span>
                    <span v-else>暂无秘算提示</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <teleport to="body">
        <Transition name="fade">
          <div
            v-if="smartEnergyConfirmOpen"
            class="fixed inset-0 z-[70] flex items-center justify-center px-4 overscroll-contain"
            :style="{ paddingTop: `calc(env(safe-area-inset-top, 0px) + 12px)`, paddingBottom: `calc(env(safe-area-inset-bottom, 0px) + 12px)` }"
            role="dialog"
            aria-modal="true"
            aria-label="确认重新解析"
          >
            <button
              class="absolute inset-0 cursor-default bg-black/60"
              type="button"
              aria-label="关闭"
              @click="closeSmartEnergyConfirm"
            />
            <div class="relative w-full max-w-[360px] overflow-hidden rounded-2xl border border-white/10 bg-[rgba(18,22,33,0.92)] shadow-[0_20px_55px_rgba(0,0,0,0.6)] backdrop-blur-xl">
              <div class="px-4 pt-4">
                <div class="flex items-center gap-2 text-base font-semibold text-white">
                  确认再行秘算？
                </div>
                <p class="mt-2 text-sm leading-relaxed text-white/70">
                  再行秘算将消耗 <span class="text-[var(--accent-2)]">10 </span>灵力，是否继续？
                </p>
                <p
                  class="mt-4 text-xs leading-[1.75] text-white/50 tracking-wide
                        border-l border-white/15 pl-4 italic">
                  命局之象，自有多重映照。<br />
                  再行秘算，非改前言之断。<br />
                  <span class="opacity-80">
                    不更命盘之本，<br />
                    仅换推演之镜，<br />
                    复算五行能量，<br />
                    以见其别样侧影与变化。
                  </span>
                </p>
              </div>
              <div class="flex items-center justify-end gap-4 px-4 pb-4 pt-3">
                <button
                  class="inline-flex items-center justify-center rounded-lg border border-white/10 bg-white/5 px-4 py-2 text-sm font-medium text-white/80 transition hover:bg-white/10"
                  type="button"
                  @click="closeSmartEnergyConfirm"
                >
                  取消
                </button>
                <button
                  class="inline-flex items-center justify-center rounded-lg bg-gradient-to-br from-[var(--accent)] to-[var(--accent-2)] px-4 py-2 text-sm font-semibold text-[#0a0604] shadow-[0_8px_22px_rgba(214,160,96,0.28)] transition hover:-translate-y-[1px] hover:shadow-[0_12px_26px_rgba(214,160,96,0.35)] active:translate-y-0 disabled:cursor-not-allowed disabled:opacity-70"
                  type="button"
                  :disabled="smartEnergyLoading"
                  @click="confirmSmartEnergyRefresh"
                >
                  确认
                </button>
              </div>
            </div>
          </div>
        </Transition>
      </teleport>

      <!-- 八字命盘卡片 -->
      <div class="panel-card">
        <PanelHeader title="八字命盘"/>
        <div class="mx-auto w-full max-w-[720px] overflow-hidden rounded-[14px] border-0 border-[rgba(255,255,255,0.08)]">
          <div class="mx-auto w-full grid grid-cols-[40px_repeat(4,minmax(0,1fr))] bg-[rgba(255,255,255,0.06)] font-semibold text-[13px]">
            <div class="flex items-center justify-center py-3 text-xs text-[var(--muted)]"></div>
            <div class="flex flex-col items-center justify-center gap-1 px-2 py-3 text-center text-sm">年柱</div>
            <div class="flex flex-col items-center justify-center gap-1 px-2 py-3 text-center text-sm">月柱</div>
            <div class="flex flex-col items-center justify-center gap-1 px-2 py-3 text-center text-sm">日柱</div>
            <div class="flex flex-col items-center justify-center gap-1 px-2 py-3 text-center text-sm">时柱</div>
          </div>
          <div class="mx-auto w-full grid grid-cols-[40px_repeat(4,minmax(0,1fr))] border-t border-[rgba(255,255,255,0.08)] bg-[rgba(255,255,255,0.02)]">
            <div class="flex items-center justify-center pl-3 py-3 text-xs text-[var(--muted)]">主星</div>
            <div class="flex flex-col items-center justify-center gap-1 px-2 py-3 text-center text-xs text-[var(--muted)]">{{ chart.year_pillar.heaven_stem.ten_god }}</div>
            <div class="flex flex-col items-center justify-center gap-1 px-2 py-3 text-center text-xs text-[var(--muted)]">{{ chart.month_pillar.heaven_stem.ten_god }}</div>
            <div class="flex flex-col items-center justify-center gap-1 px-2 py-3 text-center text-xs text-[var(--muted)]">{{ chart.day_pillar.heaven_stem.ten_god }}</div>
            <div class="flex flex-col items-center justify-center gap-1 px-2 py-3 text-center text-xs text-[var(--muted)]">{{ chart.hour_pillar.heaven_stem.ten_god }}</div>
          </div>
          <div class="mx-auto w-full grid grid-cols-[40px_repeat(4,minmax(0,1fr))] border-t border-[rgba(255,255,255,0.08)] bg-[rgba(255,255,255,0.02)]">
            <div class="flex items-center justify-center pl-3 py-3 text-xs text-[var(--muted)]">天干</div>
            <div class="flex items-center justify-center px-2 py-3 text-center">
              <span :class="['text-[26px] font-bold tracking-wide', elementClass(chart.year_pillar.heaven_stem.element)]">
                {{ chart.year_pillar.heaven_stem.name }}
              </span>
              <span class="text-sm opacity-80 ml-0.5">{{ elementIcon(chart.year_pillar.heaven_stem.element) }}</span>
            </div>
            <div class="flex items-center justify-center px-2 py-3 text-center">
              <span :class="['text-[26px] font-bold tracking-wide', elementClass(chart.month_pillar.heaven_stem.element)]">
                {{ chart.month_pillar.heaven_stem.name }}
              </span>
              <span class="text-sm opacity-80 ml-0.5">{{ elementIcon(chart.month_pillar.heaven_stem.element) }}</span>
            </div>
            <div class="flex items-center justify-center px-2 py-3 text-center">
              <span :class="['text-[26px] font-bold tracking-wide', elementClass(chart.day_pillar.heaven_stem.element)]">
                {{ chart.day_pillar.heaven_stem.name }}
              </span>
              <span class="text-sm opacity-80 ml-0.5">{{ elementIcon(chart.day_pillar.heaven_stem.element) }}</span>
            </div>
            <div class="flex items-center justify-center px-2 py-3 text-center">
              <span :class="['text-[26px] font-bold tracking-wide', elementClass(chart.hour_pillar.heaven_stem.element)]">
                {{ chart.hour_pillar.heaven_stem.name }}
              </span>
              <span class="text-sm opacity-80 ml-0.5">{{ elementIcon(chart.hour_pillar.heaven_stem.element) }}</span>
            </div>
          </div>
          <div class="mx-auto w-full grid grid-cols-[40px_repeat(4,minmax(0,1fr))] border-t border-[rgba(255,255,255,0.08)] bg-[rgba(255,255,255,0.02)]">
            <div class="flex items-center justify-center pl-3  py-3 text-xs text-[var(--muted)]">地支</div>
            <div class="flex items-center justify-center px-2 py-3 text-center">
              <span :class="['text-[26px] font-bold tracking-wide', elementClass(chart.year_pillar.earth_branch.element)]">
                {{ chart.year_pillar.earth_branch.name }}
              </span>
              <span class="text-sm opacity-80 ml-0.5">{{ elementIcon(chart.year_pillar.earth_branch.element) }}</span>
            </div>
            <div class="flex items-center justify-center px-2 py-3 text-center">
              <span :class="['text-[26px] font-bold tracking-wide', elementClass(chart.month_pillar.earth_branch.element)]">
                {{ chart.month_pillar.earth_branch.name }}
              </span>
              <span class="text-sm opacity-80 ml-0.5">{{ elementIcon(chart.month_pillar.earth_branch.element) }}</span>
            </div>
            <div class="flex items-center justify-center px-2 py-3 text-center">
              <span :class="['text-[26px] font-bold tracking-wide', elementClass(chart.day_pillar.earth_branch.element)]">
                {{ chart.day_pillar.earth_branch.name }}
              </span>
              <span class="text-sm opacity-80 ml-0.5">{{ elementIcon(chart.day_pillar.earth_branch.element) }}</span>
            </div>
            <div class="flex items-center justify-center px-2 py-3 text-center">
              <span :class="['text-[26px] font-bold tracking-wide', elementClass(chart.hour_pillar.earth_branch.element)]">
                {{ chart.hour_pillar.earth_branch.name }}
              </span>
              <span class="text-sm opacity-80 ml-0.5">{{ elementIcon(chart.hour_pillar.earth_branch.element) }}</span>
            </div>
          </div>
          <div class="mx-auto w-full grid grid-cols-[40px_repeat(4,minmax(0,1fr))] border-t border-[rgba(255,255,255,0.08)] bg-[rgba(255,255,255,0.02)]">
            <div class="flex items-center justify-center pl-3  py-3 text-xs text-[var(--muted)]">藏干</div>
            <div class="flex flex-col gap-2 px-2 py-3 text-center text-[13px]">
              <span
                v-for="stem in chart.year_pillar.earth_branch.hidden_stems"
                :key="stem.name"
              >
                <span :class="elementClass(stem.element)">{{ stem.name }}</span>
                <span class="text-[11px] text-[var(--muted)] ml-1">{{ stem.ten_god }}</span>
              </span>
            </div>
            <div class="flex flex-col gap-2 px-2 py-3 text-center text-[13px]">
              <span
                v-for="stem in chart.month_pillar.earth_branch.hidden_stems"
                :key="stem.name"
              >
                <span :class="elementClass(stem.element)">{{ stem.name }}</span>
                <span class="text-[11px] text-[var(--muted)] ml-1">{{ stem.ten_god }}</span>
              </span>
            </div>
            <div class="flex flex-col gap-2 px-2 py-3 text-center text-[13px]">
              <span
                v-for="stem in chart.day_pillar.earth_branch.hidden_stems"
                :key="stem.name"
              >
                <span :class="elementClass(stem.element)">{{ stem.name }}</span>
                <span class="text-[11px] text-[var(--muted)] ml-1">{{ stem.ten_god }}</span>
              </span>
            </div>
            <div class="flex flex-col gap-2 px-2 py-3 text-center text-[13px]">
              <span
                v-for="stem in chart.hour_pillar.earth_branch.hidden_stems"
                :key="stem.name"
              >
                <span :class="elementClass(stem.element)">{{ stem.name }}</span>
                <span class="text-[11px] text-[var(--muted)] ml-1">{{ stem.ten_god }}</span>
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- 大运卡片 -->
      <div class="panel-card">
        <PanelHeader title="大运">
          <template #title>
            <div class="flex items-center gap-3">
              <h3 class="text-base font-semibold text-(--accent-2)">十年大运</h3>
              <!-- <span v-if="destinyMeta" class="h-3 w-px bg-[rgba(255,255,255,0.2)]"></span> -->
              <span v-if="destinyMeta" class="text-xs text-[var(--muted)]">{{ destinyMeta }}</span>
            </div>
          </template>
          <template #actions>
            <div class="relative inline-flex shrink-0 cursor-pointer items-center rounded-3xl border border-[rgba(255,255,255,0.1)] bg-[rgba(15,17,24,0.9)] p-0.5">
              <span
                v-for="mode in ['60', '120']"
                :key="mode"
                :class="[
                  'relative z-[1] w-[52px] rounded-3xl px-2 py-1.5 text-center text-[12px] font-medium transition-colors duration-200',
                  destinyRangeMode === mode ? 'text-white' : 'text-white/65'
                ]"
                @click="setDestinyRangeMode(mode as '60' | '120')"
              >
                {{ mode === '60' ? '60年' : '120年' }}
              </span>
              <div
                :class="[
                  'absolute left-0.5 top-0.5 z-0 h-[calc(100%-4px)] w-[52px] rounded-3xl bg-[rgba(176,184,210,0.1)] shadow-[0_2px_8px_rgba(0,0,0,0.25)] transition-transform duration-300 ease-[cubic-bezier(0.4,0,0.2,1)]',
                  destinyRangeMode === '120' ? 'translate-x-[52px]' : ''
                ]"
              ></div>
            </div>
          </template>
        </PanelHeader>
        <div v-if="!destinyPillars.length" class="text-[var(--muted)]">暂无大运数据。</div>
        <div
          v-else
          class="grid grid-cols-6 gap-1"
        >
          <div
            v-for="(pillar, index) in destinyPillarsDisplay"
            :key="pillar.year"
            :class="[
              'flex flex-col items-center gap-2 rounded-[14px] border p-3 text-center transition-all duration-200 hover:-translate-y-0.5',
              destinyPillarTone(pillar, index)
            ]"
          >
            <div class="flex flex-wrap items-center justify-center gap-1 text-center">
              <span class="text-[13px] font-medium text-[var(--text)]">{{ pillar.year }}</span>
              <span class="text-[11px] text-[var(--muted)]">{{ pillar.age }}岁</span>
            </div>
            <div class="flex flex-nowrap items-center justify-center gap-x-[clamp(0px,0.5vw,0.25rem)] text-center">
              <span :class="['text-[22px] font-bold leading-tight tracking-wide', elementClass(pillar.heaven_stem.element)]">
                {{ pillar.heaven_stem.name }}
              </span>
              <span class="text-[10px] font-medium text-[var(--accent-2)] opacity-85 whitespace-nowrap">{{ pillar.heaven_stem.ten_god }}</span>
            </div>
            <div class="flex flex-nowrap items-center justify-center gap-x-[clamp(0px,0.5vw,0.25rem)] text-center">
              <span :class="['text-[22px] font-bold leading-tight tracking-wide', elementClass(pillar.earth_branch.element)]">
                {{ pillar.earth_branch.name }}
              </span>
              <span class="text-[10px] font-medium text-[var(--accent-2)] opacity-85 whitespace-nowrap">{{ pillar.earth_branch_ten_god }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 干支关系卡片 -->
      <div class="panel-card">
        <PanelHeader title="干支关系">
          <template #actions>
            <div
              class="relative inline-flex shrink-0 cursor-pointer items-center rounded-3xl border border-[rgba(255,255,255,0.1)] bg-[rgba(15,17,24,0.9)] p-0.5 transition-colors hover:border-[rgba(255,255,255,0.2)]"
              @click="toggleGanziMode"
            >
              <div class="relative z-[2] flex w-full">
                <span
                  :class="[
                    'relative z-[1] w-[52px] rounded-3xl px-3 py-1.5 text-center text-[12px] font-medium transition-colors duration-200',
                    !isCurrentMode ? 'text-white' : 'text-white/65'
                  ]"
                >
                  本命
                </span>
                <span
                  :class="[
                    'relative z-[1] w-[52px] rounded-3xl px-3 py-1.5 text-center text-[12px] font-medium transition-colors duration-200',
                    isCurrentMode ? 'text-white' : 'text-white/65'
                  ]"
                >
                  流运
                </span>
              </div>
              <div
                :class="[
                  'absolute left-0.5 top-0.5 z-0 h-[calc(100%-4px)] w-[52px] rounded-3xl bg-[rgba(176,184,210,0.1)] shadow-[0_2px_8px_rgba(0,0,0,0.25)] transition-transform duration-300 ease-[cubic-bezier(0.4,0,0.2,1)]',
                  isCurrentMode ? 'translate-x-[52px]' : ''
                ]"
              ></div>
            </div>
          </template>
        </PanelHeader>

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
        <div class="flex flex-col gap-2">
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
            <div v-if="!stemRelationsData.length && !branchRelationsData.length" class="text-sm text-[var(--muted)]">
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
            <div v-if="!stemRelationsData.length && !branchRelationsData.length && !stemFortuneRelationsData.length && !branchFortuneRelationsData.length" class="text-sm text-[var(--muted)]">
              当前无明显刑冲合会关系
            </div>
          </template>
        </div>

        <div class="rounded-lg p-2.5 text-xs leading-relaxed text-[var(--muted)]">
          因八字合化论流派繁多且断法各异，以上结果仅供参考
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, inject, onBeforeUnmount, onMounted, onUnmounted, ref, watch } from "vue";
import type { Chart, GanZhiRelation, PillarInfo, HeavenStemInfo, EarthBranchInfo, SmartEnergyResult } from "../types";
import PanelHeader from "./PanelHeader.vue";
import { lockBackgroundScroll } from "../utils/scroll-lock";
// 导入性别图标
import maleIconUrl from "../assets/gender-male.png";
import femaleIconUrl from "../assets/gender-female.png";
// 导入 sparkle 图标
import sparkleIconUrl from "../assets/sparkles.png";
import thinkingDoubleIconUrl from "../assets/svg/thinking-double-full.svg";
import switchArchiveIconUrl from "../assets/change-arch.png";

const props = defineProps<{
  chart: Chart | null;
}>();

const openArchivePicker = inject<() => void>("openArchivePicker", undefined);

const handleArchivePickerOpen = () => {
  openArchivePicker?.();
};

// ========== 基本信息卡片模式切换 ==========
const infoMode = ref<'basic' | 'pro'>('basic');

const toggleInfoMode = () => {
  infoMode.value = infoMode.value === "basic" ? "pro" : "basic";
};

const destinyRangeMode = ref<'60' | '120'>('60');

const setDestinyRangeMode = (mode: '60' | '120') => {
  destinyRangeMode.value = mode;
};

const infoGridClass = [
  "grid grid-cols-2 lg:grid-cols-3",
  "grid-flow-row-dense gap-x-1 gap-y-2.5 px-2 py-2.5",
].join(" ");
const infoItemClass = "flex items-center gap-2.5 min-w-0";
const infoLabelClass = [
  "inline-flex min-w-[42px] items-center justify-center rounded-lg",
  "border border-[rgba(100,120,160,0.3)] bg-[rgba(60,70,100,0.4)]",
  "px-2 py-1 text-[12px] font-medium tracking-wide text-[rgba(180,190,210,0.9)]",
].join(" ");
const infoValueClass = "flex-1 min-w-0 text-sm text-[var(--text)] break-words whitespace-normal";
const infoValueNoWrapClass = "whitespace-nowrap overflow-hidden text-ellipsis";
const infoValueInlineClass = "flex min-w-0 items-center gap-1 text-sm text-[var(--text)]";

type InfoItemType = "text" | "gender" | "birthPlace" | "element";

type InfoItem = {
  key: string;
  label: string;
  type: InfoItemType;
  value?: string;
  display?: string;
  element?: string;
  isUnknown?: boolean;
  isSpan?: boolean;
  spanClass?: string;
  noWrap?: boolean;
};

const textMeasure = (() => {
  if (typeof document === "undefined") {
    return (_text: string, _font: string) => 0;
  }
  const canvas = document.createElement("canvas");
  const context = canvas.getContext("2d");
  if (!context) {
    return (_text: string, _font: string) => 0;
  }
  return (text: string, font: string) => {
    context.font = font;
    return context.measureText(text).width;
  };
})();

const viewportWidth = ref(typeof window !== "undefined" ? window.innerWidth : 0);
const infoGridRef = ref<HTMLElement | null>(null);
const containerWidth = ref(0);

const updateViewportWidth = () => {
  if (typeof window === "undefined") return;
  viewportWidth.value = window.innerWidth;
};


onMounted(() => {
  updateViewportWidth();
  window.addEventListener("resize", updateViewportWidth);
});

onBeforeUnmount(() => {
  window.removeEventListener("resize", updateViewportWidth);
});

onMounted(() => {
  updateInfoFontFamily();
  if (typeof document !== "undefined" && "fonts" in document) {
    document.fonts.ready.then(() => {
      updateInfoFontFamily();
    });
  }
});

let infoGridObserver: ResizeObserver | null = null;

onMounted(() => {
  if (typeof ResizeObserver === "undefined") return;
  infoGridObserver = new ResizeObserver((entries) => {
    const entry = entries[0];
    if (!entry) return;
    containerWidth.value = Math.round(entry.contentRect.width);
  });
  if (infoGridRef.value) {
    infoGridObserver.observe(infoGridRef.value);
  }
});

onBeforeUnmount(() => {
  if (infoGridObserver) {
    infoGridObserver.disconnect();
    infoGridObserver = null;
  }
});

watch(infoGridRef, (nextEl, prevEl) => {
  if (!infoGridObserver) return;
  if (prevEl) {
    infoGridObserver.unobserve(prevEl);
  }
  if (nextEl) {
    infoGridObserver.observe(nextEl);
  }
  if (nextEl) {
    updateInfoFontFamily();
  }
});

const gridColumnCount = computed(() => {
  const baseWidth = containerWidth.value || viewportWidth.value;
  return baseWidth >= 1024 ? 3 : 2;
});

const columnBaseWidth = computed(() => {
  const columns = gridColumnCount.value;
  const containerPadding = 24;
  const columnGap = 4;
  const totalColumnGap = columnGap * (columns - 1);
  const baseWidth = containerWidth.value || viewportWidth.value;
  return Math.max(0, (baseWidth - containerPadding - totalColumnGap) / columns);
});

const infoFontFamily = ref("system-ui");
const valueFont = computed(() => `400 14px ${infoFontFamily.value}`);
const labelFont = computed(() => `500 12px ${infoFontFamily.value}`);
const labelMinWidth = 42;
const labelHorizontalPadding = 16;
const labelGap = 10;

const getSpanMeta = (label: string, value: string, extraWidth = 0) => {
  const columns = gridColumnCount.value;
  const valueWidth = textMeasure(value, valueFont.value) + extraWidth;
  const labelTextWidth = textMeasure(label, labelFont.value) + labelHorizontalPadding;
  const labelWidth = Math.max(labelMinWidth, labelTextWidth);
  const measuredWidth = labelWidth + labelGap + valueWidth;
  const columnWidth = columnBaseWidth.value;
  let span = 1;

  if (columns === 2) {
    if (measuredWidth > columnWidth) span = 2;
  } else if (columns === 3) {
    if (measuredWidth > columnWidth * 2) {
      span = 3;
    } else if (measuredWidth > columnWidth) {
      span = 2;
    }
  }

  const maxWidth = columnWidth * span;
  const maxValueWidth = Math.max(0, maxWidth - labelWidth - labelGap);
  return {
    isSpan: span > 1,
    spanClass: span === 2 ? "col-span-2" : span === 3 ? "col-span-3" : "",
    noWrap: span > 1 && valueWidth <= maxValueWidth,
  };
};

const updateInfoFontFamily = () => {
  if (typeof window === "undefined") return;
  const target = infoGridRef.value || document.documentElement;
  const computedStyle = window.getComputedStyle(target);
  if (computedStyle.fontFamily) {
    infoFontFamily.value = computedStyle.fontFamily;
  }
};

const basicInfoItems = computed<InfoItem[]>(() => {
  if (!props.chart) return [];
  const birthPlaceUnknown = !props.chart.birth_place || props.chart.birth_place === "未知地区";
  const birthPlaceText = birthPlaceUnknown
    ? "未知区域（不使用真太阳时）"
    : props.chart.birth_place;

  return [
    {
      key: "gender",
      label: "性别",
      type: "gender",
      value: genderText.value,
      ...getSpanMeta("性别", genderText.value, props.chart.gender ? 18 : 0),
    },
    {
      key: "zodiacAnimal",
      label: "属相",
      type: "text",
      value: props.chart.zodiac_animal || "未知",
      ...getSpanMeta("属相", props.chart.zodiac_animal || "未知"),
    },
    {
      key: "zodiacSign",
      label: "星座",
      type: "text",
      value: props.chart.zodiac_sign || "未知",
      ...getSpanMeta("星座", props.chart.zodiac_sign || "未知"),
    },
    {
      key: "starMansion",
      label: "星宿",
      type: "text",
      value: props.chart.star_mansion || "未知",
      ...getSpanMeta("星宿", props.chart.star_mansion || "未知"),
    },
    {
      key: "solar",
      label: "阳历",
      type: "text",
      value: solarText.value,
      ...getSpanMeta("阳历", solarText.value),
    },
    {
      key: "trueSolar",
      label: "真太阳时",
      type: "text",
      value: trueSolarText.value,
      ...getSpanMeta("真太阳时", trueSolarText.value),
    },
    {
      key: "birthPlace",
      label: "出生地区",
      type: "birthPlace",
      value: props.chart.birth_place || "",
      isUnknown: birthPlaceUnknown,
      ...getSpanMeta("出生地区", birthPlaceText),
    },
    {
      key: "jieqi",
      label: "出生节气",
      type: "text",
      value: jieqiText.value,
      ...getSpanMeta("出生节气", jieqiText.value),
    },
  ];
});

const proInfoItems = computed<InfoItem[]>(() => {
  if (!props.chart) return [];

  return [
    {
      key: "dayMaster",
      label: "命主五行",
      type: "element",
      display: props.chart.day_master_display || dayMasterDisplay.value,
      element: props.chart.day_master.element,
      ...getSpanMeta("命主五行", props.chart.day_master_display || dayMasterDisplay.value),
    },
    {
      key: "fortuneElement",
      label: "天运五行",
      type: "text",
      value: props.chart.fortune_element || "未知",
      ...getSpanMeta("天运五行", props.chart.fortune_element || "未知"),
    },
    {
      key: "taiYuan",
      label: "胎元",
      type: "text",
      value: taiYuanText.value,
      ...getSpanMeta("胎元", taiYuanText.value),
    },
    {
      key: "taiXi",
      label: "胎息",
      type: "text",
      value: taiXiText.value,
      ...getSpanMeta("胎息", taiXiText.value),
    },
    {
      key: "mingGong",
      label: "命宫",
      type: "text",
      value: mingGongText.value,
      ...getSpanMeta("命宫", mingGongText.value),
    },
    {
      key: "shenGong",
      label: "身宫",
      type: "text",
      value: shenGongText.value,
      ...getSpanMeta("身宫", shenGongText.value),
    },
    {
      key: "kongWang",
      label: "空亡",
      type: "text",
      value: props.chart.kong_wang || "未知",
      ...getSpanMeta("空亡", props.chart.kong_wang || "未知"),
    },
    {
      key: "renYuan",
      label: "人元司令分野",
      type: "text",
      value: props.chart.ren_yuan_si_ling || "未知",
      ...getSpanMeta("人元司令分野", props.chart.ren_yuan_si_ling || "未知"),
    },
  ];
});

// ========== 五行能量模式切换 ==========

// 生成缓存 key（需要在使用前定义）
const getEnergyCacheKey = (chart: Chart): string => {
  const dayPillar = chart.day_pillar;
  return `energy_smart_${dayPillar.heaven_stem.name}${dayPillar.earth_branch.name}`;
};

// 智能解析数据
const smartEnergyData = ref<SmartEnergyResult | null>(null);
const smartEnergyLoading = ref(false);
// 初始化检查是否有缓存
const initSmartEnergyCache = () => {
  if (props.chart) {
    const cacheKey = getEnergyCacheKey(props.chart);
    const cached = localStorage.getItem(cacheKey);

    // 如果有缓存，直接加载数据
    if (cached) {
      smartEnergyData.value = JSON.parse(cached);
    }
  }
};

// 当前能量模式（默认模式 or 神机秘算）
const energyMode = ref<'default' | 'smart'>('default');
const smartEnergyConfirmOpen = ref(false);
let releaseConfirmScrollLock: (() => void) | null = null;
const energySectionOpen = ref({
  overall: true,
  temperament: true,
  health: true,
});
const ENERGY_ESTIMATE_KEY = "energy_estimate_ms";
const INITIAL_ENERGY_ESTIMATE_MS = 10000;
const ENERGY_ESTIMATE_ALPHA = 0.2;
const ENERGY_ESTIMATE_MIN_MS = 4000;
const ENERGY_ESTIMATE_MAX_MS = 60000;

const clampEnergyEstimate = (value: number) => Math.min(
  ENERGY_ESTIMATE_MAX_MS,
  Math.max(ENERGY_ESTIMATE_MIN_MS, value),
);

const loadEnergyEstimateMs = () => {
  const raw = localStorage.getItem(ENERGY_ESTIMATE_KEY);
  const parsed = raw ? Number.parseFloat(raw) : Number.NaN;
  if (!Number.isFinite(parsed) || parsed <= 0) {
    return INITIAL_ENERGY_ESTIMATE_MS;
  }
  return clampEnergyEstimate(parsed);
};

const saveEnergyEstimateMs = (value: number) => {
  localStorage.setItem(ENERGY_ESTIMATE_KEY, String(Math.round(value)));
};

const LOADING_MESSAGES = [
  "神机运转，命局五行推演中...",
  "五行气机已起，正在校衡强弱...",
  "炉火纯青，正在凝练五行分数...",
  "收束气象，准备呈现结果...",
];

const loadingProgress = ref(0);
const energyEstimateMs = ref(loadEnergyEstimateMs());
const updateEnergyEstimateMs = (elapsedMs: number) => {
  if (!Number.isFinite(elapsedMs) || elapsedMs <= 0) return;
  const current = energyEstimateMs.value;
  const next = clampEnergyEstimate(current * (1 - ENERGY_ESTIMATE_ALPHA) + elapsedMs * ENERGY_ESTIMATE_ALPHA);
  energyEstimateMs.value = next;
  saveEnergyEstimateMs(next);
};
const LOADING_START_PROGRESS = 8;
const LOADING_MAX_PROGRESS = 95;
const LOADING_TICK_MS = 400;
const getLoadingProgress = (elapsedMs: number, estimateMs: number) => {
  const normalized = elapsedMs / Math.max(estimateMs, 1);
  const eased = 1 - Math.exp(-normalized * 2.2);
  return Math.round(eased * 100);
};
const loadingMessage = computed(() => {
  if (!smartEnergyLoading.value) return "";
  const progress = loadingProgress.value;
  if (progress < 35) return LOADING_MESSAGES[0];
  if (progress < 60) return LOADING_MESSAGES[1];
  if (progress < 80) return LOADING_MESSAGES[2];
  return LOADING_MESSAGES[3];
});
let loadingTimer: number | null = null;

const setEnergyMode = (mode: 'default' | 'smart') => {
  energyMode.value = mode;
};

// 监听 chart 变化，自动设置默认模式
watch(() => props.chart, () => {
  initSmartEnergyCache();
}, { immediate: true });

// 获取智能解析数据
const fetchSmartEnergyData = async () => {
  if (!props.chart) return;

  const cacheKey = getEnergyCacheKey(props.chart);
  const cached = localStorage.getItem(cacheKey);

  if (cached) {
    smartEnergyData.value = JSON.parse(cached);
    return;
  }

  // 请求 API
  const requestStartedAt = Date.now();
  smartEnergyLoading.value = true;
  try {
    const response = await fetch('/api/bazi/energy-analysis', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chart: props.chart }),
    });

    if (!response.ok) {
      throw new Error('请求失败');
    }

    const data = await response.json();
    smartEnergyData.value = data;

    // 缓存结果
    localStorage.setItem(cacheKey, JSON.stringify(data));
  } catch (error) {
    console.error('获取智能解析数据失败:', error);
    smartEnergyData.value = null;
  } finally {
    updateEnergyEstimateMs(Date.now() - requestStartedAt);
    smartEnergyLoading.value = false;
  }
};

const refreshSmartEnergy = () => {
  if (!props.chart) return;
  const cacheKey = getEnergyCacheKey(props.chart);
  localStorage.removeItem(cacheKey);
  smartEnergyData.value = null;
  fetchSmartEnergyData();
};

const openSmartEnergyConfirm = () => {
  smartEnergyConfirmOpen.value = true;
};

const closeSmartEnergyConfirm = () => {
  smartEnergyConfirmOpen.value = false;
};

const confirmSmartEnergyRefresh = () => {
  closeSmartEnergyConfirm();
  refreshSmartEnergy();
};

const toggleEnergySection = (key: keyof typeof energySectionOpen.value) => {
  energySectionOpen.value[key] = !energySectionOpen.value[key];
};

watch(smartEnergyConfirmOpen, (isOpen) => {
  if (isOpen) {
    if (!releaseConfirmScrollLock) {
      releaseConfirmScrollLock = lockBackgroundScroll();
    }
  } else if (releaseConfirmScrollLock) {
    releaseConfirmScrollLock();
    releaseConfirmScrollLock = null;
  }
});

watch(smartEnergyLoading, (isLoading) => {
  if (isLoading) {
    const startedAt = Date.now();
    const estimateMs = energyEstimateMs.value || INITIAL_ENERGY_ESTIMATE_MS;
    loadingProgress.value = LOADING_START_PROGRESS;
    if (loadingTimer) {
      window.clearInterval(loadingTimer);
    }
    loadingTimer = window.setInterval(() => {
      const elapsedMs = Date.now() - startedAt;
      const progress = Math.min(
        LOADING_MAX_PROGRESS,
        Math.max(LOADING_START_PROGRESS, getLoadingProgress(elapsedMs, estimateMs)),
      );
      loadingProgress.value = Math.max(loadingProgress.value, progress);
    }, LOADING_TICK_MS);
  } else {
    loadingProgress.value = 0;
    if (loadingTimer) {
      window.clearInterval(loadingTimer);
      loadingTimer = null;
    }
  }
});

onUnmounted(() => {
  if (releaseConfirmScrollLock) {
    releaseConfirmScrollLock();
    releaseConfirmScrollLock = null;
  }
  if (loadingTimer) {
    window.clearInterval(loadingTimer);
    loadingTimer = null;
  }
});

// 监听模式变化，智能解析模式下获取数据
watch(energyMode, (newMode) => {
  if (newMode === 'smart' && !smartEnergyData.value && !smartEnergyLoading.value) {
    fetchSmartEnergyData();
  }
});

// 根据当前 chart 重新获取智能解析数据（当切换档案时）
watch(() => props.chart, () => {
  if (energyMode.value === 'smart' && props.chart) {
    const cacheKey = getEnergyCacheKey(props.chart);
    const cached = localStorage.getItem(cacheKey);
    if (cached) {
      smartEnergyData.value = JSON.parse(cached);
    } else {
      smartEnergyData.value = null;
      fetchSmartEnergyData();
    }
  }
});

// 五行个数统计（不含藏干）- 前端计算
// 五行个数统计（含藏干）- 从后端获取
const fiveElementsCountWithHidden = computed(() => {
  return props.chart?.five_elements_count ?? {};
});

// 计算能量比率
const calculateRatios = (counts: Record<string, number>) => {
  const total = Object.values(counts).reduce((sum, v) => sum + v, 0);
  if (total === 0) return { 木: 0, 火: 0, 土: 0, 金: 0, 水: 0 };

  const result: Record<string, number> = {};
  for (const key of Object.keys(counts)) {
    result[key] = Math.round((counts[key] / total) * 100 * 10) / 10;
  }
  return result;
};

// 默认模式的能量数据（原进阶）
const defaultEnergyCounts = computed(() => {
  return fiveElementsCountWithHidden.value as Record<string, number>;
});

const defaultEnergyRatios = computed(() => {
  return calculateRatios(defaultEnergyCounts.value);
});

// 智能解析模式的能量数据
const smartEnergyItems = computed(() => {
  if (!smartEnergyData.value) {
    return elementOrder.map((element) => ({
      element,
      score: 0,
      description: '',
      relation: '未知',
    }));
  }

  const dayElement = props.chart?.day_master?.element ?? '';
  return elementOrder.map((element) => ({
    element,
    score: smartEnergyData.value!.elements[element as keyof typeof smartEnergyData.value.elements]?.score ?? 0,
    description: smartEnergyData.value!.elements[element as keyof typeof smartEnergyData.value.elements]?.description ?? '',
    relation: elementRelationMap[dayElement]?.[element] ?? '未知',
  }));
});

// 最大智能能量分数（用于雷达图归一化）
const maxSmartScore = computed(() => {
  const maxScore = Math.max(...smartEnergyItems.value.map((item) => item.score), 0);
  return maxScore > 0 ? maxScore : 100;
});

const smartEnergyOverall = computed(() => {
  return smartEnergyData.value?.overall || smartEnergyData.value?.summary || "";
});

const smartEnergyTemperament = computed(() => {
  return smartEnergyData.value?.temperament || "";
});

const smartEnergyHealth = computed(() => {
  return smartEnergyData.value?.health || "";
});

// 智能解析雷达图数据点
const smartRadarPoints = computed(() =>
  smartEnergyItems.value.map((item, idx) => {
    const angle = radarStartAngle + radarAngleStep * idx;
    const ratio = item.score / maxSmartScore.value;
    const radius = radarRadius * ratio;
    return {
      element: item.element,
      x: radarCenter + radius * Math.cos(angle),
      y: radarCenter + radius * Math.sin(angle),
    };
  })
);

// 智能解析雷达图形状点
const smartRadarShapePoints = computed(() =>
  smartRadarPoints.value.map((point) => `${point.x.toFixed(1)},${point.y.toFixed(1)}`).join(" ")
);

// 默认模式的五行能量条目
const defaultEnergyItems = computed(() => {
  if (!props.chart) {
    return elementOrder.map((element) => ({
      element,
      count: 0,
      ratio: 0,
      description: '',
      relation: '未知',
    }));
  }

  const counts = defaultEnergyCounts.value as Record<string, number>;
  const ratios = defaultEnergyRatios.value as Record<string, number>;
  const dayElement = props.chart.day_master?.element ?? '';

  return elementOrder.map((element) => ({
    element,
    count: counts[element] ?? 0,
    ratio: ratios[element] ?? 0,
    description: '',
    relation: elementRelationMap[dayElement]?.[element] ?? '未知',
  }));
});

// 五行能量条目（兼容现有模板）
const energyItems = computed(() => {
  if (energyMode.value === 'smart') {
    return smartEnergyItems.value.map((item) => ({
      element: item.element,
      count: item.score, // 用 score 替代 count
      ratio: item.score, // 用 score 替代 ratio
      description: item.description,
      relation: item.relation,
    }));
  }

  return defaultEnergyItems.value;
});

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
const radarRadius = 150;
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

// 默认模式最大能量比率（用于归一化）
const maxEnergyRatio = computed(() => {
  const maxValue = Math.max(...defaultEnergyItems.value.map((item) => item.ratio), 0);
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
  defaultEnergyItems.value.map((item, idx) => {
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

const renderEnergySummary = (content: string) => {
  return content
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.+?)\*/g, "<em>$1</em>")
    .replace(/`(.+?)`/g, "<code>$1</code>")
    .replace(/\n/g, "<br>");
};

const DESTINY_PILLAR_MAX = 12;

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

const destinyPillarsDisplay = computed(() => {
  const maxDisplay = destinyRangeMode.value === "60" ? 6 : DESTINY_PILLAR_MAX;
  return destinyPillarsWithAge.value.slice(0, maxDisplay);
});

const currentDestinyIndex = computed(() => {
  return destinyPillarsWithAge.value.findIndex((pillar) => pillar.is_current);
});

const destinyPillarTone = (pillar: typeof destinyPillarsWithAge.value[number], index: number) => {
  if (pillar.is_current) {
    return "border-[rgba(214,160,96,0.25)] bg-[rgba(214,160,96,0.15)] shadow-[0_0px_10px_rgba(214,160,96,0.1)]";
  }

  const currentIndex = currentDestinyIndex.value;
  let isPast = false;
  if (currentIndex >= 0) {
    isPast = index < currentIndex;
  } else {
    const currentYear = new globalThis.Date().getFullYear();
    isPast = pillar.year < currentYear;
  }

  if (isPast) {
    return "border-[rgba(110,120,130,0.18)] bg-[rgba(11,11,11,0.15)] hover:border-[rgba(120,130,150,0.5)]";
  }

  return "border-[rgba(255,255,255,0.08)] bg-[rgba(255,255,255,0.03)] hover:border-[rgba(214,160,96,0.4)]";
};

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
  // 优先使用后端提供的流年柱（已按立春界限计算），保证与干支关系一致
  if (props.chart?.current_year_pillar) {
    return props.chart.current_year_pillar;
  }

  // 兜底：若后端未返回，则按公历年份估算
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
