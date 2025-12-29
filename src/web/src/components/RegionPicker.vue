<template>
  <div class="region-picker-overlay" @click.self="handleClose">
    <div class="region-picker-modal">
      <div class="picker-header">
        <div class="picker-title">选择出生地区</div>
        <button class="picker-close" type="button" @click="handleClose">×</button>
      </div>

      <div class="picker-body">
        <!-- 两栏选择器 -->
        <div class="picker-columns two-columns">
          <!-- 省份列 -->
          <div class="picker-column">
            <div class="column-header">省份/直辖市</div>
            <div class="column-list">
              <button
                v-for="province in provinces"
                :key="province.name"
                class="column-item"
                :class="{ active: selectedProvince?.name === province.name }"
                type="button"
                @click="selectProvince(province)"
              >
                {{ province.name }}
              </button>
            </div>
          </div>

          <!-- 城市/区域列 -->
          <div class="picker-column">
            <div class="column-header">城市/区域</div>
            <div class="column-list">
              <button
                v-for="city in cities"
                :key="city.name"
                class="column-item"
                :class="{ active: selectedCity?.name === city.name }"
                type="button"
                @click="selectCity(city)"
              >
                {{ city.name }}
              </button>
              <div v-if="!cities.length" class="column-empty">请先选择省份</div>
            </div>
          </div>
        </div>

        <!-- 当前选择预览 -->
        <div class="picker-preview">
          <div class="preview-label">当前选择：</div>
          <div class="preview-value">{{ previewText }}</div>
          <div v-if="selectedCity" class="preview-coords">
            经度: {{ selectedCity.lng.toFixed(4) }}°，纬度: {{ selectedCity.lat.toFixed(4) }}°
          </div>
        </div>
      </div>

      <div class="picker-footer">
        <button class="btn secondary" type="button" @click="handleReset">重置为未知</button>
        <button class="btn primary" type="button" :disabled="!canConfirm" @click="handleConfirm">
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
.region-picker-overlay {
  position: fixed;
  inset: 0;
  background: rgba(7, 10, 16, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  z-index: 300;
}

.region-picker-modal {
  width: min(900px, 95vw);
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  background: rgba(18, 20, 28, 0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 20px;
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.5);
  overflow: hidden;
}

.picker-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.picker-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--accent-2);
}

.picker-close {
  width: 32px;
  height: 32px;
  border: none;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  color: var(--muted);
  font-size: 20px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.picker-close:hover {
  background: rgba(255, 255, 255, 0.15);
  color: var(--text);
}

.picker-body {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  padding: 16px 24px;
  gap: 16px;
}

.picker-columns {
  display: grid;
  gap: 12px;
  flex: 1;
  min-height: 0;
}

.picker-columns.two-columns {
  grid-template-columns: repeat(2, 1fr);
}

.picker-column {
  display: flex;
  flex-direction: column;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  overflow: hidden;
  background: rgba(0, 0, 0, 0.2);
}

.column-header {
  padding: 12px 14px;
  font-size: 13px;
  font-weight: 600;
  color: var(--muted);
  background: rgba(255, 255, 255, 0.05);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.column-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
  max-height: 300px;
}

.column-item {
  display: block;
  width: 100%;
  padding: 10px 12px;
  text-align: left;
  border: none;
  background: transparent;
  color: var(--text);
  font-size: 13px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.column-item:hover {
  background: rgba(255, 255, 255, 0.08);
}

.column-item.active {
  background: linear-gradient(120deg, rgba(214, 160, 96, 0.3), rgba(240, 192, 122, 0.2));
  color: var(--accent-2);
  font-weight: 500;
}

.column-empty {
  padding: 20px;
  text-align: center;
  color: var(--muted);
  font-size: 13px;
}

.picker-preview {
  padding: 14px 16px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.preview-label {
  font-size: 12px;
  color: var(--muted);
  margin-bottom: 6px;
}

.preview-value {
  font-size: 15px;
  font-weight: 500;
  color: var(--text);
}

.preview-coords {
  font-size: 12px;
  color: var(--muted);
  margin-top: 6px;
}

.picker-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

/* 滚动条样式 */
.column-list::-webkit-scrollbar {
  width: 6px;
}

.column-list::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.2);
}

.column-list::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.15);
  border-radius: 3px;
}

.column-list::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.25);
}

/* 响应式 */
@media (max-width: 720px) {
  .picker-columns.two-columns {
    grid-template-columns: 1fr;
    gap: 8px;
  }

  .column-list {
    max-height: 150px;
  }

  .region-picker-modal {
    max-height: 90vh;
  }
}
</style>

