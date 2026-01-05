<template>
  <div class="archives-page-wrapper mx-auto max-w-[1600px] px-4 pb-10 lg:px-6">
    <section class="archive-panel">
      <header class="archive-header">
        <div class="brand-left">
          <div>
            <div class="brand-title">档案列表</div>
            <div class="muted">已保存 {{ archives.length }} 份命盘档案</div>
          </div>
        </div>
        <div class="archive-actions">
          <button class="btn primary" type="button" @click="goToNewForm">
            新建档案
          </button>
        </div>
      </header>

      <div class="archive-content">
        <div class="archive-list">
          <!-- 空状态 -->
          <div v-if="archives.length === 0" class="archive-empty panel">
            <h2>还没有档案</h2>
            <p class="muted">先填写姓名与生日信息，再保存到这里。</p>
            <button class="btn primary" type="button" @click="goToNewForm">去填写</button>
          </div>

          <!-- 档案列表 -->
          <button
            v-for="entry in archives"
            :key="entry.id"
            class="archive-card"
            type="button"
            :class="{ active: entry.id === activeArchiveId }"
            @click="openArchive(entry)"
          >
            <div class="archive-main">
              <div class="archive-name">{{ entry.displayName }}</div>
              <div class="archive-birth">{{ entry.birthLabel }}</div>
            </div>
            <div class="archive-pillars">
              <div class="archive-pillar-row">
                <span
                  v-for="(pillar, idx) in entry.pillars"
                  :key="`stem-${entry.id}-${idx}`"
                  :class="['archive-char', elementClass(pillar.stemElement)]"
                >
                  {{ pillar.stem }}
                </span>
              </div>
              <div class="archive-pillar-row">
                <span
                  v-for="(pillar, idx) in entry.pillars"
                  :key="`branch-${entry.id}-${idx}`"
                  :class="['archive-char', elementClass(pillar.branchElement)]"
                >
                  {{ pillar.branch }}
                </span>
              </div>
            </div>
            <div class="archive-arrow">›</div>
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
