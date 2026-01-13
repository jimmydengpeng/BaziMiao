import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router';
// 路由配置
const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/HomePage.vue'),
    meta: { title: '神机喵算 - 首页' }
  },
  {
    path: '/bazi/form',
    name: 'BaziForm',
    component: () => import('../views/BaziFormPage.vue'),
    meta: { title: '填写生辰信息' }
  },
  {
    path: '/bazi/chart/:id',
    name: 'BaziChart',
    component: () => import('../views/BaziChartPage.vue'),
    meta: { title: '命盘详情' },
    children: [
      {
        path: '',
        redirect: 'pillars'
      },
      {
        path: 'pillars',
        name: 'ChartPillars',
        component: () => import('../views/ChartPillarsTab.vue'),
        meta: { title: '八字命盘' }
      },
      {
        path: 'report',
        name: 'ChartReport',
        component: () => import('../views/ChartReportTab.vue'),
        meta: { title: '命理报告' }
      },
      {
        path: 'detail',
        name: 'ChartDetail',
        component: () => import('../views/ChartDetailTab.vue'),
        meta: { title: '专业细盘' }
      },
      {
        // 兼容旧链接：/bazi/chart/:id/pro -> /bazi/chart/:id/detail
        path: 'pro',
        redirect: (to) => ({
          name: 'ChartDetail',
          params: to.params,
          query: to.query,
          hash: to.hash,
        }),
      },
      {
        path: 'verification',
        name: 'ChartVerification',
        component: () => import('../views/ChartVerificationTab.vue'),
        meta: { title: '前事验盘' }
      }
    ]
  },
  {
    path: '/bazi/archives/:id/edit',
    name: 'ArchiveEdit',
    component: () => import('../views/ArchiveEditPage.vue'),
    meta: { title: '编辑档案' }
  },
  {
    path: '/bazi/archives',
    name: 'Archives',
    component: () => import('../views/ArchivesPage.vue'),
    meta: { title: '档案管理' }
  },
  {
    path: '/bazi/chat',
    name: 'MasterChat',
    component: () => import('../views/MasterChatPage.vue'),
    meta: { title: '神喵大师' }
  },
  {
    // 移动端/PWA 全屏聊天页面
    path: '/chat',
    name: 'Chat',
    component: () => import('../views/ChatPage.vue'),
    meta: { title: '喵算大师', overlay: true }
  },
  {
    path: '/encyclopedia',
    name: 'Encyclopedia',
    component: () => import('../views/EncyclopediaPage.vue'),
    meta: { title: '命理百科' }
  },
  {
    path: '/compatibility',
    name: 'Compatibility',
    component: () => import('../views/CompatibilityPage.vue'),
    meta: { title: '双人合盘' }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('../views/ProfilePage.vue'),
    meta: { title: '个人中心' }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('../views/SettingsPage.vue'),
    meta: { title: '设置' }
  },
  {
    path: '/about',
    name: 'About',
    component: () => import('../views/AboutPage.vue'),
    meta: { title: '关于我们' }
  },
  {
    // 404 页面
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../views/NotFoundPage.vue'),
    meta: { title: '页面未找到' }
  }
];

// 创建路由实例
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  // 滚动由 App.vue 的 app-scroll 容器接管，这里只保持默认行为
  scrollBehavior() {
    return { top: 0 };
  },
});

// 全局前置守卫 - 设置页面标题
router.beforeEach((to, from, next) => {
  // 设置页面标题
  if (to.meta.title) {
    document.title = to.meta.title as string;
  }
  next();
});

export default router;
