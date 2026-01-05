<template>
  <div class="relative flex h-full w-full max-w-[900px] flex-col overflow-hidden rounded-[20px] border border-[rgba(255,255,255,0.08)] bg-[rgba(15,15,18,0.4)]">
    <!-- 顶部标题栏 -->
    <header class="relative z-10 flex-shrink-0 border-b border-[rgba(255,255,255,0.15)] bg-[rgba(14,13,19,0.75)] px-6 py-4 backdrop-blur-[32px] backdrop-saturate-[180%] before:absolute before:inset-0 before:bg-gradient-to-br before:from-[rgba(214,160,96,0.05)] before:to-[rgba(240,192,122,0.03)] before:pointer-events-none">
      <div class="relative flex w-full items-center justify-center">
        <div class="absolute left-0 flex gap-2">
          <button
            class="flex h-9 w-9 items-center justify-center rounded-lg border border-[rgba(255,255,255,0.1)] bg-[rgba(255,255,255,0.06)] text-[var(--muted)] transition-all duration-200 hover:bg-[rgba(255,255,255,0.1)] hover:text-[var(--text)] hover:-translate-y-[1px] active:translate-y-0"
            type="button"
            @click="newChat"
            aria-label="新建对话"
          >
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="10" y1="4" x2="10" y2="16"/>
              <line x1="4" y1="10" x2="16" y2="10"/>
            </svg>
          </button>
        </div>
        <div class="flex items-center gap-3">
          <div class="flex items-center gap-3">
            <div class="text-lg font-semibold text-[var(--text)]">神喵大师</div>
            <div class="text-xs text-[#7dd56f]">在线</div>
          </div>
        </div>
        <div class="absolute right-0 flex gap-2">
          <div class="relative inline-block">
            <button
              class="flex h-9 w-9 items-center justify-center rounded-lg border border-[rgba(255,255,255,0.1)] bg-[rgba(255,255,255,0.06)] text-[var(--muted)] transition-all duration-200 hover:bg-[rgba(255,255,255,0.1)] hover:text-[var(--text)] hover:-translate-y-[1px] active:translate-y-0"
              type="button"
              @click="showMenu = !showMenu"
              aria-label="更多"
            >
              <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                <circle cx="10" cy="4" r="1.5"/>
                <circle cx="10" cy="10" r="1.5"/>
                <circle cx="10" cy="16" r="1.5"/>
              </svg>
            </button>
            <!-- 更多菜单 -->
            <div
              v-if="showMenu"
              class="absolute right-0 top-full z-50 mt-2 min-w-[160px] rounded-lg border border-[rgba(255,255,255,0.1)] bg-[rgba(18,20,28,0.95)] p-1 shadow-lg backdrop-blur-xl"
            >
              <button
                class="flex w-full items-center gap-2 rounded-md px-3 py-2 text-sm text-[var(--text)] transition-colors hover:bg-[rgba(255,255,255,0.1)]"
                type="button"
                @click="clearMessages"
              >
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M2 4h12M5.5 4V3a1 1 0 0 1 1-1h3a1 1 0 0 1 1 1v1M7 7v4M9 7v4M3 4l1 9a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1l1-9"/>
                </svg>
                清空本轮对话
              </button>
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- 中间对话区 -->
    <div
      ref="messagesContainer"
      class="flex-1 overflow-y-auto bg-[rgba(18,20,28,0.35)] px-6 pb-6 pt-[calc(68px+24px)] backdrop-blur-[16px] scroll-smooth"
      style="margin-top: -68px;"
    >
      <div class="flex max-w-full flex-col gap-4">
        <!-- 欢迎消息 -->
        <div
          v-if="messages.length === 0"
          class="mx-auto my-[60px] max-w-[480px] rounded-2xl border border-[rgba(255,255,255,0.12)] bg-[rgba(18,20,28,0.65)] p-8 text-center backdrop-blur-[16px]"
        >
          <div class="mx-auto mb-4 flex h-20 w-20 items-center justify-center overflow-hidden rounded-full bg-[rgba(0,0,0,0.2)]">
            <img :src="logoUrl" alt="神喵大师" class="h-full w-full object-cover" />
          </div>
          <h3 class="mb-2 text-2xl font-semibold text-[var(--text)]">你好，我是神喵大师</h3>
          <p class="mb-6 text-sm leading-relaxed text-[var(--muted)]">我精通八字命理，可以为你解答命理相关的问题。</p>
          <div class="flex flex-wrap justify-center gap-2">
            <div class="rounded-lg border border-[rgba(214,160,96,0.3)] bg-[rgba(214,160,96,0.15)] px-3 py-1.5 text-xs text-[var(--accent-2)]">命理解答</div>
            <div class="rounded-lg border border-[rgba(214,160,96,0.3)] bg-[rgba(214,160,96,0.15)] px-3 py-1.5 text-xs text-[var(--accent-2)]">运势分析</div>
            <div class="rounded-lg border border-[rgba(214,160,96,0.3)] bg-[rgba(214,160,96,0.15)] px-3 py-1.5 text-xs text-[var(--accent-2)]">五行咨询</div>
          </div>
        </div>

        <!-- 消息列表 -->
        <div
          v-for="(msg, index) in messages"
          :key="index"
          :class="[
            'flex items-start gap-3 animate-[messageSlideIn_0.3s_ease]',
            msg.role === 'user' ? 'flex-row-reverse' : ''
          ]"
        >
          <div v-if="msg.role === 'assistant'" class="flex h-9 w-9 shrink-0 items-center justify-center overflow-hidden rounded-full bg-[rgba(0,0,0,0.2)] text-2xl leading-none">
            <img :src="logoUrl" alt="喵大师" class="h-full w-full object-cover" />
          </div>
          <div
            :class="[
              'relative max-w-[70%] break-words rounded-2xl px-4 py-3',
              msg.role === 'assistant'
                ? 'rounded-tl rounded-tr-none bg-[rgba(40,45,60,0.35)] backdrop-blur-[12px] border border-[rgba(255,255,255,0.08)]'
                : 'rounded-tr rounded-tl-none bg-gradient-to-br from-[rgba(214,160,96,0.3)] to-[rgba(240,192,122,0.2)] backdrop-blur-[12px] border border-[rgba(240,192,122,0.4)]'
            ]"
          >
            <div class="mb-1 text-sm leading-relaxed text-[var(--text)]" v-html="renderMessageContent(msg.content)"></div>
            <div class="text-[11px] text-[var(--muted)] opacity-70">{{ formatTime(msg.timestamp) }}</div>
          </div>
        </div>

        <!-- 正在输入指示器 -->
        <div v-if="isThinking" class="flex items-start gap-3">
          <div class="flex h-9 w-9 shrink-0 items-center justify-center overflow-hidden rounded-full bg-[rgba(0,0,0,0.2)] text-2xl leading-none">
            <img :src="logoUrl" alt="喵大师" class="h-full w-full object-cover" />
          </div>
          <div class="rounded-2xl rounded-tl bg-[rgba(40,45,60,0.35)] border border-[rgba(255,255,255,0.08)] backdrop-blur-[12px] p-4">
            <div class="flex gap-1 items-center">
              <span class="h-1.5 w-1.5 rounded-full bg-[var(--muted)] animate-[typingBounce_1.4s_infinite_ease-in-out]" style="animation-delay: -0.32s;"></span>
              <span class="h-1.5 w-1.5 rounded-full bg-[var(--muted)] animate-[typingBounce_1.4s_infinite_ease-in-out]" style="animation-delay: -0.16s;"></span>
              <span class="h-1.5 w-1.5 rounded-full bg-[var(--muted)] animate-[typingBounce_1.4s_infinite_ease-in-out]"></span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部输入区 -->
    <div class="flex-shrink-0 border-t border-[rgba(255,255,255,0.08)] bg-[rgba(18,20,28,0.85)] px-6 py-4 backdrop-blur-[20px]">
      <!-- 提示词建议 -->
      <div v-if="suggestedQuestions.length > 0 && messages.length === 0" class="mb-3 overflow-hidden">
        <div class="flex gap-2 overflow-x-auto pb-2 scrollbar-thin scrollbar-thumb-white/20 scrollbar-track-transparent">
          <button
            v-for="(question, index) in suggestedQuestions"
            :key="index"
            class="shrink-0 rounded-full border border-[rgba(214,160,96,0.35)] bg-[rgba(18,20,30,0.55)] px-2.5 py-1.5 text-xs text-[var(--text)] transition-all duration-200 hover:border-[rgba(214,160,96,0.7)] hover:text-[#f3e4c8] hover:-translate-y-[1px]"
            type="button"
            @click="selectSuggestion(question)"
          >
            {{ question }}
          </button>
        </div>
      </div>

      <!-- 输入框 -->
      <div class="flex items-end gap-2">
        <div class="flex flex-1 items-end gap-2 rounded-xl border border-[rgba(255,255,255,0.12)] bg-[rgba(14,16,24,0.7)] p-2">
          <textarea
            v-model="inputText"
            ref="inputTextarea"
            class="max-h-[120px] min-h-[40px] flex-1 resize-none rounded-lg border-0 bg-transparent px-3 py-2 text-sm text-[var(--text)] placeholder-white/40 outline-none"
            placeholder="向神喵大师提问..."
            rows="1"
            @keydown.enter.exact.prevent="sendMessage"
            @input="adjustTextareaHeight"
          ></textarea>
          <button
            :class="[
              'flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-[var(--accent)] to-[var(--accent-2)] text-[#0c0f15] transition-all duration-200 hover:scale-105 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed',
              canSend ? '' : 'opacity-50'
            ]"
            type="button"
            :disabled="!canSend"
            @click="sendMessage"
            aria-label="发送"
          >
            <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
              <path d="M2 10l16-8-8 16-2-8-6-0z" transform="rotate(45 10 10)"/>
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- 点击遮罩关闭菜单 -->
    <div
      v-if="showMenu"
      class="fixed inset-0 z-40 bg-black/20"
      @click="showMenu = false"
    ></div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted, onActivated, onDeactivated } from "vue";
import logoUrl from "../assets/logo-bazi_meow.png";

type Message = {
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
};

// 从 localStorage 恢复聊天记录
const loadMessages = (): Message[] => {
  try {
    const saved = localStorage.getItem("master-chat-messages");
    if (!saved) return [];
    const parsed = JSON.parse(saved);
    // 恢复 Date 对象
    return parsed.map((msg: any) => ({
      ...msg,
      timestamp: new Date(msg.timestamp)
    }));
  } catch (err) {
    console.warn("加载聊天记录失败:", err);
    return [];
  }
};

// 保存聊天记录到 localStorage
const saveMessages = (msgs: Message[]) => {
  try {
    localStorage.setItem("master-chat-messages", JSON.stringify(msgs));
  } catch (err) {
    console.warn("保存聊天记录失败:", err);
  }
};

const messages = ref<Message[]>(loadMessages());
const inputText = ref("");
const isThinking = ref(false);
const isStreamingActive = ref(false); // 追踪是否正在流式接收中
const showMenu = ref(false);
const messagesContainer = ref<HTMLElement | null>(null);
const inputTextarea = ref<HTMLTextAreaElement | null>(null);
let updateTimer: number | null = null; // 用于在激活状态下定期刷新视图的定时器

const suggestedQuestions = ref([
  "八字中的五行是什么意思？",
  "如何看自己的命理格局？",
  "大运对人生有什么影响？",
  "天干地支代表什么？"
]);

const canSend = computed(() => inputText.value.trim().length > 0 && !isThinking.value);

const sendMessage = async () => {
  if (!canSend.value) return;

  const userMessage: Message = {
    role: "user",
    content: inputText.value.trim(),
    timestamp: new Date()
  };

  messages.value.push(userMessage);
  saveMessages(messages.value);
  inputText.value = "";
  resetTextareaHeight();

  // 滚动到底部
  await nextTick();
  scrollToBottom();

  // 调用真实AI API
  isThinking.value = true;

  // 创建一个空的助手消息用于流式更新
  const assistantIndex = messages.value.length;
  messages.value.push({
    role: "assistant",
    content: "",
    timestamp: new Date()
  });

  try {
    // 准备历史消息
    const history = messages.value.slice(0, assistantIndex).map(msg => ({
      role: msg.role,
      content: msg.content
    }));

    const response = await fetch("/api/bazi/general-chat/stream", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ history })
    });

    if (!response.ok) {
      throw new Error(await response.text());
    }

    if (!response.body) {
      throw new Error("浏览器不支持流式响应");
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let buffer = "";

    // 标记开始流式传输
    isStreamingActive.value = true;

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() ?? "";

      for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed) continue;

        try {
          const event = JSON.parse(trimmed);

          if (event.type === "delta") {
            messages.value[assistantIndex].content += event.text;
            // 流式传输过程中实时保存消息
            saveMessages(messages.value);
            await nextTick();
            scrollToBottom();
          } else if (event.type === "done") {
            messages.value[assistantIndex].content = event.reply;
            isThinking.value = false;
            isStreamingActive.value = false; // 流式传输结束
            saveMessages(messages.value);
          } else if (event.type === "error") {
            throw new Error(event.message || "对话失败");
          }
        } catch (parseErr) {
          console.warn("解析事件失败:", parseErr);
        }
      }
    }

    // 处理剩余buffer
    buffer += decoder.decode();
    if (buffer.trim()) {
      const lines = buffer.split("\n");
      for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed) continue;
        try {
          const event = JSON.parse(trimmed);
          if (event.type === "done") {
            messages.value[assistantIndex].content = event.reply;
            isStreamingActive.value = false; // 流式传输结束
            saveMessages(messages.value);
          }
        } catch (parseErr) {
          console.warn("解析最终事件失败:", parseErr);
        }
      }
    }
  } catch (err) {
    const errorMsg = err instanceof Error ? err.message : String(err);
    messages.value[assistantIndex].content = `出错了：${errorMsg}`;
    saveMessages(messages.value);
  } finally {
    isThinking.value = false;
    isStreamingActive.value = false; // 确保在任何情况下都重置状态
    // 清除定时器（如果存在）
    if (updateTimer !== null) {
      clearInterval(updateTimer);
      updateTimer = null;
    }
    await nextTick();
    scrollToBottom();
  }
};

const selectSuggestion = (question: string) => {
  inputText.value = question;
  nextTick(() => {
    adjustTextareaHeight();
    inputTextarea.value?.focus();
  });
};

const clearMessages = () => {
  messages.value = [];
  saveMessages(messages.value);
  showMenu.value = false;
};

const newChat = () => {
  messages.value = [];
  saveMessages(messages.value);
};

const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
  }
};

const adjustTextareaHeight = () => {
  if (!inputTextarea.value) return;
  inputTextarea.value.style.height = "auto";
  const maxHeight = 120;
  const newHeight = Math.min(inputTextarea.value.scrollHeight, maxHeight);
  inputTextarea.value.style.height = `${newHeight}px`;
};

const resetTextareaHeight = () => {
  if (!inputTextarea.value) return;
  inputTextarea.value.style.height = "auto";
};

const formatTime = (date: Date) => {
  const hours = date.getHours().toString().padStart(2, "0");
  const minutes = date.getMinutes().toString().padStart(2, "0");
  return `${hours}:${minutes}`;
};

const renderMessageContent = (content: string) => {
  // 简单的markdown渲染
  return content
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.+?)\*/g, "<em>$1</em>")
    .replace(/`(.+?)`/g, "<code>$1</code>")
    .replace(/\n/g, "<br>");
};

onMounted(() => {
  // 初始化时聚焦输入框
  inputTextarea.value?.focus();
  // 如果有历史消息，滚动到底部
  if (messages.value.length > 0) {
    nextTick(() => {
      scrollToBottom();
    });
  }
});

// 组件被激活时（从其他页面切回来）
onActivated(() => {
  // 重新聚焦输入框
  inputTextarea.value?.focus();
  // 滚动到底部，显示最新消息
  nextTick(() => {
    scrollToBottom();
  });

  // 如果正在流式传输，启动定时器持续刷新视图
  if (isStreamingActive.value) {
    // 立即强制刷新一次最后一条消息
    const lastIndex = messages.value.length - 1;
    if (lastIndex >= 0 && messages.value[lastIndex].role === "assistant") {
      // 通过重新赋值触发响应式更新
      const lastMsg = messages.value[lastIndex];
      messages.value[lastIndex] = { ...lastMsg };
    }

    // 设置定时器，每100ms刷新一次视图，直到流式传输结束
    updateTimer = window.setInterval(() => {
      if (!isStreamingActive.value) {
        // 流式传输已结束，清除定时器
        if (updateTimer !== null) {
          clearInterval(updateTimer);
          updateTimer = null;
        }
        return;
      }

      // 强制刷新最后一条消息
      const idx = messages.value.length - 1;
      if (idx >= 0 && messages.value[idx].role === "assistant") {
        const msg = messages.value[idx];
        messages.value[idx] = { ...msg };
        nextTick(() => {
          scrollToBottom();
        });
      }
    }, 100);
  }
});

// 组件被停用时（切换到其他页面）
onDeactivated(() => {
  // 清除定时器
  if (updateTimer !== null) {
    clearInterval(updateTimer);
    updateTimer = null;
  }
  // 保存当前状态到 localStorage
  saveMessages(messages.value);
});
</script>

<style scoped>
/* 消息滑入动画 */
@keyframes messageSlideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 输入指示器动画 */
@keyframes typingBounce {
  0%, 80%, 100% {
    opacity: 0.4;
    transform: scale(0.8);
  }
  40% {
    opacity: 1;
    transform: scale(1);
  }
}

/* 消息内容深度选择器 */
.message-content :deep(strong) {
  font-weight: 600;
  color: var(--accent-2);
}

.message-content :deep(code) {
  background: rgba(255, 255, 255, 0.08);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
  font-size: 13px;
}

.suggestion-chip {
  flex-shrink: 0;
  padding: 8px 14px;
  background: rgba(60, 70, 100, 0.4);
  border: 1px solid rgba(100, 120, 160, 0.3);
  border-radius: 20px;
  color: var(--text);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.suggestion-chip:hover {
  background: rgba(214, 160, 96, 0.2);
  border-color: rgba(214, 160, 96, 0.4);
  transform: translateY(-1px);
}

.input-container {
  width: 100%;
}

.input-wrapper {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  background: rgba(15, 20, 30, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 16px;
  padding: 12px 16px;
  transition: all 0.2s ease;
}

.input-wrapper:focus-within {
  border-color: rgba(240, 192, 122, 0.4);
  background: rgba(15, 20, 30, 0.8);
}

.chat-input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  color: var(--text);
  font-size: 14px;
  line-height: 1.5;
  resize: none;
  max-height: 120px;
  overflow-y: auto;
  font-family: inherit;
}

.chat-input::placeholder {
  color: var(--muted);
  opacity: 0.6;
}

.send-btn {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(120deg, var(--accent), var(--accent-2));
  border: none;
  border-radius: 10px;
  color: #0c0f15;
  cursor: pointer;
  transition: all 0.2s ease;
}

.send-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(214, 160, 96, 0.4);
}

.send-btn:active:not(:disabled) {
  transform: translateY(0);
}

.send-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

/* 更多菜单 */
.menu-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: transparent;
  z-index: 9;
}

.menu-panel {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  background: rgba(18, 20, 28, 0.95);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 12px;
  padding: 8px;
  min-width: 180px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  animation: fadeIn 0.2s ease;
  z-index: 11;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  background: transparent;
  border: none;
  border-radius: 8px;
  color: var(--text);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: left;
}

.menu-item:hover {
  background: rgba(255, 255, 255, 0.08);
}

.menu-item svg {
  flex-shrink: 0;
  opacity: 0.7;
}

/* 响应式 */
@media (max-width: 768px) {
  .master-chat-container {
    border-radius: 0;
    width: 100%;
    height: 100vh;
  }

  .chat-messages {
    padding: 16px;
  }

  .message-bubble {
    max-width: 85%;
  }

  .welcome-card {
    margin: 40px 0;
    padding: 24px;
  }
}
</style>
