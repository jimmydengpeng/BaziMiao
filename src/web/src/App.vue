<template>
  <div class="app-root min-h-screen">
    <!-- 顶部导航栏（所有页面都显示） -->
    <TopNav
      :active-module="activeModule"
      :is-home="isHomePage"
      :is-authenticated="isAuthenticated"
      :current-page="currentPage"
      :can-view-report="canViewReport"
      @navigate="handleNavigate"
      @go-home="goHome"
      @start="goToForm"
      @go-login="goToLogin"
    />

    <!-- 主内容区域：路由视图 -->
    <!-- 三档响应式padding-top：手机 pt-12, 平板 pt-14, 桌面 pt-16 -->
    <div class="app-content pt-12 md:pt-14 lg:pt-16">
      <router-view />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import TopNav from './components/TopNav.vue';
import { useStore } from './composables/useStore';
import { loadBaziViewState, saveBaziViewState } from './utils/storage';

const router = useRouter();
const route = useRoute();
const { isAuthenticated, activeArchiveId, report, chart } = useStore();

// 根据当前路由计算激活的模块
const activeModule = computed(() => {
  const path = route.path;
  if (path.startsWith('/bazi/chat')) return 'master';
  if (path.startsWith('/bazi')) return 'bazi';
  if (path.startsWith('/compatibility')) return 'compatibility';
  if (path.startsWith('/profile')) return 'profile';
  if (path.startsWith('/encyclopedia')) return 'encyclopedia';
  return 'bazi';
});

// 是否在首页
const isHomePage = computed(() => route.path === '/');

// 当前页面类型（用于侧边导航/移动端菜单高亮）
const currentPage = computed(() => {
  const path = route.path;
  if (path.includes('/report')) return 'report';
  if (path.includes('/pro')) return 'pro';
  if (path.includes('/verification')) return 'verification';
  if (path.includes('/pillars')) return 'chart';
  if (path.includes('/chart')) return 'chart';
  if (path.includes('/archives')) return 'archive';
  if (path.includes('/chat')) return 'master-chat';
  if (path.includes('/form')) return 'form';
  if (path === '/') return 'home';
  return 'chart';
});

// 是否可以查看报告（需要已生成报告）
const canViewReport = computed(() => {
  return !!report.value || !!activeArchiveId.value;
});

// 处理模块导航
const handleNavigate = (module: 'bazi' | 'compatibility' | 'profile' | 'master' | 'encyclopedia') => {
  switch (module) {
    case 'bazi':
      // 智能导航：如果有活跃的命盘，恢复到之前的浏览状态；否则显示表单页
      const viewState = loadBaziViewState();
      const hasActiveChart = chart.value && (activeArchiveId.value !== null || route.params.id);
      
      if (hasActiveChart) {
        // 有活跃命盘，恢复到之前的浏览状态或默认页面
        const chartId = activeArchiveId.value || route.params.id || viewState?.chartId;
        if (chartId) {
          if (viewState && viewState.chartId === chartId) {
            // 有保存的状态，恢复到之前的页面和滚动位置
            const pagePath = viewState.page === 'chart' ? 'pillars' : viewState.page;
            router.push(`/bazi/chart/${chartId}/${pagePath}`).then(() => {
              // 延迟恢复滚动位置，等待页面渲染完成
              setTimeout(() => {
                window.scrollTo({ top: viewState.scrollPosition, behavior: 'smooth' });
              }, 100);
            });
          } else {
            // 没有保存的状态，跳转到默认页面（命盘信息）
            router.push(`/bazi/chart/${chartId}/pillars`);
          }
        } else {
          // 没有有效的 chartId，跳转到表单页
          router.push('/bazi/form');
        }
      } else {
        // 没有活跃命盘，跳转到表单页（表单页会显示新建和从档案选择两个选项）
        router.push('/bazi/form');
      }
      break;
    case 'compatibility':
      router.push('/compatibility');
      break;
    case 'profile':
      router.push('/profile');
      break;
    case 'master':
      router.push('/bazi/chat');
      break;
    case 'encyclopedia':
      router.push('/encyclopedia');
      break;
  }
};

// 回到首页
const goHome = () => {
  router.push('/');
};

// 跳转到表单页
const goToForm = () => {
  router.push('/bazi/form');
};

// 跳转到登录页
const goToLogin = () => {
  router.push('/profile');
};

// 根据路由更新 body 类名（用于样式）
watch(
  () => route.path,
  (path) => {
    const classList = document.documentElement.classList;
    classList.remove('page-home', 'page-main');

    if (path === '/') {
      classList.add('page-home');
    } else {
      classList.add('page-main');
    }
  },
  { immediate: true }
);

// 保存命盘解析模块的浏览状态（当在命盘相关页面时）
watch(
  () => route.path,
  (path) => {
    // 如果当前在命盘解析模块的页面
    if (path.startsWith('/bazi/chart/')) {
      const chartId = route.params.id as string;
      const page = currentPage.value as 'chart' | 'report' | 'pro' | 'verification';
      
      // 保存浏览状态（包括当前页面和滚动位置）
      if (chartId && page) {
        saveBaziViewState({
          page,
          scrollPosition: window.scrollY || document.documentElement.scrollTop,
          chartId,
        });
      }
    }
  }
);

// 监听滚动，实时更新滚动位置（节流处理）
let scrollTimer: number | null = null;
const handleScroll = () => {
  if (scrollTimer) {
    clearTimeout(scrollTimer);
  }
  scrollTimer = window.setTimeout(() => {
    if (route.path.startsWith('/bazi/chart/')) {
      const chartId = route.params.id as string;
      const page = currentPage.value as 'chart' | 'report' | 'pro' | 'verification';
      
      if (chartId && page) {
        saveBaziViewState({
          page,
          scrollPosition: window.scrollY || document.documentElement.scrollTop,
          chartId,
        });
      }
    }
  }, 200); // 200ms 节流
};

// 在命盘解析模块页面时监听滚动
watch(
  () => route.path,
  (path, oldPath) => {
    // 移除旧路径的监听器
    if (oldPath && oldPath.startsWith('/bazi/chart/')) {
      window.removeEventListener('scroll', handleScroll);
    }
    // 添加新路径的监听器
    if (path.startsWith('/bazi/chart/')) {
      window.addEventListener('scroll', handleScroll, { passive: true });
    }
  },
  { immediate: true }
);

// 组件卸载时清理
onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll);
  if (scrollTimer) {
    clearTimeout(scrollTimer);
  }
});
</script>

<style>
/* 全局样式保持不变，继续使用现有的 CSS */
</style>
