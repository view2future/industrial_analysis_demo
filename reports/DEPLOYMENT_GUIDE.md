# 区域产业分析小工作台 - 部署和启动指南

## 项目概述

这是一个升级版的区域产业分析小工作台，包含以下核心功能：

### 已实现的核心功能

1. **✅ LLM驱动的报告生成** (优化点1)
   - 输入城市名和行业名，使用Google Gemini自动生成完整的产业分析报告
   - 后台异步任务处理，避免长时间等待
   - 生成中英文摘要和SWOT分析

2. **✅ AI智能摘要** (优化点2)
   - 自动生成Executive Summary
   - 中英文双语支持
   - 智能问答功能 - 针对报告提问

3. **✅ 用户系统与权限管理** (优化点17)
   - 多用户登录/注册系统
   - 角色权限管理 (admin/analyst/user)
   - 报告访问控制

4. **✅ 后台任务处理**
   - Celery + Redis异步任务队列
   - 实时任务进度追踪
   - 友好的完成通知

## 安装步骤

### 1. 环境准备

确保已安装以下软件：
- Python 3.8+
- Redis (用于Celery任务队列)

### 2. 安装依赖

```bash
# 激活虚拟环境（如果有）
source venv/bin/activate  # macOS/Linux

# 安装Python依赖
pip install -r requirements.txt
```

### 3. 安装并启动Redis

macOS:
```bash
brew install redis
brew services start redis
```

或手动启动:
```bash
redis-server
```

### 4. 配置API密钥

API密钥已经配置在 `config.json` 文件中：
- Google Gemini API Key: 已配置
- 百度地图 AK: 已配置

如需修改，直接编辑 `config.json` 文件。

## 启动系统

### 方式1: 完整启动（支持后台任务）

需要启动3个进程：

**终端1 - 启动Redis**
```bash
redis-server
```

**终端2 - 启动Celery Worker**
```bash
celery -A src.tasks.celery_app worker --loglevel=info
```

**终端3 - 启动Flask应用**
```bash
python app_enhanced.py
```

然后访问: http://localhost:5000

### 方式2: 简化启动（不支持后台任务）

如果只想测试基本功能，不需要LLM报告生成：

```bash
python industry_analysis.py
```

然后访问: http://localhost:8080

## 系统使用

### 1. 登录系统

默认管理员账号：
- 用户名: `admin`
- 密码: `admin`

### 2. 生成LLM报告

1. 点击"生成报告"按钮
2. 输入城市名（如：成都、重庆、西安）
3. 输入行业名（如：人工智能、汽车产业、生物医药）
4. 可选：输入补充信息
5. 点击"生成报告"
6. 系统将在后台处理，显示实时进度
7. 完成后自动跳转到报告查看页面

### 3. 上传文档分析

1. 点击"上传文档"
2. 选择要分析的文件（.txt, .md, .json, .docx, .pdf）
3. 系统会自动分析并生成可视化结果

### 4. 查看和问答

- 在报告页面可以查看完整内容和摘要
- 使用智能问答功能对报告提问
- 切换中英文摘要

## 项目结构

```
regional-industrial-dashboard/
├── app_enhanced.py              # 增强版主应用（推荐使用）
├── industry_analysis.py         # 原始应用
├── config.json                  # 配置文件（含API密钥）
├── industry_analysis_llm_prompt.md  # LLM Prompt模板
├── requirements.txt             # Python依赖
│
├── src/
│   ├── ai/                      # AI模块
│   │   ├── llm_generator.py     # LLM报告生成器
│   │   └── __init__.py
│   ├── tasks/                   # 后台任务
│   │   ├── celery_app.py        # Celery配置
│   │   ├── report_tasks.py      # 报告生成任务
│   │   └── __init__.py
│   ├── analysis/                # 文本分析
│   │   ├── text_processor.py
│   │   └── __init__.py
│   └── visualization/           # 数据可视化
│       ├── dashboard_generator.py
│       └── __init__.py
│
├── data/
│   ├── input/                   # 上传文件
│   ├── output/                  # 分析结果
│   └── output/llm_reports/      # LLM生成的报告
│
├── templates/                   # HTML模板（需创建）
└── static/                      # 静态资源（CSS/JS）
```

## 待实现的功能

由于项目规模较大（22个优化点），以下功能框架已搭建但需要进一步开发：

### 高优先级
- [ ] 前端HTML模板（登录、注册、报告生成、报告查看页面）
- [ ] 知识图谱可视化 (优化点8, 20-22)
- [ ] 地图可视化集成 (优化点5)
- [ ] 报告导出功能 (优化点12: PDF/Word/PPT/Excel)

### 中优先级
- [ ] 多文档对比分析 (优化点4)
- [ ] 趋势预测与时间序列 (优化点3)
- [ ] 情感分析 (优化点9)
- [ ] 产业链图谱 (优化点14)
- [ ] 投资价值评估 (优化点15)
- [ ] 政策解读助手 (优化点16)

### 低优先级
- [ ] 动态数据故事 (优化点6)
- [ ] 自定义仪表板 (优化点7)
- [ ] 术语词典 (优化点10)
- [ ] 多源数据整合 (优化点11)
- [ ] 性能优化 (优化点18)
- [ ] 数据安全加密 (优化点19)

## 下一步开发建议

### 立即需要的
1. **创建HTML模板** - 系统现在缺少前端页面
2. **测试LLM集成** - 确保Google Gemini API正常工作
3. **完善错误处理** - 添加更完善的异常捕获

### 快速开发路线
1. 先实现基础UI（登录、报告生成、查看页面）
2. 测试核心功能（LLM报告生成）
3. 逐步添加可视化功能（图表、地图、知识图谱）
4. 最后优化性能和用户体验

## 故障排除

### Redis连接失败
```bash
# 检查Redis是否运行
redis-cli ping
# 应该返回 PONG
```

### Celery任务不执行
检查Celery worker是否正常启动，查看终端输出

### Google Gemini API错误
- 检查API Key是否正确
- 确认API配额是否充足
- 检查网络连接

### 数据库错误
```bash
# 删除旧数据库重新初始化
rm industrial_analysis.db
python app_enhanced.py
```

## 技术栈

- **后端**: Flask + SQLAlchemy + Flask-Login
- **任务队列**: Celery + Redis
- **AI/LLM**: Google Gemini API
- **数据处理**: Pandas, jieba (中文分词)
- **可视化**: Plotly, ECharts (待集成)
- **文档处理**: python-docx, PyPDF2
- **前端**: Bootstrap 5 + jQuery (待实现)

## 联系支持

如有问题，请检查：
1. 所有依赖是否正确安装
2. Redis是否正常运行
3. API密钥是否有效
4. 日志文件中的错误信息

---

**注意**: 当前版本专注于核心功能实现。完整的22个优化点需要持续开发和迭代。建议优先完成HTML模板和测试核心LLM功能。
