<template>
  <div class="mx-auto max-w-[1600px] px-3 pb-6 md:px-4 md:pb-8 lg:px-6 lg:pb-10">
    <section class="relative flex flex-col gap-4">
      <header class="flex items-center justify-between gap-4 rounded-[18px] border border-[rgba(255,255,255,0.12)] bg-[rgba(18,20,30,0.6)] px-4.5 py-4 backdrop-blur-[14px]">
        <div class="flex items-center gap-3">
          <div>
            <div class="text-base font-semibold text-[var(--accent-2)]">档案列表</div>
            <div class="text-sm text-[var(--muted)]">已保存 {{ archives.length }} 份命盘档案</div>
          </div>
        </div>
        <div class="flex items-center gap-2.5 flex-wrap">
          <button
            class="rounded-xl border-none bg-gradient-to-br from-[var(--accent)] to-[var(--accent-2)] px-4 py-2.5 font-semibold text-[#0c0f15] shadow-[0_14px_30px_rgba(0,0,0,0.35)] transition-all duration-200 hover:-translate-y-[1px] hover:border-[rgba(255,255,255,0.2)]"
            type="button"
            @click="goToNewForm"
          >
            新建档案
          </button>
        </div>
      </header>

      <div class="flex min-w-0 flex-col gap-3.5">
        <div class="flex flex-col gap-3.5">
          <!-- 空状态 -->
          <div
            v-if="archives.length === 0"
            class="flex flex-col gap-2.5 rounded-2xl border border-[rgba(255,255,255,0.14)] bg-[rgba(16,12,10,0.7)] p-5 text-center"
          >
            <h2 class="text-lg font-semibold text-white">还没有档案</h2>
            <p class="text-sm text-[var(--muted)]">先填写姓名与生日信息，再保存到这里。</p>
            <button
              class="mx-auto mt-2 rounded-xl border-none bg-gradient-to-br from-[var(--accent)] to-[var(--accent-2)] px-4 py-2.5 font-semibold text-[#0c0f15] shadow-[0_14px_30px_rgba(0,0,0,0.35)] transition-all duration-200 hover:-translate-y-[1px]"
              type="button"
              @click="goToNewForm"
            >
              去填写
            </button>
          </div>

          <!-- 档案列表 -->
          <button
            v-for="entry in archives"
            :key="entry.id"
            :class="[
              'grid grid-cols-[minmax(0,1fr)_auto_auto] items-center gap-4 rounded-[18px] border border-[rgba(255,255,255,0.16)] bg-[rgba(20,18,28,0.58)] px-5 py-4 text-left shadow-[0_18px_40px_rgba(0,0,0,0.45)] backdrop-blur-[14px] transition-all duration-200 hover:-translate-y-0.5 hover:border-[rgba(214,160,96,0.55)] hover:shadow-[0_22px_48px_rgba(0,0,0,0.5)]',
              entry.id === activeArchiveId
                ? 'border-[rgba(214,160,96,0.85)] shadow-[0_22px_50px_rgba(0,0,0,0.55),inset_0_0_0_1px_rgba(214,160,96,0.35)]'
                : ''
            ]"
            type="button"
            @click="openArchive(entry)"
          >
            <div class="grid gap-1.5">
              <div class="text-[22px] font-semibold tracking-wide text-[var(--accent-2)]">{{ entry.displayName }}</div>
              <div class="text-[13px] text-white/65">{{ entry.birthLabel }}</div>
            </div>
            <div class="grid gap-1.5 justify-items-center">
              <div class="grid auto-cols-[minmax(16px,1fr)] grid-flow-col gap-2.5 text-base font-semibold tracking-widest">
                <span
                  v-for="(pillar, idx) in entry.pillars"
                  :key="`stem-${entry.id}-${idx}`"
                  :class="['min-w-[18px] text-center', elementClass(pillar.stemElement)]"
                >
                  {{ pillar.stem }}
                </span>
              </div>
              <div class="grid auto-cols-[minmax(16px,1fr)] grid-flow-col gap-2.5 text-base font-semibold tracking-widest">
                <span
                  v-for="(pillar, idx) in entry.pillars"
                  :key="`branch-${entry.id}-${idx}`"
                  :class="['min-w-[18px] text-center', elementClass(pillar.branchElement)]"
                >
                  {{ pillar.branch }}
                </span>
              </div>
            </div>
            <div class="text-2xl text-[var(--accent-2)] opacity-80">›</div>
          </button>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import { useStore } from '../composables/useStore';
import type { ArchiveEntry } from '../utils/storage';

const router = useRouter();
const { archives, activeArchiveId, chart, analysis, report } = useStore();

// 打开档案，加载命盘数据并跳转到详情页
const openArchive = (entry: ArchiveEntry) => {
  activeArchiveId.value = entry.id;
  chart.value = entry.chart;

  // 清空分析和报告（需要重新生成）
  analysis.value = null;
  report.value = null;

  // 跳转到命盘详情页
  router.push(`/bazi/chart/${entry.id}/pillars`);
};

// 跳转到新建表单
const goToNewForm = () => {
  router.push('/bazi/form');
};

// 五行元素样式类
const elementClass = (element: string) => {
  const map: Record<string, string> = {
    木: 'element-wood',
    火: 'element-fire',
    土: 'element-earth',
    金: 'element-metal',
    水: 'element-water'
  };
  return map[element] ?? 'element-neutral';
};
</script>
