<template>
  <teleport to="body">
    <!-- 地区选择器：模态层，打开时锁定底层滚动，并且不遮住顶部导航栏（TopNav） -->
    <div
      class="fixed inset-x-0 bottom-0 top-[calc(48px+env(safe-area-inset-top,0px))] z-[300] flex items-center justify-center bg-[rgba(7,10,16,0.8)] px-3 pt-3 pb-[calc(env(safe-area-inset-bottom,0px)+12px)] overscroll-contain md:top-[calc(56px+env(safe-area-inset-top,0px))] md:px-4 lg:top-[calc(64px+env(safe-area-inset-top,0px))] lg:px-6"
      @click.self="handleClose"
    >
      <div class="flex h-[88dvh] max-h-full w-full min-w-0 max-w-[900px] flex-col overflow-hidden rounded-[20px] border border-[rgba(255,255,255,0.15)] bg-[rgba(18,20,28,0.95)] shadow-[0_24px_60px_rgba(0,0,0,0.5)] backdrop-blur-[20px]">
        <div class="flex items-center justify-between border-b border-[rgba(255,255,255,0.1)] px-5 py-3.5">
          <div class="text-lg font-semibold text-[var(--accent-2)]">选择出生地区</div>
          <button
            class="flex h-8 w-8 items-center justify-center rounded-lg border-0 bg-[rgba(255,255,255,0.08)] text-xl text-[var(--muted)] transition-all duration-200 hover:bg-[rgba(255,255,255,0.15)] hover:text-[var(--text)]"
            type="button"
            @click="handleClose"
          >
            ×
          </button>
        </div>

        <div class="flex flex-1 min-h-0 flex-col gap-3 overflow-hidden p-4">
          <!-- 两栏选择器 -->
          <div class="grid min-h-0 flex-1 grid-cols-2 gap-2.5 max-[340px]:grid-cols-1">
            <!-- 省份列 -->
            <div class="flex min-h-0 flex-col overflow-hidden rounded-xl border border-[rgba(255,255,255,0.1)] bg-[rgba(0,0,0,0.2)]">
              <div class="border-b border-[rgba(255,255,255,0.08)] bg-[rgba(255,255,255,0.05)] px-3 py-2.5 text-[12px] font-semibold text-[var(--muted)]">
                省份/直辖市
              </div>
              <div class="flex-1 overflow-y-auto overscroll-contain p-1.5 scrollbar-thin scrollbar-thumb-white/15 scrollbar-track-black/20 [-webkit-overflow-scrolling:touch]">
                <button
                  v-for="province in provinces"
                  :key="province.name"
                  :class="[
                    'block w-full rounded-lg border-0 bg-transparent px-3 py-2 text-left text-[12px] text-[var(--text)] transition-all duration-150',
                    selectedProvince?.name === province.name
                      ? 'bg-gradient-to-br from-[rgba(214,160,96,0.3)] to-[rgba(240,192,122,0.2)] font-medium text-[var(--accent-2)]'
                      : 'hover:bg-[rgba(255,255,255,0.08)]'
                  ]"
                  type="button"
                  @click="selectProvince(province)"
                >
                  {{ province.name }}
                </button>
              </div>
            </div>

            <!-- 城市/区域列 -->
            <div class="flex min-h-0 flex-col overflow-hidden rounded-xl border border-[rgba(255,255,255,0.1)] bg-[rgba(0,0,0,0.2)]">
              <div class="border-b border-[rgba(255,255,255,0.08)] bg-[rgba(255,255,255,0.05)] px-3 py-2.5 text-[12px] font-semibold text-[var(--muted)]">
                城市/区域
              </div>
              <div class="flex-1 overflow-y-auto overscroll-contain p-1.5 scrollbar-thin scrollbar-thumb-white/15 scrollbar-track-black/20 [-webkit-overflow-scrolling:touch]">
                <button
                  v-for="city in cities"
                  :key="city.name"
                  :class="[
                    'block w-full rounded-lg border-0 bg-transparent px-3 py-2 text-left text-[12px] text-[var(--text)] transition-all duration-150',
                    selectedCity?.name === city.name
                      ? 'bg-gradient-to-br from-[rgba(214,160,96,0.3)] to-[rgba(240,192,122,0.2)] font-medium text-[var(--accent-2)]'
                      : 'hover:bg-[rgba(255,255,255,0.08)]'
                  ]"
                  type="button"
                  @click="selectCity(city)"
                >
                  {{ city.name }}
                </button>
                <div v-if="!cities.length" class="px-4 py-4 text-center text-[12px] text-[var(--muted)]">
                  请先选择省份
                </div>
              </div>
            </div>
          </div>

          <!-- 当前选择预览 -->
          <div class="rounded-xl border border-[rgba(255,255,255,0.08)] bg-[rgba(255,255,255,0.04)] px-3.5 py-3">
            <div class="mb-1.5 text-xs text-[var(--muted)]">当前选择：</div>
            <div class="text-[14px] font-medium text-[var(--text)]">{{ previewText }}</div>
            <div v-if="selectedCity" class="mt-1 text-[11px] text-[var(--muted)]">
              经度: {{ selectedCity.lng.toFixed(4) }}°，纬度: {{ selectedCity.lat.toFixed(4) }}°
            </div>
          </div>
        </div>

        <div class="flex justify-end gap-2.5 border-t border-[rgba(255,255,255,0.1)] px-4 py-3">
          <button
            class="btn-ghost"
            type="button"
            @click="handleReset"
          >
            重置为未知
          </button>
          <button
            class="btn-primary"
            type="button"
            :disabled="!canConfirm"
            @click="handleConfirm"
          >
            确定
          </button>
        </div>
      </div>
    </div>
  </teleport>
</template>

<script setup lang="ts">
import { computed, ref, watch, onMounted, onUnmounted } from "vue";
import { chinaRegions, getDefaultRegion, type Province, type City, type SelectedRegion } from "../data/china-regions";
import { lockBackgroundScroll } from "../utils/scroll-lock";

const props = defineProps<{
  modelValue: SelectedRegion;
}>();

const emit = defineEmits<{
  (e: "update:modelValue", value: SelectedRegion): void;
  (e: "close"): void;
}>();

// 省份列表
const provinces = chinaRegions;

// 选中状态
const selectedProvince = ref<Province | null>(null);
const selectedCity = ref<City | null>(null);

// 城市/区域列表（根据选中的省份）
const cities = computed(() => {
  if (!selectedProvince.value) return [];
  return selectedProvince.value.cities || [];
});

// 预览文本
const previewText = computed(() => {
  if (!selectedProvince.value) return "未选择";
  let text = selectedProvince.value.name;
  if (selectedCity.value) {
    text += selectedCity.value.name;
  }
  return text;
});

// 是否可以确认（至少选择了城市/区域）
const canConfirm = computed(() => !!selectedCity.value);

// 打开模态时锁定底层滚动（app-scroll + body/html），避免滑动穿透
let releaseScrollLock: (() => void) | null = null;

// 初始化选中状态
const initSelection = () => {
  if (props.modelValue.province) {
    const province = provinces.find((p) => p.name === props.modelValue.province);
    if (province) {
      selectedProvince.value = province;
      if (props.modelValue.city) {
        const city = province.cities?.find((c) => c.name === props.modelValue.city);
        if (city) {
          selectedCity.value = city;
        }
      }
    }
  }
};

// 选择省份
const selectProvince = (province: Province) => {
  selectedProvince.value = province;
  selectedCity.value = null;
};

// 选择城市/区域
const selectCity = (city: City) => {
  selectedCity.value = city;
};

// 重置为未知
const handleReset = () => {
  emit("update:modelValue", getDefaultRegion());
  emit("close");
};

// 确认选择
const handleConfirm = () => {
  if (!selectedProvince.value || !selectedCity.value) return;

  const result: SelectedRegion = {
    province: selectedProvince.value.name,
    city: selectedCity.value.name,
    lng: selectedCity.value.lng,
    lat: selectedCity.value.lat,
    fullName: previewText.value,
  };

  emit("update:modelValue", result);
  emit("close");
};

// 关闭
const handleClose = () => {
  emit("close");
};

// 初始化
watch(
  () => props.modelValue,
  () => initSelection(),
  { immediate: true }
);

onMounted(() => {
  releaseScrollLock = lockBackgroundScroll();
});

onUnmounted(() => {
  if (releaseScrollLock) {
    releaseScrollLock();
    releaseScrollLock = null;
  }
});
</script>
