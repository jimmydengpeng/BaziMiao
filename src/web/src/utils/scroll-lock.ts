type ScrollLockRelease = () => void;

let lockCount = 0;
let scrollContainer: HTMLElement | null = null;
let previousOverflowY = "";
let previousBodyOverflow = "";
let previousHtmlOverflow = "";
let previousBodyOverscrollY = "";
let previousHtmlOverscrollY = "";

const applyScrollLock = () => {
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

const restoreScrollLock = () => {
  if (scrollContainer) {
    scrollContainer.style.overflowY = previousOverflowY;
    scrollContainer = null;
  }
  document.body.style.overflow = previousBodyOverflow;
  document.documentElement.style.overflow = previousHtmlOverflow;
  document.body.style.overscrollBehaviorY = previousBodyOverscrollY;
  document.documentElement.style.overscrollBehaviorY = previousHtmlOverscrollY;
};

export const lockBackgroundScroll = (): ScrollLockRelease => {
  if (typeof document === "undefined") {
    return () => {};
  }
  if (lockCount === 0) {
    applyScrollLock();
  }
  lockCount += 1;
  let released = false;
  return () => {
    if (released) return;
    released = true;
    lockCount = Math.max(0, lockCount - 1);
    if (lockCount === 0) {
      restoreScrollLock();
    }
  };
};
