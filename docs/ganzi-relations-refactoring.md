# 干支关系数据结构重构说明

## 重构背景

### 原有问题

1. **数据结构混乱**：使用位置索引（positions: [0,1,2,3,4,5]）标识柱，容易导致前后端映射混乱
2. **职责不清**：后端返回位置索引，前端需要进行复杂的映射，职责不明确
3. **代码重复**：`calculate_ganzi_relations` 和 `calculate_extended_ganzi_relations` 逻辑重复
4. **扩展性差**：增加新的柱（如胎元、命宫）需要修改多处代码
5. **Bug隐患**：位置映射错误导致显示问题（如"巳辰自刑"的bug）

### 重构目标

1. **前后端职责分离**：后端只负责数据准确性，前端负责显示逻辑
2. **使用语义化标识**：用柱名称而非位置索引标识关系
3. **一次性计算所有关系**：后端一次性返回本命+大运+流年的所有关系
4. **简化前端逻辑**：前端根据显示模式过滤关系，无需复杂映射

## 新的数据结构

### GanZhiRelation (单个关系)

```typescript
export interface GanZhiRelation {
  type: string;                 // 关系类型：合化、相克、六合、三合、相刑等
  pillars: string[];            // 涉及的柱标识数组
  ganzi_items: string[];        // 涉及的干支名称数组
  description: string;          // 关系描述
  element?: string | null;      // 合化后的五行（如有）
  category: string;             // 关系类别: stem/branch/stem_branch
  involves_fortune: boolean;    // 是否涉及大运或流年
}
```

#### 柱标识 (pillars)

- `year`: 年柱
- `month`: 月柱  
- `day`: 日柱
- `hour`: 时柱
- `destiny`: 大运柱
- `year_fortune`: 流年柱

#### 示例

**寅刑巳** (本命关系):
```json
{
  "type": "相刑",
  "pillars": ["year", "month"],
  "ganzi_items": ["寅", "巳"],
  "description": "寅刑巳（无恩之刑）",
  "element": null,
  "category": "branch",
  "involves_fortune": false
}
```

**乙巳自刑** (涉及流年):
```json
{
  "type": "自刑",
  "pillars": ["month", "year_fortune"],
  "ganzi_items": ["巳", "巳"],
  "description": "巳巳自刑",
  "element": null,
  "category": "branch",
  "involves_fortune": true
}
```

### GanZhiRelations (关系汇总)

```typescript
export interface GanZhiRelations {
  stem_relations: GanZhiRelation[];           // 天干关系（包含所有）
  branch_relations: GanZhiRelation[];         // 地支关系（包含所有）
  stem_branch_relations: GanZhiRelation[];    // 天干地支相生关系
}
```

**移除的字段**:
- ~~`extended_stem_relations`~~
- ~~`extended_branch_relations`~~

所有关系统一存放在 `stem_relations` 和 `branch_relations` 中，通过 `involves_fortune` 字段区分。

## 后端实现

### 统一的计算函数

```python
def calculate_all_ganzi_relations(
    self,
    year_pillar: PillarInfo,
    month_pillar: PillarInfo,
    day_pillar: PillarInfo,
    hour_pillar: PillarInfo,
    destiny_pillar: Optional[PillarInfo] = None,
    year_fortune_pillar: Optional[PillarInfo] = None
) -> GanZhiRelations:
    """一次性计算所有干支关系（本命四柱 + 大运 + 流年）"""
```

### 主要改进

1. **柱字典管理**:
```python
pillar_dict = {
    "year": year_pillar,
    "month": month_pillar,
    "day": day_pillar,
    "hour": hour_pillar,
}
if destiny_pillar:
    pillar_dict["destiny"] = destiny_pillar
if year_fortune_pillar:
    pillar_dict["year_fortune"] = year_fortune_pillar
```

2. **语义化关系创建**:
```python
GanZhiRelation(
    type="相刑",
    pillars=[pid1, pid2],
    ganzi_items=[branch1, branch2],
    description=f"{branch1}刑{branch2}（{punishment_type}）",
    element=None,
    category="branch",
    involves_fortune=(pid1 in ['destiny', 'year_fortune'] or 
                     pid2 in ['destiny', 'year_fortune'])
)
```

3. **删除冗余函数**:
- ~~`calculate_ganzi_relations`~~ (已被 `calculate_all_ganzi_relations` 替代)
- `calculate_extended_ganzi_relations` → `calculate_extended_ganzi_relations_DEPRECATED`

## 前端实现

### 1. 柱位置映射

前端维护柱标识到显示位置的映射：

```typescript
// 本命模式
const pillarPositionMap_native = {
  year: 0,
  month: 1,
  day: 2,
  hour: 3
};

// 当前模式
const pillarPositionMap_current = {
  year_fortune: 0,
  destiny: 1,
  year: 2,
  month: 3,
  day: 4,
  hour: 5
};
```

### 2. 关系过滤

根据显示模式过滤关系：

```typescript
const visibleRelations = computed(() => {
  const allRelations = props.chart.ganzi_relations.stem_relations; // 或 branch_relations
  
  if (isCurrentMode.value) {
    // 当前模式：显示所有关系
    return allRelations;
  } else {
    // 本命模式：只显示不涉及大运流年的关系
    return allRelations.filter(rel => !rel.involves_fortune);
  }
});
```

### 3. 位置计算

根据柱标识计算显示位置：

```typescript
const getRelationPositions = (relation: GanZhiRelation): number[] => {
  const posMap = isCurrentMode.value ? pillarPositionMap_current : pillarPositionMap_native;
  
  return relation.pillars
    .map(pillarId => posMap[pillarId])
    .filter(pos => pos !== undefined)
    .sort((a, b) => a - b);
};
```

### 4. 连线绘制

```typescript
const stemConnectionLines = computed(() => {
  const lines = [];
  const relations = visibleRelations_stem.value;
  
  // 分配关系到行
  const rowMap = allocateRelationsToRows(relations);
  
  rowMap.forEach((rowRelations, level) => {
    for (const rel of rowRelations) {
      const positions = getRelationPositions(rel);
      if (positions.length < 2) continue;
      
      const [p1, p2] = [positions[0], positions[positions.length - 1]];
      const path = createStemArc(p1, p2, level);
      
      lines.push({
        path,
        type: rel.type,
        label: getRelationLabel(rel),
        // ...
      });
    }
  });
  
  return lines;
});
```

## 迁移指南

### 后端迁移

1. 更新 `src/models/chart.py` 中的 `GanZhiRelation` 和 `GanZhiRelations` 模型
2. 在 `src/engine/bazi_engine.py` 中实现 `calculate_all_ganzi_relations`
3. 在 `calculate_chart` 中调用新函数
4. 标记旧函数为 deprecated

### 前端迁移

1. 更新 `src/web/src/types.ts` 中的类型定义
2. 在 `ChartPanel.vue` 中：
   - 添加柱位置映射
   - 实现关系过滤逻辑
   - 更新连线绘制逻辑
   - 移除旧的 `mapPosition` 函数
   - 移除对 `extended_stem_relations` 和 `extended_branch_relations` 的引用
3. 测试两种模式下的显示效果

## 优势总结

1. **数据准确性**：使用名称而非索引，避免映射错误
2. **代码可维护性**：职责清晰，逻辑简单
3. **扩展性**：易于添加新的柱类型
4. **性能**：一次计算，前端简单过滤
5. **调试友好**：数据结构语义化，易于理解和调试

## Bug修复

原bug：流年"乙巳"和月柱"丙辰"显示"自刑"

**根本原因**：位置映射逻辑错误，导致前端将不同的关系误认为同一关系

**修复方案**：使用新的数据结构，明确标识每个关系涉及的具体柱和干支，从根本上避免此类问题

