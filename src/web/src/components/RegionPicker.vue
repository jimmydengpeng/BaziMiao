<template>
  <div class="fixed inset-0 z-[300] flex items-center justify-center bg-[rgba(7,10,16,0.8)] p-5" @click.self="handleClose">
    <div class="flex h-[80vh] w-full min-w-0 max-w-[900px] flex-col overflow-hidden rounded-[20px] border border-[rgba(255,255,255,0.15)] bg-[rgba(18,20,28,0.95)] shadow-[0_24px_60px_rgba(0,0,0,0.5)] backdrop-blur-[20px]">
      <div class="flex items-center justify-between border-b border-[rgba(255,255,255,0.1)] px-6 py-4.5">
        <div class="text-lg font-semibold text-[var(--accent-2)]">选择出生地区</div>
        <button
          class="flex h-8 w-8 items-center justify-center rounded-lg border-0 bg-[rgba(255,255,255,0.08)] text-xl text-[var(--muted)] transition-all duration-200 hover:bg-[rgba(255,255,255,0.15)] hover:text-[var(--text)]"
          type="button"
          @click="handleClose"
        >
          ×
        </button>
      </div>

      <div class="flex flex-1 min-h-0 flex-col gap-4 overflow-hidden p-6">
        <!-- 两栏选择器 -->
        <div class="grid min-h-0 flex-1 grid-cols-1 gap-3 lg:grid-cols-2">
          <!-- 省份列 -->
          <div class="flex min-h-0 flex-col overflow-hidden rounded-xl border border-[rgba(255,255,255,0.1)] bg-[rgba(0,0,0,0.2)]">
            <div class="border-b border-[rgba(255,255,255,0.08)] bg-[rgba(255,255,255,0.05)] px-3.5 py-3 text-[13px] font-semibold text-[var(--muted)]">
              省份/直辖市
            </div>
            <div class="flex-1 overflow-y-auto p-2 scrollbar-thin scrollbar-thumb-white/15 scrollbar-track-black/20">
              <button
                v-for="province in provinces"
                :key="province.name"
                :class="[
                  'block w-full rounded-lg border-0 bg-transparent px-3 py-2.5 text-left text-[13px] text-[var(--text)] transition-all duration-150',
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
            <div class="border-b border-[rgba(255,255,255,0.08)] bg-[rgba(255,255,255,0.05)] px-3.5 py-3 text-[13px] font-semibold text-[var(--muted)]">
              城市/区域
            </div>
            <div class="flex-1 overflow-y-auto p-2 scrollbar-thin scrollbar-thumb-white/15 scrollbar-track-black/20">
              <button
                v-for="city in cities"
                :key="city.name"
                :class="[
                  'block w-full rounded-lg border-0 bg-transparent px-3 py-2.5 text-left text-[13px] text-[var(--text)] transition-all duration-150',
                  selectedCity?.name === city.name
                    ? 'bg-gradient-to-br from-[rgba(214,160,96,0.3)] to-[rgba(240,192,122,0.2)] font-medium text-[var(--accent-2)]'
                    : 'hover:bg-[rgba(255,255,255,0.08)]'
                ]"
                type="button"
                @click="selectCity(city)"
              >
                {{ city.name }}
              </button>
              <div v-if="!cities.length" class="px-5 py-5 text-center text-[13px] text-[var(--muted)]">
                请先选择省份
              </div>
            </div>
          </div>
        </div>

        <!-- 当前选择预览 -->
        <div class="rounded-xl border border-[rgba(255,255,255,0.08)] bg-[rgba(255,255,255,0.04)] px-4 py-3.5">
          <div class="mb-1.5 text-xs text-[var(--muted)]">当前选择：</div>
          <div class="text-[15px] font-medium text-[var(--text)]">{{ previewText }}</div>
          <div v-if="selectedCity" class="mt-1.5 text-xs text-[var(--muted)]">
            经度: {{ selectedCity.lng.toFixed(4) }}°，纬度: {{ selectedCity.lat.toFixed(4) }}°
          </div>
        </div>
      </div>

      <div class="flex justify-end gap-3 border-t border-[rgba(255,255,255,0.1)] px-6 py-4">
        <button
          class="rounded-xl border border-[rgba(255,255,255,0.1)] bg-[rgba(18,20,30,0.72)] px-4 py-2.5 font-semibold text-[#f3e4c8] transition-all duration-200 hover:bg-[rgba(255,255,255,0.08)]"
          type="button"
          @click="handleReset"
        >
          重置为未知
        </button>
        <button
          class="rounded-xl border-none bg-gradient-to-br from-[var(--accent)] to-[var(--accent-2)] px-4 py-2.5 font-semibold text-[#0c0f15] transition-all duration-200 hover:-translate-y-[1px] disabled:opacity-50 disabled:cursor-not-allowed"
          type="button"
          :disabled="!canConfirm"
          @click="handleConfirm"
        >
          确定
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { chinaRegions, getDefaultRegion, type Province, type City, type SelectedRegion } from "../data/china-regions";

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
</script>

<style scoped>
/* 响应式调整 */
@media (max-width: 720px) {
  .region-picker-modal {
    max-height: 90vh;
  }
}
</style>

