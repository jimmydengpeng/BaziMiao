<template>
  <div class="relative min-h-screen overflow-hidden">
    <div
      class="relative mx-auto flex w-full max-w-[1100px] flex-col gap-10 px-5 pb-[calc(env(safe-area-inset-bottom,0px)+48px)] pt-[calc(64px+env(safe-area-inset-top,0px))]"
    >
      <!-- Hero -->
      <section class="panel-card p-6 md:p-9">
        <div class="flex flex-col items-center text-center">
          <div class="mb-2 inline-flex items-center gap-2 text-xs uppercase tracking-[0.22em] text-[var(--accent)]">
            <!-- <span class="h-1.5 w-1.5 rounded-full bg-[var(--accent)]"></span> -->
            <span>AI × 命理 × 工具</span>
          </div>

          <h1
            class="bg-[linear-gradient(135deg,#f4d03f_0%,#d6a060_25%,#f0c07a_50%,#d6a060_75%,#f4d03f_100%)] bg-clip-text font-['Ma_Shan_Zheng',serif] text-[clamp(52px,7vw,88px)] font-normal leading-[1.15] tracking-[0.08em] text-transparent drop-shadow-[0_0_40px_rgba(214,160,96,0.35)] animate-[shimmer_3s_ease-in-out_0.6s_infinite]"
          >
            神机喵算
          </h1>

          <div class="mt-3 font-['Cinzel',serif] text-sm uppercase tracking-[0.32em] text-white/60">
            BaziMiao
          </div>

          <p class="mt-6 max-w-[46rem] text-[15px] leading-[1.9] text-white/70 md:text-base">
            融合最先进的人工智能技术与传统命理体系，用更客观、可解释的方式，帮助你读懂八字命盘、理解术语与推演逻辑。
          </p>

          <blockquote class="mt-6 max-w-[56rem] rounded-2xl border border-white/10 bg-white/5 px-4 py-4 text-left md:px-5 md:py-6">
            <div class="space-y-4">
              <div class="space-y-1">
                <div class="text-[15px] leading-relaxed text-white/75 md:text-base">
                  “不知命，无以为君子。”
                </div>
                <div class="text-xs text-white/45 text-right">— 孔子</div>
              </div>
              <div class="border-t border-white/10 pt-4 space-y-1">
                <div class="text-[15px] leading-relaxed text-white/75 md:text-base">
                  “一个人到了四十岁还不信命，此人悟性太差。”
                </div>
                <div class="text-xs text-white/45 text-right">— 复旦大学哲学院教授 王德峰</div>
              </div>
            </div>
          </blockquote>

          <div class="mt-8 flex w-full flex-col items-center gap-4">
            <button
              class="btn-primary w-full max-w-[360px] px-8 py-4 text-base md:text-lg"
              type="button"
              @click="goToForm"
            >
              开始排盘
            </button>
            <div class="flex flex-wrap items-center justify-center gap-3">
              <button
                class="btn-ghost flex items-center gap-1.5 px-3 py-2 text-[14px] text-white/70 opacity-80 transition hover:opacity-100"
                type="button"
                :disabled="archives.length === 0"
                @click="openArchivePicker"
              >
                <span>选择档案</span>
                <svg class="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M9 6l6 6-6 6" stroke-linecap="round" stroke-linejoin="round" />
                </svg>
              </button>
              <button
                v-if="selectedArchive"
                class="btn-ghost flex items-center gap-1.5 px-3 py-2 text-[14px] text-white/70 opacity-80 transition hover:opacity-100"
                type="button"
                @click="goToLastArchive"
              >
                <span>继续浏览：{{ selectedArchive.displayName || selectedArchive.name }}</span>
                <svg class="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M9 6l6 6-6 6" stroke-linecap="round" stroke-linejoin="round" />
                </svg>
              </button>
            </div>
          </div>

          <div class="mt-6 text-xs tracking-[0.15em] text-white/45">
            命由天定 · 运在人为
          </div>
        </div>
      </section>

      <!-- 核心理念 -->
      <section class="flex flex-col gap-4">
        <div class="flex items-end justify-between gap-3">
          <h2 class="text-lg font-semibold text-white">核心理念</h2>
        </div>
        <div class="grid grid-cols-1 gap-3 md:grid-cols-3">
          <FeatureCard>
            <template #icon>
              <svg class="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 3v18M3 12h18" stroke-linecap="round" stroke-linejoin="round" />
              </svg>
            </template>
            <template #title>AI 辅助解读</template>
            <template #description>
              用对话式方式拆解命盘信息：先给结论，再解释依据，减少“只看不懂”的挫败感。
            </template>
          </FeatureCard>

          <FeatureCard>
            <template #icon>
              <svg class="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M4 6h16M4 12h10M4 18h16" stroke-linecap="round" stroke-linejoin="round" />
              </svg>
            </template>
            <template #title>术语翻译与结构化</template>
            <template #description>
              把神煞、十神、格局等概念“翻译”成明确含义，并按主题归类，方便快速学习与复盘。
            </template>
          </FeatureCard>

          <FeatureCard>
            <template #icon>
              <svg class="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 20V10M18 20V4M6 20v-6" stroke-linecap="round" stroke-linejoin="round" />
              </svg>
            </template>
            <template #title>理论支撑与可追溯</template>
            <template #description>
              结论尽量对应到“哪一条信息、哪一步推导”，为爱好者与专业命理师提供可参考的助手工具。
            </template>
          </FeatureCard>
        </div>
      </section>

      <!-- 核心模块 -->
      <section class="flex flex-col gap-4">
        <div class="flex items-end justify-between gap-3">
          <h2 class="text-lg font-semibold text-white">核心模块</h2>
        </div>

        <div class="grid grid-cols-1 gap-3 md:grid-cols-2">
          <FeatureCard>
            <template #icon>
              <svg class="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M4 20h16M6 4h12v12H6z" stroke-linecap="round" stroke-linejoin="round" />
              </svg>
            </template>
            <template #title>命盘解析</template>
            <template #description>新建排盘、查看八字命盘、生成报告、深度细盘与前事验盘。</template>
            <template #footer>
              <button class="btn-primary w-full" type="button" @click="goToForm">进入排盘</button>
            </template>
          </FeatureCard>

          <FeatureCard>
            <template #icon>
              <svg class="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M8 7h8M8 12h8M8 17h8" stroke-linecap="round" stroke-linejoin="round" />
                <path d="M6 4h12v16H6z" stroke-linecap="round" stroke-linejoin="round" />
              </svg>
            </template>
            <template #title>双人合盘</template>
            <template #description>用于关系匹配、互动趋势与相处建议的对照视角（逐步完善）。</template>
            <template #footer>
              <button class="btn-ghost w-full" type="button" @click="router.push('/compatibility')">进入合盘</button>
            </template>
          </FeatureCard>

          <FeatureCard>
            <template #icon>
              <svg class="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M5 4h14v16H5z" stroke-linecap="round" stroke-linejoin="round" />
                <path d="M8 8h8M8 12h6" stroke-linecap="round" stroke-linejoin="round" />
              </svg>
            </template>
            <template #title>命理百科</template>
            <template #description>把核心概念做成可查的知识卡片，学习时可以快速定位与理解。</template>
            <template #footer>
              <button class="btn-ghost w-full" type="button" @click="router.push('/encyclopedia')">进入百科</button>
            </template>
          </FeatureCard>

          <FeatureCard>
            <template #icon>
              <svg class="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15a4 4 0 0 1-4 4H7l-4 3V7a4 4 0 0 1 4-4h10a4 4 0 0 1 4 4z" stroke-linecap="round" stroke-linejoin="round" />
              </svg>
            </template>
            <template #title>自由对话</template>
            <template #description>随时提问：用更自然的语言交流命理思路，适合学习、复盘与灵感记录。</template>
            <template #footer>
              <button class="btn-ghost w-full" type="button" @click="router.push('/chat')">开始对话</button>
            </template>
          </FeatureCard>
        </div>
      </section>

      <!-- Footer -->
      <footer class="p-6">
        <div class="flex flex-col gap-6 md:flex-row md:items-start md:justify-between">
          <div class="min-w-0">
            <div class="text-base font-semibold text-white">神机喵算 · BaziMiao</div>
            <div class="mt-2 text-sm leading-relaxed text-white/60">
              MVP 阶段：功能会持续迭代。欢迎反馈你的使用体验与需求。
            </div>
          </div>

          <div class="grid grid-cols-2 gap-x-6 gap-y-2 text-sm md:grid-cols-1">
            <router-link class="text-white/70 transition hover:text-white" to="/about">关于我们</router-link>
            <router-link class="text-white/70 transition hover:text-white" :to="{ path: '/about', query: { tab: 'contact' } }">联系我们</router-link>
            <router-link class="text-white/70 transition hover:text-white" :to="{ path: '/about', query: { tab: 'feedback' } }">反馈意见</router-link>
            <router-link class="text-white/70 transition hover:text-white" :to="{ path: '/about', query: { tab: 'terms' } }">服务条款</router-link>
            <router-link class="text-white/70 transition hover:text-white" :to="{ path: '/about', query: { tab: 'privacy' } }">隐私政策</router-link>
          </div>
        </div>
        <div class="mt-6 border-t border-white/10 pt-4 text-xs text-white/40">
          © {{ currentYear }} BaziMiao · All rights reserved.
        </div>
      </footer>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, inject, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import FeatureCard from '../components/FeatureCard.vue';
import { useStore } from '../composables/useStore';

const router = useRouter();
const { archives, activeArchiveId, chart, analysis, report } = useStore();
const openArchivePickerInjected = inject<() => void>('openArchivePicker', undefined);
const currentYear = new Date().getFullYear();
const selectedArchive = computed(() => {
  if (activeArchiveId.value === null) return null;
  return archives.value.find((entry) => entry.id === activeArchiveId.value) ?? null;
});

const goToLastArchive = () => {
  if (!selectedArchive.value) return;
  activeArchiveId.value = selectedArchive.value.id;
  chart.value = selectedArchive.value.chart;
  analysis.value = null;
  report.value = selectedArchive.value.reportState.report ?? null;
  router.push({ name: 'ChartBasic', params: { id: selectedArchive.value.id } });
};

// 导航到表单页
const goToForm = () => {
  router.push('/bazi/form');
};

const openArchivePicker = () => {
  openArchivePickerInjected?.();
};

// 设置页面样式
onMounted(() => {
  document.documentElement.classList.add('page-home');
  document.documentElement.classList.remove('page-main');
});

onUnmounted(() => {
  document.documentElement.classList.remove('page-home');
});
</script>

<style scoped>
@keyframes shimmer {
  0%, 100% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
}
</style>
