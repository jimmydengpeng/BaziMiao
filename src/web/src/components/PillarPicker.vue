<template>
  <div class="picker-overlay" @click.self="$emit('close')">
    <div class="panel picker-card open pillar-picker">
      <div class="picker-head">
        <div class="pillar-title">输入四柱八字</div>
        <button class="btn ghost" type="button" @click="$emit('close')">关闭</button>
      </div>

      <!-- 当前选择的步骤说明 -->
      <div class="pillar-progress">
        <div class="progress-text">
          <span class="progress-step">步骤 {{ Math.min(currentStep + 1, 8) }}/8</span>
          <span class="progress-hint">{{ stepHints[Math.min(currentStep, 7)] }}</span>
        </div>
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: `${Math.min(currentStep / 8, 1) * 100}%` }"></div>
        </div>
      </div>

      <!-- 已选择的四柱预览 -->
      <div class="pillar-preview">
        <div
          v-for="(pillar, idx) in pillars"
          :key="idx"
          class="preview-pillar"
          :class="{ active: Math.floor(currentStep / 2) === idx }"
        >
          <div class="preview-label">{{ pillarLabels[idx] }}</div>
          <div class="preview-chars">
            <span
              class="preview-char"
              :class="[pillar.stem ? getElementClass(pillar.stem) : 'empty']"
            >
              {{ pillar.stem || "?" }}
            </span>
            <span
              class="preview-char"
              :class="[pillar.branch ? getElementClass(pillar.branch) : 'empty']"
            >
              {{ pillar.branch || "?" }}
            </span>
          </div>
        </div>
      </div>

      <!-- 选择区域 -->
      <div class="pillar-selection">
        <div class="selection-title">
          {{ isSelectingStem ? "选择天干" : "选择地支" }}
        </div>
        <div class="selection-grid" :class="{ 'grid-branches': !isSelectingStem }">
          <button
            v-for="item in availableOptions"
            :key="item"
            type="button"
            class="selection-btn"
            :class="getElementClass(item)"
            @click="selectItem(item)"
          >
            {{ item }}
          </button>
        </div>
      </div>

      <!-- 操作按钮 -->
      <div class="picker-footer">
        <button
          class="btn secondary"
          type="button"
          :disabled="currentStep === 0"
          @click="goBack"
        >
          上一步
        </button>
        <button
          class="btn secondary"
          type="button"
          @click="reset"
        >
          重置
        </button>
        <button
          v-if="isComplete"
          class="btn primary"
          type="button"
          :disabled="loading"
          @click="findDates"
        >
          {{ loading ? "查找中..." : "查找日期" }}
        </button>
      </div>

      <!-- 查找进度 -->
      <div v-if="searchProgress" class="search-progress">
        {{ searchProgress }}
      </div>

      <!-- 查找结果 -->
      <div v-if="matchedDates.length > 0" class="matched-dates">
        <div class="matched-title">找到 {{ matchedDates.length }} 个匹配的日期</div>
        <div class="matched-list">
          <button
            v-for="(date, idx) in matchedDates"
            :key="idx"
            type="button"
            class="date-option"
            @click="selectDate(date)"
          >
            <div class="date-main">{{ formatDate(date) }}</div>
            <div class="date-lunar">{{ date.lunar_display }}</div>
          </button>
        </div>
      </div>

      <!-- 错误信息 -->
      <div v-if="error" class="pillar-error">{{ error }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";

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
.pillar-picker {
  width: min(780px, 100%);
  max-height: 85vh;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.pillar-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--accent-2);
}

.pillar-progress {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 14px 16px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border);
}

.progress-text {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  font-size: 13px;
}

.progress-step {
  font-weight: 600;
  color: var(--accent-2);
}

.progress-hint {
  color: var(--muted);
}

.progress-bar {
  height: 6px;
  border-radius: 3px;
  background: rgba(255, 255, 255, 0.08);
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--accent), var(--accent-2));
  border-radius: 3px;
  transition: width 0.3s ease;
}

.pillar-preview {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.preview-pillar {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 12px 8px;
  border-radius: 12px;
  border: 2px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.02);
  transition: all 0.3s ease;
}

.preview-pillar.active {
  border-color: var(--accent);
  background: rgba(214, 160, 96, 0.1);
}

.preview-label {
  font-size: 12px;
  color: var(--muted);
  letter-spacing: 1px;
}

.preview-chars {
  display: flex;
  flex-direction: column;
  gap: 4px;
  align-items: center;
}

.preview-char {
  font-size: 28px;
  font-weight: 700;
  letter-spacing: 1px;
  min-width: 40px;
  text-align: center;
}

.preview-char.empty {
  color: rgba(255, 255, 255, 0.15);
}

.pillar-selection {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border);
}

.selection-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--accent-2);
  text-align: center;
}

.selection-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 10px;
  /* 固定最小高度，确保单排和双排时高度一致，避免卡片跳动 */
  min-height: 180px;
  align-content: start;
}

.selection-grid.grid-branches {
  grid-template-columns: repeat(6, 1fr);
}

.selection-btn {
  padding: 16px 12px;
  border-radius: 12px;
  border: 2px solid var(--border);
  background: rgba(255, 255, 255, 0.04);
  color: var(--text);
  font-size: 24px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
}

.selection-btn:hover {
  transform: translateY(-2px);
  border-color: var(--accent);
  box-shadow: 0 8px 20px rgba(214, 160, 96, 0.3);
}

.matched-dates {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px;
  border-radius: 12px;
  background: rgba(125, 213, 111, 0.08);
  border: 1px solid rgba(125, 213, 111, 0.3);
}

.matched-title {
  font-size: 15px;
  font-weight: 600;
  color: #7dd56f;
  text-align: center;
}

.matched-list {
  display: grid;
  gap: 8px;
  max-height: 240px;
  overflow-y: auto;
}

.date-option {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 4px;
  padding: 12px 14px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: rgba(255, 255, 255, 0.04);
  color: var(--text);
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: left;
}

.date-option:hover {
  border-color: var(--accent);
  background: rgba(214, 160, 96, 0.1);
  transform: translateX(4px);
}

.date-main {
  font-size: 15px;
  font-weight: 600;
  color: var(--accent-2);
}

.date-lunar {
  font-size: 12px;
  color: var(--muted);
}

.search-progress {
  padding: 12px 14px;
  border-radius: 10px;
  background: rgba(90, 169, 255, 0.15);
  border: 1px solid rgba(90, 169, 255, 0.3);
  color: #5aa9ff;
  font-size: 13px;
  text-align: center;
}

.pillar-error {
  padding: 12px 14px;
  border-radius: 10px;
  background: rgba(255, 107, 107, 0.15);
  border: 1px solid rgba(255, 107, 107, 0.3);
  color: #ff6b6b;
  font-size: 13px;
  text-align: center;
}

@media (max-width: 680px) {
  .pillar-preview {
    grid-template-columns: repeat(2, 1fr);
  }

  .selection-grid {
    grid-template-columns: repeat(4, 1fr);
    /* 移动端也保持固定高度，但稍小一些 */
    min-height: 200px;
  }

  .selection-grid.grid-branches {
    grid-template-columns: repeat(4, 1fr);
  }

  .preview-char {
    font-size: 24px;
  }

  .selection-btn {
    font-size: 20px;
    padding: 14px 10px;
  }
}
</style>

