<template>
  <div class="master-chat-container">
    <!-- 顶部标题栏 -->
    <header class="chat-header">
      <div class="chat-header-content">
        <div class="chat-actions-left">
          <button class="icon-btn" type="button" @click="newChat" aria-label="新建对话">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="10" y1="4" x2="10" y2="16"/>
              <line x1="4" y1="10" x2="16" y2="10"/>
            </svg>
          </button>
        </div>
        <div class="chat-title">
          <div class="chat-title-text">
            <div class="chat-name">神喵大师</div>
            <div class="chat-status">在线</div>
          </div>
        </div>
        <div class="chat-actions">
          <div class="menu-container">
            <button class="icon-btn" type="button" @click="showMenu = !showMenu" aria-label="更多">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                <circle cx="10" cy="4" r="1.5"/>
                <circle cx="10" cy="10" r="1.5"/>
                <circle cx="10" cy="16" r="1.5"/>
              </svg>
            </button>
            <!-- 更多菜单 -->
            <div v-if="showMenu" class="menu-panel">
              <button class="menu-item" type="button" @click="clearMessages">
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
    <div class="chat-messages" ref="messagesContainer">
      <div class="messages-wrapper">
        <!-- 欢迎消息 -->
        <div v-if="messages.length === 0" class="welcome-card">
          <div class="welcome-avatar">
            <img :src="logoUrl" alt="神喵大师" class="welcome-avatar-img" />
          </div>
          <h3>你好，我是神喵大师</h3>
          <p class="muted">我精通八字命理，可以为你解答命理相关的问题。</p>
          <div class="welcome-features">
            <div class="feature-tag">命理解答</div>
            <div class="feature-tag">运势分析</div>
            <div class="feature-tag">五行咨询</div>
          </div>
        </div>

        <!-- 消息列表 -->
        <div
          v-for="(msg, index) in messages"
          :key="index"
          class="message-item"
          :class="{ 'message-user': msg.role === 'user', 'message-assistant': msg.role === 'assistant' }"
        >
          <div v-if="msg.role === 'assistant'" class="message-avatar">
            <img :src="logoUrl" alt="喵大师" class="avatar-img" />
          </div>
          <div class="message-bubble">
            <div class="message-content" v-html="renderMessageContent(msg.content)"></div>
            <div class="message-time">{{ formatTime(msg.timestamp) }}</div>
          </div>
        </div>

        <!-- 正在输入指示器 -->
        <div v-if="isThinking" class="message-item message-assistant">
          <div class="message-avatar">
            <img :src="logoUrl" alt="喵大师" class="avatar-img" />
          </div>
          <div class="message-bubble typing-indicator">
            <div class="typing-dots">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部输入区 -->
    <div class="chat-input-area">
      <!-- 提示词建议 -->
      <div v-if="suggestedQuestions.length > 0 && messages.length === 0" class="suggestions-container">
        <div class="suggestions-scroll">
          <button
            v-for="(question, index) in suggestedQuestions"
            :key="index"
            class="suggestion-chip"
            type="button"
            @click="selectSuggestion(question)"
          >
            {{ question }}
          </button>
        </div>
      </div>

      <!-- 输入框 -->
      <div class="input-container">
        <div class="input-wrapper">
          <textarea
            v-model="inputText"
            ref="inputTextarea"
            class="chat-input"
            placeholder="向神喵大师提问..."
            rows="1"
            @keydown.enter.exact.prevent="sendMessage"
            @input="adjustTextareaHeight"
          ></textarea>
          <button
            class="send-btn"
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
    <div v-if="showMenu" class="menu-overlay" @click="showMenu = false"></div>
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
.master-chat-container {
  display: flex;
  flex-direction: column;
  width: 100%;
  max-width: 900px;
  height: 100%;
  margin: 0 auto;
  background: rgba(15, 15, 18, 0.4);
  border-radius: 20px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.08);
  position: relative;
}

/* 顶部标题栏 */
.chat-header {
  background: rgba(14, 13, 19, 0.75);
  backdrop-filter: blur(32px) saturate(180%);
  -webkit-backdrop-filter: blur(32px) saturate(180%);
  border-bottom: 1px solid rgba(255, 255, 255, 0.15);
  padding: 16px 24px;
  flex-shrink: 0;
  position: relative;
  z-index: 10;
}

.chat-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(214, 160, 96, 0.05), rgba(240, 192, 122, 0.03));
  pointer-events: none;
}

.chat-header-content {
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.chat-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.chat-title-text {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 12px;
}

.chat-name {
  font-size: 18px;
  font-weight: 600;
  color: var(--text);
}

.chat-status {
  font-size: 12px;
  color: #7dd56f;
}

.chat-actions-left {
  display: flex;
  gap: 8px;
  position: absolute;
  left: 0;
}

.chat-actions {
  display: flex;
  gap: 8px;
  position: absolute;
  right: 0;
}

.menu-container {
  position: relative;
  display: inline-block;
}

.icon-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: var(--muted);
  cursor: pointer;
  transition: all 0.2s ease;
}

.icon-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: var(--text);
  transform: translateY(-1px);
}

.icon-btn:active {
  transform: translateY(0);
}

/* 消息区域 */
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  padding-top: calc(68px + 24px); /* 标题栏高度 + 原padding */
  margin-top: -68px; /* 负值让消息区域向上延伸到标题栏下方 */
  scroll-behavior: smooth;
  background: rgba(18, 20, 28, 0.35);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
}

.messages-wrapper {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-width: 100%;
}

/* 欢迎卡片 */
.welcome-card {
  background: rgba(18, 20, 28, 0.65);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 16px;
  padding: 32px;
  text-align: center;
  margin: 60px auto;
  max-width: 480px;
}

.welcome-avatar {
  width: 80px;
  height: 80px;
  margin: 0 auto 16px;
  border-radius: 50%;
  overflow: hidden;
  background: rgba(0, 0, 0, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
}

.welcome-avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.welcome-card h3 {
  font-size: 24px;
  font-weight: 600;
  color: var(--text);
  margin-bottom: 8px;
}

.welcome-card p {
  font-size: 14px;
  line-height: 1.6;
  margin-bottom: 24px;
}

.welcome-features {
  display: flex;
  gap: 8px;
  justify-content: center;
  flex-wrap: wrap;
}

.feature-tag {
  padding: 6px 12px;
  background: rgba(214, 160, 96, 0.15);
  border: 1px solid rgba(214, 160, 96, 0.3);
  border-radius: 8px;
  font-size: 12px;
  color: var(--accent-2);
}

/* 消息项 */
.message-item {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  animation: messageSlideIn 0.3s ease;
}

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

.message-user {
  flex-direction: row-reverse;
}

.message-avatar {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  line-height: 1;
  border-radius: 50%;
  overflow: hidden;
  background: rgba(0, 0, 0, 0.2);
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.message-bubble {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 16px;
  position: relative;
  word-wrap: break-word;
}

.message-assistant .message-bubble {
  background: rgba(40, 45, 60, 0.35);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-top-left-radius: 4px;
}

.message-user .message-bubble {
  background: linear-gradient(120deg, rgba(214, 160, 96, 0.3), rgba(240, 192, 122, 0.2));
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(240, 192, 122, 0.4);
  border-top-right-radius: 4px;
}

.message-content {
  font-size: 14px;
  line-height: 1.6;
  color: var(--text);
  margin-bottom: 4px;
}

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

.message-time {
  font-size: 11px;
  color: var(--muted);
  opacity: 0.7;
}

/* 正在输入指示器 */
.typing-indicator {
  padding: 16px;
}

.typing-dots {
  display: flex;
  gap: 4px;
  align-items: center;
}

.typing-dots span {
  width: 6px;
  height: 6px;
  background: var(--muted);
  border-radius: 50%;
  animation: typingBounce 1.4s infinite ease-in-out;
}

.typing-dots span:nth-child(1) {
  animation-delay: -0.32s;
}

.typing-dots span:nth-child(2) {
  animation-delay: -0.16s;
}

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

/* 输入区域 */
.chat-input-area {
  flex-shrink: 0;
  background: rgba(18, 20, 28, 0.85);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  padding: 16px 24px;
}

.suggestions-container {
  margin-bottom: 12px;
  overflow: hidden;
}

.suggestions-scroll {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding-bottom: 8px;
  scrollbar-width: thin;
  scrollbar-color: rgba(255, 255, 255, 0.2) transparent;
}

.suggestions-scroll::-webkit-scrollbar {
  height: 4px;
}

.suggestions-scroll::-webkit-scrollbar-track {
  background: transparent;
}

.suggestions-scroll::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 2px;
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
