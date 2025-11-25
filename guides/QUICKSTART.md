# 🚀 快速启动指南

## 一键启动（推荐）

只需一个命令即可启动整个系统：

```bash
./start.sh
```

该脚本会自动：
- ✅ 检查Python环境
- ✅ 创建并激活虚拟环境
- ✅ 安装所有依赖
- ✅ 检查并启动Redis
- ✅ 启动Celery后台任务处理器
- ✅ 启动Flask Web应用
- ✅ 自动打开浏览器（可选）

## 访问系统

启动成功后，访问：
- **URL**: http://localhost:5000
- **默认账号**: admin
- **默认密码**: admin

## 停止系统

按 `Ctrl+C` 即可优雅停止所有服务

## 系统功能

### 1. 🤖 AI驱动的报告生成
1. 点击"生成报告"按钮
2. 输入城市名（如：成都）
3. 输入行业名（如：人工智能）
4. 点击"开始生成报告"
5. 等待2-5分钟，系统后台自动生成
6. 自动跳转到报告页面

### 2. 📊 智能摘要与SWOT分析
- 查看中英文双语摘要
- 自动生成的SWOT分析
- 完整报告内容展示

### 3. 💬 智能问答
- 在报告页面直接提问
- AI基于报告内容回答
- 实时交互式问答

### 4. 📁 文档上传分析
- 支持 .txt, .md, .json, .docx, .pdf
- 自动文本分析和分类
- 可视化展示结果

## 故障排除

### Redis连接失败
```bash
# 检查Redis是否运行
redis-cli ping

# 手动启动Redis (macOS)
brew services start redis

# 手动启动Redis (Linux)
redis-server --daemonize yes
```

### Python依赖问题
```bash
# 重新安装依赖
pip install -r requirements.txt
```

### 权限问题
```bash
# 确保脚本有执行权限
chmod +x start.sh
```

### 数据库初始化问题
```bash
# 删除旧数据库重新初始化
rm industrial_analysis.db
./start.sh
```

## 日志查看

系统日志保存在 `logs/` 目录：
- `celery.log` - Celery任务日志

查看实时日志：
```bash
tail -f logs/celery.log
```

## 手动启动（高级用户）

如果需要分别控制各个服务：

### 终端1 - Redis
```bash
redis-server
```

### 终端2 - Celery Worker
```bash
source venv/bin/activate
celery -A src.tasks.celery_app worker --loglevel=info
```

### 终端3 - Flask应用
```bash
source venv/bin/activate
python app_enhanced.py
```

## 系统要求

- **操作系统**: macOS / Linux
- **Python**: 3.8+
- **Redis**: 最新稳定版
- **磁盘空间**: 至少500MB
- **内存**: 建议2GB+

## 下一步

- 查看完整文档: `DEPLOYMENT_GUIDE.md`
- 项目总结: `README_UPGRADE.md`
- 配置说明: `config.json`

## 技术支持

如遇问题，请检查：
1. Python版本是否>=3.8
2. Redis是否正常运行
3. 虚拟环境是否正确激活
4. API密钥是否配置正确

---

**享受使用吧！**🎉
