<template>
  <div class="flex min-h-[calc(100vh-64px)] items-center justify-center px-4 py-12">
    <div
      class="w-full max-w-md rounded-2xl border border-[rgba(255,255,255,0.12)] bg-[rgba(18,22,33,0.7)] p-6 text-left shadow-[0_20px_60px_rgba(0,0,0,0.45)] backdrop-blur-xl"
    >
      <div class="mb-4 flex items-center gap-2 text-xs uppercase tracking-[0.2em] text-[var(--accent)]">
        <span class="h-1.5 w-1.5 rounded-full bg-[var(--accent)]"></span>
        <span>登录</span>
      </div>
      <h2 class="mb-2 text-2xl font-semibold text-white">
        {{ isAuthenticated ? "已登录" : "欢迎回来" }}
      </h2>
      <p class="mb-6 text-sm text-white/60">
        {{ isAuthenticated ? "您已完成登录，可返回首页或继续体验。" : "使用邮箱登录，或一键使用 Google 登录。" }}
      </p>

      <template v-if="!isAuthenticated">
        <form class="space-y-4" @submit.prevent="handleSubmit">
          <label class="block space-y-2">
            <span class="text-sm text-white/80">邮箱</span>
            <input
              v-model.trim="email"
              type="email"
              required
              class="w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-white placeholder-white/40 outline-none transition focus:border-[var(--accent)]"
              placeholder="you@example.com"
            />
          </label>
          <label class="block space-y-2">
            <span class="text-sm text-white/80">密码</span>
            <input
              v-model="password"
              type="password"
              required
              class="w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-white placeholder-white/40 outline-none transition focus:border-[var(--accent)]"
              placeholder="请输入密码"
            />
          </label>
          <button
            type="submit"
            class="inline-flex w-full items-center justify-center gap-2 rounded-lg bg-gradient-to-br from-[var(--accent)] to-[var(--accent-2)] px-4 py-2.5 text-sm font-semibold text-[#0a0604] shadow-[0_10px_30px_rgba(214,160,96,0.35)] transition hover:-translate-y-[1px] active:translate-y-0"
          >
            邮箱登录
          </button>
        </form>

        <div class="my-4 flex items-center gap-2 text-xs uppercase tracking-[0.2em] text-white/40">
          <span class="h-px flex-1 bg-white/10"></span>
          <span>或</span>
          <span class="h-px flex-1 bg-white/10"></span>
        </div>

        <button
          type="button"
          class="inline-flex w-full items-center justify-center gap-2 rounded-lg border border-white/15 bg-white/5 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-white/10"
          @click="handleGoogle"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <path
              d="M21.6 12.2273C21.6 11.5182 21.5273 10.8364 21.3909 10.1818H12V14.05H17.0455C16.8273 15.1682 16.2 16.1091 15.2591 16.7409V19.2682H18.3091C20.0727 17.6455 21.6 15.1909 21.6 12.2273Z"
              fill="#4285F4"
            />
            <path
              d="M12 21.6C14.7 21.6 16.9636 20.7091 18.3091 19.2682L15.2591 16.7409C14.5364 17.2182 13.5636 17.5091 12 17.5091C9.38637 17.5091 7.19093 15.8682 6.4091 13.5091H3.27271V16.1091C4.6091 19.2818 8.04547 21.6 12 21.6Z"
              fill="#34A853"
            />
            <path
              d="M6.4091 13.5091C6.2091 13.0318 6.1 12.5091 6.1 12C6.1 11.4909 6.2091 10.9682 6.4091 10.4909V7.89087H3.27271C2.6091 9.28178 2.2091 10.7909 2.2091 12.4C2.2091 14.0091 2.6091 15.5182 3.27271 16.9091L6.4091 13.5091Z"
              fill="#FBBC05"
            />
            <path
              d="M12 6.49087C13.7 6.49087 15.0182 7.08178 15.9818 7.99087L18.3818 5.59087C16.9636 4.29087 14.7 3.40002 12 3.40002C8.04547 3.40002 4.6091 5.71825 3.27271 8.89087L6.4091 12.4909C7.19093 10.1318 9.38637 8.49087 12 8.49087Z"
              fill="#EA4335"
            />
          </svg>
          <span>使用 Google 登录</span>
        </button>

        <p class="mt-4 text-center text-xs text-white/50">
          登录功能待接入账号体系，当前为占位交互。
        </p>
      </template>

      <template v-else>
        <div class="rounded-xl border border-[rgba(255,255,255,0.12)] bg-white/5 p-4 text-white/80">
          登录成功状态占位。后续可在此展示账户信息、历史记录等。
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";

const props = defineProps<{
  isAuthenticated?: boolean;
}>();

const emit = defineEmits<{
  (e: "login"): void;
}>();

const email = ref("");
const password = ref("");

const handleSubmit = () => {
  emit("login");
};

const handleGoogle = () => {
  emit("login");
};
</script>
