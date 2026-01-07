<template>
  <!-- 统一聊天组件：支持桌面弹窗模式和移动全屏模式 -->
  <div
    :class="[
      'unified-chat flex flex-col',
      // 桌面弹窗模式
      mode === 'modal' && 'h-full w-full overflow-hidden rounded-[20px] border border-[rgba(255,255,255,0.12)] bg-gradient-to-br from-[rgba(18,16,24,0.95)] to-[rgba(10,12,18,0.92)] shadow-[0_24px_60px_rgba(0,0,0,0.5)] backdrop-blur-[14px]',
      // 移动全屏模式：绝对定位在外层容器内
      mode === 'page' && 'absolute inset-0 bg-[rgba(12,14,20,0.98)]'
    ]"
  >
    <!-- 顶部标题栏：移动模式绝对定位 -->
    <header
      :class="[
        'z-10 flex-shrink-0 border-b border-[rgba(255,255,255,0.12)] bg-[rgba(14,13,19,0.85)] backdrop-blur-[32px] backdrop-saturate-[180%]',
        mode === 'modal' ? 'relative px-4 py-3 rounded-t-[20px]' : 'absolute inset-x-0 top-0 px-4',
        // 移动全屏模式：标题栏高度与全局 TopNav 对齐（48/56/64 + safe-area）
        mode === 'page' &&
          'box-border h-[calc(48px+env(safe-area-inset-top,0px))] md:h-[calc(56px+env(safe-area-inset-top,0px))] lg:h-[calc(64px+env(safe-area-inset-top,0px))] pt-[env(safe-area-inset-top,0px)]'
      ]"
    >
      <div class="relative flex h-full w-full items-center justify-between">
        <!-- 左侧按钮 -->
        <div class="flex items-center gap-2">
          <!-- 移动全屏模式：返回按钮 -->
          <button
            v-if="mode === 'page'"
            class="flex h-9 w-9 items-center justify-center rounded-lg text-[var(--muted)] transition-opacity duration-200 hover:text-[var(--text)] hover:opacity-80 active:opacity-60"
            type="button"
            @click="handleBack"
            aria-label="返回"
          >
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 4l-6 6 6 6"/>
            </svg>
          </button>
        </div>

        <!-- 中间：Logo + 标题 -->
        <div class="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 flex items-center gap-2">
          <img :src="logoNavUrl" alt="Logo" class="h-7 w-7 object-contain" />
          <span class="text-base font-semibold text-[var(--text)]">喵算大师</span>
          <span class="text-xs text-[#7dd56f]">在线</span>
        </div>

        <!-- 右侧按钮 -->
        <div class="flex items-center gap-2">
          <button
            class="flex h-9 w-9 items-center justify-center rounded-lg transition-opacity duration-200 hover:opacity-80 active:opacity-60"
            type="button"
            @click="showHistoryPanel = true"
            aria-label="对话历史"
          >
            <img :src="chatHistoryIconUrl" alt="" class="h-6 w-6 object-contain" />
          </button>

          <button
            class="flex h-9 w-9 items-center justify-center rounded-lg transition-opacity duration-200 hover:opacity-80 active:opacity-60"
            type="button"
            @click="newChat"
            aria-label="新建对话"
          >
            <img :src="chatNewIconUrl" alt="" class="h-6 w-6 object-contain" />
          </button>

          <!-- 桌面弹窗模式：关闭按钮 -->
          <button
            v-if="mode === 'modal'"
            class="flex h-9 w-9 items-center justify-center rounded-lg text-[var(--muted)] transition-opacity duration-200 hover:text-[var(--text)] hover:opacity-80 active:opacity-60"
            type="button"
            @click="$emit('close')"
            aria-label="关闭"
          >
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="4" y1="4" x2="16" y2="16"/>
              <line x1="16" y1="4" x2="4" y2="16"/>
            </svg>
          </button>
        </div>
      </div>
    </header>

    <!-- 中间对话区：移动模式需要预留顶部和底部空间 -->
    <div
      ref="messagesContainer"
      :class="[
        'flex-1 overflow-y-auto bg-[rgba(18,20,28,0.35)] px-4 backdrop-blur-[16px] scroll-smooth md:px-6',
        mode === 'page' ? 'pt-[calc(68px+env(safe-area-inset-top,0px))] pb-[calc(80px+env(safe-area-inset-bottom,0px))]' : 'py-6'
      ]"
    >
      <div class="mx-auto flex max-w-[700px] flex-col gap-4">
        <!-- 欢迎消息 -->
        <div
          v-if="currentMessages.length === 0"
          class="mx-auto my-8 max-w-[420px] rounded-2xl border border-[rgba(255,255,255,0.1)] bg-[rgba(18,20,28,0.6)] p-6 text-center backdrop-blur-[16px] md:my-12 md:p-8"
        >
          <div class="mx-auto mb-4 flex h-16 w-16 items-center justify-center overflow-hidden rounded-full bg-[rgba(0,0,0,0.25)] md:h-20 md:w-20">
            <img :src="logoAvatarUrl" alt="喵算大师" class="h-full w-full object-cover" />
          </div>
          <h3 class="mb-2 text-xl font-semibold text-[var(--text)] md:text-2xl">你好，我是喵算大师</h3>
          <p class="mb-5 text-sm leading-relaxed text-[var(--muted)]">我精通八字命理，可以为你解答命理相关的问题。</p>
          <div class="flex flex-wrap justify-center gap-2">
            <div class="rounded-lg border border-[rgba(214,160,96,0.3)] bg-[rgba(214,160,96,0.12)] px-3 py-1.5 text-xs text-[var(--accent-2)]">命理解答</div>
            <div class="rounded-lg border border-[rgba(214,160,96,0.3)] bg-[rgba(214,160,96,0.12)] px-3 py-1.5 text-xs text-[var(--accent-2)]">运势分析</div>
            <div class="rounded-lg border border-[rgba(214,160,96,0.3)] bg-[rgba(214,160,96,0.12)] px-3 py-1.5 text-xs text-[var(--accent-2)]">五行咨询</div>
          </div>
        </div>

        <!-- 消息列表 -->
        <div
          v-for="(msg, index) in currentMessages"
          :key="index"
          :class="[
            'flex items-start gap-3 animate-[messageSlideIn_0.3s_ease]',
            msg.role === 'user' ? 'flex-row-reverse' : ''
          ]"
        >
          <div v-if="msg.role === 'assistant'" class="flex h-8 w-8 shrink-0 items-center justify-center overflow-hidden rounded-full bg-[rgba(0,0,0,0.25)] md:h-9 md:w-9">
            <img :src="logoAvatarUrl" alt="喵大师" class="h-full w-full object-cover" />
          </div>
          <div
            :class="[
              'relative max-w-[75%] break-words rounded-2xl px-4 py-3 md:max-w-[70%]',
              msg.role === 'assistant'
                ? 'rounded-tl bg-[rgba(40,45,60,0.4)] backdrop-blur-[12px] border border-[rgba(255,255,255,0.08)]'
                : 'rounded-tr bg-gradient-to-br from-[rgba(214,160,96,0.35)] to-[rgba(240,192,122,0.25)] backdrop-blur-[12px] border border-[rgba(240,192,122,0.45)]'
            ]"
          >
            <div class="mb-1 text-sm leading-relaxed text-[var(--text)]" v-html="renderMessageContent(msg.content)"></div>
            <div class="text-[11px] text-[var(--muted)] opacity-70">{{ formatTime(msg.timestamp) }}</div>
          </div>
        </div>

        <!-- 正在输入指示器 -->
        <div v-if="isThinking" class="flex items-start gap-3">
          <div class="flex h-8 w-8 shrink-0 items-center justify-center overflow-hidden rounded-full bg-[rgba(0,0,0,0.25)] md:h-9 md:w-9">
            <img :src="logoAvatarUrl" alt="喵大师" class="h-full w-full object-cover" />
          </div>
          <div class="rounded-2xl rounded-tl bg-[rgba(40,45,60,0.4)] border border-[rgba(255,255,255,0.08)] backdrop-blur-[12px] p-4">
            <div class="flex gap-1 items-center">
              <span class="h-1.5 w-1.5 rounded-full bg-[var(--muted)] animate-[typingBounce_1.4s_infinite_ease-in-out]" style="animation-delay: -0.32s;"></span>
              <span class="h-1.5 w-1.5 rounded-full bg-[var(--muted)] animate-[typingBounce_1.4s_infinite_ease-in-out]" style="animation-delay: -0.16s;"></span>
              <span class="h-1.5 w-1.5 rounded-full bg-[var(--muted)] animate-[typingBounce_1.4s_infinite_ease-in-out]"></span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部输入区：移动模式绝对定位 -->
    <div
      :class="[
        'flex-shrink-0 border-t border-[rgba(255,255,255,0.08)] bg-[rgba(18,20,28,0.9)] px-4 py-3 backdrop-blur-[20px] md:px-6 md:py-4',
        // 移动全屏模式：绝对定位在底部
        mode === 'page' ? 'absolute inset-x-0 bottom-0 pb-[calc(12px+env(safe-area-inset-bottom,0px))]' : 'relative'
      ]"
    >
      <!-- 提示词建议 -->
      <div v-if="suggestedQuestions.length > 0 && currentMessages.length === 0" class="mb-3 overflow-hidden">
        <div class="flex gap-2 overflow-x-auto pb-2 scrollbar-thin scrollbar-thumb-white/20 scrollbar-track-transparent">
          <button
            v-for="(question, index) in suggestedQuestions"
            :key="index"
            class="shrink-0 rounded-full border border-[rgba(214,160,96,0.35)] bg-[rgba(18,20,30,0.55)] px-3 py-1.5 text-xs text-[var(--text)] transition-all duration-200 hover:border-[rgba(214,160,96,0.7)] hover:text-[#f3e4c8] hover:-translate-y-[1px]"
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
            placeholder="向喵算大师提问..."
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

    <!-- 历史对话面板 -->
    <Transition name="slide-panel">
      <div
        v-if="showHistoryPanel"
        class="absolute inset-0 z-50 flex flex-col bg-[rgba(12,14,20,0.98)] backdrop-blur-lg"
      >
        <!-- 历史面板头部 -->
        <header
          :class="[
            'flex-shrink-0 border-b border-[rgba(255,255,255,0.1)] bg-[rgba(14,13,19,0.9)] px-4 py-3',
            mode === 'page' && 'pt-[calc(12px+env(safe-area-inset-top,0px))]'
          ]"
        >
          <div class="flex items-center justify-between">
            <button
              class="flex h-9 w-9 items-center justify-center rounded-lg text-[var(--muted)] transition-opacity duration-200 hover:text-[var(--text)] hover:opacity-80 active:opacity-60"
              type="button"
              @click="showHistoryPanel = false"
              aria-label="返回"
            >
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 4l-6 6 6 6"/>
              </svg>
            </button>
            <span class="text-base font-semibold text-[var(--text)]">历史对话</span>
            <div class="w-9"></div>
          </div>
        </header>

        <!-- 历史列表 -->
        <div class="flex-1 overflow-y-auto p-4">
          <div v-if="historySessions.length === 0" class="flex flex-col items-center justify-center py-16 text-center">
            <svg class="mb-4 h-12 w-12 text-[var(--muted)] opacity-50" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
            </svg>
            <p class="text-sm text-[var(--muted)]">暂无历史对话</p>
          </div>
          <div v-else class="space-y-2">
            <button
              v-for="session in historySessions"
              :key="session.id"
              :class="[
                'w-full rounded-xl border p-4 text-left transition-all duration-200',
                session.id === currentSessionId
                  ? 'border-[rgba(214,160,96,0.5)] bg-[rgba(214,160,96,0.1)]'
                  : 'border-[rgba(255,255,255,0.08)] bg-[rgba(255,255,255,0.03)] hover:bg-[rgba(255,255,255,0.06)]'
              ]"
              @click="switchSession(session.id)"
            >
              <div class="flex items-start justify-between gap-3">
                <div class="min-w-0 flex-1">
                  <p class="truncate text-sm font-medium text-[var(--text)]">{{ session.title || '新对话' }}</p>
                  <p class="mt-1 truncate text-xs text-[var(--muted)]">{{ session.preview }}</p>
                </div>
                <div class="flex shrink-0 flex-col items-end gap-1">
                  <span class="text-[10px] text-[var(--muted)]">{{ formatSessionDate(session.updatedAt) }}</span>
                  <button
                    class="rounded p-1 text-[var(--muted)] transition-colors hover:bg-[rgba(200,16,46,0.15)] hover:text-[var(--accent-red)]"
                    @click.stop="deleteSession(session.id)"
                    aria-label="删除对话"
                  >
                    <svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5">
                      <path d="M2 4h12M5.5 4V3a1 1 0 0 1 1-1h3a1 1 0 0 1 1 1v1M7 7v4M9 7v4M3 4l1 9a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1l1-9"/>
                    </svg>
                  </button>
                </div>
              </div>
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- 轻提示（Toast）：用于“已是新对话”等弱打断提示 -->
    <teleport to="body">
      <Transition
        enter-active-class="transition-all duration-200 ease-out motion-reduce:transition-none"
        enter-from-class="opacity-0 -translate-y-2"
        enter-to-class="opacity-100 translate-y-0"
        leave-active-class="transition-all duration-150 ease-in motion-reduce:transition-none"
        leave-from-class="opacity-100 translate-y-0"
        leave-to-class="opacity-0 -translate-y-2"
      >
        <div
          v-if="toastVisible"
          class="fixed inset-x-0 z-[400] flex justify-center px-3"
          :style="{ top: `calc(12px + env(safe-area-inset-top, 0px))` }"
        >
          <div class="max-w-[520px] rounded-full border border-white/10 bg-[rgba(18,20,28,0.92)] px-4 py-2 text-sm text-white/90 shadow-[0_12px_30px_rgba(0,0,0,0.45)] backdrop-blur-xl">
            {{ toastMessage }}
          </div>
        </div>
      </Transition>
    </teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted, onActivated, onDeactivated } from "vue";
import logoNavUrl from "../assets/logo-nav.png";
import logoAvatarUrl from "../assets/logo-bazi_meow.png";
import chatHistoryIconUrl from "../assets/chat_history.png";
import chatNewIconUrl from "../assets/chat_new.png";

// Props
const props = withDefaults(defineProps<{
  // 显示模式：modal（桌面弹窗）或 page（移动全屏）
  mode?: 'modal' | 'page';
}>(), {
  mode: 'modal'
});

const emit = defineEmits<{
  (event: "close"): void;
}>();

// ========== 类型定义 ==========
type Message = {
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
};

type ChatSession = {
  id: string;
  title: string;
  preview: string;
  messages: Message[];
  createdAt: Date;
  updatedAt: Date;
  // draft 会话：空对话占位，不写入 localStorage，也不出现在历史列表
  isDraft?: boolean;
};

// ========== 状态 ==========
const inputText = ref("");
const isThinking = ref(false);
const isStreamingActive = ref(false);
const showHistoryPanel = ref(false);
const messagesContainer = ref<HTMLElement | null>(null);
const inputTextarea = ref<HTMLTextAreaElement | null>(null);
let updateTimer: number | null = null;

// 聊天会话管理
const chatSessions = ref<ChatSession[]>([]);
const currentSessionId = ref<string | null>(null);

// 只展示“真正有内容”的历史会话（避免出现一堆空的新对话）
const historySessions = computed(() =>
  chatSessions.value.filter(session => !session.isDraft && session.messages.length > 0)
);

// 当前会话的消息
const currentMessages = computed(() => {
  const session = chatSessions.value.find(s => s.id === currentSessionId.value);
  return session?.messages || [];
});

const suggestedQuestions = ref([
  "八字中的五行是什么意思？",
  "如何看自己的命理格局？",
  "大运对人生有什么影响？",
  "天干地支代表什么？"
]);

const canSend = computed(() => inputText.value.trim().length > 0 && !isThinking.value);

// ========== 存储管理 ==========
const STORAGE_KEY = "unified-chat-sessions";
const CURRENT_SESSION_KEY = "unified-chat-current-session";

const loadSessions = (): ChatSession[] => {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (!saved) return [];
    const parsed = JSON.parse(saved);
    const sessions: ChatSession[] = parsed.map((s: any) => ({
      ...s,
      messages: s.messages.map((m: any) => ({
        ...m,
        timestamp: new Date(m.timestamp)
      })),
      createdAt: new Date(s.createdAt),
      updatedAt: new Date(s.updatedAt)
    }));
    // 兼容旧数据：过滤掉空会话（新的逻辑不再保存空会话）
    return sessions.filter(s => Array.isArray(s.messages) && s.messages.length > 0);
  } catch (err) {
    console.warn("加载聊天会话失败:", err);
    return [];
  }
};

const saveSessions = () => {
  try {
    // 只持久化非 draft 且有消息的会话
    localStorage.setItem(STORAGE_KEY, JSON.stringify(historySessions.value));
    const currentSession = chatSessions.value.find(s => s.id === currentSessionId.value);
    if (currentSession && !currentSession.isDraft && currentSession.messages.length > 0) {
      localStorage.setItem(CURRENT_SESSION_KEY, currentSessionId.value);
    } else {
      localStorage.removeItem(CURRENT_SESSION_KEY);
    }
  } catch (err) {
    console.warn("保存聊天会话失败:", err);
  }
};

const loadCurrentSessionId = (): string | null => {
  try {
    return localStorage.getItem(CURRENT_SESSION_KEY);
  } catch {
    return null;
  }
};

// ========== 会话管理 ==========
const generateSessionId = () => `session_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;

const createNewSession = (options?: { isDraft?: boolean }): ChatSession => {
  const session: ChatSession = {
    id: generateSessionId(),
    title: "",
    preview: "新对话",
    messages: [],
    createdAt: new Date(),
    updatedAt: new Date(),
    isDraft: options?.isDraft ?? false,
  };
  chatSessions.value.unshift(session);
  currentSessionId.value = session.id;
  if (!session.isDraft) saveSessions();
  return session;
};

const getCurrentSession = () =>
  chatSessions.value.find(session => session.id === currentSessionId.value) || null;

const cleanupEmptyDraftSession = () => {
  const session = getCurrentSession();
  if (!session) return;
  if (!session.isDraft) return;
  if (session.messages.length > 0) return;
  const index = chatSessions.value.findIndex(s => s.id === session.id);
  if (index > -1) chatSessions.value.splice(index, 1);
};

// ========== 轻提示（Toast） ==========
const toastVisible = ref(false);
const toastMessage = ref("");
let toastTimer: number | null = null;
const showToast = (message: string) => {
  toastMessage.value = message;
  toastVisible.value = true;
  if (toastTimer !== null) window.clearTimeout(toastTimer);
  toastTimer = window.setTimeout(() => {
    toastVisible.value = false;
    toastTimer = null;
  }, 1800);
};

const newChat = () => {
  if (isThinking.value || isStreamingActive.value) {
    showToast("正在生成回复，稍后再新建对话");
    return;
  }

  const session = getCurrentSession();
  const isAlreadyNewChat = !session || session.messages.length === 0;
  if (isAlreadyNewChat) {
    showToast("当前已经是新对话，无需新建");
    return;
  }

  // 当前会话有记录：确保落盘后再开启一轮新的空对话（空对话不落盘）
  saveSessions();
  cleanupEmptyDraftSession();
  createNewSession({ isDraft: true });
  // 当前是空对话占位：不应记录“上一次会话 id”
  saveSessions();
  nextTick(() => {
    scrollToBottom();
    inputTextarea.value?.focus();
  });
};

const switchSession = (sessionId: string) => {
  if (isThinking.value || isStreamingActive.value) {
    showToast("正在生成回复，稍后再切换对话");
    return;
  }
  // 切换前：有内容的会话需要保存；空的新对话（draft）不保存，直接丢弃
  cleanupEmptyDraftSession();
  saveSessions();
  currentSessionId.value = sessionId;
  showHistoryPanel.value = false;
  saveSessions();
  nextTick(() => {
    scrollToBottom();
  });
};

const deleteSession = (sessionId: string) => {
  const index = chatSessions.value.findIndex(s => s.id === sessionId);
  if (index > -1) {
    chatSessions.value.splice(index, 1);
    // 如果删除的是当前会话，切换到第一个或创建新会话
    if (sessionId === currentSessionId.value) {
      if (chatSessions.value.length > 0) {
        currentSessionId.value = chatSessions.value[0].id;
      } else {
        createNewSession({ isDraft: true });
      }
    }
    saveSessions();
  }
};

const updateCurrentSession = (messages: Message[]) => {
  const session = chatSessions.value.find(s => s.id === currentSessionId.value);
  if (session) {
    session.messages = messages;
    session.updatedAt = new Date();
    // draft 只要产生了内容，就转为真实会话并落盘
    if (session.isDraft && messages.length > 0) {
      session.isDraft = false;
    }
    // 更新标题和预览
    const firstUserMsg = messages.find(m => m.role === 'user');
    if (firstUserMsg) {
      session.title = firstUserMsg.content.slice(0, 30) + (firstUserMsg.content.length > 30 ? '...' : '');
    }
    const lastMsg = messages[messages.length - 1];
    if (lastMsg) {
      session.preview = lastMsg.content.slice(0, 50) + (lastMsg.content.length > 50 ? '...' : '');
    }
    saveSessions();
  }
};

// ========== 消息处理 ==========
const sendMessage = async () => {
  if (!canSend.value) return;

  // 确保有当前会话
  if (!currentSessionId.value) {
    createNewSession();
  }

  const messages = [...currentMessages.value];
  const userMessage: Message = {
    role: "user",
    content: inputText.value.trim(),
    timestamp: new Date()
  };

  messages.push(userMessage);
  updateCurrentSession(messages);
  inputText.value = "";
  resetTextareaHeight();

  await nextTick();
  scrollToBottom();

  // 调用 AI API
  isThinking.value = true;

  const assistantMessage: Message = {
    role: "assistant",
    content: "",
    timestamp: new Date()
  };
  messages.push(assistantMessage);
  updateCurrentSession(messages);

  try {
    const history = messages.slice(0, -1).map(msg => ({
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
            messages[messages.length - 1].content += event.text;
            updateCurrentSession(messages);
            await nextTick();
            scrollToBottom();
          } else if (event.type === "done") {
            messages[messages.length - 1].content = event.reply;
            isThinking.value = false;
            isStreamingActive.value = false;
            updateCurrentSession(messages);
          } else if (event.type === "error") {
            throw new Error(event.message || "对话失败");
          }
        } catch (parseErr) {
          console.warn("解析事件失败:", parseErr);
        }
      }
    }

    // 处理剩余 buffer
    buffer += decoder.decode();
    if (buffer.trim()) {
      const lines = buffer.split("\n");
      for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed) continue;
        try {
          const event = JSON.parse(trimmed);
          if (event.type === "done") {
            messages[messages.length - 1].content = event.reply;
            isStreamingActive.value = false;
            updateCurrentSession(messages);
          }
        } catch (parseErr) {
          console.warn("解析最终事件失败:", parseErr);
        }
      }
    }
  } catch (err) {
    const errorMsg = err instanceof Error ? err.message : String(err);
    messages[messages.length - 1].content = `出错了：${errorMsg}`;
    updateCurrentSession(messages);
  } finally {
    isThinking.value = false;
    isStreamingActive.value = false;
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

// ========== 辅助函数 ==========
const handleBack = () => {
  // ChatPage 需要“先滑出再返回”，这里交给外层处理（ChatPage 监听 close）
  showHistoryPanel.value = false;
  emit("close");
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

const formatSessionDate = (date: Date) => {
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  const days = Math.floor(diff / (1000 * 60 * 60 * 24));

  if (days === 0) {
    return formatTime(date);
  } else if (days === 1) {
    return '昨天';
  } else if (days < 7) {
    return `${days}天前`;
  } else {
    return `${date.getMonth() + 1}/${date.getDate()}`;
  }
};

const renderMessageContent = (content: string) => {
  return content
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.+?)\*/g, "<em>$1</em>")
    .replace(/`(.+?)`/g, "<code>$1</code>")
    .replace(/\n/g, "<br>");
};

// 判断是否为移动设备
const isMobile = () => {
  return window.matchMedia('(max-width: 1023px)').matches;
};

// ========== 生命周期 ==========
onMounted(() => {
  // 加载会话数据
  chatSessions.value = loadSessions();
  const savedCurrentId = loadCurrentSessionId();

  if (savedCurrentId && chatSessions.value.some(s => s.id === savedCurrentId)) {
    currentSessionId.value = savedCurrentId;
  } else if (chatSessions.value.length > 0) {
    currentSessionId.value = chatSessions.value[0].id;
  } else {
    createNewSession({ isDraft: true });
  }
  // 统一一次落盘：清理旧的空会话/无效 currentSessionId
  saveSessions();

  // 桌面端自动聚焦，移动端不自动聚焦（避免键盘弹出）
  if (props.mode === 'modal' || !isMobile()) {
    inputTextarea.value?.focus();
  }

  if (currentMessages.value.length > 0) {
    nextTick(() => {
      scrollToBottom();
    });
  }
});

onActivated(() => {
  // 桌面端自动聚焦，移动端不自动聚焦（避免键盘弹出）
  if (props.mode === 'modal' || !isMobile()) {
    inputTextarea.value?.focus();
  }

  nextTick(() => {
    scrollToBottom();
  });

  if (isStreamingActive.value) {
    updateTimer = window.setInterval(() => {
      if (!isStreamingActive.value) {
        if (updateTimer !== null) {
          clearInterval(updateTimer);
          updateTimer = null;
        }
        return;
      }
      nextTick(() => {
        scrollToBottom();
      });
    }, 100);
  }
});

onDeactivated(() => {
  if (updateTimer !== null) {
    clearInterval(updateTimer);
    updateTimer = null;
  }
  saveSessions();
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

/* 历史面板滑入 */
.slide-panel-enter-active,
.slide-panel-leave-active {
  transition: all 0.3s ease;
}

.slide-panel-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.slide-panel-leave-to {
  opacity: 0;
  transform: translateX(100%);
}

/* 消息内容样式 */
:deep(strong) {
  font-weight: 600;
  color: var(--accent-2);
}

:deep(code) {
  background: rgba(255, 255, 255, 0.08);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
  font-size: 13px;
}
</style>
