---
name: modal-scroll-lock
description: Prevent background page scrolling when a modal/overlay contains scrollable content (scroll chaining / overscroll bounce), especially on iOS Safari. Use when users report "swiping inside the modal scrolls the page behind it" or "modal list won't scroll but the underlying page moves" in SPA apps (Vue/React) with fixed overlays, Teleport/Portal, and nested scroll containers (e.g., .app-scroll).
---

# Modal Scroll Lock

## 目标
- 让“模态弹窗”真正悬浮：底层页面不能滚动（包括 iOS 回弹带动底层）。
- 让弹窗内部的滚动区域正常滚动：比如“省份/城市”两栏列表。
- 兼容常见 SPA 布局：页面滚动不是 body，而是自定义容器（例如 `.app-scroll`）。
- 处理 safe-area：底部按钮/内容不要贴到 iPhone Home 指示条上。

## 快速判断（定位原因）
- 现象：在弹窗里上下滑动时，底层页面在动；弹窗里的列表不滚（或滚到边界后继续带动底层）。
- 根因：浏览器存在“滚动链/回弹传递（scroll chaining / overscroll bounce）”：
  - 手指落点如果不在可滚动容器上，滚动会传递给最近的可滚动祖先（可能是 `.app-scroll` 或 body）。
  - 当内部列表滚到顶/底，继续滑会触发回弹；iOS Safari 常把这部分手势继续传给外层，导致“底下页面在动”的错觉。
  - `z-index` 只影响点击命中，不会自动阻止滚动链。

## 解决方案（推荐组合拳）
按顺序做，通常 2-3 步就能明显改善；iOS 上建议全部做完。

### 1) 确保弹窗内部“真的有可滚动容器”
- 弹窗中间内容区必须有高度约束：父容器用 `min-h-0`，子列表用 `overflow-y-auto`。
- 列表区域加上 iOS 体验优化：`-webkit-overflow-scrolling: touch`。

Tailwind 参考（示例）：
- 列表容器：`class="flex-1 min-h-0 overflow-y-auto [-webkit-overflow-scrolling:touch]"`

### 2) 阻断滚动链（overscroll）
- 在弹窗遮罩层/根容器加：`overscroll-contain`（或更强 `overscroll-none`）。
- 在真正滚动的列表容器也加：`overscroll-contain`。

Tailwind 参考：
- 遮罩：`class="fixed inset-0 overscroll-contain ..."`
- 列表：`class="overflow-y-auto overscroll-contain ..."`

### 3) 锁定底层滚动（关键）
不要只锁 body；很多 SPA 的滚动在自定义容器上（例如 `.app-scroll`）。

做法：
- 打开弹窗时：
  - 把滚动容器（例：`.app-scroll`）的 `overflowY` 设为 `hidden`
  - 同时把 `document.body` 和 `document.documentElement` 的 `overflow` 设为 `hidden`
  - 同时把 body/html 的 `overscrollBehaviorY` 设为 `none`（iOS 回弹更稳）
- 关闭弹窗时：把上述 style 恢复到打开前的值（避免污染其他页面）

Vue 3（Composition API）模板：
```ts
import { onMounted, onUnmounted } from "vue";

let scrollContainer: HTMLElement | null = null;
let previousOverflowY = "";
let previousBodyOverflow = "";
let previousHtmlOverflow = "";
let previousBodyOverscrollY = "";
let previousHtmlOverscrollY = "";

const lockBackgroundScroll = () => {
  scrollContainer = document.querySelector(".app-scroll") as HTMLElement | null;
  if (scrollContainer) {
    previousOverflowY = scrollContainer.style.overflowY;
    scrollContainer.style.overflowY = "hidden";
  }

  previousBodyOverflow = document.body.style.overflow;
  previousHtmlOverflow = document.documentElement.style.overflow;
  previousBodyOverscrollY = document.body.style.overscrollBehaviorY;
  previousHtmlOverscrollY = document.documentElement.style.overscrollBehaviorY;

  document.body.style.overflow = "hidden";
  document.documentElement.style.overflow = "hidden";
  document.body.style.overscrollBehaviorY = "none";
  document.documentElement.style.overscrollBehaviorY = "none";
};

const unlockBackgroundScroll = () => {
  if (scrollContainer) {
    scrollContainer.style.overflowY = previousOverflowY;
    scrollContainer = null;
  }
  document.body.style.overflow = previousBodyOverflow;
  document.documentElement.style.overflow = previousHtmlOverflow;
  document.body.style.overscrollBehaviorY = previousBodyOverscrollY;
  document.documentElement.style.overscrollBehaviorY = previousHtmlOverscrollY;
};

onMounted(lockBackgroundScroll);
onUnmounted(unlockBackgroundScroll);
```

### 4) 确保是“真正的模态层”（可选但推荐）
- 用 `Teleport/Portal` 把弹窗挂到 `body`（避免被父容器的 overflow、transform 等影响）。
- 遮罩全屏固定定位：`fixed inset-0`（或按需避开 TopNav 的高度）。

### 5) safe-area（底部留白）
- 遮罩层或弹窗容器加：`padding-bottom: calc(env(safe-area-inset-bottom, 0px) + 12px)`
- 如果底部有按钮条，按钮条也可单独加 safe-area padding，避免按钮贴底

## 验收清单（怎么确认修好了）
- 在弹窗“非列表区域”上下滑：底层页面不动。
- 在省份/城市列表上下滑：只有列表滚动。
- 列表滑到顶/底继续滑：不会带动底层页面（iOS 上重点测）。
- 关闭弹窗后：底层页面滚动恢复正常（不残留 `overflow: hidden`）。

## 常见坑（排查顺序）
- 弹窗容器少了 `min-h-0`：子元素即使 `overflow-y-auto` 也不会变成真正滚动区。
- 外层有 `transform`/`filter`/`backdrop-filter` 等导致 fixed 参照异常：用 `Teleport` 挂到 body 更稳。
- 只锁 `.app-scroll` 不锁 body/html：iOS 回弹时仍可能带动底层（尤其是列表到边界后）。
