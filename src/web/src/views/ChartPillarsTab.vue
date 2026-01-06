<template>
  <div class="flex flex-col gap-5">
    <div v-if="chart" class="flex flex-col gap-5">
      <!-- 命盘展示 -->
      <ChartPanel :chart="chart" />

    </div>

    <div v-else class="rounded-2xl border border-[rgba(255,255,255,0.08)] bg-[var(--panel)] p-5 shadow-[0_12px_40px_rgba(0,0,0,0.35)]">
      <p class="mb-4 text-sm text-[var(--muted)]">未找到命盘数据，请先填写生辰信息。</p>
      <button
        class="rounded-xl border-none bg-gradient-to-br from-[var(--accent)] to-[var(--accent-2)] px-4 py-2.5 font-semibold text-[#0c0f15] shadow-[0_14px_30px_rgba(0,0,0,0.35)] transition-all duration-200 hover:-translate-y-[1px]"
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
