<template>
  <div class="flex flex-col gap-3">
    <div v-if="!chart" class="report-section-card p-5 text-sm text-[var(--muted)]">
      未找到命盘数据，
      <router-link to="/bazi/form" class="text-[var(--accent)] hover:underline">去填写</router-link>
    </div>

    <!-- 未生成报告：引导卡片 -->
    <div v-else-if="!shouldShowStreamView && !report" class="report-section-card p-5 flex flex-col gap-3">
      <div class="flex items-start gap-3">
        <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-[rgba(255,255,255,0.1)] bg-white/5">
          <span
            class="icon-mask h-5 w-5 text-[var(--accent-2)]"
            :style="{ maskImage: `url(${thinkingIconUrl})`, WebkitMaskImage: `url(${thinkingIconUrl})` }"
            aria-hidden="true"
          ></span>
        </div>
        <div class="min-w-0">
          <div class="text-sm font-semibold text-white/90">神机秘算</div>
          <div class="mt-0.5 text-xs leading-relaxed text-[var(--muted)]">
            基于当前命盘生成详细报告，支持流式分段解锁，并在本地自动保存。
          </div>
        </div>
      </div>

      <button
        class="btn-primary min-h-[48px] w-full gap-2 text-base"
        type="button"
        :disabled="isGenerating"
        @click="generateReport"
      >
        {{ isGenerating ? '秘算中...' : '开始秘算' }}
        <span
          class="icon-mask h-4 w-4"
          :style="{ maskImage: `url(${thinkingIconUrl})`, WebkitMaskImage: `url(${thinkingIconUrl})` }"
          aria-hidden="true"
        ></span>
      </button>
    </div>

    <div v-if="chart && !shouldShowStreamView && !report" class="grid gap-3">
      <ReportSectionStatusCard
        v-for="item in reportPlaceholders"
        :key="item.key"
        :title="item.title"
        :description="item.description"
        :state="'idle'"
        :show-toggle="true"
        :show-sample="placeholderSampleMap[item.key]"
        :placeholder-bars="item.placeholderBars"
        @toggle-sample="togglePlaceholderSample(item.key)"
      >
        <template #sample>
          <ReportSectionContent
            :section-id="sampleSectionIdForPlaceholder(item.key)"
            :structured="sampleSectionForPlaceholder(item.key)?.structured"
            :content-md="sampleSectionForPlaceholder(item.key)?.content_md ?? ''"
            compact
          />
        </template>
      </ReportSectionStatusCard>
    </div>

    <!-- 流式生成中：分段解锁 -->
    <div v-if="shouldShowStreamView" class="grid gap-3">
      <ReportSectionCard
        v-if="stream.isStreaming.value"
        title="秘算进行中"
        variant="accent"
      >
        <template #actions>
          <button
            class="btn-ghost rounded-full px-2.5 py-1 text-xs"
            type="button"
            @click="cancelStream"
          >
            取消
          </button>
        </template>

        <div class="flex items-center gap-3">
          <div class="relative">
            <div class="h-7 w-7 animate-spin rounded-full border-2 border-[rgba(255,255,255,0.14)] border-t-[var(--accent-2)]"></div>
            <img :src="sparkleIconUrl" class="absolute left-1/2 top-1/2 h-4 w-4 -translate-x-1/2 -translate-y-1/2 opacity-80" alt="" />
          </div>
          <div class="text-xs leading-relaxed text-[var(--muted)]">
            {{ reportLoadingMessage }}
          </div>
        </div>
        <div class="mt-3 pb-2">
          <div class="h-1.5 overflow-hidden rounded-full bg-[rgba(255,255,255,0.08)]">
            <div
              class="h-full rounded-full bg-[var(--accent-2)] transition-[width] duration-300"
              :style="{ width: `${reportLoadingProgress}%` }"
            ></div>
          </div>
        </div>
      </ReportSectionCard>

      <ReportSectionCard
        v-if="mergedError"
        title="生成失败"
        variant="danger"
      >
        <template #actions>
          <button class="btn-primary px-3 py-1.5 text-xs" type="button" :disabled="isGenerating" @click="generateReport">
            重试全篇
          </button>
        </template>
        <div class="text-xs leading-relaxed text-[var(--muted)]">
          {{ mergedError }}
        </div>
      </ReportSectionCard>

      <template v-for="item in streamSectionsPlan" :key="item.sectionId">
        <ReportSectionStatusCard
          v-if="sectionById(item.sectionId).status !== 'done' && sectionById(item.sectionId).status !== 'error'"
          :title="displaySectionTitle(item.sectionId, item.title)"
          :description="sectionPlaceholder(item.sectionId).description"
          :state="sectionById(item.sectionId).status === 'generating' ? 'generating' : 'queued'"
          :queued-text="stream.isStreaming.value ? '即将生成' : '等待解锁'"
          :generating-text="reportLoadingMessage"
          :placeholder-bars="sectionPlaceholder(item.sectionId).placeholderBars"
        />

        <ReportSectionCard
          v-else-if="sectionById(item.sectionId).status === 'done'"
          :title="displaySectionTitle(item.sectionId, item.title)"
        >
          <ReportSectionContent
            :section-id="item.sectionId"
            :structured="sectionById(item.sectionId).structured"
            :content-md="sectionById(item.sectionId).contentMd"
          />
        </ReportSectionCard>

        <ReportSectionCard
          v-else
          :title="displaySectionTitle(item.sectionId, item.title)"
          variant="danger"
        >
          <div class="text-xs text-[rgba(255,160,160,1)]">
            该段生成失败。
          </div>
        </ReportSectionCard>
      </template>
    </div>

    <!-- 报告已生成 -->
    <div v-else-if="report" class="grid gap-3">
      <ReportSectionCard v-for="sec in finalSections" :key="sec.key" :title="displaySectionTitle(sec.id, sec.title)">
        <ReportSectionContent
          :section-id="sec.id"
          :structured="sec.structured"
          :content-md="sec.content"
        />
      </ReportSectionCard>
    </div>

    <ReportSectionCard v-if="shouldShowDebugPrompt" title="提示词（开发）" :meta="debugPromptCollapsed ? '已折叠' : '已展开'">
      <template #actions>
        <button
          class="btn-ghost rounded-full px-2.5 py-1 text-xs"
          type="button"
          @click="debugPromptCollapsed = !debugPromptCollapsed"
        >
          {{ debugPromptCollapsed ? '展开' : '收起' }}
        </button>
      </template>
      <div v-if="!debugPromptCollapsed" class="max-h-[52vh] overflow-auto rounded-xl border border-white/10 bg-black/25 p-3">
        <pre class="whitespace-pre-wrap break-words text-[11px] leading-relaxed text-white/70">{{ safeStringify(debugPrompt) }}</pre>
      </div>
      <div v-else class="text-xs text-[var(--muted)]">
        开发阶段用于排查提示词/入参，后期可隐藏或删除。
      </div>
    </ReportSectionCard>
  </div>
</template>

<script setup lang="ts">
defineOptions({ name: 'ChartReportTab' });

import { ref, computed, watch, onUnmounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useStore } from '../composables/useStore';
import ReportSectionCard from '../components/ReportSectionCard.vue';
import ReportSectionStatusCard from '../components/ReportSectionStatusCard.vue';
import ReportSectionContent from '../components/ReportSectionContent.vue';
import { useBaziReportStream } from '../composables/useBaziReportStream';
import type { BaziReportV1, LegacyReport, Report } from '../types';
import { normalizeChartForRequest } from '../utils/chart';
import thinkingIconUrl from '../assets/svg/thinking-tripple-full.svg';
import sparkleIconUrl from '../assets/sparkles.png';
import type { ArchiveReportState } from '../utils/storage';

const route = useRoute();
const router = useRouter();
const { chart, analysis, report, activeArchiveId, updateActiveArchiveReportState, devMode } = useStore();

const chartId = computed(() => route.params.id as string);
const stream = useBaziReportStream();
const uiError = ref('');
const debugPromptCollapsed = ref(true);

// 开发早期用于排查模型输出/提示词；生产构建默认不显示（后期可直接删掉这块）
const ENABLE_DEBUG_PROMPT_PANEL = import.meta.env.DEV;

const streamState = stream.state;
const streamHasSections = computed(() => streamState.sectionsPlan.length > 0);
const streamSectionsPlan = computed(() => streamState.sectionsPlan);
const mergedError = computed(() => uiError.value || streamState.error || '');
const shouldShowStreamView = computed(() =>
  stream.isStreaming.value || (!!mergedError.value || (!report.value && streamHasSections.value))
);
const isGenerating = computed(() => stream.isStreaming.value);

const legacyRawPrompt = computed(() => {
  const value = report.value;
  if (!value) return null;
  const maybe = value as LegacyReport;
  return maybe?.raw_prompt ?? null;
});

const debugPrompt = computed(() => streamState.prompt ?? legacyRawPrompt.value ?? null);
const shouldShowDebugPrompt = computed(() => devMode.value && ENABLE_DEBUG_PROMPT_PANEL && !!debugPrompt.value);

const SAMPLE_REPORT = {
  meta: {
    version: 'bazi_report_v1',
    generated_at: '2026-01-16T08:13:28.093Z',
    language: 'zh-CN',
    tone: '温和中肯',
    disclaimer: '本报告仅基于已提供事实进行解读，不构成确定性承诺或医疗/投资建议。',
  },
  input_refs: {
    solar_date: '1999年10月17日',
    lunar_date: '1999年9月9日',
    birth_time: '9点9分',
    bazi_str: '己卯 甲戌 壬寅 乙巳',
    gender: '男',
    cur_dayun: '辛未',
    cur_liunian: '乙巳',
    day_master: '壬',
    five_elements_count: '木6，火4，土5，金2，水1',
    pattern_tags: ['身强', '官杀偏旺', '食伤泄秀'],
    yong_shen: ['土', '水'],
    ji_shen: ['水', '金', '火'],
  },
  sections: [
    {
      id: 'chart_basic',
      title: '八字基本命盘分析',
      content_md: '您的八字为 **己卯 甲戌 壬寅 乙巳**，日主为 **壬水**，生于戌月，土旺水弱，但全局木火土众，日主得根于寅中壬水，综合判定为 **身强格局**。五行分布中，**木元素最为旺盛**（占33.3%），其次为土与火，金水相对较弱。命局特点包括 **官杀偏旺** 与 **食伤泄秀**，形成一种既有约束又有输出的能量结构。用神取向为 **土**（官杀）与 **水**（比劫），用以制衡过旺的木火之势；忌神为 **水、金、火**，在相关岁运需注意其影响。',
      structured: {
        day_master_strength: {
          label: '身强',
          confidence: 0.8,
          reasons: [
            '日主壬水得根于日支寅中壬水，但月令戌土克水，全局木火土众，综合判定身强',
          ],
        },
        strength_gauge: {
          score: 76,
          label: '身强',
          confidence: 0.8,
          notes: ['基于五行计数和格局分析，身强程度较高'],
        },
        pattern: {
          name: '身强，官杀偏旺，食伤泄秀',
          reasons: ['日主壬水身强，官杀土元素偏旺，食伤木元素泄秀'],
        },
        yong_ji: {
          yong_shen: ['土', '水'],
          ji_shen: ['水', '金', '火'],
          notes: ['用神土以制木、水以助身；忌神水金火可能加剧克泄耗，需谨慎应对'],
        },
      },
    },
    {
      id: 'personality',
      title: '性格底色',
      content_md: '命局食伤星（木）旺盛，赋予您 **聪慧敏捷** 的思维与 **丰富的表达欲**。官杀星（土）偏旺，带来 **较强的责任感** 与 **自我约束力**，但有时也易感压力。日主壬水身强，比肩助身，性格中带有 **独立自主** 的倾向，不喜依赖他人。整体上，您是一个 **内外兼修** 的人，既有创意输出，又能务实落地。',
    },
    {
      id: 'appearance',
      title: '外貌特点',
      content_md: '命局木元素旺盛，通常暗示 **身形较为修长**，举止优雅。火土元素亦有力，可能带来 **面色红润** 与 **骨架结实** 的特点。整体气质 **聪颖而稳重**。',
    },
    {
      id: 'talent_radar',
      title: '特长天赋雷达图',
      content_md: '从十神角度看，食伤木星主导 **学习吸收** 与 **创意表达**，官杀土星强化 **执行落地** 与 **统筹领导**。财星火星为忌， **商业嗅觉** 需培养审慎眼光；比劫水星为忌， **人际协同** 需注意平衡。',
      structured: {
        dimensions: [
          { key: 'learning', label: '学习吸收', score: 85 },
          { key: 'execution', label: '执行落地', score: 80 },
          { key: 'leadership', label: '统筹领导', score: 75 },
          { key: 'creativity', label: '创意表达', score: 85 },
          { key: 'business', label: '商业嗅觉', score: 60 },
          { key: 'relationship', label: '人际协同', score: 65 },
        ],
        ten_gods_basis: [
          { god: '食神', weight: 0.3, notes: '月干甲木食神，主导学习与创意' },
          { god: '伤官', weight: 0.25, notes: '年支卯木伤官、时干乙木伤官，增强表达与才华' },
          { god: '正官', weight: 0.2, notes: '年干己土正官，带来责任感与纪律' },
          { god: '七杀', weight: 0.15, notes: '月支戌土、日支寅土、时支巳土中藏七杀，强化执行与压力应对' },
          { god: '偏财', weight: 0.05, notes: '日支寅火、时支巳火中藏偏财，但为忌神，商业活动需谨慎' },
          { god: '比肩', weight: 0.05, notes: '日干壬水比肩，为忌神，人际合作需注意' },
        ],
        career_matches: ['教育、研发、创意设计', '项目管理、工程技术', '管理咨询、公共事务'],
      },
    },
    {
      id: 'career_industry',
      title: '适合的工作/行业',
      content_md: '结合命局特点，您适合从事需要 **智力输出** 与 **严谨执行** 的领域。例如 **教育、研发、创意设计** 能发挥食伤优势； **项目管理、工程技术** 则契合官杀特质。避免过度依赖 **投机性商业** 或 **高风险投资**，因财星为忌。在 **公共事务、管理咨询** 等领域，您的统筹能力可得施展。',
    },
    {
      id: 'wealth_career',
      title: '财富/事业',
      content_md: '财富结构上， **技能变现** 是您最可靠的收入来源，食伤旺相利于专业深耕。 **资源整合** 通过官杀运筹，亦有潜力。正偏财为忌， **投资投机** 需格外谨慎。',
      structured: {
        wealth_sources: [
          { key: 'zhengcai', label: '正财', score: 60, notes: '正财藏于月支戌中，需通过稳定工作获取' },
          { key: 'piancai', label: '偏财', score: 55, notes: '偏财透于日时支，但为忌神，额外收入需审慎' },
          { key: 'skill', label: '技能变现', score: 85, notes: '食伤旺，专业技能强，易通过才华获利' },
          { key: 'resource', label: '资源整合', score: 75, notes: '官杀旺，有管理资源能力，适合整合运作' },
          { key: 'investment', label: '投资投机', score: 40, notes: '财星为忌，投资风险高，不宜冒进' },
          { key: 'accumulation', label: '长期积累', score: 70, notes: '用神土，利于通过持续努力积累财富' },
        ],
        summary: '财富以技能和专业为主，投资需谨慎，长期积累可期',
      },
    },
    {
      id: 'love_marriage',
      title: '姻缘/感情',
      content_md: '配偶宫坐寅木，藏食神、偏财、七杀，暗示伴侣可能 **聪慧能干**，且具备一定经济能力。但寅巳刑害，感情中需注意 **沟通磨合** 与 **潜在冲突**。官杀为用神，婚姻能带来 **责任感提升** 与 **人生稳定**。宜选择 **性格稳重、务实** 的伴侣，以土元素补益为佳。',
    },
    {
      id: 'family',
      title: '家庭六亲',
      content_md: '年柱正官坐伤官，父母辈可能 **管教较严**，但亦鼓励才华发展。月柱食神透干，家庭氛围 **重视教育与文化**，利于早年智力启蒙。日支寅木为妻宫，与月支戌土半合，暗示 **配偶与家庭关系融洽**。但时柱伤官，子女缘需注意 **教育方式**，避免过度放纵。',
    },
    {
      id: 'health',
      title: '身体健康',
      content_md: '命局木土相战，需关注 **脾胃系统** 的健康，避免饮食不节。火元素为忌，注意 **心血管** 与 **炎症** 问题，保持作息规律。用神土水，可通过 **适度运动** 与 **饮食调理** 强化体质。金元素为忌， **呼吸道** 也需留意，尤其在干燥季节。',
    },
    {
      id: 'recent_trend',
      title: '近年趋势与提醒',
      content_md: '当前大运辛未（2022-2032），金土气势，用神土得助，利于 **事业积累**，但忌神金亦现，需防 **过度压力** 与 **健康波动**。2026乙巳年，木火忌神旺， **工作压力** 增大，财务需保守。2027丙午年，火势更烈， **情绪管理** 与 **健康保养** 尤为重要。2028戊申年，土用神透干， **运势回升**，有利项目推进。2029己酉年，土金相生， **稳步前进**，但忌神金需注意细节。2030庚戌年，金土， **持续积累**，可把握机会。',
      structured: {
        trend_lines: {
          years: [2026, 2027, 2028, 2029, 2030],
          series: [
            {
              key: 'overall',
              label: '综合走势',
              values: [50, 45, 70, 60, 60],
            },
          ],
          dayun_context: '当前大运辛未，金土气势，用神土得助，但忌神金亦现，流年需结合五行生克判断。',
          notes: ['2026-2027火旺忌神年，运势较低；2028后土用神年，运势回升'],
        },
      },
    },
    {
      id: 'summary',
      title: '总结',
      content_md: '综上所述，您的命局以 **身强食伤泄秀** 为核心，用神土水为助力。行动上，优先 **强化专业技能**、 **务实积累资源**，并 **规避财务风险**。',
      structured: {
        action_priorities: [
          { rank: 1, title: '深耕专业技能', score: 90, why: '食伤旺相，技能变现能力最强', how: '持续学习，考取认证，在专业领域建立权威' },
          { rank: 2, title: '务实工作积累', score: 85, why: '用神土，利于通过稳定工作积累财富', how: '选择稳健行业，注重长期职业规划，避免频繁跳槽' },
          { rank: 3, title: '谨慎投资理财', score: 80, why: '财星为忌，投资投机风险高', how: '以储蓄和低风险理财为主，避免高风险投机' },
          { rank: 4, title: '维护人际关系', score: 70, why: '比劫为忌，人际协同需平衡', how: '选择志同道合的伙伴，避免利益冲突，加强沟通' },
          { rank: 5, title: '注重健康保养', score: 65, why: '木土相战，火忌神，健康需关注', how: '规律作息，均衡饮食，定期体检，适度运动' },
        ],
      },
    },
  ],
};

const getSampleSection = (sectionId: string) => SAMPLE_REPORT.sections.find((item) => item.id === sectionId);
const sampleSectionIdForPlaceholder = (key: string) => {
  if (key === 'overview') return 'chart_basic';
  return key;
};
const sampleSectionForPlaceholder = (key: string) => getSampleSection(sampleSectionIdForPlaceholder(key));

const reportPlaceholders = [
  {
    key: 'overview',
    title: '命局总览',
    description: '概览整体格局与主线关键词。',
    placeholderBars: [68, 100, 82],
  },
  {
    key: 'chart_basic',
    title: '五行强弱',
    description: '概览五行偏旺偏弱与补偏方向。',
    placeholderBars: [60, 96, 78],
  },
  {
    key: 'talent_radar',
    title: '天赋特长',
    description: '简述优势能力与擅长领域画像。',
    placeholderBars: [62, 92, 74],
  },
  {
    key: 'recent_trend',
    title: '运势走势',
    description: '提示近期走势波动与关键节点。',
    placeholderBars: [66, 98, 72],
  },
  {
    key: 'wealth_career',
    title: '财富与事业',
    description: '梳理事业发力点与财源方向。',
    placeholderBars: [70, 94, 76],
  },
  {
    key: 'summary',
    title: '行动建议',
    description: '给出近期行动优先级与提示。',
    placeholderBars: [64, 90, 80],
  },
];

const placeholderSampleMap = ref<Record<string, boolean>>({});
const togglePlaceholderSample = (key: string) => {
  const next = !placeholderSampleMap.value[key];
  placeholderSampleMap.value = {
    ...placeholderSampleMap.value,
    [key]: next,
  };
};
const sectionPlaceholder = (sectionId: string) => {
  const found = reportPlaceholders.find((item) => item.key === sectionId);
  if (found) return found;
  return {
    key: sectionId,
    title: displaySectionTitle(sectionId, sectionId),
    description: '简述该段要点与核心结论。',
    placeholderBars: [64, 96, 78],
  };
};

const safeStringify = (value: unknown) => {
  try {
    return JSON.stringify(value, null, 2);
  } catch (err) {
    return err instanceof Error ? err.message : String(err);
  }
};

const isBaziReportV1 = (value: Report | null): value is BaziReportV1 => {
  if (!value || typeof value !== 'object') return false;
  return 'meta' in value && 'input_refs' in value && 'sections' in value;
};

const toFinalSections = (value: Report): Array<{ key: string; id?: string; title: string; content: string; structured?: unknown }> => {
  if (isBaziReportV1(value)) {
    return value.sections.map((sec) => ({
      key: sec.id,
      id: sec.id,
      title: sec.title,
      content: sec.content_md,
      structured: sec.structured,
    }));
  }
  const legacy = value as LegacyReport;
  return legacy.sections.map((sec, idx) => ({
    key: `${idx}-${sec.title}`,
    title: sec.title,
    content: sec.content,
  }));
};

const finalSections = computed(() => (report.value ? toFinalSections(report.value) : []));

const sectionById = (sectionId: string) => streamState.sections[sectionId] ?? {
  sectionId,
  title: sectionId,
  status: 'idle',
  contentMd: '',
};

const displaySectionTitle = (sectionId: string | undefined, fallbackTitle: string) => {
  if (sectionId === 'talent_radar') return '天赋特长';
  return fallbackTitle;
};

const REPORT_LOADING_MESSAGES = [
  '正在翻译古籍，抽丝剥茧校验格局...',
  '正在翻阅《滴天髓》，寻章摘句校验格局...',
  '正在翻阅《子平真诠》，对照格局与用神...',
  '正在翻阅《三命通会》，推衍岁运变化...',
  '正在掐指一算，核对五行气机...',
  '香火已燃，命理推演渐入佳境...',
  '天机微动，正在校准命盘关键点...',
  '阴阳交感，正梳理运势脉络...',
];
const REPORT_ESTIMATE_KEY = 'report_estimate_ms';
const REPORT_INITIAL_ESTIMATE_MS = 18000;
const REPORT_ESTIMATE_ALPHA = 0.2;
const REPORT_ESTIMATE_MIN_MS = 5000;
const REPORT_ESTIMATE_MAX_MS = 60000;
const REPORT_LOADING_START_PROGRESS = 6;
const REPORT_LOADING_MAX_PROGRESS = 95;
const REPORT_LOADING_TICK_MS = 400;
const reportLoadingProgress = ref(0);
const reportLoadingSeed = ref(0);
const loadReportEstimateMs = () => {
  const raw = localStorage.getItem(REPORT_ESTIMATE_KEY);
  const parsed = raw ? Number.parseFloat(raw) : Number.NaN;
  if (!Number.isFinite(parsed) || parsed <= 0) {
    return REPORT_INITIAL_ESTIMATE_MS;
  }
  return Math.min(REPORT_ESTIMATE_MAX_MS, Math.max(REPORT_ESTIMATE_MIN_MS, parsed));
};
const reportEstimateMs = ref(loadReportEstimateMs());
const saveReportEstimateMs = (value: number) => {
  localStorage.setItem(REPORT_ESTIMATE_KEY, String(Math.round(value)));
};
const updateReportEstimateMs = (elapsedMs: number) => {
  if (!Number.isFinite(elapsedMs) || elapsedMs <= 0) return;
  const current = reportEstimateMs.value;
  const next = Math.min(
    REPORT_ESTIMATE_MAX_MS,
    Math.max(REPORT_ESTIMATE_MIN_MS, current * (1 - REPORT_ESTIMATE_ALPHA) + elapsedMs * REPORT_ESTIMATE_ALPHA),
  );
  reportEstimateMs.value = next;
  saveReportEstimateMs(next);
};
const getReportLoadingProgress = (elapsedMs: number, estimateMs: number) => {
  const normalized = elapsedMs / Math.max(estimateMs, 1);
  const eased = 1 - Math.exp(-normalized * 2.2);
  return Math.round(eased * 100);
};
const reportLoadingMessage = computed(() => {
  if (!stream.isStreaming.value) return '';
  const steps = REPORT_LOADING_MESSAGES.length;
  const bucketSize = 100 / steps;
  const bucket = Math.min(steps - 1, Math.floor(reportLoadingProgress.value / bucketSize));
  const index = (reportLoadingSeed.value + bucket) % steps;
  return REPORT_LOADING_MESSAGES[index];
});
let reportLoadingTimer: number | null = null;
let reportLoadingStartedAt = 0;

// 生成报告
const generateReport = async () => {
  if (!chart.value) {
    uiError.value = '暂无命盘数据，请先填写生辰信息';
    return;
  }
  if (stream.isStreaming.value) return;

  const generationForArchiveId = activeArchiveId.value;
  const generationForChartId = chartId.value;

  uiError.value = '';
  report.value = null;
  stream.reset();

  const payload = {
    chart: normalizeChartForRequest(chart.value),
    focus: []
  };

  try {
    router.push(`/bazi/chart/${route.params.id}/report`);

    await stream.start(payload);

    // 如果用户在生成过程中切换了档案/命盘，就不要把旧结果写进当前档案里
    if (generationForArchiveId !== activeArchiveId.value || generationForChartId !== chartId.value) {
      return;
    }

    if (streamState.analysis) {
      analysis.value = streamState.analysis;
    }

    if (streamState.finalReport) {
      report.value = streamState.finalReport;
      updateActiveArchiveReportState({ updatedAt: Date.now() } satisfies Partial<ArchiveReportState>);
    } else if (!streamState.error && streamHasSections.value) {
      const legacy: LegacyReport = {
        overall_tone: '温和中肯',
        sections: streamSectionsPlan.value.map((sec) => ({
          title: sec.title,
          content: sectionById(sec.sectionId).contentMd || '',
        })),
      };
      report.value = legacy;
      updateActiveArchiveReportState({ updatedAt: Date.now() } satisfies Partial<ArchiveReportState>);
    }

    if (streamState.error) {
      uiError.value = streamState.error;
    }
  } catch (err) {
    if (err instanceof Error && err.name === 'AbortError') {
      // 用户主动取消/切换档案导致的终止：不当作错误展示
      return;
    }
    uiError.value = err instanceof Error ? err.message : '生成报告失败';
  } finally {
    // 这里不主动停止 stream：切换页面时仍应继续生成；stream.isStreaming 会自行收敛
  }
};

const cancelStream = () => {
  stream.abort();
};

watch(() => stream.isStreaming.value, (isLoading) => {
  if (isLoading) {
    reportLoadingSeed.value = Math.floor(Math.random() * REPORT_LOADING_MESSAGES.length);
    reportLoadingStartedAt = Date.now();
    reportLoadingProgress.value = REPORT_LOADING_START_PROGRESS;
    if (reportLoadingTimer) {
      window.clearInterval(reportLoadingTimer);
    }
    const estimateMs = reportEstimateMs.value || REPORT_INITIAL_ESTIMATE_MS;
    reportLoadingTimer = window.setInterval(() => {
      const elapsedMs = Date.now() - reportLoadingStartedAt;
      const progress = Math.min(
        REPORT_LOADING_MAX_PROGRESS,
        Math.max(REPORT_LOADING_START_PROGRESS, getReportLoadingProgress(elapsedMs, estimateMs)),
      );
      reportLoadingProgress.value = Math.max(reportLoadingProgress.value, progress);
    }, REPORT_LOADING_TICK_MS);
  } else {
    if (reportLoadingTimer) {
      window.clearInterval(reportLoadingTimer);
      reportLoadingTimer = null;
    }
    if (reportLoadingStartedAt) {
      updateReportEstimateMs(Date.now() - reportLoadingStartedAt);
    }
    reportLoadingStartedAt = 0;
    reportLoadingProgress.value = 0;
  }
});

onUnmounted(() => {
  if (reportLoadingTimer) {
    window.clearInterval(reportLoadingTimer);
    reportLoadingTimer = null;
  }
});

// 监听 report / debug 信息变化，写回到当前档案
watch(report, (newReport) => {
  if (newReport) {
    uiError.value = '';
  }
  updateActiveArchiveReportState({ report: newReport } satisfies Partial<ArchiveReportState>);
}, { immediate: true });

watch(debugPrompt, (value) => {
  if (!value) return;
  updateActiveArchiveReportState({ debugPrompt: value } satisfies Partial<ArchiveReportState>);
});
</script>
