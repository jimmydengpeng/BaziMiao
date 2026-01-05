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
    <div class="app-content pt-14 lg:pt-16">
      <router-view />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import TopNav from './components/TopNav.vue';
import { useStore } from './composables/useStore';

const router = useRouter();
const route = useRoute();
const { isAuthenticated, activeArchiveId, report } = useStore();

// 根据当前路由计算激活的模块
const activeModule = computed(() => {
  const path = route.path;
  if (path.startsWith('/bazi')) return 'bazi';
  if (path.startsWith('/compatibility')) return 'compatibility';
  if (path.startsWith('/profile')) return 'profile';
  return 'bazi';
});

// 是否在首页
const isHomePage = computed(() => route.path === '/');

// 当前页面类型（用于侧边导航/移动端菜单高亮）
const currentPage = computed(() => {
  const path = route.path;
  if (path.includes('/pillars') || path.includes('/chart')) return 'chart';
  if (path.includes('/report')) return 'report';
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
const handleNavigate = (module: 'bazi' | 'compatibility' | 'profile') => {
  switch (module) {
    case 'bazi':
      router.push('/bazi/form');
      break;
    case 'compatibility':
      router.push('/compatibility');
      break;
    case 'profile':
      router.push('/profile');
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
</script>

<style>
/* 全局样式保持不变，继续使用现有的 CSS */
</style>
