<template>
  <div class="panel stack">
    <div class="status-line">
      <strong>对话</strong>
      <span class="badge">基于当前命盘</span>
      <span class="muted">继续追问事业/财富/情感等</span>
    </div>
    <div class="chat" v-if="messages.length">
      <div
        v-for="(msg, idx) in messages"
        :key="idx"
        class="bubble"
        :class="msg.role === 'user' ? 'me' : 'bot'"
      >
        {{ msg.content }}
      </div>
    </div>
    <div v-else class="muted">还没有对话，先问一个问题吧。</div>
    <div class="chat-input">
      <input
        v-model="input"
        type="text"
        placeholder="例如：我适合今年换工作吗？"
        @keydown.enter.prevent="send"
      />
      <button class="btn primary" :disabled="pending || !input" @click="send">
        {{ pending ? "发送中..." : "发送" }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from "vue";
import type { Analysis, Chart, ChatMessage, ChatResponse } from "../types";

const props = defineProps<{
  chart: Chart | null;
  analysis: Analysis | null;
  focus: string[];
}>();

const messages = ref<ChatMessage[]>([]);
const input = ref("");
const pending = ref(false);

watch(
  () => props.chart,
  () => {
    // reset when chart changes
    messages.value = [];
  }
);

const send = async () => {
  if (!input.value.trim() || !props.chart || !props.analysis) return;
  const userMsg: ChatMessage = { role: "user", content: input.value.trim() };
  messages.value.push(userMsg);
  input.value = "";
  pending.value = true;
  try {
    const res = await fetch("/api/bazi/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        chart: props.chart,
        analysis: props.analysis,
        history: messages.value,
        focus: props.focus
      })
    });
    if (!res.ok) throw new Error(await res.text());
    const data = (await res.json()) as ChatResponse;
    const replyText =
      data.reply?.sections?.map((s) => `${s.title}：${s.content}`).join("\n") ||
      data.reply?.overall_tone ||
      "已收到。";
    messages.value.push({ role: "assistant", content: replyText });
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    messages.value.push({ role: "assistant", content: `出错了：${msg}` });
  } finally {
    pending.value = false;
  }
};
</script>
