<template>
  <teleport to="body">
    <div
      class="fixed inset-0 z-[230] flex items-center justify-center bg-[rgba(7,10,16,0.72)] px-4 pt-4 pb-[calc(env(safe-area-inset-bottom,0px)+12px)] overscroll-contain"
      role="dialog"
      aria-modal="true"
      @click.self="$emit('close')"
    >
      <div class="flex w-full max-w-[720px] flex-col gap-4 rounded-2xl border border-[rgba(255,255,255,0.08)] bg-[rgba(15,24,40,0.65)] p-5 shadow-[0_22px_60px_rgba(0,0,0,0.6)] backdrop-blur-xl">
        <div class="relative flex items-center justify-center">
          <div class="text-lg font-semibold text-[var(--text)]">输入四柱八字</div>
          <div class="absolute right-0 top-1/2 -translate-y-1/2">
            <CloseIconButton @click="$emit('close')" />
          </div>
        </div>

      <!-- 当前选择的步骤说明 -->
      <div class="flex flex-col gap-2">
        <div class="flex items-center justify-between text-sm">
          <span class="font-semibold text-[var(--text)]">步骤 {{ Math.min(currentStep + 1, 8) }}/8</span>
          <span class="text-[var(--muted)]">{{ stepHints[Math.min(currentStep, 7)] }}</span>
        </div>
        <div class="h-2 overflow-hidden rounded-full bg-[rgba(255,255,255,0.08)]">
          <div
            class="h-full rounded-full bg-gradient-to-r from-[var(--accent)] to-[var(--accent-2)] transition-[width] duration-300"
            :style="{ width: `${Math.min(currentStep / 8, 1) * 100}%` }"
          ></div>
        </div>
      </div>

      <!-- 已选择的四柱预览 -->
      <div class="grid grid-cols-4 gap-3">
        <div
          v-for="(pillar, idx) in pillars"
          :key="idx"
          :class="[
            'flex flex-col items-center gap-2 rounded-xl border border-[rgba(255,255,255,0.08)] bg-[rgba(255,255,255,0.03)] p-3 transition-all duration-200',
            Math.floor(currentStep / 2) === idx
              ? 'border-[rgba(214,160,96,0.4)] bg-[rgba(214,160,96,0.1)]'
              : ''
          ]"
        >
          <div class="text-xs text-[var(--muted)]">{{ pillarLabels[idx] }}</div>
          <div class="flex flex-col gap-1">
            <span
              :class="[
                'flex h-12 w-12 items-center justify-center rounded-lg text-2xl font-bold',
                pillar.stem ? getElementClass(pillar.stem) : 'bg-[rgba(255,255,255,0.05)] text-[var(--muted)]'
              ]"
            >
              {{ pillar.stem || "?" }}
            </span>
            <span
              :class="[
                'flex h-12 w-12 items-center justify-center rounded-lg text-2xl font-bold',
                pillar.branch ? getElementClass(pillar.branch) : 'bg-[rgba(255,255,255,0.05)] text-[var(--muted)]'
              ]"
            >
              {{ pillar.branch || "?" }}
            </span>
          </div>
        </div>
      </div>

      <!-- 选择区域 -->
      <div class="flex flex-col gap-3">
        <div class="text-sm font-semibold text-[var(--text)]">
          {{ isSelectingStem ? "选择天干" : "选择地支" }}
        </div>
        <div :class="['grid gap-2', !isSelectingStem ? 'grid-cols-4' : 'grid-cols-5']">
          <button
            v-for="item in availableOptions"
            :key="item"
            type="button"
            :class="[
              'rounded-xl border border-[rgba(255,255,255,0.08)] bg-[rgba(255,255,255,0.03)] px-4 py-3 text-lg font-bold transition-all duration-200 hover:border-[rgba(255,255,255,0.2)] hover:bg-[rgba(255,255,255,0.08)]',
              getElementClass(item)
            ]"
            @click="selectItem(item)"
          >
            {{ item }}
          </button>
        </div>
      </div>

      <!-- 操作按钮 -->
      <div class="flex items-center justify-between gap-3">
        <button
          class="rounded-xl border border-[rgba(255,255,255,0.1)] bg-[rgba(18,20,30,0.72)] px-4 py-2.5 font-semibold text-[#f3e4c8] transition-all duration-200 hover:bg-[rgba(255,255,255,0.08)] disabled:opacity-50 disabled:cursor-not-allowed"
          type="button"
          :disabled="currentStep === 0"
          @click="goBack"
        >
          上一步
        </button>
        <button
          class="rounded-xl border border-[rgba(255,255,255,0.1)] bg-[rgba(18,20,30,0.72)] px-4 py-2.5 font-semibold text-[#f3e4c8] transition-all duration-200 hover:bg-[rgba(255,255,255,0.08)]"
          type="button"
          @click="reset"
        >
          重置
        </button>
        <button
          v-if="isComplete"
          class="btn-primary"
          type="button"
          :disabled="loading"
          @click="findDates"
        >
          {{ loading ? "查找中..." : "查找日期" }}
        </button>
      </div>

      <!-- 查找进度 -->
      <div v-if="searchProgress" class="rounded-lg border border-[rgba(255,255,255,0.08)] bg-[rgba(255,255,255,0.04)] px-4 py-3 text-sm text-[var(--text)]">
        {{ searchProgress }}
      </div>

      <!-- 查找结果 -->
      <div v-if="matchedDates.length > 0" class="flex flex-col gap-3">
        <div class="text-base font-semibold text-[var(--text)]">找到 {{ matchedDates.length }} 个匹配的日期</div>
        <div class="grid grid-cols-1 gap-2 max-h-[300px] overflow-y-auto scrollbar-thin scrollbar-thumb-white/15 scrollbar-track-black/20">
          <button
            v-for="(date, idx) in matchedDates"
            :key="idx"
            type="button"
            class="rounded-xl border border-[rgba(255,255,255,0.08)] bg-[rgba(255,255,255,0.03)] px-4 py-3 text-left transition-all duration-200 hover:border-[rgba(214,160,96,0.4)] hover:bg-[rgba(214,160,96,0.1)]"
            @click="selectDate(date)"
          >
            <div class="text-[15px] font-medium text-[var(--text)]">{{ formatDate(date) }}</div>
            <div class="mt-1 text-xs text-[var(--muted)]">{{ date.lunar_display }}</div>
          </button>
        </div>
      </div>

      <!-- 错误信息 -->
      <div v-if="error" class="rounded-lg border border-[rgba(200,16,46,0.3)] bg-[rgba(200,16,46,0.1)] px-4 py-3 text-sm text-[var(--accent-red)]">
        {{ error }}
      </div>
      </div>
    </div>
  </teleport>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from "vue";
import CloseIconButton from "./CloseIconButton.vue";
import { lockBackgroundScroll } from "../utils/scroll-lock";

// 十天干和十二地支
const TIAN_GAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"];
const DI_ZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"];

// 阳干阳支、阴干阴支配对规则
const YANG_GAN = ["甲", "丙", "戊", "庚", "壬"]; // 阳干
const YIN_GAN = ["乙", "丁", "己", "辛", "癸"]; // 阴干
const YANG_ZHI = ["子", "寅", "辰", "午", "申", "戌"]; // 阳支
const YIN_ZHI = ["丑", "卯", "巳", "未", "酉", "亥"]; // 阴支

// 五行映射（用于着色）
const ELEMENT_MAP: Record<string, string> = {
  甲: "wood", 乙: "wood",
  丙: "fire", 丁: "fire",
  戊: "earth", 己: "earth",
  庚: "metal", 辛: "metal",
  壬: "water", 癸: "water",
  子: "water", 丑: "earth",
  寅: "wood", 卯: "wood",
  辰: "earth", 巳: "fire",
  午: "fire", 未: "earth",
  申: "metal", 酉: "metal",
  戌: "earth", 亥: "water",
};

interface Pillar {
  stem: string;
  branch: string;
}

interface MatchedDate {
  year: number;
  month: number;
  day: number;
  hour: number;
  minute: number;
  lunar_display: string;
}

const emit = defineEmits<{
  close: [];
  select: [date: MatchedDate];
}>();

const currentStep = ref(0); // 0-8: 0表示第1步，7表示第8步，8表示所有步骤完成
const pillars = ref<Pillar[]>([
  { stem: "", branch: "" },
  { stem: "", branch: "" },
  { stem: "", branch: "" },
  { stem: "", branch: "" },
]);

const pillarLabels = ["年柱", "月柱", "日柱", "时柱"];
const stepHints = [
  "请选择年柱的天干",
  "请选择年柱的地支",
  "请选择月柱的天干",
  "请选择月柱的地支",
  "请选择日柱的天干",
  "请选择日柱的地支",
  "请选择时柱的天干",
  "请选择时柱的地支",
];

const loading = ref(false);
const error = ref("");
const matchedDates = ref<MatchedDate[]>([]);
const searchProgress = ref("");  // 查找进度信息

let releaseScrollLock: (() => void) | null = null;

onMounted(() => {
  releaseScrollLock = lockBackgroundScroll();
});

onUnmounted(() => {
  if (releaseScrollLock) {
    releaseScrollLock();
    releaseScrollLock = null;
  }
});

// 当前是否在选择天干（偶数步骤选天干，奇数步骤选地支）
const isSelectingStem = computed(() => currentStep.value % 2 === 0);

// 当前可选的选项
const availableOptions = computed(() => {
  if (isSelectingStem.value) {
    // 选择天干，所有天干都可选
    return TIAN_GAN;
  } else {
    // 选择地支，根据刚选的天干决定阴阳
    const pillarIndex = Math.floor(currentStep.value / 2);
    const selectedStem = pillars.value[pillarIndex].stem;
    if (!selectedStem) return DI_ZHI;

    // 阳干配阳支，阴干配阴支
    if (YANG_GAN.includes(selectedStem)) {
      return YANG_ZHI;
    } else if (YIN_GAN.includes(selectedStem)) {
      return YIN_ZHI;
    }
    return DI_ZHI;
  }
});

// 是否已完成所有选择
const isComplete = computed(() => {
  return pillars.value.every((p) => p.stem && p.branch);
});

// 选择一个天干或地支
const selectItem = (item: string) => {
  const pillarIndex = Math.floor(currentStep.value / 2);
  if (isSelectingStem.value) {
    pillars.value[pillarIndex].stem = item;
  } else {
    pillars.value[pillarIndex].branch = item;
  }

  // 自动进入下一步（包括最后一步也要递增）
  if (currentStep.value < 8) {
    currentStep.value++;
  }
};

// 返回上一步
const goBack = () => {
  if (currentStep.value > 0) {
    // 要撤销的是上一步（currentStep - 1）的选择
    const prevStep = currentStep.value - 1;
    const pillarIndex = Math.floor(prevStep / 2);
    const shouldResetStem = prevStep % 2 === 0;
    
    if (shouldResetStem) {
      pillars.value[pillarIndex].stem = "";
    } else {
      pillars.value[pillarIndex].branch = "";
    }
    
    // 减少步骤
    currentStep.value--;
  }
};

// 重置所有选择
const reset = () => {
  currentStep.value = 0;
  pillars.value = [
    { stem: "", branch: "" },
    { stem: "", branch: "" },
    { stem: "", branch: "" },
    { stem: "", branch: "" },
  ];
  matchedDates.value = [];
  error.value = "";
  searchProgress.value = "";
};

// 获取五行对应的CSS类
const getElementClass = (char: string) => {
  const element = ELEMENT_MAP[char];
  return element ? `element-${element}` : "";
};

// 查找匹配的日期
const findDates = async () => {
  const startYear = 1801;
  const endYear = 2099;
  
  loading.value = true;
  error.value = "";
  matchedDates.value = [];
  searchProgress.value = `正在查找 ${startYear}-${endYear} 年范围内的匹配日期...`;

  try {
    const response = await fetch("/api/bazi/find-dates-by-pillars", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        year_pillar: pillars.value[0].stem + pillars.value[0].branch,
        month_pillar: pillars.value[1].stem + pillars.value[1].branch,
        day_pillar: pillars.value[2].stem + pillars.value[2].branch,
        hour_pillar: pillars.value[3].stem + pillars.value[3].branch,
        start_year: startYear,
        end_year: endYear,
      }),
    });

    if (!response.ok) {
      throw new Error(await response.text());
    }

    const data = await response.json();
    matchedDates.value = data.matched_dates || [];

    if (matchedDates.value.length === 0) {
      error.value = `在 ${startYear}-${endYear} 年范围内未找到匹配的日期`;
    } else {
      searchProgress.value = `在 ${startYear}-${endYear} 年范围内找到 ${matchedDates.value.length} 个匹配日期`;
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : String(err);
    searchProgress.value = "";
  } finally {
    loading.value = false;
  }
};

// 格式化日期显示
const formatDate = (date: MatchedDate) => {
  const year = date.year;
  const month = String(date.month).padStart(2, "0");
  const day = String(date.day).padStart(2, "0");
  const hour = String(date.hour).padStart(2, "0");
  const minute = String(date.minute).padStart(2, "0");
  return `${year}-${month}-${day} ${hour}:${minute}`;
};

// 选择一个日期
const selectDate = (date: MatchedDate) => {
  emit("select", date);
  emit("close");
};
</script>

<style scoped>
/* 所有样式已迁移到 Tailwind CSS，五行元素类在 main.css 中定义 */
</style>
