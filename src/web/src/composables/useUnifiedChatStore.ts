/**
 * 统一聊天（UnifiedChat）全局状态 + 流式请求管理
 *
 * 目标：
 * - 流式读取与 UI 解耦：组件卸载/路由回退后仍能继续接收；
 * - 组件回来后继续显示当前进度（同一个 SPA 会话内）；
 * - 同步写入 localStorage，保证“看见当前回答到哪了”（即使回来时没有订阅者也能恢复）。
 */

import { computed, ref } from "vue";

export type MessageRole = "user" | "assistant";

export type FeedbackType = 'like' | 'dislike';

export type Message = {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: Date;
  feedback?: FeedbackType; // 点赞/点踩反馈
};

export type ChatSession = {
  id: string;
  title: string;
  preview: string;
  messages: Message[];
  createdAt: Date;
  updatedAt: Date;
  archiveId?: number | null;
  // draft 会话：空对话占位，不写入 localStorage，也不出现在历史列表
  isDraft?: boolean;
};

export type ChatSubject = {
  name: string;
  birth: string;
  gender?: string;
  destiny?: string;
  chart?: unknown;
};

export type SendMessageOptions = {
  // 命主上下文（可选）：用于把“姓名 + 出生日期文本”发送给后端做提示词增强
  subject?: ChatSubject | null;
  // 深度思考开关（可选）
  deepThinking?: boolean;
  // LLM 渠道（可选）
  llmProvider?: "local" | "openai";
  // 自定义系统提示词（可选，覆盖默认）
  systemPrompt?: string | null;
};

const STORAGE_KEY = "unified-chat-sessions";
const CURRENT_SESSION_KEY = "unified-chat-current-session";

const chatSessions = ref<ChatSession[]>([]);
const currentSessionId = ref<string | null>(null);
const isThinking = ref(false);
const isStreamingActive = ref(false);

// 用于触发 UI 在“delta 合并刷新”后做滚动等副作用
const mutationTick = ref(0);

// 当前流的归属（防止并发流写错会话/消息）
const activeStream = ref<{
  sessionId: string;
  messageId: string;
  abortController: AbortController;
} | null>(null);

let initialized = false;

const bumpMutation = () => {
  mutationTick.value += 1;
};

const safeParseSessions = (raw: string): ChatSession[] => {
  const parsed = JSON.parse(raw);
  return (parsed as any[]).map((s: any) => ({
    ...s,
    messages: (s.messages ?? []).map((m: any) => ({
      ...m,
      timestamp: new Date(m.timestamp),
    })),
    createdAt: new Date(s.createdAt),
    updatedAt: new Date(s.updatedAt),
  }));
};

const loadSessions = (): ChatSession[] => {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (!saved) return [];
    const sessions = safeParseSessions(saved);
    // 兼容旧数据：过滤掉空会话（新的逻辑不再保存空会话）
    return sessions.filter((s) => Array.isArray(s.messages) && s.messages.length > 0);
  } catch (err) {
    console.warn("加载聊天会话失败:", err);
    return [];
  }
};

const loadCurrentSessionId = (): string | null => {
  try {
    return localStorage.getItem(CURRENT_SESSION_KEY);
  } catch {
    return null;
  }
};

const historySessions = computed(() => chatSessions.value.filter((s) => !s.isDraft));

const currentSession = computed(() => {
  if (!currentSessionId.value) return null;
  return chatSessions.value.find((s) => s.id === currentSessionId.value) ?? null;
});

const currentMessages = computed(() => currentSession.value?.messages ?? []);

const saveSessions = () => {
  try {
    // 只持久化非 draft 且有消息的会话
    localStorage.setItem(STORAGE_KEY, JSON.stringify(historySessions.value));
    const session = currentSession.value;
    if (session && !session.isDraft && session.messages.length > 0) {
      localStorage.setItem(CURRENT_SESSION_KEY, session.id);
    } else {
      localStorage.removeItem(CURRENT_SESSION_KEY);
    }
  } catch (err) {
    console.warn("保存聊天会话失败:", err);
  }
};

let persistTimer: number | null = null;
const schedulePersist = () => {
  // 关键优化：流式阶段不要每个 chunk 都写 localStorage，会卡 UI
  if (persistTimer !== null) return;
  persistTimer = window.setTimeout(() => {
    persistTimer = null;
    saveSessions();
  }, 350);
};

const generateSessionId = () =>
  `session_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;

const generateMessageId = () =>
  `msg_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;

const createNewSession = (options?: { isDraft?: boolean; archiveId?: number | null }): ChatSession => {
  const session: ChatSession = {
    id: generateSessionId(),
    title: "",
    preview: "新对话",
    messages: [],
    createdAt: new Date(),
    updatedAt: new Date(),
    archiveId: options?.archiveId ?? null,
    isDraft: options?.isDraft ?? false,
  };
  chatSessions.value.unshift(session);
  currentSessionId.value = session.id;
  if (!session.isDraft) saveSessions();
  bumpMutation();
  return session;
};

const cleanupEmptyDraftSession = () => {
  const session = currentSession.value;
  if (!session) return;
  if (!session.isDraft) return;
  if (session.messages.length > 0) return;
  const index = chatSessions.value.findIndex((s) => s.id === session.id);
  if (index > -1) chatSessions.value.splice(index, 1);
};

const updateCurrentSessionMessages = (messages: Message[]) => {
  const session = currentSession.value;
  if (!session) return;

  session.messages = messages;
  session.updatedAt = new Date();

  // draft 只要产生了内容，就转为真实会话并落盘
  if (session.isDraft && messages.length > 0) {
    session.isDraft = false;
  }

  // 更新标题和预览
  const firstUserMsg = messages.find((m) => m.role === "user");
  if (firstUserMsg) {
    session.title =
      firstUserMsg.content.slice(0, 30) + (firstUserMsg.content.length > 30 ? "..." : "");
  }
  const lastMsg = messages[messages.length - 1];
  if (lastMsg) {
    session.preview = lastMsg.content.slice(0, 50) + (lastMsg.content.length > 50 ? "..." : "");
  }

  schedulePersist();
  bumpMutation();
};

const setCurrentSessionArchiveId = (archiveId: number | null) => {
  const session = currentSession.value;
  if (!session) return;
  if (session.archiveId === archiveId) return;
  session.archiveId = archiveId;
  session.updatedAt = new Date();
  schedulePersist();
  bumpMutation();
};

const switchSession = (sessionId: string) => {
  if (isThinking.value || isStreamingActive.value) {
    return { ok: false as const, reason: "正在生成回复，稍后再切换对话" };
  }
  cleanupEmptyDraftSession();
  saveSessions();
  currentSessionId.value = sessionId;
  saveSessions();
  bumpMutation();
  return { ok: true as const };
};

const deleteSession = (sessionId: string) => {
  const index = chatSessions.value.findIndex((s) => s.id === sessionId);
  if (index === -1) return;

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
  bumpMutation();
};

const newChat = () => {
  if (isThinking.value || isStreamingActive.value) {
    return { ok: false as const, reason: "正在生成回复，稍后再新建对话" };
  }

  const session = currentSession.value;
  const isAlreadyNewChat = !session || session.messages.length === 0;
  if (isAlreadyNewChat) {
    return { ok: false as const, reason: "当前已经是新对话，无需新建" };
  }

  // 当前会话有记录：确保落盘后再开启一轮新的空对话（空对话不落盘）
  saveSessions();
  cleanupEmptyDraftSession();
  createNewSession({ isDraft: true });
  saveSessions();
  bumpMutation();
  return { ok: true as const };
};

const stopStreaming = () => {
  activeStream.value?.abortController.abort();
};

// 发送反馈（点赞/点踩）
const sendFeedback = async (messageId: string, feedback: FeedbackType) => {
  const session = currentSession.value;
  if (!session) return;

  const message = session.messages.find((m) => m.id === messageId);
  if (!message) return;

  // 如果已经是同样的反馈，取消反馈
  if (message.feedback === feedback) {
    message.feedback = undefined;
  } else {
    message.feedback = feedback;
  }

  schedulePersist();
  bumpMutation();

  // 发送到后端
  try {
    await fetch("/api/bazi/feedback", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: session.id,
        message_id: messageId,
        feedback: message.feedback ?? null,
      }),
    });
  } catch (err) {
    console.warn("发送反馈失败:", err);
  }
};

const sendMessage = async (content: string, options?: SendMessageOptions) => {
  const text = content.trim();
  if (!text) return;

  // 同一时间只允许一个流（避免并发写错最后一条 assistant message）
  if (isStreamingActive.value) return;

  // 确保有当前会话
  if (!currentSessionId.value) {
    createNewSession({ isDraft: true });
  }

  const messages = [...currentMessages.value];
  const userMessage: Message = {
    id: generateMessageId(),
    role: "user",
    content: text,
    timestamp: new Date(),
  };

  messages.push(userMessage);
  updateCurrentSessionMessages(messages);

  isThinking.value = true;

  const assistantMessage: Message = {
    id: generateMessageId(),
    role: "assistant",
    content: "",
    timestamp: new Date(),
  };
  messages.push(assistantMessage);
  updateCurrentSessionMessages(messages);

  const sessionIdForThisStream = currentSessionId.value!;
  const messageIdForThisStream = assistantMessage.id;

  const abortController = new AbortController();
  activeStream.value = {
    sessionId: sessionIdForThisStream,
    messageId: messageIdForThisStream,
    abortController,
  };

  let flushRaf: number | null = null;
  let pendingDelta = "";
  let didReceiveFirstDelta = false;

  const flushDelta = () => {
    flushRaf = null;
    if (!pendingDelta) return;

    // 注意：流式期间用户可能切换会话/新建对话（我们在 UI 侧禁用，但仍做防御）
    const active = activeStream.value;
    if (!active) return;
    if (active.sessionId !== sessionIdForThisStream) return;

    const session = chatSessions.value.find((s) => s.id === sessionIdForThisStream);
    if (!session) return;

    const last = session.messages.find((m) => m.id === messageIdForThisStream);
    if (!last) return;

    last.content += pendingDelta;
    pendingDelta = "";
    session.updatedAt = new Date();
    schedulePersist();
    bumpMutation();
  };

  const scheduleFlush = () => {
    if (flushRaf !== null) return;
    flushRaf = window.requestAnimationFrame(flushDelta);
  };

  try {
    const history = messages.slice(0, -1).map((msg) => ({
      role: msg.role,
      content: msg.content,
    }));

    isStreamingActive.value = true;

    const response = await fetch("/api/bazi/general-chat/stream", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        history,
        system_prompt: options?.systemPrompt ?? undefined,
        llm_provider: options?.llmProvider ?? "openai",
        subject_enabled: Boolean(options?.subject),
        subject_name: options?.subject?.name ?? undefined,
        subject_birth: options?.subject?.birth ?? undefined,
        subject_gender: options?.subject?.gender ?? undefined,
        subject_destiny: options?.subject?.destiny ?? undefined,
        subject_chart: options?.subject?.chart ?? undefined,
        deep_think: Boolean(options?.deepThinking),
      }),
      signal: abortController.signal,
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
    let doneReceived = false;

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
            pendingDelta += String(event.text ?? "");
            scheduleFlush();
            if (!didReceiveFirstDelta && pendingDelta) {
              didReceiveFirstDelta = true;
              isThinking.value = false;
            }
          } else if (event.type === "done") {
            // 先把 pending delta 刷到 message，再用 done 覆盖最终文本（避免重复/缺字）
            if (flushRaf !== null) {
              window.cancelAnimationFrame(flushRaf);
              flushRaf = null;
            }
            flushDelta();

            const session = chatSessions.value.find((s) => s.id === sessionIdForThisStream);
            const last = session?.messages.find((m) => m.id === messageIdForThisStream);
            if (last) last.content = String(event.reply ?? last.content);
            isThinking.value = false;
            isStreamingActive.value = false;
            activeStream.value = null;
            saveSessions();
            bumpMutation();
            doneReceived = true;
            break;
          } else if (event.type === "error") {
            throw new Error(event.message || "对话失败");
          }
        } catch (parseErr) {
          console.warn("解析事件失败:", parseErr);
        }
      }

      // 收到 done 后就不再继续读取，避免后台仍保持连接导致前端循环等待
      if (doneReceived) break;
    }

    if (doneReceived) {
      try {
        await reader.cancel();
      } catch {
        // ignore
      }
    }

    // 处理剩余 buffer（最后可能没有换行）
    buffer += decoder.decode();
    if (buffer.trim()) {
      const lines = buffer.split("\n");
      for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed) continue;
        try {
          const event = JSON.parse(trimmed);
          if (event.type === "done") {
            if (flushRaf !== null) {
              window.cancelAnimationFrame(flushRaf);
              flushRaf = null;
            }
            flushDelta();

            const session = chatSessions.value.find((s) => s.id === sessionIdForThisStream);
            const last = session?.messages.find((m) => m.id === messageIdForThisStream);
            if (last) last.content = String(event.reply ?? last.content);
            isStreamingActive.value = false;
            activeStream.value = null;
            saveSessions();
            bumpMutation();
          }
        } catch (parseErr) {
          console.warn("解析最终事件失败:", parseErr);
        }
      }
    }
  } catch (err) {
    // fetch 被 abort 时：不弹错误，直接结束
    if (err instanceof DOMException && err.name === "AbortError") {
      isThinking.value = false;
      isStreamingActive.value = false;
      activeStream.value = null;
      saveSessions();
      bumpMutation();
      return;
    }

    const errorMsg = err instanceof Error ? err.message : String(err);
    const session = chatSessions.value.find((s) => s.id === sessionIdForThisStream);
    const last = session?.messages.find((m) => m.id === messageIdForThisStream);
    if (last) last.content = `出错了：${errorMsg}`;
    schedulePersist();
    bumpMutation();
  } finally {
    isThinking.value = false;
    isStreamingActive.value = false;
    activeStream.value = null;

    if (flushRaf !== null) {
      window.cancelAnimationFrame(flushRaf);
      flushRaf = null;
    }
    if (pendingDelta) {
      flushDelta();
    }
    if (persistTimer !== null) {
      window.clearTimeout(persistTimer);
      persistTimer = null;
    }
    saveSessions();
  }
};

const initializeUnifiedChatStore = () => {
  if (initialized) return;

  chatSessions.value = loadSessions();
  const savedCurrentId = loadCurrentSessionId();

  if (savedCurrentId && chatSessions.value.some((s) => s.id === savedCurrentId)) {
    currentSessionId.value = savedCurrentId;
  } else if (chatSessions.value.length > 0) {
    currentSessionId.value = chatSessions.value[0].id;
  } else {
    createNewSession({ isDraft: true });
  }

  // 统一一次落盘：清理旧的空会话/无效 currentSessionId
  saveSessions();
  initialized = true;
};

export const useUnifiedChatStore = () => {
  if (!initialized) initializeUnifiedChatStore();

  return {
    // state
    chatSessions,
    historySessions,
    currentSessionId,
    currentSession,
    currentMessages,
    isThinking,
    isStreamingActive,
    mutationTick,

    // actions
    createNewSession,
    setCurrentSessionArchiveId,
    switchSession,
    deleteSession,
    newChat,
    sendMessage,
    stopStreaming,
    sendFeedback,
  };
};
