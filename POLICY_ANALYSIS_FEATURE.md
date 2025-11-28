# 政策解读工作台系统

## 系统概述

这是一个基于邮箱的政策解读工作台系统，用户将政策文章的URL发送到指定邮箱，系统自动读取邮件、抓取政策内容、分析解读，并提供分类存储、搜索和可视化展示功能。

## 核心功能

### 1. 邮箱URL读取
- 自动读取指定邮箱中的新邮件
- 提取邮件正文中的政策文章URL
- 支持纯文本和HTML格式邮件

### 2. 政策内容抓取
- 从URL抓取政策文章内容
- 智能识别政策文档特征
- 清理无关内容，提取核心政策信息

### 3. 政策分析与解读
- 政策要点提取
- 补贴和税收优惠识别
- 时间节点梳理
- 适用性评估
- LLM驱动的深度解读

### 4. 分类存储
- 按区域、行业、年度分类
- 政策类型自动识别
- 智能标签系统

### 5. 搜索与过滤
- 全文搜索
- 多维度筛选（区域、行业、年份、政策类型）
- 高级搜索功能

### 6. 可视化展示
- 区域分布图（饼图）
- 行业分布图（柱状图）
- 时间趋势图（折线图）
- 政策类型分布图（饼图）
- 知识图谱展示

## 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   用户邮箱      │───▶│  邮件读取模块   │───▶│  网页抓取模块   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                           │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  分析结果存储   │◀───│  政策分析模块   │◀───│  LLM解读模块    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    政策工作台前端界面                           │
└─────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────┐
│  数据库存储     │
└─────────────────┘
```

## 配置要求

### 1. 邮箱配置

在 `config.json` 中配置邮箱信息：

```json
{
  "email": {
    "server": "imap.gmail.com",
    "port": 993,
    "username": "your-email@gmail.com",
    "password": "your-app-password",
    "folder": "INBOX"
  }
}
```

### 2. API密钥配置

在 `config.json` 中配置LLM服务API密钥：

```json
{
  "api_keys": {
    "kimi": "your-kimi-api-key",
    "google_gemini": "your-gemini-api-key"
  }
}
```

## 模块说明

### 1. 邮箱读取模块 (`src/utils/email_reader.py`)
- 读取配置邮箱的IMAP
- 解析邮件内容提取URL
- 支持多种邮件格式

### 2. 网页抓取模块 (`src/data/policy_web_scraper.py`)
- 智能抓取政策文章
- 内容清理和结构化
- 元数据提取

### 3. 政策分析模块 (`src/analysis/policy_analysis_integrator.py`)
- 整合现有政策分析功能
- 调用LLM进行深度解读
- 生成知识图谱

### 4. 数据库模型 (`app.py`)
- PolicyAnalysis模型存储分析结果
- 支持多维度分类和搜索

### 5. 前端界面 (`templates/policy_analysis_dashboard.html`)
- 响应式设计
- 实时数据展示
- 交互式图表

## API接口

- `GET /policy-analysis` - 政策分析工作台页面
- `GET /api/policy-stats` - 获取统计信息
- `GET /api/policies` - 获取政策列表（支持分页、过滤、搜索）
- `GET /api/policy/<id>` - 获取政策详情
- `POST /api/check-email-policies` - 检查邮箱获取新政策
- `GET /api/policy-visualizations` - 获取可视化数据

## 数据库表结构

### PolicyAnalysis 表
- `id`: 主键
- `title`: 政策标题
- `original_url`: 原始URL
- `source_type`: 来源类型（email）
- `content`: 政策内容
- `content_summary`: 内容摘要
- `analysis_result`: 分析结果（JSON）
- `classification_region`: 区域分类
- `classification_industry`: 行业分类
- `classification_year`: 年度分类
- `classification_policy_type`: 政策类型
- `applicability_score`: 适用性评分
- `entities`: 实体信息（JSON）
- `knowledge_graph`: 知识图谱数据（JSON）
- `llm_interpretation`: LLM解读结果（JSON）
- `status`: 状态（pending, processing, completed, failed）
- `tags`: 标签
- `created_at`: 创建时间
- `updated_at`: 更新时间

## 使用流程

1. **配置邮箱**：在config.json中配置邮箱和API密钥
2. **发送邮件**：将政策文章URL发送到指定邮箱
3. **自动处理**：系统定期检查邮箱，处理新邮件
4. **查看结果**：在工作台查看分析结果
5. **搜索分类**：使用过滤器和搜索功能查找政策

## 特色功能

- **自动化处理**：定时检查邮箱，自动处理新政策
- **智能分类**：自动识别政策的区域、行业、年份
- **深度解读**：LLM生成政策解读和建议
- **可视化展示**：多维度数据可视化
- **知识图谱**：政策实体关系图
- **工作台管理**：类似文件柜的政策管理界面

## 技术栈

- Python 3.8+
- Flask Web框架
- SQLite数据库
- ECharts可视化库
- Requests网页抓取
- BeautifulSoup内容解析
- Jieba中文分词
- 现有的政策分析和LLM集成模块

## 扩展功能

- 支持更多邮箱服务（Outlook、QQ邮箱等）
- 增加企业匹配度评估
- 政策时效性提醒
- 导出功能（PDF/Excel）
- 多用户权限管理