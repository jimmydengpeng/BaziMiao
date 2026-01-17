<template>
  <div class="mx-auto flex min-h-[calc(100vh-64px)] max-w-[960px] flex-col gap-4 px-5 py-8">
    <div class="panel-card p-6">
      <div class="flex flex-col gap-4">
        <div class="flex items-center gap-2 text-xs uppercase tracking-[0.2em] text-[var(--accent)]">
          <span class="h-1.5 w-1.5 rounded-full bg-[var(--accent)]"></span>
          <span>信息中心</span>
        </div>

        <div class="flex flex-wrap gap-2">
          <button
            v-for="t in tabs"
            :key="t.key"
            type="button"
            :class="[
              'rounded-xl border px-4 py-2 text-sm font-semibold transition',
              activeTab === t.key
                ? 'border-[rgba(214,160,96,0.45)] bg-[rgba(214,160,96,0.12)] text-[var(--accent-2)]'
                : 'border-white/10 bg-white/5 text-white/70 hover:bg-white/10 hover:text-white'
            ]"
            @click="setTab(t.key)"
          >
            {{ t.label }}
          </button>
        </div>

        <div class="rounded-2xl border border-white/10 bg-white/5 p-5">
          <h2 class="text-xl font-semibold text-white">{{ current.title }}</h2>
          <p class="mt-2 text-sm leading-relaxed text-white/60">{{ current.description }}</p>
          <div v-if="current.items?.length" class="mt-4 flex flex-col gap-2 text-sm text-white/70">
            <div v-for="(it, idx) in current.items" :key="idx" class="rounded-xl border border-white/10 bg-black/10 px-4 py-3">
              {{ it }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';

const router = useRouter();
const route = useRoute();

const tabs = [
  { key: 'about', label: '关于我们' },
  { key: 'contact', label: '联系我们' },
  { key: 'feedback', label: '反馈意见' },
  { key: 'terms', label: '服务条款' },
  { key: 'privacy', label: '隐私政策' },
] as const;

type TabKey = (typeof tabs)[number]['key'];

const activeTab = computed<TabKey>(() => {
  const q = (route.query.tab as string | undefined)?.toLowerCase();
  const exists = tabs.some((t) => t.key === (q as TabKey));
  return exists ? (q as TabKey) : 'about';
});

const contentMap: Record<TabKey, { title: string; description: string; items?: string[] }> = {
  about: {
    title: '关于神机喵算',
    description:
      '神机喵算是一个融合 AI 与传统命理的工具型 MVP：目标是让排盘、术语理解、推演逻辑与复盘都更直观。',
    items: [
      '神机喵算并非一言定命，而是因问而推，因心而算。小喵道童观其象，喵道长入其局。',
      '定位：命理爱好者的学习助手 / 专业命理师的参考工具',
      '阶段：MVP 快速迭代中，欢迎提出需求',
    ],
  },
  contact: {
    title: '联系我们',
    description: '目前处于 MVP 阶段，联系方式后续补充。你也可以先通过“反馈意见”把想法发给我。',
    items: ['建议：把你的使用场景、目标、痛点描述清楚，我会更快定位需求'],
  },
  feedback: {
    title: '反馈意见',
    description: '欢迎告诉我：哪里不好用、哪里看不懂、以及你希望增加的能力。',
    items: ['建议反馈格式：页面/功能 + 你期待的行为 + 你实际看到的行为 + 截图（可选）'],
  },
  terms: {
    title: '服务条款（占位）',
    description: '本页面为占位：MVP 阶段后续会补充更完整的服务条款内容。',
  },
  privacy: {
    title: '隐私政策（占位）',
    description: '本页面为占位：MVP 阶段后续会补充更完整的隐私政策内容。',
  },
};

const current = computed(() => contentMap[activeTab.value]);

const setTab = (key: TabKey) => {
  router.replace({ path: '/about', query: key === 'about' ? {} : { tab: key } });
};
</script>
