/**
 * 云朵生成算法
 * 使用分层分布 + 空间哈希网格
 * 特性：两侧密集中间稀疏、均匀纵向、不重叠、高性能
 */

// ============= 类型定义 =============
export interface CloudImage {
  src: string
  width: number
  height: number
}

export interface CloudInstance {
  id: number
  x: number
  y: number
  width: number
  height: number
  scale: number
  rotation: number
  imageSrc: string
  opacity: number
  flipX: boolean
}

export interface CloudGeneratorOptions {
  width: number
  height: number
  imageList: string[]
  baseSize?: number
  isMobile?: boolean
  config?: Partial<typeof LAYERED_CONFIG>
}

// ============= 分层算法配置（核心调参区）=============
export const LAYERED_CONFIG = {
  // 两侧聚集强度（越大越靠边，2-3 效果较好）
  horizontalBiasK: 2.5,

  // X轴边缘留白
  horizontalMargin: 80,

  // 纵向密度（越大越密，1.0-1.3 效果较好）
  verticalDensity: 1.1,

  // 每层Y扰动比例（避免排队感）
  verticalJitterRatio: 0.15,

  // 缩放范围
  scaleMin: 0.8,
  scaleMax: 1.2,

  // 空间哈希网格尺寸系数
  overlapFactor: 1.1,

  // 每层最大尝试次数
  maxAttemptsPerLayer: 8,

  // 移动端缩放倍数
  mobileScaleMultiplier: 2.5,
}

// ============= 工具函数 =============

/** X轴采样：两侧密、中间稀 */
function sampleX(width: number, biasK: number, margin: number): number {
  const u = Math.random()
  const side = Math.random() < 0.5 ? -1 : 1
  const d = Math.pow(u, biasK)
  const half = width / 2 - margin
  return width / 2 + side * d * half
}

/** 随机缩放因子 */
function randomScale(min: number, max: number): number {
  return min + Math.random() * (max - min)
}

/** AABB 碰撞检测 */
function overlap(
  a: { x: number; y: number; width: number; height: number },
  b: { x: number; y: number; width: number; height: number }
): boolean {
  return !(
    a.x + a.width < b.x ||
    a.x > b.x + b.width ||
    a.y + a.height < b.y ||
    a.y > b.y + b.height
  )
}

// ============= 空间哈希网格 =============

class SpatialGrid {
  cellSize: number
  grid = new Map<string, CloudInstance[]>()

  constructor(cellSize: number) {
    this.cellSize = cellSize
  }

  private key(x: number, y: number): string {
    return `${x},${y}`
  }

  private cellCoord(x: number): number {
    return Math.floor(x / this.cellSize)
  }

  /** 获取附近的所有云朵 */
  getNearby(x: number, y: number): CloudInstance[] {
    const cx = this.cellCoord(x)
    const cy = this.cellCoord(y)
    const result: CloudInstance[] = []

    for (let dx = -1; dx <= 1; dx++) {
      for (let dy = -1; dy <= 1; dy++) {
        const k = this.key(cx + dx, cy + dy)
        const list = this.grid.get(k)
        if (list) result.push(...list)
      }
    }
    return result
  }

  /** 插入云朵 */
  insert(cloud: CloudInstance) {
    const cx = this.cellCoord(cloud.x)
    const cy = this.cellCoord(cloud.y)
    const k = this.key(cx, cy)

    if (!this.grid.has(k)) {
      this.grid.set(k, [])
    }
    this.grid.get(k)!.push(cloud)
  }
}

// ============= 主生成函数（分层算法）=============

export function generateCloudsLayered(
  images: CloudImage[],
  canvasWidth: number,
  canvasHeight: number,
  config: typeof LAYERED_CONFIG,
  isMobile: boolean
): CloudInstance[] {
  // 计算平均高度
  const avgHeight = images.reduce((s, i) => s + i.height, 0) / images.length

  // 空间哈希网格
  const cellSize = avgHeight * config.overlapFactor
  const grid = new SpatialGrid(cellSize)

  // 计算层数
  const layerHeight = avgHeight * config.verticalDensity
  const layers = Math.ceil(canvasHeight / layerHeight)

  const clouds: CloudInstance[] = []
  const scaleMultiplier = isMobile ? config.mobileScaleMultiplier : 1

  // 主循环：按层生成
  for (let i = 0; i < layers; i++) {
    const baseY = i * layerHeight
    const jitter = layerHeight * config.verticalJitterRatio

    for (let attempt = 0; attempt < config.maxAttemptsPerLayer; attempt++) {
      const img = images[Math.floor(Math.random() * images.length)]
      const scale = randomScale(config.scaleMin, config.scaleMax) * scaleMultiplier

      const w = img.width * scale
      const h = img.height * scale

      // X轴：幂函数采样（两侧密集）
      const x = sampleX(canvasWidth, config.horizontalBiasK, config.horizontalMargin) - w / 2

      // Y轴：层内随机 + 抖动
      const y = baseY + Math.random() * layerHeight + (Math.random() * 2 - 1) * jitter

      const cloud: CloudInstance = {
        id: clouds.length,
        x,
        y,
        width: w,
        height: h,
        scale,
        rotation: (Math.random() - 0.5) * 10,
        imageSrc: img.src,
        opacity: 0.05 + Math.random() * 0.08,
        flipX: Math.random() > 0.5
      }

      // 碰撞检测（只检查附近）
      const neighbors = grid.getNearby(x, y)
      if (neighbors.every(c => !overlap(c, cloud))) {
        grid.insert(cloud)
        clouds.push(cloud)
        break
      }
    }
  }

  return clouds
}

// ============= 图片加载工具 =============

async function loadImages(srcs: string[]): Promise<CloudImage[]> {
  const promises = srcs.map(
    (src) =>
      new Promise<CloudImage>((resolve) => {
        const img = new Image()
        img.onload = () => {
          resolve({ src, width: img.width, height: img.height })
        }
        img.onerror = () => {
          // 加载失败时使用默认尺寸
          resolve({ src, width: 200, height: 100 })
        }
        img.src = src
      })
  )
  return Promise.all(promises)
}

// ============= 公开 API（兼容旧接口）=============

export function generateCloudInstances(options: CloudGeneratorOptions): CloudInstance[] {
  const { width, height, imageList, baseSize, isMobile = false, config } = options

  // 合并配置
  const cfg = { ...LAYERED_CONFIG, ...config }

  // 加载图片获取尺寸
  const images = imageList.map((src) => ({ src, width: 200, height: 100 }))

  // 使用分层算法生成
  return generateCloudsLayered(images, width, height, cfg, isMobile)
}

// ============= 保留旧版 Poisson 算法（可选使用）=============

export interface PoissonConfig {
  width: number
  height: number
  minDistance: number
  padding?: number
  maxCount?: number
  maxTries?: number
  centerVoid?: {
    x: number
    y: number
    width: number
    height: number
  }
}

const randomBetween = (min: number, max: number): number => {
  return Math.random() * (max - min) + min
}

const distanceSquared = (a: { x: number; y: number }, b: { x: number; y: number }): number => {
  const dx = a.x - b.x
  const dy = a.y - b.y
  return dx * dx + dy * dy
}

const isInsideRect = (
  x: number,
  y: number,
  rect: { x: number; y: number; width: number; height: number }
): boolean => {
  return (
    x >= rect.x && x <= rect.x + rect.width && y >= rect.y && y <= rect.y + rect.height
  )
}

export function generateCloudPoints(config: PoissonConfig): { x: number; y: number }[] {
  const {
    width,
    height,
    minDistance: r,
    padding = 0,
    maxCount = Infinity,
    maxTries = 30,
    centerVoid,
  } = config

  const minX = -padding
  const minY = -padding
  const maxX = width + padding
  const maxY = height + padding

  const cellSize = r / Math.SQRT2
  const gridWidth = Math.ceil((maxX - minX) / cellSize)
  const gridHeight = Math.ceil((maxY - minY) / cellSize)

  const grid: Array<number | null> = new Array(gridWidth * gridHeight).fill(null)
  const points: { x: number; y: number }[] = []
  const activeList: number[] = []

  const gridIndex = (x: number, y: number): number => {
    const gx = Math.floor((x - minX) / cellSize)
    const gy = Math.floor((y - minY) / cellSize)
    return gy * gridWidth + gx
  }

  const isValidPoint = (x: number, y: number): boolean => {
    if (centerVoid && isInsideRect(x, y, centerVoid)) {
      return false
    }

    const gx = Math.floor((x - minX) / cellSize)
    const gy = Math.floor((y - minY) / cellSize)

    for (let yy = gy - 2; yy <= gy + 2; yy++) {
      for (let xx = gx - 2; xx <= gx + 2; xx++) {
        if (xx < 0 || yy < 0 || xx >= gridWidth || yy >= gridHeight) continue
        const index = grid[yy * gridWidth + xx]
        if (index !== null) {
          const p = points[index]
          if (distanceSquared({ x, y }, p) < r * r) {
            return false
          }
        }
      }
    }
    return true
  }

  const initialPoint = {
    x: randomBetween(minX, maxX),
    y: randomBetween(minY, maxY),
  }

  points.push(initialPoint)
  activeList.push(0)
  grid[gridIndex(initialPoint.x, initialPoint.y)] = 0

  while (activeList.length > 0 && points.length < maxCount) {
    const activeIndex = activeList[Math.floor(Math.random() * activeList.length)]
    const origin = points[activeIndex]
    let found = false

    for (let i = 0; i < maxTries; i++) {
      const angle = Math.random() * Math.PI * 2
      const radius = randomBetween(r, 2 * r)
      const x = origin.x + Math.cos(angle) * radius
      const y = origin.y + Math.sin(angle) * radius

      if (x < minX || x > maxX || y < minY || y > maxY) continue
      if (!isValidPoint(x, y)) continue

      const newIndex = points.length
      points.push({ x, y })
      activeList.push(newIndex)
      grid[gridIndex(x, y)] = newIndex
      found = true
      break
    }

    if (!found) {
      const idx = activeList.indexOf(activeIndex)
      if (idx !== -1) activeList.splice(idx, 1)
    }
  }

  return points
}
