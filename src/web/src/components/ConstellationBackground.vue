<template>
  <canvas ref="canvasRef" class="absolute inset-0 h-full w-full" aria-hidden="true"></canvas>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue';

type RGB = { r: number; g: number; b: number };

const props = withDefaults(
  defineProps<{
    particleCount?: number;
    maxLinkDistance?: number;
  }>(),
  {
    particleCount: 96,
    maxLinkDistance: 140,
  }
);

const canvasRef = ref<HTMLCanvasElement | null>(null);

type Particle = {
  x: number;
  y: number;
  vx: number;
  vy: number;
  radius: number;
  baseAlpha: number;
  phase: number;
  twinkleSpeed: number;
  twinklePhase: number;
};

const parseColorToRgb = (value: string): RGB | null => {
  const v = value.trim();
  if (!v) return null;

  if (v.startsWith('#')) {
    const hex = v.slice(1);
    const normalized =
      hex.length === 3
        ? hex
            .split('')
            .map((c) => c + c)
            .join('')
        : hex;
    if (normalized.length !== 6) return null;
    const num = Number.parseInt(normalized, 16);
    if (Number.isNaN(num)) return null;
    return { r: (num >> 16) & 255, g: (num >> 8) & 255, b: num & 255 };
  }

  const m = v.match(/rgba?\\(([^)]+)\\)/i);
  if (m) {
    const parts = m[1]
      .split(',')
      .map((p) => p.trim())
      .slice(0, 3)
      .map((p) => Number.parseFloat(p));
    if (parts.length !== 3 || parts.some((n) => Number.isNaN(n))) return null;
    return { r: parts[0], g: parts[1], b: parts[2] };
  }

  return null;
};

const getAccentRgb = (): RGB => {
  const css = getComputedStyle(document.documentElement);
  const accent2 = css.getPropertyValue('--accent-2');
  const accent = css.getPropertyValue('--accent');
  return (
    parseColorToRgb(accent2) ||
    parseColorToRgb(accent) || {
      r: 214,
      g: 160,
      b: 96,
    }
  );
};

const createSeededRandom = (seed: number) => {
  let t = seed >>> 0;
  return () => {
    // xorshift32
    t ^= t << 13;
    t ^= t >>> 17;
    t ^= t << 5;
    return ((t >>> 0) % 1_000_000) / 1_000_000;
  };
};

let rafId: number | null = null;
let particles: Particle[] = [];
let dpr = 1;
let width = 0;
let height = 0;
let accentRgb: RGB = { r: 214, g: 160, b: 96 };
let startAt = 0;

const setupCanvas = () => {
  const canvas = canvasRef.value;
  if (!canvas) return null;

  const rect = canvas.getBoundingClientRect();
  width = Math.max(1, Math.floor(rect.width));
  height = Math.max(1, Math.floor(rect.height));
  dpr = Math.min(2, window.devicePixelRatio || 1);
  canvas.width = Math.floor(width * dpr);
  canvas.height = Math.floor(height * dpr);

  const ctx = canvas.getContext('2d');
  if (!ctx) return null;
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  return ctx;
};

const buildParticles = () => {
  const isMobile = width < 768;
  const count = Math.max(32, Math.floor((isMobile ? 0.7 : 1) * props.particleCount));
  const speed = isMobile ? 0.04 : 0.06;

  particles = Array.from({ length: count }, (_, idx) => {
    const rand = createSeededRandom((idx + 1) * 987654321);
    const radius = 1.2 + rand() * 1.8;
    const baseAlpha = 0.35 + rand() * 0.45;
    const angle = rand() * Math.PI * 2;
    return {
      x: rand() * width,
      y: rand() * height,
      vx: Math.cos(angle) * speed * (0.6 + rand()),
      vy: Math.sin(angle) * speed * (0.6 + rand()),
      radius,
      baseAlpha,
      phase: rand() * Math.PI * 2,
      twinkleSpeed: 0.5 + rand() * 0.9,
      twinklePhase: rand() * Math.PI * 2,
    };
  });
};

const step = (ctx: CanvasRenderingContext2D, t: number) => {
  const time = (t - startAt) / 1000;
  ctx.clearRect(0, 0, width, height);

  const maxDist = (width < 768 ? 0.9 : 1) * props.maxLinkDistance;
  const maxDist2 = maxDist * maxDist;

  for (const p of particles) {
    p.x += p.vx;
    p.y += p.vy;

    const wiggle = 0.18;
    p.x += Math.sin(time * 0.35 + p.phase) * wiggle;
    p.y += Math.cos(time * 0.3 + p.phase) * wiggle;

    if (p.x < -20) p.x = width + 20;
    if (p.x > width + 20) p.x = -20;
    if (p.y < -20) p.y = height + 20;
    if (p.y > height + 20) p.y = -20;
  }

  // 连接线：只画近邻，避免过密
  for (let i = 0; i < particles.length; i += 1) {
    const a = particles[i];
    let links = 0;
    for (let j = i + 1; j < particles.length; j += 1) {
      const b = particles[j];
      const dx = a.x - b.x;
      const dy = a.y - b.y;
      const d2 = dx * dx + dy * dy;
      if (d2 > maxDist2) continue;

      const d = Math.sqrt(d2);
      const k = 1 - d / maxDist;
      const alpha = 0.18 * k;
      ctx.strokeStyle = `rgba(${accentRgb.r},${accentRgb.g},${accentRgb.b},${alpha})`;
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(a.x, a.y);
      ctx.lineTo(b.x, b.y);
      ctx.stroke();

      links += 1;
      if (links >= 3) break;
    }
  }

  // 粒子点
  for (const p of particles) {
    const twinkle = 0.55 + 0.45 * Math.sin(time * p.twinkleSpeed + p.twinklePhase);
    const alpha = p.baseAlpha * twinkle;
    const r = p.radius * (0.92 + 0.12 * twinkle);

    const glow = 10 + r * 2;
    ctx.shadowBlur = glow;
    ctx.shadowColor = `rgba(${accentRgb.r},${accentRgb.g},${accentRgb.b},${Math.min(0.65, alpha)})`;

    const g = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, r * 2.2);
    g.addColorStop(0, `rgba(${accentRgb.r},${accentRgb.g},${accentRgb.b},${alpha})`);
    g.addColorStop(0.55, `rgba(${accentRgb.r},${accentRgb.g},${accentRgb.b},${alpha * 0.25})`);
    g.addColorStop(1, `rgba(${accentRgb.r},${accentRgb.g},${accentRgb.b},0)`);
    ctx.fillStyle = g;
    ctx.beginPath();
    ctx.arc(p.x, p.y, r, 0, Math.PI * 2);
    ctx.fill();
  }

  ctx.shadowBlur = 0;
};

const loop = (ctx: CanvasRenderingContext2D, t: number) => {
  if (!startAt) startAt = t;
  step(ctx, t);
  rafId = window.requestAnimationFrame((next) => loop(ctx, next));
};

const start = () => {
  const prefersReducedMotion = window.matchMedia?.('(prefers-reduced-motion: reduce)')?.matches;
  if (prefersReducedMotion) return;

  accentRgb = getAccentRgb();
  const ctx = setupCanvas();
  if (!ctx) return;
  buildParticles();
  rafId = window.requestAnimationFrame((t) => loop(ctx, t));
};

const stop = () => {
  if (rafId) {
    window.cancelAnimationFrame(rafId);
    rafId = null;
  }
  startAt = 0;
};

const handleResize = () => {
  stop();
  start();
};

onMounted(() => {
  start();
  window.addEventListener('resize', handleResize);
});

onUnmounted(() => {
  stop();
  window.removeEventListener('resize', handleResize);
});
</script>
