<template>
  <div class="fixed inset-0 pointer-events-none overflow-hidden z-0">
    <div
      v-for="cloud in clouds"
      :key="cloud.id"
      class="absolute animate-fade-in"
      :style="{
        width: cloud.width + 'px',
        height: cloud.height + 'px',
        left: cloud.x + 'px',
        top: cloud.y + 'px',
        opacity: cloud.opacity
      }"
    >
      <img
        :src="cloud.imageSrc"
        :alt="`cloud-${cloud.id}`"
        class="w-full h-full object-contain"
        :style="{
          transform: [
            cloud.flipX ? 'scaleX(-1)' : 'none',
            `rotate(${cloud.rotation}deg)`
          ].join(' ')
        }"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { generateCloudInstances, type CloudInstance, LAYERED_CONFIG } from '../utils/cloudGenerator'

// 导入云朵图片
const cloudImages = import.meta.glob('../assets/bg_cloud_middle/*.png', { eager: true, as: 'url' })
const cloudImageList = Object.values(cloudImages) as string[]

const clouds = ref<CloudInstance[]>([])

// ============= 云朵配置（使用分层算法配置）=============
const CLOUD_CONFIG = {
  // 两侧聚集强度（越大越靠边，2-3 效果较好）
  horizontalBiasK: 1,

  // X轴边缘留白
  horizontalMargin: -100,

  // 纵向密度（越大越密，1.0-1.3 效果较好）
  verticalDensity: 1.2,

  // 每层Y扰动比例
  verticalJitterRatio: 0.2,

  // 缩放范围
  scaleMin: 0.8,
  scaleMax: 1.2,

  // 空间哈希网格尺寸系数
  overlapFactor: 0.8,

  // 每层最大尝试次数
  maxAttemptsPerLayer: 16,

  // 移动端缩放倍数
  mobileScaleMultiplier: 0.8,
}

const generateClouds = () => {
  const w = window.innerWidth
  const h = window.innerHeight
  const isMobile = w < 768

  clouds.value = generateCloudInstances({
    width: w,
    height: h,
    imageList: cloudImageList,
    isMobile,
    config: CLOUD_CONFIG
  })
}

const handleResize = () => {
  generateClouds()
}

onMounted(() => {
  generateClouds()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 0.1; }
}

.animate-fade-in {
  animation: fadeIn 5s ease-out forwards;
}
</style>
