# 部署到Render

本指南将帮助您将区域产业分析小工作台部署到Render平台。

## 部署步骤

### 1. 注册Render账户
1. 访问 [Render官网](https://render.com/)
2. 点击"Get Started"注册账户
3. 验证邮箱并登录

### 2. 连接GitHub仓库
1. 在Render仪表板中，点击"New Web Service"
2. 选择"Build and deploy from a Git repository"
3. 连接您的GitHub账户
4. 选择包含此项目的仓库

### 3. 配置Web服务
1. **Name**: 为您的服务命名（例如：regional-industrial-dashboard）
2. **Region**: 选择离您最近的区域
3. **Branch**: 选择要部署的分支（通常是main或master）
4. **Root Directory**: 如果项目在仓库根目录则留空，否则填写相对路径
5. **Environment**: 选择"Python"
6. **Build Command**: `pip install -r requirements.txt`
7. **Start Command**: `gunicorn -w 4 -b 0.0.0.0:$PORT industry_analysis:app`

### 4. 设置环境变量
在"Advanced"部分添加以下环境变量：
```
PYTHON_VERSION=3.8
```

### 5. 部署
1. 点击"Create Web Service"
2. Render将自动开始构建和部署过程
3. 等待部署完成（通常需要5-10分钟）

## 配置说明

### 环境变量
- `PORT`: Render自动设置，应用会监听此端口
- `PYTHON_VERSION`: 指定Python版本

### 数据持久化
Render的免费层在服务不活跃时会停机，且没有持久化存储。如果需要持久化数据：
1. 使用外部数据库（如Render提供的PostgreSQL）
2. 使用外部文件存储服务（如AWS S3、Cloudinary等）

## 常见问题

### 1. 构建失败
- 检查requirements.txt中的依赖是否正确
- 确保所有依赖都能通过pip安装
- 查看构建日志以获取详细错误信息

### 2. 应用启动失败
- 检查应用是否监听$PORT环境变量
- 确保没有硬编码端口号
- 查看应用日志以获取详细错误信息

### 3. 性能问题
- Render免费层有资源限制
- 考虑升级到付费计划以获得更好性能
- 优化应用代码以减少资源使用

## 升级建议

对于生产环境，建议：
1. 使用Render的数据库服务存储用户数据
2. 配置自定义域名
3. 启用自动SSL证书
4. 设置环境特定的配置
5. 考虑使用Render的cron job功能处理定时任务