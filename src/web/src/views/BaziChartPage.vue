<template>
  <!-- 命盘主页面：
       - 手机端：底部有固定 Tab Bar，预留更大底部内边距避免内容被遮挡
       - 平板 / 桌面端：正常内边距，由顶部导航 + 悬浮 Tab Bar 协同控制 -->
  <div class="bazi-chart-page-wrapper mx-auto max-w-[1600px] px-1.5 pb-20 md:px-4 md:pb-8 lg:px-6 lg:pb-10">
    <section class="main-shell grid grid-cols-1 items-start gap-3 md:gap-4 lg:gap-5 lg:grid-cols-[auto_minmax(0,1fr)]">
      <!-- 模块级侧边导航（使用 SideNav 组件，桌面端显示） -->
      <SideNav
        :current-page="currentPage"
        :can-view-report="canViewReport"
      />

      <div class="workspace flex min-w-0 gap-3 md:gap-4 lg:gap-5 lg:items-start">
        <!-- main-content：
             - 手机端：轻微上内边距，和底部 Tab Bar 形成平衡
             - 平板端和桌面端：顶部间距已由 App.vue 的 app-content 统一处理 -->
        <main
          class="main-content relative w-full min-w-0 max-w-[900px] space-y-3 pt-1 md:space-y-4 lg:space-y-5"
        >
          <!-- 子路由内容 -->
          <router-view />
        </main>
      </div>

      <!-- 固定层 UI（Tab Bar）从滚动容器中 Teleport 到 body，避免 iOS 惯性滚动吞点击 -->
      <teleport to="body">
        <!-- 移动端 / 平板端 Tab Bar（最多 4 个 Tab，对应侧边栏核心功能） -->
        <!-- 说明：
             - 手机端和平板端：统一固定在屏幕底部上方，参考 iOS 风格的悬浮 Tab Bar，背景使用毛玻璃效果
             - 平板端：宽度略更大，使用更"弹性"的宽度以适配不同尺寸的平板
             - 桌面端：由左侧 SideNav 负责导航，隐藏此 Tab Bar -->
        <TabBar :items="tabItems" />
      </teleport>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import SideNav from '../components/SideNav.vue';
import TabBar from '../components/TabBar.vue';
import { useStore } from '../composables/useStore';
// 与侧边栏保持一致的核心功能图标
import baziChartIconUrl from '../assets/bazi-chart.png';
import reportIconUrl from '../assets/report.png';
import detailChartIconUrl from '../assets/pages.png';
import verifyChartIconUrl from  '../assets/check-list-1.png';

const route = useRoute();
const { report } = useStore();

// 当前命盘 ID
const chartId = computed(() => route.params.id as string);

// 根据当前路由计算当前页面（用于 SideNav 高亮）
const currentPage = computed(() => {
  const path = route.path;
  if (path.includes('/pillars')) return 'chart';
  if (path.includes('/report')) return 'report';
  if (path.includes('/detail') || path.includes('/pro')) return 'detail';
  if (path.includes('/verification')) return 'verification';
  return 'chart';
});

// 底部 Tab Bar 配置，复用统一的样式
const tabItems = computed(() => {
  const id = chartId.value;
  return [
    {
      key: 'chart',
      label: '命盘信息',
      icon: baziChartIconUrl,
      to: `/bazi/chart/${id}/pillars`,
      active: currentPage.value === 'chart'
    },
    {
      key: 'report',
      label: '命理报告',
      icon: reportIconUrl,
      to: `/bazi/chart/${id}/report`,
      active: currentPage.value === 'report'
    },
    {
      key: 'detail',
      label: '专业细盘',
      icon: detailChartIconUrl,
      to: `/bazi/chart/${id}/detail`,
      active: currentPage.value === 'detail'
    },
    {
      key: 'verification',
      label: '前事验盘',
      icon: verifyChartIconUrl,
      to: `/bazi/chart/${id}/verification`,
      active: currentPage.value === 'verification'
    }
  ];
});

// 是否可以查看报告
const canViewReport = computed(() => !!report.value);

// 页面样式由 App.vue 统一控制，避免路由切换时误删全局类名
</script>
