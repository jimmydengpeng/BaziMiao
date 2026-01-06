<template>
  <section class="flex flex-col gap-4">
    <!-- 表单介绍 -->
    <div v-if="showIntro" class="flex items-end justify-between flex-wrap gap-2">
      <div class="flex items-center gap-2 text-sm">
        <strong class="text-white">{{ title }}</strong>
        <span class="text-[var(--muted)]">{{ subtitle }}</span>
      </div>
      <p class="text-[var(--muted)] text-sm">{{ helper }}</p>
    </div>
    
    <!-- 表单卡片 -->
    <div class="flex justify-center">
      <div class="flex w-full min-w-0 max-w-[640px] flex-col gap-4 rounded-2xl border border-[rgba(255,255,255,0.08)] bg-[var(--panel)] p-5 shadow-[0_12px_40px_rgba(0,0,0,0.35)] animate-[fade-up_0.35s_ease_both]">
        <!-- 姓名 -->
        <div class="flex flex-col gap-1.5">
          <label class="block text-[13px] text-[var(--muted)]">姓名</label>
          <input
            v-model.trim="form.name"
            placeholder="请输入姓名"
            class="w-full rounded-[14px] border border-[rgba(255,255,255,0.08)] bg-[#0d1626] px-3.5 py-3 text-[15px] text-[var(--text)] outline-none transition-colors focus:border-[rgba(255,255,255,0.2)]"
          />
        </div>
        
        <!-- 性别和历法 -->
        <div class="flex flex-wrap gap-3 items-end">
          <div class="flex flex-1 min-w-[220px] flex-col gap-1.5">
            <label class="block text-[13px] text-[var(--muted)]">性别</label>
            <div class="inline-flex gap-2 rounded-xl border border-[rgba(255,255,255,0.08)] bg-[#0f1421] p-1.5">
              <button
                :class="[
                  'flex-1 rounded-[10px] border border-transparent bg-transparent px-4 py-1.5 text-sm transition-all duration-200',
                  form.gender === 'male'
                    ? 'border-[rgba(255,255,255,0.2)] bg-gradient-to-br from-[var(--accent)] to-[var(--accent-2)] text-[#0a0d12] font-semibold shadow-sm'
                    : 'text-[var(--muted)] hover:bg-white/5'
                ]"
                type="button"
                @click="form.gender = 'male'"
              >
                男
              </button>
              <button
                :class="[
                  'flex-1 rounded-[10px] border border-transparent bg-transparent px-4 py-1.5 text-sm transition-all duration-200',
                  form.gender === 'female'
                    ? 'border-[rgba(255,255,255,0.2)] bg-gradient-to-br from-[var(--accent)] to-[var(--accent-2)] text-[#0a0d12] font-semibold shadow-sm'
                    : 'text-[var(--muted)] hover:bg-white/5'
                ]"
                type="button"
                @click="form.gender = 'female'"
              >
                女
              </button>
            </div>
          </div>
          <div class="flex flex-1 min-w-[220px] flex-col gap-1.5">
            <label class="block text-[13px] text-[var(--muted)]">历法</label>
            <div class="inline-flex gap-2 rounded-xl border border-[rgba(255,255,255,0.08)] bg-[#0f1421] p-1.5">
              <button
                :class="[
                  'flex-1 rounded-[10px] border border-transparent bg-transparent px-4 py-1.5 text-sm transition-all duration-200',
                  form.calendar === 'solar'
                    ? 'border-[rgba(255,255,255,0.2)] bg-gradient-to-br from-[var(--accent)] to-[var(--accent-2)] text-[#0a0d12] font-semibold shadow-sm'
                    : 'text-[var(--muted)] hover:bg-white/5'
                ]"
                type="button"
                @click="form.calendar = 'solar'"
              >
                公历
              </button>
              <button
                :class="[
                  'flex-1 rounded-[10px] border border-transparent bg-transparent px-4 py-1.5 text-sm transition-all duration-200',
                  form.calendar === 'lunar'
                    ? 'border-[rgba(255,255,255,0.2)] bg-gradient-to-br from-[var(--accent)] to-[var(--accent-2)] text-[#0a0d12] font-semibold shadow-sm'
                    : 'text-[var(--muted)] hover:bg-white/5'
                ]"
                type="button"
                @click="form.calendar = 'lunar'"
              >
                农历
              </button>
              <button
                :class="[
                  'flex-1 rounded-[10px] border border-transparent bg-transparent px-4 py-1.5 text-sm transition-all duration-200',
                  form.calendar === 'pillar'
                    ? 'border-[rgba(255,255,255,0.2)] bg-gradient-to-br from-[var(--accent)] to-[var(--accent-2)] text-[#0a0d12] font-semibold shadow-sm'
                    : 'text-[var(--muted)] hover:bg-white/5'
                ]"
                type="button"
                @click="openPillarPicker"
              >
                四柱
              </button>
            </div>
          </div>
        </div>
        
        <!-- 出生时间 -->
        <div class="flex flex-col gap-1.5">
          <label class="block text-[13px] text-[var(--muted)]">出生时间（必填）</label>
          <button
            class="flex w-full items-center justify-between gap-3 rounded-[14px] border border-[rgba(255,255,255,0.08)] bg-[rgba(15,24,40,0.9)] px-3.5 py-3 text-left text-[15px] text-[var(--text)] transition-all duration-200 hover:border-[rgba(255,255,255,0.2)] hover:-translate-y-[1px]"
            type="button"
            @click="pickerOpen = !pickerOpen"
          >
            <span>{{ displayDate }}</span>
            <span v-if="!pickerOpen" class="text-[var(--muted)] text-lg">&gt;</span>
          </button>
        </div>
        
        <!-- 时间选择器弹窗 -->
        <div
          v-if="pickerOpen"
          class="fixed inset-0 z-[200] flex items-center justify-center bg-[rgba(7,10,16,0.72)] p-5"
          role="dialog"
          aria-modal="true"
          @click.self="pickerOpen = false"
        >
          <div class="flex w-full max-w-[720px] flex-col gap-4 rounded-2xl border border-[rgba(255,255,255,0.08)] bg-[rgba(15,24,40,0.65)] p-5 shadow-[0_22px_60px_rgba(0,0,0,0.6)] backdrop-blur-xl">
            <!-- 选择器头部 -->
            <div class="flex items-center justify-between gap-3">
              <div class="inline-flex gap-2 rounded-xl border border-[rgba(255,255,255,0.08)] bg-[#0f1421] p-1.5">
                <button
                  :class="[
                    'rounded-[10px] border border-transparent bg-transparent px-4 py-1.5 text-sm transition-all duration-200',
                    form.calendar === 'solar'
                      ? 'border-[rgba(255,255,255,0.2)] bg-gradient-to-br from-[var(--accent)] to-[var(--accent-2)] text-[#0a0d12] font-semibold shadow-sm'
                      : 'text-[var(--muted)] hover:bg-white/5'
                  ]"
                  type="button"
                  @click="form.calendar = 'solar'"
                >
                  公历
                </button>
                <button
                  :class="[
                    'rounded-[10px] border border-transparent bg-transparent px-4 py-1.5 text-sm transition-all duration-200',
                    form.calendar === 'lunar'
                      ? 'border-[rgba(255,255,255,0.2)] bg-gradient-to-br from-[var(--accent)] to-[var(--accent-2)] text-[#0a0d12] font-semibold shadow-sm'
                      : 'text-[var(--muted)] hover:bg-white/5'
                  ]"
                  type="button"
                  @click="form.calendar = 'lunar'"
                >
                  农历
                </button>
              </div>
              <button
                class="rounded-[10px] border border-[rgba(255,255,255,0.08)] bg-[rgba(255,255,255,0.06)] px-3 py-1.5 text-xs font-semibold text-[var(--text)] transition-all duration-200 hover:bg-[rgba(255,255,255,0.1)]"
                type="button"
                @click="setToday"
              >
                今天
              </button>
            </div>
            
            <!-- 选择器网格 -->
            <div class="grid grid-cols-[repeat(auto-fit,minmax(88px,1fr))] gap-3">
              <div class="flex flex-col gap-2">
                <span class="text-xs uppercase tracking-wider text-[var(--muted)]">年</span>
                <select
                  v-model.number="form.year"
                  class="w-full rounded-[14px] border border-[rgba(255,255,255,0.08)] bg-[#0d1626] px-2.5 py-3 text-[15px] text-[var(--text)] outline-none transition-colors focus:border-[rgba(255,255,255,0.2)]"
                >
                  <option v-for="year in years" :key="year" :value="year">{{ year }}</option>
                </select>
              </div>
              <div class="flex flex-col gap-2">
                <span class="text-xs uppercase tracking-wider text-[var(--muted)]">月</span>
                <select
                  v-model.number="form.month"
                  class="w-full rounded-[14px] border border-[rgba(255,255,255,0.08)] bg-[#0d1626] px-2.5 py-3 text-[15px] text-[var(--text)] outline-none transition-colors focus:border-[rgba(255,255,255,0.2)]"
                >
                  <option v-for="month in monthOptions" :key="month.value" :value="month.value">
                    {{ month.label }}
                  </option>
                </select>
              </div>
              <div class="flex flex-col gap-2">
                <span class="text-xs uppercase tracking-wider text-[var(--muted)]">日</span>
                <select
                  v-model.number="form.day"
                  class="w-full rounded-[14px] border border-[rgba(255,255,255,0.08)] bg-[#0d1626] px-2.5 py-3 text-[15px] text-[var(--text)] outline-none transition-colors focus:border-[rgba(255,255,255,0.2)]"
                >
                  <option v-for="day in days" :key="day" :value="day">{{ day }}</option>
                </select>
              </div>
              <div class="flex flex-col gap-2">
                <span class="text-xs uppercase tracking-wider text-[var(--muted)]">时</span>
                <select
                  v-model.number="form.hour"
                  class="w-full rounded-[14px] border border-[rgba(255,255,255,0.08)] bg-[#0d1626] px-2.5 py-3 text-[15px] text-[var(--text)] outline-none transition-colors focus:border-[rgba(255,255,255,0.2)]"
                >
                  <option v-for="hour in hours" :key="hour" :value="hour">
                    {{ hour.toString().padStart(2, "0") }}
                  </option>
                </select>
              </div>
              <div class="flex flex-col gap-2">
                <span class="text-xs uppercase tracking-wider text-[var(--muted)]">分</span>
                <select
                  v-model.number="form.minute"
                  class="w-full rounded-[14px] border border-[rgba(255,255,255,0.08)] bg-[#0d1626] px-2.5 py-3 text-[15px] text-[var(--text)] outline-none transition-colors focus:border-[rgba(255,255,255,0.2)]"
                >
                  <option v-for="minute in minutes" :key="minute" :value="minute">
                    {{ minute.toString().padStart(2, "0") }}
                  </option>
                </select>
              </div>
            </div>
            
            <!-- 闰月选项 -->
            <div v-if="isLunar" class="flex flex-col gap-1.5">
              <label class="block text-[13px] text-[var(--muted)]">闰月</label>
              <label class="inline-flex items-center gap-2 rounded-xl border border-[rgba(255,255,255,0.08)] bg-[#0f1421] px-3 py-2.5 text-sm text-[var(--text)]">
                <input
                  v-model="form.isLeapMonth"
                  type="checkbox"
                  class="accent-[var(--accent-2)]"
                />
                <span>本月为闰月</span>
              </label>
            </div>
            
            <!-- 选择器底部 -->
            <div class="flex items-center justify-between gap-3">
              <span class="text-xs text-[var(--muted)]">选择好后点击确定收起。</span>
              <button
                class="rounded-xl border-none bg-gradient-to-br from-[var(--accent)] to-[var(--accent-2)] px-4 py-2.5 font-semibold text-[#0c0f15] transition-all duration-200 hover:-translate-y-[1px]"
                type="button"
                @click="pickerOpen = false"
              >
                确定
              </button>
            </div>
          </div>
        </div>
        
        <!-- 出生地点 -->
        <div class="flex flex-col gap-1.5">
          <label class="block text-[13px] text-[var(--muted)]">出生地点</label>
          <button
            class="flex w-full items-center justify-between gap-3 rounded-[14px] border border-[rgba(255,255,255,0.08)] bg-[rgba(15,24,40,0.9)] px-3.5 py-3 text-left text-[15px] text-[var(--text)] transition-all duration-200 hover:border-[rgba(255,255,255,0.2)] hover:-translate-y-[1px]"
            type="button"
            @click="showRegionPicker = true"
          >
            <span>{{ form.birthPlace.fullName }}</span>
            <span class="text-[var(--muted)] text-lg">&gt;</span>
          </button>
          <span class="mt-2 block text-xs text-[var(--muted)] opacity-70">
            选择地区后将根据经度计算真太阳时，使排盘更加精确。
          </span>
        </div>
        
        <!-- 提交按钮 -->
        <div class="flex flex-wrap items-center justify-center gap-4">
          <button
            :class="[
              'min-w-[220px] rounded-xl border-none bg-gradient-to-br from-[var(--accent)] to-[var(--accent-2)] px-8 py-3 font-semibold text-[#0c0f15] shadow-[0_14px_30px_rgba(0,0,0,0.35)] transition-all duration-200 hover:-translate-y-[1px] hover:shadow-[0_16px_34px_rgba(0,0,0,0.4)] disabled:opacity-50 disabled:cursor-not-allowed',
              loading ? 'cursor-wait' : ''
            ]"
            :disabled="loading"
            @click="handleSubmit"
          >
            {{ loading ? "排盘中..." : "一键排盘" }}
          </button>
          <span v-if="error" class="text-sm text-[var(--muted)]">{{ error }}</span>
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
      @close="handlePillarClose"
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
const previousCalendar = ref<"solar" | "lunar">("solar"); // 保存打开四柱选择器前的历法状态

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
  // 记住进入四柱模式前的历法，关闭时恢复，避免提交时 calendar 留在 pillar
  previousCalendar.value = form.value.calendar === "lunar" ? "lunar" : "solar";
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

const handlePillarClose = () => {
  showPillarPicker.value = false;
  if (form.value.calendar === "pillar") {
    form.value.calendar = previousCalendar.value;
  }
};

const handleSubmit = () => {
  emit("submit", { ...form.value });
};

const title = computed(() => props.title || "填写生辰");
const subtitle = computed(() => props.subtitle || "仅用于排盘，不会长期存储");
const helper = computed(() => props.helper || "支持公历/农历切换，点击出生时间唤起选择器。");
const showIntro = computed(() => props.showIntro !== false);
</script>
