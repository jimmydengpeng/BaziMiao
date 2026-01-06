import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import "./styles/tailwind.css";
import "./styles/main.css";

// 安装到主屏幕后禁用缩放，避免 PWA 界面被误触放大
const disableZoomWhenStandalone = () => {
  if (typeof window === "undefined") return;

  const isStandalone =
    window.matchMedia?.("(display-mode: standalone)")?.matches ||
    (navigator as Navigator & { standalone?: boolean }).standalone === true;

  if (!isStandalone) return;

  const viewport = document.querySelector('meta[name="viewport"]');

  if (viewport) {
    const current = viewport.getAttribute("content") ?? "";
    const extras = ["maximum-scale=1", "user-scalable=no"].filter(
      (token) => !current.includes(token),
    );
    const content = [current, ...extras].filter(Boolean).join(", ");
    viewport.setAttribute("content", content);
  }

  document.addEventListener(
    "gesturestart",
    (event) => event.preventDefault(),
    { passive: false },
  );

  let lastTouchEnd = 0;
  document.addEventListener(
    "touchend",
    (event) => {
      const now = Date.now();
      if (now - lastTouchEnd <= 300) {
        event.preventDefault();
      }
      lastTouchEnd = now;
    },
    { passive: false },
  );
};

disableZoomWhenStandalone();

const app = createApp(App);

// 注册路由
app.use(router);

app.mount("#app");
