<template>
  <div class="home-page-wrapper min-h-screen overflow-hidden">
    <!-- 首屏欢迎区 -->
    <section class="home-hero relative flex min-h-screen items-center justify-center overflow-hidden px-4">
      <!-- 装饰性背景元素 - 粒子系统 -->
      <div class="home-decoration pointer-events-none absolute inset-0 overflow-hidden" aria-hidden="true">
        <!-- 金色粒子点 - 使用 v-for 生成 -->
        <div
          v-for="i in particleCount"
          :key="`particle-${i}`"
          class="gold-particle"
          :style="getParticleStyle(i)"
        ></div>
      </div>

      <!-- 主内容 -->
      <div
        class="relative z-10 flex w-full max-w-[calc(100%-32px)] flex-col items-center rounded-[24px] border border-[rgba(214,160,96,0.15)] bg-[rgba(15,15,18,0.35)] px-7 py-10 text-center backdrop-blur-[24px] shadow-[0_20px_60px_rgba(0,0,0,0.5),0_0_80px_rgba(214,160,96,0.1),inset_0_1px_0_rgba(255,255,255,0.05)] sm:max-w-[560px] sm:rounded-[28px] sm:px-9 sm:py-12 md:max-w-[680px] md:rounded-[32px] md:px-12 md:py-14"
      >
        <!-- 项目名称 - 使用书法字体 -->
        <h1
          class="mb-4 bg-[linear-gradient(135deg,#f4d03f_0%,#d6a060_25%,#f0c07a_50%,#d6a060_75%,#f4d03f_100%)] bg-clip-text font-['Ma_Shan_Zheng',serif] text-[clamp(56px,8vw,96px)] font-normal leading-[1.2] tracking-[0.08em] text-transparent drop-shadow-[0_0_40px_rgba(214,160,96,0.4)] opacity-0 animate-[fade-in-up_1s_ease-out_0.2s_forwards,shimmer_3s_ease-in-out_1.2s_infinite]"
        >
          神机喵算
        </h1>

        <!-- 英文副标题 -->
        <div
          class="mb-10 font-['Cinzel',serif] text-[clamp(16px,2vw,22px)] uppercase tracking-[0.3em] text-[var(--accent)] opacity-0 animate-[fade-in-up_1s_ease-out_0.4s_forwards]"
        >
          BaziMiao
        </div>

        <!-- 简介 -->
        <p
          class="mb-4 text-[clamp(15px,1.8vw,18px)] font-medium tracking-[0.05em] text-[rgba(236,227,214,0.9)] opacity-0 animate-[fade-in-up_1s_ease-out_0.6s_forwards]"
        >
          基于八字排盘的 AI 命理 WebApp
        </p>

        <!-- Slogan -->
        <p
          class="mb-12 text-[clamp(14px,1.6vw,17px)] leading-[1.8] tracking-[0.03em] text-[var(--muted)] opacity-0 animate-[fade-in-up_1s_ease-out_0.8s_forwards]"
        >
          用 AI 读懂八字，看到趋势与选择
        </p>

        <!-- 开始按钮 -->
        <button
          class="home-cta group relative inline-flex items-center gap-3 rounded-full bg-gradient-to-br from-[var(--accent)] to-[var(--accent-2)] px-12 py-4 text-lg font-semibold tracking-[0.08em] text-[#0a0604] shadow-[0_8px_24px_rgba(214,160,96,0.3),0_0_60px_rgba(214,160,96,0.2),inset_0_1px_0_rgba(255,255,255,0.3)] transition-transform duration-300 ease-[cubic-bezier(0.4,0,0.2,1)] opacity-0 animate-[fade-in-up_1s_ease-out_1s_forwards] hover:-translate-y-[3px] hover:scale-[1.02] active:-translate-y-[1px]"
          type="button"
          @click="goToForm"
        >
          <span class="relative z-[1]">开始探索</span>
          <span class="relative z-[1] text-2xl transition-transform duration-300 group-hover:translate-x-1.5">→</span>
        </button>

        <!-- 底部装饰文字 -->
        <div
          class="mt-16 flex items-center gap-4 text-[13px] tracking-[0.15em] text-[var(--muted)] opacity-0 animate-[fade-in-up_1s_ease-out_1.2s_forwards] max-[480px]:flex-col max-[480px]:gap-2 max-[480px]:text-[12px]"
        >
          <span class="text-[var(--accent)] opacity-50 max-[480px]:hidden">—</span>
          <span class="font-medium">命由天定 · 运在人为</span>
          <span class="text-[var(--accent)] opacity-50 max-[480px]:hidden">—</span>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

// 粒子系统配置
const particleCount = 128;

// 生成粒子样式的函数
const getParticleStyle = (index: number) => {
  // 使用索引作为随机种子，确保每次渲染位置一致
  const seed = index * 9876543;
  const random = (min: number, max: number, offset: number = 0) => {
    const x = Math.sin(seed + offset) * 10000;
    return min + (Math.abs(x) % (max - min));
  };

  // 随机位置（覆盖整个页面）
  const top = random(5, 95, 1);
  const left = random(5, 95, 2);

  // 随机大小（2-6px）
  const size = Math.floor(random(2, 7, 3));

  // 随机动画延迟（0-10s）
  const delay = random(0, 10, 4);

  // 随机动画时长（6-12s）
  const duration = random(6, 12, 5);

  // 随机透明度变化范围
  const opacity = random(0.4, 0.9, 6);

  return {
    top: `${top}%`,
    left: `${left}%`,
    width: `${size}px`,
    height: `${size}px`,
    animationDelay: `${delay}s`,
    animationDuration: `${duration}s`,
    '--particle-opacity': opacity
  };
};

// 导航到表单页
const goToForm = () => {
  router.push('/bazi/form');
};

// 设置页面样式
onMounted(() => {
  document.documentElement.classList.add('page-home');
  document.documentElement.classList.remove('page-main');
});

onUnmounted(() => {
  document.documentElement.classList.remove('page-home');
});
</script>

<style scoped>
/* 粒子动画样式 */
.gold-particle {
  position: absolute;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(214, 160, 96, var(--particle-opacity, 0.6)) 0%, transparent 70%);
  pointer-events: none;
  animation: particle-float infinite ease-in-out;
}

@keyframes particle-float {
  0%, 100% {
    transform: translateY(0) scale(1);
    opacity: var(--particle-opacity, 0.6);
  }
  50% {
    transform: translateY(-20px) scale(1.1);
    opacity: calc(var(--particle-opacity, 0.6) * 0.4);
  }
}

@keyframes fade-in-up {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes shimmer {
  0%, 100% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
}
</style>
