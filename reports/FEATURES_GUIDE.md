# 🎯 系统新功能使用指南

## 📋 目录

- [功能概览](#功能概览)
- [1. AI智能报告生成](#1-ai智能报告生成)
- [2. 趋势预测分析](#2-趋势预测分析)
- [3. 多文档对比](#3-多文档对比)
- [4. 3D可视化地图](#4-3d可视化地图)
- [5. 产业链图谱](#5-产业链图谱)
- [6. 知识图谱](#6-知识图谱)
- [7. 政策解读助手](#7-政策解读助手)
- [8. 术语词典](#8-术语词典)
- [9. 情感分析](#9-情感分析)
- [10. 投资评估](#10-投资评估)
- [11. 实体识别](#11-实体识别)
- [12. 报告导出](#12-报告导出)
- [13. 性能优化](#13-性能优化)

---

## 功能概览

本系统共实现了 **20个核心功能**，涵盖AI分析、数据可视化、报告管理等多个方面。

### 快速访问
- 主页：`http://localhost:5000`
- 报告生成：`http://localhost:5000/generate-llm-report`
- 报告列表：`http://localhost:5000/reports`

---

## 1. AI智能报告生成

### 功能说明
使用Kimi大模型自动生成7大模块的产业分析报告，包含执行摘要、产业概览、政策环境、产业生态、产业链分析、AI融合潜力、SWOT分析等。

### 使用步骤

#### 方式1：Web界面（推荐）
1. 登录系统后，点击顶部导航「生成AI报告」
2. 填写表单：
   - **城市**：如"成都"、"武汉"、"深圳"
   - **产业**：如"人工智能"、"汽车产业"、"芯片制造"
   - **补充说明**（可选）：如"重点关注新能源领域"
3. 点击「开始生成」
4. 实时查看生成进度（进度条显示）
5. 生成完成后自动跳转到报告页面

#### 方式2：API调用
```bash
curl -X POST http://localhost:5000/api/generate-llm-report \
  -H "Content-Type: application/json" \
  -d '{
    "city": "成都",
    "industry": "人工智能",
    "additional_context": "重点分析AI+制造融合"
  }'
```

### 生成的报告包含
- ✅ 中英文双语执行摘要
- ✅ SWOT战略分析（优势、劣势、机遇、威胁）
- ✅ 7大章节详细内容
- ✅ 智能问答功能
- ✅ 元数据（token使用、生成时间等）

### 查看报告
- 报告列表：点击「我的报告」
- 报告详情：点击任意报告卡片
- SWOT分析：报告页面自动展示4个维度

---

## 2. 趋势预测分析

### 功能说明
基于多份历史报告，分析产业发展趋势，预测未来6-12期走势，计算置信区间。

### 使用步骤

#### 前提条件
至少需要3份相关的历史报告（相同产业或城市）

#### Web界面使用
1. 进入「报告列表」页面
2. 选择3份以上同类报告（勾选复选框）
3. 点击「趋势分析」按钮
4. 选择分析指标：
   - 市场规模
   - 企业数量
   - 增长率
   - 投资金额
5. 查看分析结果：
   - 📈 趋势方向（上升/下降/稳定）
   - 📊 平均增长率
   - 🔮 未来预测值
   - 📉 置信区间
   - 📊 趋势图表

#### API调用
```bash
curl -X POST http://localhost:5000/api/trend-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "report_ids": ["report_001", "report_002", "report_003"],
    "metric": "market_size"
  }'
```

### 返回数据示例
```json
{
  "trend_direction": "上升",
  "avg_growth_rate": 12.5,
  "predictions": {
    "values": [3500, 3850, 4200, 4550],
    "confidence_intervals": {
      "upper": [3700, 4100, 4500, 4900],
      "lower": [3300, 3600, 3900, 4200]
    }
  },
  "chart": { /* ECharts配置 */ }
}
```

---

## 3. 多文档对比

### 功能说明
横向对比不同城市或产业的报告，生成综合排名、雷达图、对比柱状图和文字分析。

### 使用步骤

#### Web界面
1. 进入「报告列表」
2. 勾选2-5份要对比的报告
3. 点击「对比分析」按钮
4. 查看对比结果：
   - 🏆 综合排名表
   - 🎯 雷达图（多维度对比）
   - 📊 柱状图（指标对比）
   - 📝 文字分析报告
   - 🔤 关键词词频对比

#### API调用
```bash
curl -X POST http://localhost:5000/api/comparison \
  -H "Content-Type: application/json" \
  -d '{
    "report_ids": ["report_cd_ai", "report_bj_ai", "report_sz_ai"]
  }'
```

### 对比维度
- 市场规模
- 企业数量
- 政策支持力度
- 技术创新水平
- 产业链完整度
- 人才储备

---

## 4. 3D可视化地图

### 功能说明
将产业数据以地图形式可视化，包括POI展现及分析等。

### 使用步骤

#### 查看报告地图
1. 打开任意LLM生成的报告
2. 滚动到「地理可视化」区域
3. 查看以下图表：
   - 🗺️ 省份分布地图（中国地图）
   - 📊 3D柱状图（自动旋转）
   - 🌐 地理散点图（动态连线）
   - 🔗 产业关系网络图

#### API获取地图数据
```bash
curl http://localhost:5000/api/report/report_001/visualizations
```

### 返回数据
```json
{
  "province_map": { /* ECharts地图配置 */ },
  "bar_3d": { /* 3D柱状图配置 */ },
  "geo_scatter": { /* 散点图配置 */ },
  "network_graph": { /* 网络图配置 */ }
}
```

### 自定义地图（开发者）
```python
from src.visualization.map_visualizer import MapVisualizer

visualizer = MapVisualizer()

# 省份数据
province_data = {"四川": 2500, "北京": 3500, "广东": 4000}
map_config = visualizer.generate_province_map(province_data, title="AI产业分布")

# 3D柱状图
data_3d = [
    {"x": "AI", "y": "成都", "z": 2500},
    {"x": "AI", "y": "北京", "z": 3500}
]
bar_3d = visualizer.generate_3d_bar_chart(data_3d)
```

---

## 5. 产业链图谱

### 功能说明
自动识别产业链上中下游，评估完整度，标注薄弱环节。

### 使用步骤

#### 查看产业链图谱
1. 打开报告详情页
2. 找到「产业链分析」模块
3. 查看：
   - 🔼 上游（原材料、核心技术）
   - ➡️ 中游（核心产品、制造）
   - 🔽 下游（应用、分销）
   - 📊 完整度评分
   - ⚠️ 薄弱环节预警

#### API调用
```bash
curl http://localhost:5000/api/report/report_001/industry-chain
```

### 返回示例
```json
{
  "upstream": {
    "components": ["芯片", "传感器", "原材料"],
    "strength": "较强",
    "gaps": ["高端芯片依赖进口"]
  },
  "midstream": {
    "components": ["整车制造", "系统集成"],
    "strength": "成熟"
  },
  "downstream": {
    "components": ["销售渠道", "售后服务"],
    "strength": "良好"
  },
  "completeness_score": 75,
  "weak_points": ["上游高端芯片", "下游国际市场"]
}
```

---

## 6. 知识图谱

### 功能说明
从报告中提取实体和关系，生成可交互的知识图谱。

### 使用步骤

#### 查看知识图谱
1. 打开LLM报告
2. 点击「知识图谱」标签页
3. 交互操作：
   - 🖱️ 拖拽节点
   - 🔍 缩放视图
   - 💡 点击节点查看详情
   - 🔗 查看关系连线

#### 图谱类型
- **完整图谱**：所有实体和关系
- **企业子图**：只显示企业相关
- **技术子图**：只显示技术相关
- **政策子图**：只显示政策相关

#### API调用
```bash
# 完整图谱
curl http://localhost:5000/api/report/report_001/knowledge-graph

# 企业子图
curl http://localhost:5000/api/report/report_001/knowledge-graph?type=company
```

### 开发者使用
```python
from src.visualization.knowledge_graph_visualizer import KnowledgeGraphVisualizer

visualizer = KnowledgeGraphVisualizer()

# 添加实体
visualizer.add_entity("e1", "华为", "company")
visualizer.add_entity("e2", "5G", "technology")

# 添加关系
visualizer.add_relationship("e1", "e2", "研发")

# 生成图谱
graph_config = visualizer.generate_graph()
```

---

## 7. 政策解读助手

### 功能说明
自动提取政策要点、补贴信息、税收优惠，生成政策时间轴。

### 使用步骤

#### 上传政策文档
1. 进入「政策解读」页面
2. 上传政策文件（PDF/Word/TXT）
3. 系统自动分析

#### 查看解读结果
- 📋 政策要点（3-5条）
- 💰 补贴信息（金额、条件）
- 🏛️ 税收优惠（类型、比例）
- 📅 政策时间轴
- 🎯 适用性评分

#### API调用
```bash
curl -X POST http://localhost:5000/api/policy-analysis \
  -F "file=@policy_document.pdf" \
  -F "industry=人工智能"
```

### 返回示例
```json
{
  "key_points": [
    "支持AI企业研发投入，给予最高500万补贴",
    "税收减免30%，持续3年",
    "优先土地供应和人才引进"
  ],
  "subsidies": [
    {"type": "研发补贴", "amount": "最高500万", "condition": "年研发投入>1000万"}
  ],
  "tax_benefits": [
    {"type": "企业所得税", "reduction": "30%", "duration": "3年"}
  ],
  "timeline": [ /* 时间轴数据 */ ],
  "applicability_score": 85
}
```

---

## 8. 术语词典

### 功能说明
自动提取专业术语，生成词典和词云图，支持多格式导出。

### 使用步骤

#### 查看术语词典
1. 打开报告详情
2. 点击「术语词典」标签
3. 查看：
   - 📖 术语列表（带释义）
   - ☁️ 词云图
   - 📊 词频统计

#### 导出词典
- 📄 TXT格式
- 📊 CSV格式
- 📝 JSON格式
- 📋 Markdown格式

#### API调用
```bash
# 生成词典
curl http://localhost:5000/api/report/report_001/terminology

# 导出词典
curl http://localhost:5000/api/report/report_001/terminology/export?format=json
```

### 术语类别
- 产业术语
- 政策术语
- 技术术语
- 企业术语
- 地理术语
- 经济术语
- AI术语

---

## 9. 情感分析

### 功能说明
分析报告文本情感倾向，识别积极/消极情绪，发现风险点。

### 使用步骤

#### 查看情感分析
1. 打开报告
2. 找到「情感分析」区域
3. 查看：
   - 😊 整体情感倾向（积极/中性/消极）
   - 📊 情感分值（0-1）
   - 🎯 情感分布图
   - ⚠️ 风险警示

#### API调用
```bash
curl http://localhost:5000/api/report/report_001/sentiment
```

### 返回示例
```json
{
  "overall_sentiment": "积极",
  "sentiment_score": 0.72,
  "positive_ratio": 0.65,
  "negative_ratio": 0.15,
  "neutral_ratio": 0.20,
  "risk_points": [
    "人才流失严重",
    "核心技术依赖进口"
  ]
}
```

---

## 10. 投资评估

### 功能说明
多维度评估产业投资价值，给出投资建议和风险预警。

### 使用步骤

#### 查看投资评估
1. 打开报告
2. 找到「投资价值评估」模块
3. 查看：
   - 🎯 综合评分（0-100）
   - 📊 维度评分（市场、技术、政策等）
   - 💡 投资建议
   - ⚠️ 风险提示

#### 评估维度
- 市场规模与增长
- 政策支持力度
- 技术创新能力
- 产业链完整度
- 竞争格局
- 人才储备

#### API调用
```bash
curl http://localhost:5000/api/report/report_001/investment-evaluation
```

---

## 11. 实体识别

### 功能说明
自动识别报告中的企业、人物、地点、技术、产品等实体。

### 使用步骤

#### 查看实体
1. 打开报告
2. 点击「实体识别」标签
3. 按类别查看：
   - 🏢 企业（如"华为"、"腾讯"）
   - 👤 人物（如"任正非"）
   - 📍 地点（如"深圳"）
   - 🔬 技术（如"5G"）
   - 📦 产品（如"鸿蒙系统"）

#### API调用
```bash
curl http://localhost:5000/api/report/report_001/entities
```

---

## 12. 报告导出

### 功能说明
将报告导出为PDF、Word、Excel格式，支持精美排版。

### 使用步骤

#### 导出报告
1. 打开报告详情
2. 滚动到底部「导出选项」
3. 选择格式：
   - 📕 PDF（精美排版，适合打印）
   - 📘 Word（可编辑）
   - 📗 Excel（数据表格）
4. 点击下载

#### API调用
```bash
# PDF
curl http://localhost:5000/export/report/report_001/pdf -o report.pdf

# Word
curl http://localhost:5000/export/report/report_001/word -o report.docx

# Excel
curl http://localhost:5000/export/report/report_001/excel -o report.xlsx
```

### PDF特性
- ✅ 中文字体支持
- ✅ SWOT分析彩色展示
- ✅ 章节分页
- ✅ 目录自动生成

### Word特性
- ✅ 完整段落格式
- ✅ 列表项符号
- ✅ 多级标题
- ✅ 可编辑内容

---

## 13. 性能优化

### 功能说明
内置缓存机制、批量处理、性能监控。

### 开发者使用

#### 缓存装饰器
```python
from src.utils.performance_optimizer import PerformanceOptimizer

optimizer = PerformanceOptimizer()

@optimizer.cache(ttl=3600)  # 缓存1小时
def expensive_function(param):
    # 耗时操作
    return result

# 清除缓存
optimizer.clear_cache()
```

#### 批量处理
```python
# 批量处理报告
batch_results = optimizer.batch_process(
    items=report_ids,
    process_func=analyze_report,
    batch_size=10
)
```

#### 性能监控
```python
# 监控函数性能
@optimizer.monitor_performance
def process_data():
    pass

# 查看性能统计
stats = optimizer.get_performance_stats()
```

---

## 🚀 快速开始示例

### 完整工作流

```bash
# 1. 启动系统
./start.sh

# 2. 注册/登录
# 访问 http://localhost:5000/register

# 3. 生成AI报告
# 访问 http://localhost:5000/generate-llm-report
# 填写：城市=成都，产业=人工智能

# 4. 等待生成（约1-2分钟）
# 查看实时进度

# 5. 查看报告
# 自动跳转到报告详情页
# 查看SWOT、地图、图表等

# 6. 导出报告
# 点击底部导出按钮
# 选择PDF/Word/Excel
```

---

## 📞 技术支持

### API文档
完整API文档：`http://localhost:5000/api/docs`

### 常见问题

#### Q: SWOT分析为什么显示为空？
A: 需要重新生成报告。旧报告的SWOT数据可能为空，新生成的报告会包含完整SWOT分析。

#### Q: 如何查看所有功能？
A: 登录后，所有功能都在顶部导航栏和报告详情页中。

#### Q: 能否批量生成报告？
A: 目前不支持Web批量操作，但可以通过API循环调用。

#### Q: 导出的PDF中文乱码？
A: 已修复，使用系统中文字体（STHeiti/Songti）。

---

## 📊 功能清单速查

| 编号 | 功能 | 入口 | 状态 |
|------|------|------|------|
| 1 | AI报告生成 | 顶部导航/生成报告 | ✅ |
| 2 | 趋势预测 | 报告列表/选择多个报告 | ✅ |
| 3 | 多文档对比 | 报告列表/选择多个报告 | ✅ |
| 4 | 3D地图 | 报告详情/地理可视化 | ✅ |
| 5 | 产业链图谱 | 报告详情/产业链分析 | ✅ |
| 6 | 知识图谱 | 报告详情/知识图谱标签 | ✅ |
| 7 | 政策解读 | 顶部导航/政策解读 | ✅ |
| 8 | 术语词典 | 报告详情/术语词典标签 | ✅ |
| 9 | 情感分析 | 报告详情/情感分析区域 | ✅ |
| 10 | 投资评估 | 报告详情/投资价值模块 | ✅ |
| 11 | 实体识别 | 报告详情/实体识别标签 | ✅ |
| 12 | 报告导出 | 报告详情/底部导出按钮 | ✅ |
| 13 | 用户系统 | 注册/登录页面 | ✅ |
| 14 | 性能监控 | API性能统计 | ✅ |

---

**更新时间**: 2024-11-04  
**版本**: v1.0  
**完成度**: 20/22 (91%)

🎉 **开始探索这些强大的新功能吧！**
### POI清单上传与坐标说明

- 上传页面：`http://localhost:5000/poi-map-visualization` → 标签页「上传机构清单」
- 坐标来源：系统现已直接使用上传JSON中 `location.latitude` 与 `location.longitude`（或 `location.lat` 与 `location.lng`）作为坐标，不再进行实时地址地理编码。
- 校验规则：
  - `longitude`/`lng` ∈ [-180, 180]
  - `latitude`/`lat` ∈ [-90, 90]
  - 无效或缺失坐标记录将被忽略，并在处理完成统计中展示「有效/总计/无效」数量。
- 进度展示：上传后界面显示解析进度条与处理统计，便于快速了解数据质量。
