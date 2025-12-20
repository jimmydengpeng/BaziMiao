<template>
  <div class="app-shell stack">
    <section class="hero">
      <div>
        <div class="badge">神机喵算 · BaziMiao</div>
        <h1>用 AI 读懂八字，看到趋势与选择</h1>
        <p class="subtitle">
          确定性排盘 + 规则层 + LLM 解读。模型不重算命盘，只负责解释与润色，帮你看到事业、财富、情感的走向。
        </p>
        <div class="cta-row">
          <button class="btn primary" @click="scrollToForm">开始占测</button>
          <button class="btn" @click="prefillExample">填充示例</button>
        </div>
      </div>
      <div class="panel stack">
        <div class="status-line">
          <strong>命盘概览</strong>
          <span class="badge">后端排盘</span>
        </div>
        <div class="card-grid">
          <div class="pill" v-if="analysis?.pattern">
            <span>身强弱</span>
            <strong>{{ analysis?.pattern }}</strong>
          </div>
          <div class="pill" v-if="analysis?.strength_score !== undefined">
            <span>强度</span>
            <strong>{{ analysis?.strength_score }}</strong>
          </div>
          <div class="pill" v-if="analysis?.yi_yong_shen?.length">
            <span>用神</span>
            <strong>{{ analysis?.yi_yong_shen.join("、") }}</strong>
          </div>
          <div class="pill" v-if="analysis?.ji_shen?.length">
            <span>忌神</span>
            <strong>{{ analysis?.ji_shen.join("、") }}</strong>
          </div>
        </div>
        <div class="muted" v-if="!chart">尚未排盘，填写信息后生成命盘与报告。</div>
        <div v-else class="sections">
          <div class="section-card">
            <h3>四柱</h3>
            <div class="card-grid">
              <div class="pill">
                年柱：{{ chart.year_pillar.heaven_stem.name }}{{ chart.year_pillar.earth_branch.name }}
              </div>
              <div class="pill">
                月柱：{{ chart.month_pillar.heaven_stem.name }}{{ chart.month_pillar.earth_branch.name }}
              </div>
              <div class="pill">
                日柱：{{ chart.day_pillar.heaven_stem.name }}{{ chart.day_pillar.earth_branch.name }}
              </div>
              <div class="pill">
                时柱：{{ chart.hour_pillar.heaven_stem.name }}{{ chart.hour_pillar.earth_branch.name }}
              </div>
            </div>
          </div>
          <div class="section-card">
            <h3>大运起运</h3>
            <div class="muted">
              {{ chart.destiny_cycle.start_age.year }}岁{{ chart.destiny_cycle.start_age.month }}月起运，
              {{ chart.destiny_cycle.is_forward ? "顺行" : "逆行" }}。
            </div>
            <div class="card-grid" style="margin-top: 8px">
              <div
                v-for="(lp, idx) in chart.destiny_cycle.destiny_pillars.slice(0, 4)"
                :key="idx"
                class="pill"
              >
                {{ lp.year }} · {{ lp.heaven_stem.name }}{{ lp.earth_branch.name }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="panel stack" ref="formBlock">
      <div class="status-line">
        <strong>填写生辰</strong>
        <span class="muted">仅用于排盘，不会长期存储</span>
      </div>
      <div class="form-grid">
        <div class="field">
          <label>姓名（可选）</label>
          <input v-model="form.name" placeholder="神机喵算用户" />
        </div>
        <div class="field">
          <label>性别</label>
          <select v-model="form.gender">
            <option value="male">男</option>
            <option value="female">女</option>
            <option value="other">其他/不公开</option>
          </select>
        </div>
        <div class="field">
          <label>出生日期时间（公历）</label>
          <input v-model="form.birth" type="datetime-local" />
        </div>
        <div class="field">
          <label>时区偏移（小时，例如北京 +8）</label>
          <input v-model.number="form.tzOffsetHours" type="number" step="1" />
        </div>
        <div class="field">
          <label>关注方向</label>
          <select v-model="form.focus" multiple>
            <option value="事业">事业</option>
            <option value="财富">财富</option>
            <option value="情感">情感</option>
            <option value="健康">健康</option>
          </select>
        </div>
      </div>
      <div class="cta-row">
        <button class="btn primary" :disabled="loading" @click="submit">
          {{ loading ? "生成中..." : "生成报告" }}
        </button>
        <span class="muted" v-if="error">{{ error }}</span>
      </div>
    </section>

    <section class="grid-two">
      <div class="panel stack">
        <div class="status-line">
          <strong>命理报告</strong>
          <span class="badge">LLM 解释器</span>
        </div>
        <div v-if="!report" class="muted">提交后会生成分章节报告。</div>
        <div v-else class="sections">
          <div class="section-card" v-for="(sec, idx) in report.sections" :key="idx">
            <h3>{{ sec.title }}</h3>
            <div>{{ sec.content }}</div>
          </div>
        </div>
      </div>
      <ChatPanel :chart="chart" :analysis="analysis" :focus="form.focus" />
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import ChatPanel from "./components/ChatPanel.vue";
import type { Analysis, Chart, Report, ReportResponse } from "./types";

const formBlock = ref<HTMLElement | null>(null);
const form = ref({
  name: "",
  gender: "male",
  birth: "",
  tzOffsetHours: 8,
  focus: ["事业", "财富"] as string[]
});
const loading = ref(false);
const error = ref("");
const chart = ref<Chart | null>(null);
const analysis = ref<Analysis | null>(null);
const report = ref<Report | null>(null);

const scrollToForm = () => {
  formBlock.value?.scrollIntoView({ behavior: "smooth" });
};

const prefillExample = () => {
  form.value = {
    name: "测试用户",
    gender: "male",
    birth: "1992-07-27T08:00",
    tzOffsetHours: 8,
    focus: ["事业", "财富"]
  };
  scrollToForm();
};

const submit = async () => {
  error.value = "";
  if (!form.value.birth) {
    error.value = "请填写出生日期时间";
    return;
  }
  loading.value = true;
  report.value = null;
  try {
    const res = await fetch("/api/bazi/report", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: form.value.name,
        gender: form.value.gender,
        birth: form.value.birth,
        tz_offset_hours: form.value.tzOffsetHours,
        focus: form.value.focus
      })
    });
    if (!res.ok) throw new Error(await res.text());
    const data = (await res.json()) as ReportResponse;
    chart.value = data.chart;
    analysis.value = data.analysis;
    report.value = data.report;
  } catch (err) {
    error.value = err instanceof Error ? err.message : String(err);
  } finally {
    loading.value = false;
  }
};
</script>
