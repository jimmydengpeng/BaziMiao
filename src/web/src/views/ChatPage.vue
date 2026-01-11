<template>
  <!-- 移动端/PWA 全屏聊天页面：进入无动画，退出向右滑动 -->
  <Transition
    :css="true"
    enter-active-class=""
    enter-from-class=""
    enter-to-class=""
    leave-active-class="transition-all duration-300 ease-[cubic-bezier(0.25,0.1,0.25,1)] motion-reduce:transition-none"
    leave-from-class="opacity-100 translate-x-0"
    leave-to-class="opacity-0 translate-x-full"
    @after-leave="finalizeExit"
  >
    <div v-show="isVisible" class="chat-page">
      <UnifiedChat mode="page" @close="requestExit" />
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { nextTick, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import UnifiedChat from '../components/UnifiedChat.vue';

const router = useRouter();
const isVisible = ref(false);
const isLeaving = ref(false);

const requestExit = () => {
  if (isLeaving.value) return;
  isLeaving.value = true;
  isVisible.value = false;
};

const finalizeExit = () => {
  if (window.history.length > 1) {
    router.back();
  } else {
    router.push('/');
  }
};

onMounted(() => {
  // 立即显示聊天页面（无进入动画）
  nextTick(() => {
    isVisible.value = true;
  });
});
</script>

<style scoped>
.chat-page {
  /* 固定定位，使用视口高度单位防止键盘影响 */
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  width: 100%;
  height: 100vh;
  height: 100dvh; /* 动态视口高度，iOS Safari 支持 */
  overflow: hidden;
  /* 覆盖全局 TopNav / TabBar 等固定层 */
  z-index: 100;
}
</style>
