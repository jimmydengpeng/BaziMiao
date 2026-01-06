<template>
  <div :class="[wrapperBaseClass, wrapperClass]">
    <div :class="[containerBaseClass, containerClass]">
      <router-link
        v-for="item in items"
        :key="item.key"
        :to="item.to"
        :class="[
          itemBaseClass,
          itemClass,
          item.disabled ? disabledClass : item.active ? activeClassComputed : inactiveClassComputed
        ]"
        :aria-disabled="item.disabled ? 'true' : 'false'"
        :tabindex="item.disabled ? -1 : undefined"
      >
        <span :class="[iconWrapperBaseClass, iconWrapperClass]">
          <img :src="item.icon" :alt="item.label" :class="[iconBaseClass, iconClass]" />
        </span>
        <span class="font-medium" style="font-family: 'Noto Sans SC','Microsoft YaHei','PingFang SC',sans-serif;">
          {{ item.label }}
        </span>
      </router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

type TabItem = {
  key: string;
  label: string;
  icon: string;
  to: string;
  active?: boolean;
  disabled?: boolean;
};

const props = defineProps<{
  items: TabItem[];
  wrapperClass?: string;
  containerClass?: string;
  itemClass?: string;
  activeClass?: string;
  inactiveClass?: string;
  disabledClass?: string;
  iconWrapperClass?: string;
  iconClass?: string;
}>();

// 基础类名：外层定位 + 容器 + 每个条目 + 图标大小
const wrapperBaseClass = 'mobile-tabs fixed inset-x-0 bottom-6 z-40 flex justify-center lg:hidden';
const containerBaseClass =
  'inline-flex w-[calc(100%-56px)] max-w-[400px] items-stretch rounded-full border border-[rgba(255,255,255,0.16)] bg-[rgba(18,22,33,0.75)] px-1.5 py-1.5 shadow-[0_10px_25px_rgba(0,0,0,0.45)] backdrop-blur-md md:w-[calc(100%-120px)] md:max-w-[520px] md:bg-[rgba(18,22,33,0.5)]';
const itemBaseClass =
  'flex flex-1 flex-col items-center justify-center gap-0.5 rounded-full px-2.5 py-1 text-[10px] font-medium transition md:px-3 md:py-2 md:text-[11px]';
const iconWrapperBaseClass = 'flex h-7 w-7 items-center justify-center md:h-8 md:w-8';
const iconBaseClass = 'h-6 w-6 md:h-7 md:w-7 object-contain';

// 状态类名（允许外部覆盖）
const activeClassComputed = computed(
  () => props.activeClass || 'bg-[rgba(214,160,96,0.3)] text-[var(--accent-2)]'
);
const inactiveClassComputed = computed(
  () => props.inactiveClass || 'text-white/75 hover:bg-white/5'
);
const disabledClass = computed(() => props.disabledClass || 'opacity-50 pointer-events-none');
</script>
