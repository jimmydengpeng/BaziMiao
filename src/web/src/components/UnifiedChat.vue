<template>
  <!-- 统一聊天组件：支持桌面弹窗模式和移动全屏模式 -->
  <div
    :class="[
      'unified-chat flex min-h-0 flex-col',
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
          <!-- 新建对话按钮 -->
          <button
            class="flex h-9 w-9 items-center justify-center rounded-lg transition-opacity duration-200 hover:opacity-80 active:opacity-60"
            type="button"
            @click="newChat"
            aria-label="新建对话"
          >
            <img :src="chatNewIconUrl" alt="" class="h-6 w-6 object-contain" />
          </button>

          <!-- 更多按钮（三个点） -->
          <div class="relative">
            <button
              class="flex h-9 w-9 items-center justify-center rounded-lg text-[var(--muted)] transition-opacity duration-200 hover:text-[var(--text)] hover:opacity-80 active:opacity-60"
              type="button"
              @click="showMoreMenu = !showMoreMenu"
              aria-label="更多"
            >
              <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                <circle cx="10" cy="4" r="1.5"/>
                <circle cx="10" cy="10" r="1.5"/>
                <circle cx="10" cy="16" r="1.5"/>
              </svg>
            </button>
            <!-- 更多菜单下拉 -->
            <Transition name="menu-fade">
              <div
                v-if="showMoreMenu"
                class="absolute right-0 top-full z-50 mt-2 min-w-[140px] rounded-xl border border-[rgba(255,255,255,0.1)] bg-[rgba(18,20,28,0.95)] py-2 shadow-lg backdrop-blur-xl"
              >
                <button
                  class="flex w-full items-center gap-3 px-4 py-2.5 text-left text-sm text-[var(--text)] transition-colors hover:bg-[rgba(255,255,255,0.08)]"
                  @click="openHistoryFromMenu"
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10"/>
                    <polyline points="12,6 12,12 16,14"/>
                  </svg>
                  历史对话
                </button>
              </div>
            </Transition>
            <!-- 点击外部关闭菜单 -->
            <div
              v-if="showMoreMenu"
              class="fixed inset-0 z-40"
              @click="closeMoreMenu"
            ></div>
          </div>

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

    <!-- 中间对话区：背景渐变固定，不随对话滚动 -->
    <div class="relative min-h-0 flex-1">
      <div
        aria-hidden="true"
        class="pointer-events-none absolute inset-0 bg-gradient-to-b from-[rgba(14,14,21,0.92)] via-[rgba(12,18,44,0.96)] to-[rgba(6,8,18,0.98)]"
      ></div>

      <div
        ref="messagesContainer"
        @scroll.passive="handleMessagesScroll"
        :class="[
          'unified-chat-scroll absolute inset-x-0 top-0 bottom-0 z-[1] overflow-y-auto px-4 md:px-6',
          mode === 'page'
            ? 'pt-[calc(68px+env(safe-area-inset-top,0px))]'
            : 'py-6'
        ]"
        :style="mode === 'page' ? { paddingBottom: `calc(${inputDockHeight}px + 16px)` } : undefined"
      >
        <div class="mx-auto flex max-w-[700px] flex-col gap-5">
        <!-- 欢迎消息 -->
        <div
          v-if="currentMessages.length === 0"
          class="mx-auto my-8 max-w-[420px] rounded-2xl border border-[rgba(255,255,255,0.12)] bg-[rgba(18,20,28,0.7)] p-6 text-center backdrop-blur-xl md:my-12 md:p-8"
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
          v-for="(msg, index) in visibleMessages"
          :key="msg.id"
          :class="[
            'animate-[messageSlideIn_0.3s_ease]',
            msg.role === 'user' ? 'flex justify-end' : ''
          ]"
        >
          <!-- 用户消息：气泡样式 -->
          <div v-if="msg.role === 'user'" class="flex max-w-[75%] flex-col items-end md:max-w-[70%]">
            <div
              class="relative w-full break-words rounded-2xl rounded-br-sm bg-gradient-to-br from-[rgba(214,160,96,0.45)] to-[rgba(240,192,122,0.35)] px-4 py-3 backdrop-blur-md border border-[rgba(240,192,122,0.5)]"
            >
              <div class="text-sm leading-relaxed text-[var(--text)]" v-html="renderMessageContent(msg.content)"></div>
            </div>
            <div class="mt-1 text-[11px] text-[var(--muted)] opacity-70">{{ formatTime(msg.timestamp) }}</div>
          </div>

          <!-- AI 回复：毛玻璃圆角框包裹内容，点赞按钮在框外 -->
          <div v-else class="w-full">
            <!-- AI 回复内容框：毛玻璃深蓝背景 -->
            <div class="rounded-2xl rounded-bl-sm border border-[rgba(255,255,255,0.1)] bg-[rgba(20,28,50,0.25)] px-4 py-3 backdrop-blur-sm">
              <div class="text-sm leading-relaxed text-[var(--text)]" v-html="renderMessageContent(msg.content)"></div>
            </div>
            <!-- 点赞点踩按钮：在框外，只在非流式状态且有内容时显示 -->
            <div
              v-if="msg.content && !isStreamingActive"
              class="mt-2 flex items-center gap-3"
            >
              <button
                :class="[
                  'flex h-7 w-7 items-center justify-center rounded-lg transition-all duration-200',
                  msg.feedback === 'like'
                    ? 'bg-[rgba(125,213,111,0.2)] scale-110'
                    : 'opacity-50 hover:opacity-100 hover:bg-[rgba(255,255,255,0.08)]'
                ]"
                @click="sendFeedback(msg.id, 'like')"
                aria-label="点赞"
              >
                <img :src="thumbUpUrl" alt="" class="h-4 w-4 object-contain" />
              </button>
              <button
                :class="[
                  'flex h-7 w-7 items-center justify-center rounded-lg transition-all duration-200',
                  msg.feedback === 'dislike'
                    ? 'bg-[rgba(200,16,46,0.2)] scale-110'
                    : 'opacity-50 hover:opacity-100 hover:bg-[rgba(255,255,255,0.08)]'
                ]"
                @click="sendFeedback(msg.id, 'dislike')"
                aria-label="点踩"
              >
                <img :src="thumbDownUrl" alt="" class="h-4 w-4 object-contain" />
              </button>
            </div>
          </div>
        </div>

        <!-- 正在思考指示器：渐变闪烁文字 -->
        <div v-if="isThinking" class="animate-[messageSlideIn_0.3s_ease]">
          <div class="thinking-text text-sm py-2">
            {{ displayedThinkingText }}...
          </div>
        </div>
      </div>
      </div>
    </div>

    <!-- 底部输入区：悬浮面板 -->
    <div
      ref="inputDock"
      :class="[
        'flex-shrink-0 px-3 py-2 md:px-4 md:py-3',
        // 移动全屏模式：绝对定位在底部
        mode === 'page'
          ? 'absolute inset-x-0 bottom-0 z-20 pb-[calc(8px+env(safe-area-inset-bottom,0px))]'
          : 'relative z-20'
      ]"
    >
      <!-- 提示词建议 -->
      <div v-if="suggestedQuestions.length > 0 && currentMessages.length === 0" class="mb-3 overflow-hidden px-1">
        <div class="flex gap-2 overflow-x-auto pb-2 scrollbar-thin scrollbar-thumb-white/20 scrollbar-track-transparent">
          <button
            v-for="(question, index) in suggestedQuestions"
            :key="index"
            class="shrink-0 rounded-full border border-[rgba(255,255,255,0.15)] bg-[rgba(18,20,30,0.7)] px-3 py-1.5 text-xs text-[var(--text)] backdrop-blur-md transition-all duration-200 hover:border-[rgba(214,160,96,0.7)] hover:text-[#f3e4c8] hover:-translate-y-[1px]"
            type="button"
            @click="selectSuggestion(question)"
          >
            {{ question }}
          </button>
        </div>
      </div>

      <!-- 悬浮输入面板：毛玻璃 + 全圆角 -->
      <div class="flex flex-col gap-1.5 rounded-3xl border border-[rgba(124,125,131,0.18)] bg-[rgba(22,22,25,0.55)] px-1.5 py-2 shadow-[0_-8px_16px_rgba(10,10,10,0.55)] backdrop-blur-3xl">
        <!-- 上层：输入区域（点击进入输入状态） -->
        <div class="flex" @click="focusInput">
          <textarea
            v-model="inputText"
            ref="inputTextarea"
            class="max-h-[160px] min-h-[40px] w-full flex-1 resize-none border-0 bg-transparent px-2 py-1.5 text-sm text-[var(--text)] placeholder-white/40 outline-none"
            placeholder="向喵算大师提问..."
            rows="1"
            @keydown.enter.exact.prevent="handleSendOrStop"
            @input="adjustTextareaHeight"
          ></textarea>
        </div>

        <!-- 下层：功能区（左/右两个区域） -->
        <div class="flex items-center justify-between gap-2 px-1">
          <div class="flex min-w-0 items-center gap-2">
            <!-- 1. “+” 选择档案 -->
            <button
              class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full border border-white/10 bg-white/5 text-white/85 transition hover:bg-white/10 active:opacity-70"
              type="button"
              @click="toggleArchivePicker"
              aria-label="选择命主档案"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M12 5v14M5 12h14"/>
              </svg>
            </button>

            <!-- 2. 当前对话命主名称（可切换选中/未选中） -->
            <button
              :class="[
                'min-w-0 max-w-[52vw] md:max-w-[380px] truncate rounded-full border px-2 py-1 text-sm transition',
                selectedArchive
                  ? (subjectEnabled ? 'border-[rgba(214,160,96,0.55)] bg-[rgba(214,160,96,0.18)] text-[var(--accent-2)]' : 'border-white/10 bg-white/5 text-white/75 hover:bg-white/10')
                  : 'border-white/10 bg-white/5 text-white/60'
              ]"
              type="button"
              @click="toggleSubjectEnabled"
              :aria-pressed="subjectEnabled"
              :disabled="!selectedArchive"
	            >
	              {{ selectedArchive ? selectedArchive.displayName : '未选择命主' }}
	            </button>

	            <!-- 3. 模型选择（本地 / DeepSeek） -->
	            <button
	              :class="[
	                'ui-sans-font shrink-0 rounded-full border px-2.5 py-1 text-sm transition',
	                selectedLlmProvider === 'deepseek'
	                  ? 'border-[rgba(88,150,250,0.55)] bg-[rgba(88,150,250,0.14)] text-[#7fb0ff]'
	                  : 'border-white/10 bg-white/5 text-white/75 hover:bg-white/10'
	              ]"
	              type="button"
	              @click="toggleLlmProvider"
	              aria-label="选择模型"
	            >
	              {{ selectedLlmProvider === 'deepseek' ? 'DeepSeek' : '本地' }}
	            </button>

	            <!-- 4. 深度思考（仅 DeepSeek 可切换；本地默认开启） -->
	            <button
	              :class="[
	                'ui-sans-font shrink-0 rounded-xl border px-2.5 py-1 text-sm transition',
	                effectiveDeepThinkingEnabled
	                  ? 'border-[rgba(125,213,111,0.55)] bg-[rgba(125,213,111,0.16)] text-[#7dd56f]'
	                  : 'border-white/10 bg-white/5 text-white/75 hover:bg-white/10',
	                selectedLlmProvider === 'local' ? 'cursor-not-allowed opacity-70' : ''
	              ]"
	              type="button"
	              @click="toggleDeepThinking"
	              :aria-pressed="effectiveDeepThinkingEnabled"
	              :disabled="selectedLlmProvider === 'local'"
	            >
	              深度思考
	            </button>
	          </div>

	          <!-- 右侧：发送/停止按钮（保持原逻辑） -->
	          <button
            :class="[
              'flex h-9 w-9 shrink-0 items-center justify-center rounded-full transition-all duration-200',
              isStreamingActive
                ? 'bg-[rgba(59,66,92,0.52)] ring-1 ring-white/10 hover:bg-[rgba(18,20,28,1)]'
                : 'bg-gradient-to-br from-[var(--accent)] to-[var(--accent-2)] hover:scale-105 active:scale-95',
              !canSend && !isStreamingActive ? 'opacity-50 cursor-not-allowed' : ''
            ]"
            type="button"
            :disabled="!canSend && !isStreamingActive"
            @click="handleSendOrStop"
            :aria-label="isStreamingActive ? '停止' : '发送'"
          >
            <!-- 发送图标：SVG 向上箭头（深色） -->
            <svg
              v-if="!isStreamingActive"
              class="h-5 w-5 text-[#0a0604]"
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="3"
              stroke-linecap="round"
              stroke-linejoin="round"
              aria-hidden="true"
            >
              <path d="M12 20V4" />
              <path d="M6 10l6-6 6 6" />
            </svg>
            <!-- 停止图标：带圆角的矩形 -->
            <svg v-else width="12" height="12" viewBox="0 0 14 14" fill="currentColor" class="text-white">
              <rect x="0" y="0" width="14" height="14" rx="2" ry="2"/>
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- 历史对话面板 -->
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
        <div class="unified-chat-scroll flex-1 overflow-y-auto p-4">
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

    <!-- 档案选择面板（不离开当前界面） -->
    <teleport to="body">
      <Transition name="menu-fade">
        <div v-if="archivePickerOpen" class="fixed inset-0 z-[500]">
          <div class="absolute inset-0 bg-black/50" @click="closeArchivePicker"></div>
          <div class="absolute inset-x-0 bottom-0 pb-[env(safe-area-inset-bottom,0px)]">
            <div class="mx-auto w-full max-w-[720px] rounded-t-2xl border border-white/10 bg-[rgba(18,20,28,0.96)] shadow-[0_-18px_50px_rgba(0,0,0,0.55)] backdrop-blur-xl">
              <div class="flex items-center justify-between gap-3 px-4 py-3">
                <div class="min-w-0">
                  <div class="text-sm font-semibold text-white/90">选择命主档案</div>
                  <div class="text-[11px] text-white/55">选中后会显示在下方“命主”按钮里</div>
                </div>
                <button
                  class="flex h-9 w-9 items-center justify-center rounded-lg text-white/70 transition hover:bg-white/10 hover:text-white"
                  type="button"
                  @click="closeArchivePicker"
                  aria-label="关闭"
                >
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M18 6L6 18M6 6l12 12"/>
                  </svg>
                </button>
              </div>

              <div class="px-4 pb-4">
                <input
                  v-model="archivePickerQuery"
                  type="text"
                  class="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white/85 placeholder-white/35 outline-none focus:border-[rgba(214,160,96,0.55)]"
                  placeholder="搜索档案名称..."
                />
              </div>

              <div class="max-h-[55vh] overflow-y-auto px-2 pb-4">
                <div v-if="filteredArchives.length === 0" class="px-4 py-8 text-center text-sm text-white/60">
                  暂无可选档案
                </div>
                <button
                  v-for="entry in filteredArchives"
                  :key="entry.id"
                  :class="[
                    'mx-2 mb-2 flex w-[calc(100%-16px)] items-start justify-between gap-3 rounded-xl border px-4 py-3 text-left transition',
                    entry.id === selectedArchiveId ? 'border-[rgba(214,160,96,0.55)] bg-[rgba(214,160,96,0.12)]' : 'border-white/10 bg-white/5 hover:bg-white/10'
                  ]"
                  type="button"
                  @click="selectArchiveForChat(entry.id)"
                >
                  <div class="min-w-0">
                    <div class="truncate text-sm font-medium text-white/90">{{ entry.displayName }}</div>
                    <div class="mt-1 truncate text-xs text-white/55">{{ entry.birthLabel }}</div>
                  </div>
                  <div class="shrink-0 pt-0.5 text-[11px] text-white/45">#{{ entry.id }}</div>
                </button>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </teleport>

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
import { ref, computed, nextTick, onMounted, onActivated, onUnmounted, watch } from "vue";
import logoNavUrl from "../assets/logo-nav.png";
import logoAvatarUrl from "../assets/logo-bazi_meow.png";
import chatNewIconUrl from "../assets/chat_new.png";
import thumbUpUrl from "../assets/thumb-up.png";
import thumbDownUrl from "../assets/thumb-down.png";
import { useUnifiedChatStore } from "../composables/useUnifiedChatStore";
import { useStore } from "../composables/useStore";

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

const {
  historySessions,
  currentMessages,
  currentSessionId,
  isThinking,
  isStreamingActive,
  mutationTick,
  newChat: newChatInStore,
  switchSession: switchSessionInStore,
  deleteSession: deleteSessionInStore,
  sendMessage: sendMessageInStore,
  stopStreaming,
  sendFeedback: sendFeedbackInStore,
} = useUnifiedChatStore();

const { archives, activeArchiveId } = useStore();

// 仅展示“有效消息”：隐藏等待期间用于占位的空 assistant 消息
const visibleMessages = computed(() => currentMessages.value.filter((msg) => {
  if (msg.role !== "assistant") return true;
  return msg.content.trim().length > 0;
}));

// ========== 状态 ==========
const inputText = ref("");
const showHistoryPanel = ref(false);
const showMoreMenu = ref(false); // 更多菜单显示状态
const messagesContainer = ref<HTMLElement | null>(null);
const inputTextarea = ref<HTMLTextAreaElement | null>(null);
const inputDock = ref<HTMLElement | null>(null);
const inputDockHeight = ref(0);
const autoScrollEnabled = ref(true);
const lastScrollTop = ref(0);

// ========== 输入区：命主/档案上下文 ==========
const archivePickerOpen = ref(false);
const archivePickerQuery = ref("");
// 选中的“命主档案”（只影响聊天上下文，不会改变当前浏览的命盘页面）
const selectedArchiveId = ref<number | null>(null);
	// 是否把命主信息一起发给后端（命主按钮的选中/未选中状态）
	const subjectEnabled = ref(true);
	// LLM 渠道选择：local(本地 Ollama) / deepseek(云端)
	const selectedLlmProvider = ref<"local" | "deepseek">("deepseek");
	// 深度思考开关：仅 DeepSeek 可切换；本地默认开启
	const deepThinkingEnabledForDeepseek = ref(false);
// 是否跟随当前正在查看的档案（activeArchiveId）。用户手动选择后会切到 manual。
const archiveSelectionMode = ref<"auto" | "manual">("auto");
const didInitSubjectDefaults = ref(false);

const effectiveDeepThinkingEnabled = computed(() => {
  if (selectedLlmProvider.value === "local") return true;
  return deepThinkingEnabledForDeepseek.value;
});

const toggleLlmProvider = () => {
  selectedLlmProvider.value = selectedLlmProvider.value === "local" ? "deepseek" : "local";
};

const toggleDeepThinking = () => {
  if (selectedLlmProvider.value !== "deepseek") return;
  deepThinkingEnabledForDeepseek.value = !deepThinkingEnabledForDeepseek.value;
};

const selectedArchive = computed(() => {
  if (selectedArchiveId.value == null) return null;
  return archives.value.find((entry) => entry.id === selectedArchiveId.value) ?? null;
});

const filteredArchives = computed(() => {
  const query = archivePickerQuery.value.trim();
  if (!query) return archives.value;
  return archives.value.filter((entry) => {
    const haystack = `${entry.displayName} ${entry.birthLabel} #${entry.id}`.toLowerCase();
    return haystack.includes(query.toLowerCase());
  });
});

const closeArchivePicker = () => {
  archivePickerOpen.value = false;
  archivePickerQuery.value = "";
};

const toggleArchivePicker = () => {
  archivePickerOpen.value = !archivePickerOpen.value;
  if (!archivePickerOpen.value) {
    archivePickerQuery.value = "";
  }
};

const selectArchiveForChat = (archiveId: number) => {
  selectedArchiveId.value = archiveId;
  archiveSelectionMode.value = "manual";
  subjectEnabled.value = true;
  closeArchivePicker();
};

const toggleSubjectEnabled = () => {
  if (!selectedArchive.value) return;
  subjectEnabled.value = !subjectEnabled.value;
};

const focusInput = () => {
  inputTextarea.value?.focus();
};

let inputDockResizeObserver: ResizeObserver | null = null;
const updateInputDockHeight = () => {
  if (!inputDock.value) {
    inputDockHeight.value = 0;
    return;
  }
  inputDockHeight.value = Math.ceil(inputDock.value.getBoundingClientRect().height);
};

// 等待状态随机文字
const thinkingTexts = [
  "正在掐指一算",
  "正在翻阅古籍",
  "正在观星推演",
  "正在卜卦问天",
  "正在参悟玄机",
  "正在排盘校时",
  "正在推演十神旺衰",
  "正在比对天干地支合冲刑害",
  "正在细算流年流月的起伏",
  "正在斟酌用神与忌神",
  "正在核对五行强弱与调候",
  "正在拆解格局与喜忌取舍",
  "正在看大运交接点的变化",
  "正在合参命盘与现实经历",
  "正在抓取关键时间节点",
  "正在整理结论与建议",
  "正在用更直白的话说明白",
  "正在把复杂推演变简单",
  "正在确认你的问题重点",
  "正在把答案写得更具体些",
  "正在结合你提供的信息复核",
  "正在给出可执行的建议清单",
  "正在避免空泛，尽量说人话",
  "正在收尾，马上就好",
];
const currentThinkingText = ref(thinkingTexts[0]);
const displayedThinkingText = ref("");
let thinkingTextTimer: number | null = null;
let thinkingLoopActive = false;

const TYPEWRITER_STEP_MS = 160;
const TYPEWRITER_DONE_PAUSE_MS = 2500;

const pickRandomThinkingText = () => {
  if (thinkingTexts.length === 0) return;
  if (thinkingTexts.length === 1) {
    currentThinkingText.value = thinkingTexts[0];
    return;
  }

  let next = currentThinkingText.value;
  for (let i = 0; i < 6 && next === currentThinkingText.value; i += 1) {
    next = thinkingTexts[Math.floor(Math.random() * thinkingTexts.length)];
  }
  currentThinkingText.value = next;
};

const startThinkingTextCarousel = () => {
  if (thinkingLoopActive) return;
  thinkingLoopActive = true;

  const clearTimer = () => {
    if (thinkingTextTimer === null) return;
    window.clearTimeout(thinkingTextTimer);
    thinkingTextTimer = null;
  };

  const typeText = (text: string) => {
    if (!thinkingLoopActive) return;
    clearTimer();

    if (!text) {
      pickRandomThinkingText();
      return typeText(currentThinkingText.value);
    }

    let index = 1;
    displayedThinkingText.value = text.slice(0, index);

    const step = () => {
      if (!thinkingLoopActive) return;
      if (index >= text.length) {
        thinkingTextTimer = window.setTimeout(() => {
          if (!thinkingLoopActive) return;
          pickRandomThinkingText();
          typeText(currentThinkingText.value);
        }, TYPEWRITER_DONE_PAUSE_MS);
        return;
      }

      index += 1;
      displayedThinkingText.value = text.slice(0, index);
      thinkingTextTimer = window.setTimeout(step, TYPEWRITER_STEP_MS);
    };

    thinkingTextTimer = window.setTimeout(step, TYPEWRITER_STEP_MS);
  };

  // 首次启动：如果外部已经挑好了（sendMessage），就直接用那条；否则随机挑一条。
  if (!currentThinkingText.value) pickRandomThinkingText();
  typeText(currentThinkingText.value);
};

const stopThinkingTextCarousel = () => {
  thinkingLoopActive = false;
  if (thinkingTextTimer !== null) {
    window.clearTimeout(thinkingTextTimer);
    thinkingTextTimer = null;
  }
  displayedThinkingText.value = "";
};

const suggestedQuestions = ref([
  "八字中的五行是什么意思？",
  "如何看自己的命理格局？",
  "大运对人生有什么影响？",
  "天干地支代表什么？"
]);

const canSend = computed(
  () => inputText.value.trim().length > 0 && !isThinking.value && !isStreamingActive.value,
);

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
  const result = newChatInStore();
  if (!result.ok) showToast(result.reason);
  showHistoryPanel.value = false;
  autoScrollEnabled.value = true;
  nextTick(() => {
    scrollToBottom();
    inputTextarea.value?.focus();
  });
};

const switchSession = (sessionId: string) => {
  const result = switchSessionInStore(sessionId);
  if (!result.ok) {
    showToast(result.reason);
    return;
  }
  showHistoryPanel.value = false;
  autoScrollEnabled.value = true;
  nextTick(() => {
    scrollToBottom();
  });
};

const deleteSession = (sessionId: string) => {
  deleteSessionInStore(sessionId);
};

// ========== 消息处理 ==========
const sendMessage = async () => {
  if (!canSend.value) return;

  const text = inputText.value;
  inputText.value = "";
  resetTextareaHeight();

  // 立即给一个文案，避免等待态出现时空白
  pickRandomThinkingText();
  displayedThinkingText.value = currentThinkingText.value.slice(0, 1);

  // 用户主动发送时：强制启用自动滚动，确保 AI 回复期间始终贴底
  autoScrollEnabled.value = true;

  // 命主信息：只有 subjectEnabled 为 true 时才随消息发送（目前只传姓名 + 出生日期文本，简化后端处理）
  const subject = subjectEnabled.value && selectedArchive.value
    ? { name: selectedArchive.value.displayName, birth: selectedArchive.value.birthLabel }
    : null;

  sendMessageInStore(text, {
    subject,
    deepThinking: effectiveDeepThinkingEnabled.value,
    llmProvider: selectedLlmProvider.value,
  });

  // 发送后立即滚动到底部
  await nextTick();
  scrollToBottom();

  // 再次确保滚动到底部（处理 DOM 更新延迟）
  setTimeout(() => {
    if (autoScrollEnabled.value) {
      scrollToBottom();
    }
  }, 50);
};

// 处理发送/停止按钮点击
const handleSendOrStop = () => {
  if (isStreamingActive.value) {
    stopStreaming();
  } else {
    sendMessage();
  }
};

// 发送反馈
const sendFeedback = (messageId: string, feedback: 'like' | 'dislike') => {
  sendFeedbackInStore(messageId, feedback);
};

// 关闭更多菜单
const closeMoreMenu = () => {
  showMoreMenu.value = false;
};

// 点击更多菜单中的历史对话
const openHistoryFromMenu = () => {
  showMoreMenu.value = false;
  showHistoryPanel.value = true;
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
  const el = messagesContainer.value;
  if (!el) return;
  el.scrollTop = el.scrollHeight;
  lastScrollTop.value = el.scrollTop;
};

const isNearBottom = () => {
  const el = messagesContainer.value;
  if (!el) return true;
  const threshold = 80;
  return el.scrollHeight - (el.scrollTop + el.clientHeight) <= threshold;
};

const handleMessagesScroll = () => {
  const el = messagesContainer.value;
  if (!el) return;

  // 关键：只要用户往上滚（哪怕一点点），就立刻关闭自动贴底
  const currentTop = el.scrollTop;
  const scrolledUp = currentTop < lastScrollTop.value - 2;
  lastScrollTop.value = currentTop;
  if (scrolledUp) {
    autoScrollEnabled.value = false;
    return;
  }

  autoScrollEnabled.value = isNearBottom();
};

const adjustTextareaHeight = () => {
  if (!inputTextarea.value) return;
  inputTextarea.value.style.height = "auto";
  const maxHeight = 160;
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

// 让聊天“命主上下文”默认跟随当前正在查看的档案（activeArchiveId），用户手动选中后则不再自动跟随
watch([archives, activeArchiveId], ([nextArchives, nextActiveId]) => {
  // 当前选中的档案不存在了（被删除等），则回退到 auto 模式
  if (selectedArchiveId.value !== null) {
    const exists = nextArchives.some((entry) => entry.id === selectedArchiveId.value);
    if (!exists) {
      selectedArchiveId.value = null;
      archiveSelectionMode.value = "auto";
    }
  }

  if (archiveSelectionMode.value === "auto") {
    const fallbackId = nextArchives[0]?.id ?? null;
    selectedArchiveId.value = nextActiveId ?? fallbackId;
  } else if (selectedArchiveId.value === null) {
    // manual 模式但没有选中（极端情况）：给一个合理默认值
    selectedArchiveId.value = nextActiveId ?? nextArchives[0]?.id ?? null;
  }

  // 只在首次初始化时自动开启；之后尊重用户的手动开关
  if (!didInitSubjectDefaults.value) {
    subjectEnabled.value = selectedArchiveId.value !== null;
    didInitSubjectDefaults.value = true;
    return;
  }

  // 没有命主可选时，强制关闭（避免“选中但无内容”）
  if (selectedArchiveId.value === null) {
    subjectEnabled.value = false;
  }
}, { immediate: true, deep: true });

// ========== 生命周期 ==========
onMounted(() => {
  // 桌面端自动聚焦，移动端不自动聚焦（避免键盘弹出）
  if (props.mode === 'modal' || !isMobile()) {
    inputTextarea.value?.focus();
  }

  updateInputDockHeight();
  if (typeof ResizeObserver !== "undefined") {
    inputDockResizeObserver = new ResizeObserver(() => {
      updateInputDockHeight();
    });
    if (inputDock.value) {
      inputDockResizeObserver.observe(inputDock.value);
    }
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

  autoScrollEnabled.value = true;
  nextTick(() => {
    scrollToBottom();
  });
});

watch(mutationTick, () => {
  if (!autoScrollEnabled.value) return;
  nextTick(() => {
    scrollToBottom();
  });
});

onUnmounted(() => {
  inputDockResizeObserver?.disconnect();
  inputDockResizeObserver = null;
  stopThinkingTextCarousel();
});

watch(isThinking, (value) => {
  if (value) startThinkingTextCarousel();
  else stopThinkingTextCarousel();
});

</script>

<style scoped>
.unified-chat-scroll {
  -webkit-overflow-scrolling: touch;
  overscroll-behavior: contain;
  touch-action: pan-y;
}

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

/* 渐变闪烁文字动画 */
.thinking-text {
  background: linear-gradient(
    90deg,
    rgba(214, 160, 96, 0.9) 0%,
    rgba(240, 192, 122, 1) 25%,
    rgba(255, 220, 160, 1) 50%,
    rgba(240, 192, 122, 1) 75%,
    rgba(214, 160, 96, 0.9) 100%
  );
  background-size: 200% 100%;
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  animation: shimmer 2s ease-in-out infinite;
}

@keyframes shimmer {
  0% {
    background-position: -100% 50%;
  }
  100% {
    background-position: 100% 50%;
  }
}

/* 更多菜单淡入淡出 */
.menu-fade-enter-active,
.menu-fade-leave-active {
  transition: all 0.2s ease;
}

.menu-fade-enter-from,
.menu-fade-leave-to {
  opacity: 0;
  transform: translateY(-8px) scale(0.95);
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
