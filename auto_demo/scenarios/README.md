# 演示场景 (Demo Scenarios)

本目录包含多个预定义的演示场景，每个场景展示不同的功能和用例。

## 可用场景

### 1. default_demo.yaml (默认演示)
**时长**: 约2-3分钟  
**描述**: 完整的AI报告生成流程演示  
**适用场景**: 产品演示、功能讲解

**包含步骤**:
- 首页浏览和滚动
- 点击进入报告生成
- 填写表单（城市：成都，行业：人工智能）
- 提交生成请求
- 后台运行（可选）
- V3.0功能蓝图展示

**运行**:
```bash
python start_demo.py
# 或
python start_demo.py --scenario auto_demo/scenarios/default_demo.yaml
```

### 2. quick_demo.yaml (快速演示)
**时长**: 约30秒  
**描述**: 快速概览主要功能  
**适用场景**: 快速展示、时间有限的场合

**包含步骤**:
- 首页快速浏览
- 报告生成页面
- V3蓝图预览

**运行**:
```bash
python start_demo.py --scenario auto_demo/scenarios/quick_demo.yaml
```

## YAML 场景文件结构

### 基本结构

```yaml
name: "场景名称"
description: "场景描述"
base_url: "http://localhost:5000"

config:
  scroll_duration: 10    # 滚动时长（秒）
  action_delay: 1.5      # 动作间隔（秒）
  slow_motion: 50        # 慢动作延迟（毫秒）

steps:
  - action: navigate
    url: "/"
    description: "步骤描述"
```

### 配置说明

#### config 部分
- `scroll_duration`: 默认滚动持续时间
- `action_delay`: 每个动作之间的等待时间
- `slow_motion`: Playwright 慢动作模式，便于观看

#### steps 部分
每个步骤包含：
- `action`: 动作类型
- `description`: 步骤描述（用于日志）
- 其他参数：根据动作类型而定

## 动作类型详解

### navigate (导航)
```yaml
- action: navigate
  url: "/report/123"
  description: "打开报告页面"
```

### click (点击)
```yaml
- action: click
  selector: "button.submit"
  description: "点击提交"
  optional: false       # 可选步骤
  fallback:            # 备选选择器
    - selector: "#submitBtn"
    - selector: "text=提交"
```

### fill (填充)
```yaml
- action: fill
  selector: "#inputField"
  value: "输入内容"
  description: "填写字段"
```

### scroll_smooth (平滑滚动)
```yaml
- action: scroll_smooth
  direction: "down"     # 或 "up"
  duration: 10          # 秒
  description: "向下滚动"
```

### wait (等待)
```yaml
- action: wait
  duration: 2           # 秒
  description: "等待加载"
```

### message (消息)
```yaml
- action: message
  text: "演示完成！"
  description: "显示消息"
```

## 选择器最佳实践

### 1. 优先使用语义化选择器
```yaml
# ✅ 推荐：使用文本内容
selector: "text=生成AI报告"

# ✅ 推荐：组合选择器
selector: "button:has-text('提交')"
```

### 2. 使用ID和类名
```yaml
# ✅ 推荐：ID选择器
selector: "#city"

# ✅ 可用：类名选择器
selector: ".btn-primary"
```

### 3. 避免脆弱的选择器
```yaml
# ❌ 不推荐：复杂的CSS路径
selector: "div > div > button:nth-child(3)"

# ✅ 推荐：使用fallback
selector: "text=提交"
fallback:
  - selector: "#submitBtn"
  - selector: ".submit-button"
```

## 创建自定义场景

### 步骤1: 规划场景

明确演示目标和关键步骤：
1. 需要展示哪些功能？
2. 演示时长要求？
3. 目标受众是谁？

### 步骤2: 创建YAML文件

```bash
# 在 scenarios 目录创建新文件
touch auto_demo/scenarios/my_demo.yaml
```

### 步骤3: 编写场景

参考现有场景，编写步骤

### 步骤4: 测试场景

```bash
# Headed 模式测试（观察执行过程）
python start_demo.py --headed --scenario auto_demo/scenarios/my_demo.yaml

# Headless 模式测试（快速验证）
python start_demo.py --scenario auto_demo/scenarios/my_demo.yaml
```

### 步骤5: 调试优化

- 调整 `action_delay` 和 `slow_motion`
- 添加 fallback 选择器
- 标记可选步骤为 `optional: true`

## 场景设计技巧

### 1. 合理控制节奏
- 快速演示：`action_delay: 0.8`, `scroll_duration: 3`
- 标准演示：`action_delay: 1.5`, `scroll_duration: 5`
- 详细讲解：`action_delay: 2.5`, `scroll_duration: 10`

### 2. 突出重点功能
```yaml
# 在关键步骤增加停留时间
- action: fill
  selector: "#city"
  value: "成都"
  description: "填写城市"

- action: wait
  duration: 2
  description: "展示填写结果"
```

### 3. 流畅的过渡
```yaml
# 使用平滑滚动而非跳转
- action: scroll_smooth
  direction: "down"
  duration: 3

# 而非
- action: wait
  duration: 1
```

### 4. 错误处理
```yaml
# 关键步骤：不使用optional
- action: click
  selector: "button.submit"
  optional: false

# 次要步骤：使用optional
- action: click
  selector: "button.optional-feature"
  optional: true
```

## 场景模板

### 最小场景模板
```yaml
name: "基础演示"
description: "最简单的演示场景"
base_url: "http://localhost:5000"

steps:
  - action: navigate
    url: "/"
    description: "打开首页"
  
  - action: wait
    duration: 2
    description: "等待"
  
  - action: message
    text: "演示完成"
    description: "结束"
```

### 完整功能模板
```yaml
name: "完整功能演示"
description: "展示所有支持的动作"
base_url: "http://localhost:5000"

config:
  scroll_duration: 5
  action_delay: 1.5
  slow_motion: 50

steps:
  - action: navigate
    url: "/"
    description: "导航"
  
  - action: scroll_smooth
    direction: "down"
    duration: 5
    description: "滚动"
  
  - action: click
    selector: "button"
    description: "点击"
    optional: false
    fallback:
      - selector: "#btn"
  
  - action: fill
    selector: "#input"
    value: "文本"
    description: "填充"
  
  - action: wait
    duration: 2
    description: "等待"
  
  - action: message
    text: "完成"
    description: "消息"
```

## 常见问题

### Q: 如何加快演示速度？
A: 减少 `action_delay` 和 `slow_motion` 的值

### Q: 某个元素找不到怎么办？
A: 使用 fallback 选择器，或标记为 optional

### Q: 如何录制演示视频？
A: 添加 `--record` 参数：
```bash
python start_demo.py --headed --record
```

### Q: 可以暂停演示吗？
A: 在YAML中增加较长的 `wait` 步骤

## 贡献场景

欢迎贡献新的演示场景！请确保：
1. 场景文件格式正确
2. 包含清晰的描述
3. 经过测试验证
4. 更新本README

## 相关资源

- [主文档](../README.md)
- [动作参考](../README.md#支持的动作-actions)
- [选择器指南](../README.md#选择器-selectors)
