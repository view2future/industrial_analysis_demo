# 自动化演示系统 - 快速入门

## 5分钟快速开始

### 步骤 1: 安装依赖 (2分钟)

```bash
# 安装 Python 包
pip install -r auto_demo/requirements.txt

# 安装 Playwright 浏览器（约300MB，需要几分钟）
playwright install chromium
```

### 步骤 2: 启动服务器 (30秒)

在**新终端窗口**中：

```bash
python app.py
```

等待看到：
```
* Running on http://localhost:5000
```

### 步骤 3: 运行演示 (2分钟)

在**原终端**中：

```bash
# 可视化模式（推荐首次使用）
python start_demo.py --headed
```

就这么简单！浏览器会自动打开并执行完整的演示流程。

## 常用命令

```bash
# 快速演示（30秒）
python start_demo.py --scenario auto_demo/scenarios/quick_demo.yaml --headed

# 录制演示视频
python start_demo.py --headed --record

# 无头模式（后台运行，速度更快）
python start_demo.py
```

## 录制视频

启用 `--record` 后，视频保存在：
```
auto_demo/recordings/
```

查看录制的视频：
```bash
ls -lh auto_demo/recordings/
open auto_demo/recordings/*.webm  # macOS
```

## 自定义演示场景

编辑或创建 YAML 文件：

```bash
# 复制默认场景
cp auto_demo/scenarios/default_demo.yaml auto_demo/scenarios/my_demo.yaml

# 编辑场景
nano auto_demo/scenarios/my_demo.yaml

# 运行自定义场景
python start_demo.py --headed --scenario auto_demo/scenarios/my_demo.yaml
```

## 故障排除

### 问题：Flask 未运行

```
⚠️  Flask 服务器未运行在 http://localhost:5000
```

**解决**：在另一个终端运行 `python app.py`

### 问题：Playwright 未安装

```
Error: Executable doesn't exist
```

**解决**：运行 `playwright install chromium`

### 问题：端口被占用

```
Error: [Errno 48] Address already in use
```

**解决**：
```bash
# 查找占用进程
lsof -ti:5000

# 结束进程
kill -9 $(lsof -ti:5000)
```

## 下一步

- 📖 阅读完整文档: `auto_demo/README.md`
- 🎬 查看场景示例: `auto_demo/scenarios/README.md`
- 🛠 安装指南: `auto_demo/INSTALL.md`
- 📋 实施总结: `AUTO_DEMO_IMPLEMENTATION.md`

## 需要帮助？

详细的文档和故障排除指南：
- [README](auto_demo/README.md)
- [安装指南](auto_demo/INSTALL.md)
- [场景编写](auto_demo/scenarios/README.md)

---

**提示**: 首次运行建议使用 `--headed` 模式观察演示过程，熟悉后可以使用更快的 headless 模式。
