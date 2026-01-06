<template>
  <div class="flex flex-col gap-5">
    <div v-if="chart" class="flex flex-col gap-5">
      <!-- 命盘展示 -->
      <ChartPanel :chart="chart" />

    </div>

    <div v-else class="panel-card">
      <p class="mb-4 text-sm text-[var(--muted)]">未找到命盘数据，请先填写生辰信息。</p>
      <button
        class="btn-primary"
        type="button"
        @click="goToForm"
      >
        去填写
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import ChartPanel from '../components/ChartPanel.vue';
import { useStore } from '../composables/useStore';

const router = useRouter();
const { chart } = useStore();

const goToForm = () => {
  router.push('/bazi/form');
};
</script>
