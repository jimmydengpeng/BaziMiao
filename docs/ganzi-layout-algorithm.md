# 干支关系连线布局算法

## 概述

本文档描述了 `ChartPanel.vue` 中天干和地支关系连线的绘制布局算法。该算法通过智能的行分配策略，让不重叠的关系可以共享同一行，从而节省垂直空间并提升视觉美观度。

## 问题背景

在八字命盘的干支关系图中，需要用连线表示不同柱位之间的关系（如六冲、六合、三合等）。原始的简单实现是让每个关系独占一行，这会导致：

- **空间浪费**：即使多个关系没有重叠，也会占用多行空间
- **视觉混乱**：关系数量较多时，图形会变得很高，不够紧凑

## 算法设计

### 核心思想

使用"格子模型"（Slot Model）来管理行内的空间占用，通过贪心策略将不重叠的关系分配到同一行。

### 1. 格子模型

四柱（年、月、日、时）之间有3个可占用的空位（格子）：

```
格子索引:     0         1         2
位置:    年柱 ─── 月柱 ─── 日柱 ─── 时柱
```

- **格子 0**：年柱-月柱之间的空间
- **格子 1**：月柱-日柱之间的空间
- **格子 2**：日柱-时柱之间的空间

每个关系占用的格子由其连接的柱位决定。

### 2. 跨度计算

**跨度（span）** = 最大位置索引 - 最小位置索引

示例：
- 年柱(0) - 月柱(1) 关系：跨度 = 1，占用格子 [0]
- 年柱(0) - 日柱(2) 关系：跨度 = 2，占用格子 [0, 1]
- 年柱(0) - 时柱(3) 关系：跨度 = 3，占用格子 [0, 1, 2]
- 月柱(1) - 时柱(3) 关系：跨度 = 2，占用格子 [1, 2]

对于三元关系（如三合、三会），跨度覆盖所有涉及的柱位。例如：
- 年柱(0) - 月柱(1) - 日柱(2) 三合：跨度 = 2，占用格子 [0, 1]
- 年柱(0) - 月柱(1) - 时柱(3) 三合：跨度 = 3，占用格子 [0, 1, 2]

### 3. 行分配算法

算法使用贪心策略，按以下步骤执行：

#### 步骤 1：计算跨度
遍历所有关系，计算每个关系的跨度和占用的格子。

#### 步骤 2：排序
按跨度从小到大排序所有关系。这样可以优先处理短关系，提高空间利用率。

#### 步骤 3：贪心分配
```
初始化: currentRow = 0, occupiedSlots = {}

对于每个关系 (按跨度升序):
    requiredSlots = 该关系需要的格子
    
    if requiredSlots 与 occupiedSlots 有交集:
        // 当前行放不下，换到下一行
        currentRow += 1
        occupiedSlots = {}  // 重置格子占用状态
    
    // 分配到当前行
    将关系添加到 rows[currentRow]
    将 requiredSlots 加入 occupiedSlots
```

### 4. 算法示例

假设有以下地支关系：

| 关系 | 柱位 | 跨度 | 占用格子 |
|------|------|------|----------|
| A: 年支-月支 六冲 | [0,1] | 1 | [0] |
| B: 月支-日支 六合 | [1,2] | 1 | [1] |
| C: 日支-时支 相害 | [2,3] | 1 | [2] |
| D: 年支-时支 相刑 | [0,3] | 3 | [0,1,2] |

**分配过程：**

1. 排序后顺序：A, B, C, D（按跨度升序）
2. 处理 A：currentRow=0, occupiedSlots={}，分配到行0，occupiedSlots={0}
3. 处理 B：currentRow=0, occupiedSlots={0}，需要{1}，不冲突，分配到行0，occupiedSlots={0,1}
4. 处理 C：currentRow=0, occupiedSlots={0,1}，需要{2}，不冲突，分配到行0，occupiedSlots={0,1,2}
5. 处理 D：currentRow=0, occupiedSlots={0,1,2}，需要{0,1,2}，**冲突**，换到行1，分配到行1

**最终布局：**
```
行0: A(年-月) + B(月-日) + C(日-时)  ← 三个短关系共享一行
行1: D(年-时)                      ← 长关系独占一行
```

**对比原始布局：**
```
原始:          优化后:
行0: A         行0: A + B + C
行1: B         行1: D
行2: C         
行3: D         

空间节省: 从4行减少到2行（50%）
```

## 实现细节

### 数据结构

```typescript
// 关系及其跨度信息
interface RelationWithSpan {
  relation: GanZhiRelation;    // 原始关系数据
  positions: number[];          // 排序后的位置索引
  span: number;                 // 跨度
  minPos: number;               // 最小位置
  maxPos: number;               // 最大位置
}
```

### 核心函数

#### `getOccupiedSlots(minPos, maxPos)`
计算关系占用的格子索引数组。

```typescript
const getOccupiedSlots = (minPos: number, maxPos: number): number[] => {
  const slots: number[] = [];
  for (let i = minPos; i < maxPos; i++) {
    slots.push(i);
  }
  return slots;
};
```

#### `allocateRelationsToRows(relations)`
核心行分配算法，返回 `Map<行号, 关系数组>`。

```typescript
const allocateRelationsToRows = (relations: GanZhiRelation[]): Map<number, GanZhiRelation[]> => {
  // 1. 计算跨度
  const relationsWithSpan = relations
    .filter(rel => rel.positions.length >= 2)
    .map(rel => {
      const positions = rel.positions.map(mapPosition).sort((a, b) => a - b);
      return {
        relation: rel,
        positions,
        span: positions[positions.length - 1] - positions[0],
        minPos: positions[0],
        maxPos: positions[positions.length - 1],
      };
    });
  
  // 2. 按跨度排序
  relationsWithSpan.sort((a, b) => a.span - b.span);
  
  // 3. 贪心分配
  const rows: Map<number, GanZhiRelation[]> = new Map();
  let currentRow = 0;
  let occupiedSlots: Set<number> = new Set();
  
  for (const item of relationsWithSpan) {
    const requiredSlots = getOccupiedSlots(item.minPos, item.maxPos);
    const canFit = requiredSlots.every(slot => !occupiedSlots.has(slot));
    
    if (!canFit) {
      currentRow++;
      occupiedSlots = new Set();
    }
    
    if (!rows.has(currentRow)) {
      rows.set(currentRow, []);
    }
    rows.get(currentRow)!.push(item.relation);
    
    requiredSlots.forEach(slot => occupiedSlots.add(slot));
  }
  
  return rows;
};
```

### 应用

该算法同时应用于：
- **天干关系连线**（`stemConnectionLines`）：在天干上方绘制
- **地支关系连线**（`branchConnectionLines`）：在地支下方绘制

## 算法特性

### 时间复杂度
- **排序**：O(n log n)，其中 n 是关系数量
- **分配**：O(n × m)，其中 m 是平均跨度（最多3）
- **总体**：O(n log n)

### 空间复杂度
- O(n)，用于存储关系信息和行映射

### 优点
1. **空间高效**：显著减少垂直空间占用
2. **视觉清晰**：短关系在内层，长关系在外层，形成层次感
3. **支持复杂关系**：正确处理三合、三会等多元关系
4. **可预测性**：相同输入总是产生相同输出

### 局限性
1. **贪心非最优**：贪心策略不保证全局最优解，但在实际场景中表现良好
2. **顺序敏感**：依赖跨度排序，相同跨度的关系顺序可能影响结果
3. **静态布局**：不支持动态调整（但这也是优点，保证一致性）

## 扩展可能性

### 后端预计算
如果性能成为瓶颈，可以在后端预先计算跨度：

```python
class GanZhiRelation(BaseModel):
    type: str
    positions: List[int]
    description: str
    element: Optional[str] = None
    span: Optional[int] = None  # 跨度 = max(positions) - min(positions)
```

### 更优化的算法
可以使用区间调度算法（Interval Scheduling）来获得更优的布局，但需要更复杂的实现。当前的贪心算法在实际使用中已经足够高效和美观。

## 参考

- 文件位置：`src/web/src/components/ChartPanel.vue`
- 相关类型定义：`src/web/src/types.ts` (GanZhiRelation)
- 算法实现起始行：约第 985 行

---

*本文档记录了干支关系连线的智能布局算法，该算法显著提升了命盘视图的空间利用率和视觉美观度。*

