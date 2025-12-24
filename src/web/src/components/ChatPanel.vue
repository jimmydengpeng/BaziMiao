<template>
  <div class="panel stack chat-panel">
    <div class="status-line">
      <strong>对话</strong>
      <span class="badge">基于当前命盘</span>
      <span class="muted">继续追问事业/财富/情感等</span>
    </div>
    <div class="chat-body">
      <div class="chat" v-if="messages.length" ref="chatScroll">
        <div
          v-for="(msg, idx) in messages"
          :key="idx"
          class="bubble"
          :class="msg.role === 'user' ? 'me' : 'bot'"
        >
          <div
            v-if="msg.role === 'assistant' && msg.thinking"
            class="bubble-thinking"
          >
            <div class="thinking-header">
              <span class="thinking-label">思考</span>
              <button
                class="btn ghost"
                type="button"
                @click="msg.thinkingCollapsed = !msg.thinkingCollapsed"
              >
                {{ msg.thinkingCollapsed ? "展开" : "收起" }}
              </button>
            </div>
            <div v-if="!msg.thinkingCollapsed" class="thinking-text">
              {{ msg.thinking }}
            </div>
          </div>
          <div v-if="msg.content" class="bubble-text">{{ msg.content }}</div>
        </div>
      </div>
      <div v-else class="muted">还没有对话，先问一个问题吧。</div>
    </div>
    <div class="chat-suggestions-header">
      <strong>提问建议</strong>
      <button
        class="btn ghost"
        type="button"
        @click="suggestionsExpanded = !suggestionsExpanded"
      >
        {{ suggestionsExpanded ? "收起" : "展开" }}
      </button>
    </div>
    <div v-if="suggestionsExpanded" class="chat-suggestions">
      <button
        v-for="(item, idx) in suggestions"
        :key="idx"
        type="button"
        class="suggestion-pill"
        :disabled="pending"
        @click="applySuggestion(item)"
      >
        {{ item }}
      </button>
    </div>
    <div class="chat-input">
      <input
        ref="inputRef"
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
import { nextTick, ref, watch } from "vue";
import type { Analysis, Chart, ChatMessage, ChatResponse, ChatStreamEvent } from "../types";

const props = defineProps<{
  chart: Chart | null;
  analysis: Analysis | null;
  focus: string[];
}>();

const messages = ref<ChatMessage[]>([]);
const input = ref("");
const pending = ref(false);
const inputRef = ref<HTMLInputElement | null>(null);
const chatScroll = ref<HTMLDivElement | null>(null);
const suggestionsExpanded = ref(true);

const suggestions = [
  "我今年的姻缘怎么样？",
  "我适合今年换工作吗？",
  "未来三年的财运趋势如何？",
  "我的性格优势和短板是什么？"
];

watch(
  () => props.chart,
  () => {
    // reset when chart changes
    messages.value = [];
    input.value = "";
    pending.value = false;
    suggestionsExpanded.value = true;
  }
);

watch(
  () => messages.value.length,
  (length) => {
    if (length === 0) {
      suggestionsExpanded.value = true;
    }
  }
);

const scrollToBottom = () => {
  const el = chatScroll.value;
  if (!el) return;
  el.scrollTop = el.scrollHeight;
};

const applySuggestion = (text: string) => {
  input.value = text;
  inputRef.value?.focus();
};

const send = async () => {
  if (pending.value || !input.value.trim() || !props.chart || !props.analysis) return;
  const userMsg: ChatMessage = { role: "user", content: input.value.trim() };
  messages.value.push(userMsg);
  const historyPayload = messages.value.map((msg) => ({ role: msg.role, content: msg.content }));
  input.value = "";
  pending.value = true;
  const assistantIndex = messages.value.length;
  messages.value.push({ role: "assistant", content: "", thinking: "", thinkingCollapsed: false });
  await nextTick(scrollToBottom);
  try {
    const payload = JSON.stringify({
      chart: props.chart,
      analysis: props.analysis,
      history: historyPayload,
      focus: props.focus
    });

    const streamReply = async () => {
      const res = await fetch("/api/bazi/chat/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: payload
      });
      if (!res.ok) throw new Error(await res.text());
      if (!res.body) throw new Error("浏览器不支持流式响应");

      const reader = res.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let buffer = "";
      let doneReceived = false;

      const handleLine = (line: string) => {
        const trimmed = line.trim();
        if (!trimmed) return;
        let event: ChatStreamEvent;
        try {
          event = JSON.parse(trimmed) as ChatStreamEvent;
        } catch {
          return;
        }
        if (event.type === "thinking") {
          const current = messages.value[assistantIndex];
          current.thinking = (current.thinking || "") + event.text;
          if (current.thinkingCollapsed === undefined) {
            current.thinkingCollapsed = false;
          }
          void nextTick(scrollToBottom);
          return;
        }
        if (event.type === "delta") {
          messages.value[assistantIndex].content += event.text;
          void nextTick(scrollToBottom);
          return;
        }
        if (event.type === "error") {
          throw new Error(event.message || "对话失败");
        }
        if (event.type === "done") {
          messages.value[assistantIndex].content = event.reply || "已收到。";
          if (event.thinking) {
            messages.value[assistantIndex].thinking = event.thinking;
          }
          suggestionsExpanded.value = false;
          doneReceived = true;
        }
      };

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() ?? "";
        lines.forEach(handleLine);
      }

      buffer += decoder.decode();
      if (buffer.trim()) {
        buffer.split("\n").forEach(handleLine);
      }

      if (!doneReceived) {
        throw new Error("流式响应未返回完成事件");
      }
    };

    const fetchOnce = async () => {
      const res = await fetch("/api/bazi/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: payload
      });
      if (!res.ok) throw new Error(await res.text());
      const data = (await res.json()) as ChatResponse;
      const replyText =
        data.reply?.sections?.map((s) => `${s.title}：${s.content}`).join("\n") ||
        data.reply?.overall_tone ||
        "已收到。";
      messages.value[assistantIndex].content = replyText;
      suggestionsExpanded.value = false;
    };

    try {
      await streamReply();
    } catch (streamErr) {
      await fetchOnce();
    }
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    messages.value[assistantIndex].content = `出错了：${msg}`;
  } finally {
    pending.value = false;
    await nextTick(scrollToBottom);
  }
};
</script>
