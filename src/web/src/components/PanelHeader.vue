<template>
  <div class="panel-header">
    <div
      class="flex items-center justify-between gap-2 pt-0 pl-2 pr-0 pb-2 mb-0"
      :class="clickable ? 'cursor-pointer' : ''"
      @click="handleHeaderClick"
    >
      <div class="flex items-center gap-2">
        <slot name="title">
          <h3 class="text-base font-semibold text-(--accent-2)">{{ title }}</h3>
        </slot>
      </div>
      <div class="panel-actions" @click.stop>
        <slot name="actions"></slot>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps({
  title: {
    type: String,
    required: true,
  },
  clickable: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits<{
  (event: "header-click"): void;
}>();

const handleHeaderClick = () => {
  if (!props.clickable) return;
  emit("header-click");
};
</script>
