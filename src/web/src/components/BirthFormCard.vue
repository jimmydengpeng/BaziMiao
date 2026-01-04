<template>
  <section class="form-shell">
    <div class="form-intro" v-if="showIntro">
      <div class="status-line">
        <strong>{{ title }}</strong>
        <span class="muted">{{ subtitle }}</span>
      </div>
      <p class="muted">{{ helper }}</p>
    </div>
    <div class="form-layout">
      <div class="panel form-card stack">
        <div class="field-group">
          <label>姓名</label>
          <input v-model.trim="form.name" placeholder="请输入姓名" />
        </div>
        <div class="field-row">
          <div class="field-group">
            <label>性别</label>
            <div class="segmented">
              <button
                class="segmented-btn"
                :class="{ active: form.gender === 'male' }"
                type="button"
                @click="form.gender = 'male'"
              >
                男
              </button>
              <button
                class="segmented-btn"
                :class="{ active: form.gender === 'female' }"
                type="button"
                @click="form.gender = 'female'"
              >
                女
              </button>
            </div>
          </div>
          <div class="field-group calendar-row">
            <label>历法</label>
            <div class="segmented">
              <button
                class="segmented-btn"
                :class="{ active: form.calendar === 'solar' }"
                type="button"
                @click="form.calendar = 'solar'"
              >
                公历
              </button>
              <button
                class="segmented-btn"
                :class="{ active: form.calendar === 'lunar' }"
                type="button"
                @click="form.calendar = 'lunar'"
              >
                农历
              </button>
              <button
                class="segmented-btn"
                :class="{ active: form.calendar === 'pillar' }"
                type="button"
                @click="openPillarPicker"
              >
                四柱
              </button>
            </div>
          </div>
        </div>
        <div class="field-group">
          <label>出生时间（必填）</label>
          <button class="date-display" type="button" @click="pickerOpen = !pickerOpen">
            <span>{{ displayDate }}</span>
            <span v-if="!pickerOpen" class="chevron">&gt;</span>
          </button>
        </div>
        <div v-if="pickerOpen" class="picker-overlay" role="dialog" aria-modal="true">
          <div class="panel picker-card open">
            <div class="picker-head">
              <div class="segmented">
                <button
                  class="segmented-btn"
                  :class="{ active: form.calendar === 'solar' }"
                  type="button"
                  @click="form.calendar = 'solar'"
                >
                  公历
                </button>
                <button
                  class="segmented-btn"
                  :class="{ active: form.calendar === 'lunar' }"
                  type="button"
                  @click="form.calendar = 'lunar'"
                >
                  农历
                </button>
              </div>
              <button class="btn ghost today-btn" type="button" @click="setToday">今天</button>
            </div>
            <div class="picker-grid">
              <div class="picker-column">
                <span class="picker-label">年</span>
                <select v-model.number="form.year" class="picker-select">
                  <option v-for="year in years" :key="year" :value="year">{{ year }}</option>
                </select>
              </div>
              <div class="picker-column">
                <span class="picker-label">月</span>
                <select v-model.number="form.month" class="picker-select">
                  <option v-for="month in monthOptions" :key="month.value" :value="month.value">
                    {{ month.label }}
                  </option>
                </select>
              </div>
              <div class="picker-column">
                <span class="picker-label">日</span>
                <select v-model.number="form.day" class="picker-select">
                  <option v-for="day in days" :key="day" :value="day">{{ day }}</option>
                </select>
              </div>
              <div class="picker-column">
                <span class="picker-label">时</span>
                <select v-model.number="form.hour" class="picker-select">
                  <option v-for="hour in hours" :key="hour" :value="hour">
                    {{ hour.toString().padStart(2, "0") }}
                  </option>
                </select>
              </div>
              <div class="picker-column">
                <span class="picker-label">分</span>
                <select v-model.number="form.minute" class="picker-select">
                  <option v-for="minute in minutes" :key="minute" :value="minute">
                    {{ minute.toString().padStart(2, "0") }}
                  </option>
                </select>
              </div>
            </div>
            <div v-if="isLunar" class="field-group">
              <label>闰月</label>
              <label class="check">
                <input v-model="form.isLeapMonth" type="checkbox" />
                <span>本月为闰月</span>
              </label>
            </div>
            <div class="picker-footer">
              <span class="muted picker-note">选择好后点击确定收起。</span>
              <button class="btn primary" type="button" @click="pickerOpen = false">
                确定
              </button>
            </div>
          </div>
        </div>
        <!-- 出生地点选择 -->
        <div class="field-group">
          <label>出生地点</label>
          <button class="date-display" type="button" @click="showRegionPicker = true">
            <span>{{ form.birthPlace.fullName }}</span>
            <span class="chevron">&gt;</span>
          </button>
          <span class="muted field-hint">
            选择地区后将根据经度计算真太阳时，使排盘更加精确。
          </span>
        </div>
        <div class="cta-row center">
          <button class="btn primary cta-primary" :disabled="loading" @click="handleSubmit">
            {{ loading ? "排盘中..." : "一键排盘" }}
          </button>
          <span class="muted" v-if="error">{{ error }}</span>
        </div>
      </div>
    </div>

    <!-- 地区选择器弹窗 -->
    <RegionPicker
      v-if="showRegionPicker"
      v-model="form.birthPlace"
      @close="showRegionPicker = false"
    />

    <!-- 四柱输入选择器 -->
    <PillarPicker
      v-if="showPillarPicker"
      @close="showPillarPicker = false"
      @select="handlePillarSelect"
    />
  </section>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
import RegionPicker from "./RegionPicker.vue";
import PillarPicker from "./PillarPicker.vue";
import { getDefaultRegion } from "../data/china-regions";
import type { BirthFormValues, PillarMatchedDate } from "../types/forms";
import { lunarMonthLabels } from "../types/forms";

const props = defineProps<{
  loading?: boolean;
  error?: string;
  title?: string;
  subtitle?: string;
  helper?: string;
  showIntro?: boolean;
}>();

const emit = defineEmits<{
  (e: "submit", value: BirthFormValues): void;
}>();

const form = ref<BirthFormValues>({
  name: "",
  gender: "male",
  calendar: "solar",
  year: 2000,
  month: 1,
  day: 1,
  hour: 0,
  minute: 0,
  isLeapMonth: false,
  birthPlace: getDefaultRegion()
});

const pickerOpen = ref(false);
const showRegionPicker = ref(false);
const showPillarPicker = ref(false);

const nowYear = new Date().getFullYear();
const years = Array.from({ length: nowYear - 1801 + 1 }, (_, idx) => nowYear - idx);
const hours = Array.from({ length: 24 }, (_, idx) => idx);
const minutes = Array.from({ length: 60 }, (_, idx) => idx);

const isLunar = computed(() => form.value.calendar === "lunar");

const monthOptions = computed(() =>
  Array.from({ length: 12 }, (_, idx) => {
    const value = idx + 1;
    const label =
      form.value.calendar === "lunar"
        ? `${lunarMonthLabels[idx]}`
        : `${value.toString().padStart(2, "0")}月`;
    return { value, label };
  })
);

const days = computed(() => {
  if (form.value.calendar === "lunar") {
    return Array.from({ length: 30 }, (_, idx) => idx + 1);
  }
  const lastDay = new Date(form.value.year, form.value.month, 0).getDate();
  return Array.from({ length: lastDay }, (_, idx) => idx + 1);
});

const displayDate = computed(() => {
  const year = form.value.year;
  const monthLabel =
    form.value.calendar === "lunar"
      ? `${form.value.isLeapMonth ? "闰" : ""}${lunarMonthLabels[form.value.month - 1]}`
      : form.value.month.toString().padStart(2, "0");
  const day = form.value.day.toString().padStart(2, "0");
  const hour = form.value.hour.toString().padStart(2, "0");
  const minute = form.value.minute.toString().padStart(2, "0");
  return form.value.calendar === "lunar"
    ? `${year}年 ${monthLabel} ${day}日 ${hour}:${minute}`
    : `${year}-${monthLabel}-${day} ${hour}:${minute}`;
});

watch([() => form.value.year, () => form.value.month, () => form.value.calendar], () => {
  const maxDay =
    form.value.calendar === "lunar" ? 30 : new Date(form.value.year, form.value.month, 0).getDate();
  if (form.value.day > maxDay) {
    form.value.day = maxDay;
  }
});

watch(
  () => form.value.calendar,
  (value) => {
    if (value === "solar") {
      form.value.isLeapMonth = false;
    }
  }
);

const setToday = () => {
  const now = new Date();
  form.value.calendar = "solar";
  form.value.isLeapMonth = false;
  form.value.year = now.getFullYear();
  form.value.month = now.getMonth() + 1;
  form.value.day = now.getDate();
  form.value.hour = now.getHours();
  form.value.minute = now.getMinutes();
};

const openPillarPicker = () => {
  form.value.calendar = "pillar";
  showPillarPicker.value = true;
};

const handlePillarSelect = (date: PillarMatchedDate) => {
  form.value.calendar = "solar";
  form.value.year = date.year;
  form.value.month = date.month;
  form.value.day = date.day;
  form.value.hour = date.hour;
  form.value.minute = date.minute;
  showPillarPicker.value = false;
};

const handleSubmit = () => {
  emit("submit", { ...form.value });
};

const title = computed(() => props.title || "填写生辰");
const subtitle = computed(() => props.subtitle || "仅用于排盘，不会长期存储");
const helper = computed(() => props.helper || "支持公历/农历切换，点击出生时间唤起选择器。");
const showIntro = computed(() => props.showIntro !== false);
</script>
