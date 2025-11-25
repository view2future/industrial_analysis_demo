# 安装指南 (Installation Guide)

## 系统要求

- **Python**: 3.8 或更高版本
- **操作系统**: macOS, Linux, 或 Windows
- **内存**: 最少 4GB RAM
- **磁盘空间**: 约 500MB（用于Playwright浏览器）

## 快速安装

### 步骤 1: 安装 Python 依赖

```bash
# 在项目根目录执行
cd /Users/wangyu94/regional-industrial-dashboard

# 安装依赖
pip install -r auto_demo/requirements.txt
```

预期输出：
```
Successfully installed playwright-1.40.0 PyYAML-6.0
```

### 步骤 2: 安装 Playwright 浏览器

```bash
# 安装 Chromium 浏览器
playwright install chromium
```

预期输出：
```
Downloading Chromium 119.0.6045.9 (playwright build v1084)
...
Chromium 119.0.6045.9 (playwright build v1084) downloaded to /Users/xxx/Library/Caches/ms-playwright
```

**注意**: 这一步会下载约 300MB 的浏览器文件，可能需要几分钟。

### 步骤 3: 验证安装

```bash
# 测试 Playwright 是否正常工作
python -c "from playwright.sync_api import sync_playwright; print('✅ Playwright 安装成功')"
```

## 详细安装步骤

### macOS 用户

```bash
# 1. 确认 Python 版本
python3 --version  # 应该 >= 3.8

# 2. 创建虚拟环境（可选但推荐）
python3 -m venv venv
source venv/bin/activate

# 3. 安装依赖
pip install -r auto_demo/requirements.txt

# 4. 安装浏览器
playwright install chromium

# 5. 验证
python start_demo.py --help
```

### Linux 用户

```bash
# 1. 安装系统依赖（Ubuntu/Debian）
sudo apt-get update
sudo apt-get install -y python3 python3-pip

# 2. 安装 Python 依赖
pip3 install -r auto_demo/requirements.txt

# 3. 安装 Playwright 系统依赖
playwright install-deps chromium

# 4. 安装浏览器
playwright install chromium

# 5. 验证
python3 start_demo.py --help
```

### Windows 用户

```powershell
# 1. 在 PowerShell 中执行
python --version  # 确认 >= 3.8

# 2. 安装依赖
pip install -r auto_demo\requirements.txt

# 3. 安装浏览器
playwright install chromium

# 4. 验证
python start_demo.py --help
```

## 常见问题

### 问题 1: pip install 失败

```
ERROR: Could not find a version that satisfies the requirement playwright
```

**解决方案**:
```bash
# 升级 pip
pip install --upgrade pip

# 重试安装
pip install -r auto_demo/requirements.txt
```

### 问题 2: playwright install 失败

```
Error: Failed to download Chromium
```

**解决方案**:
```bash
# 设置代理（如果在墙内）
export PLAYWRIGHT_DOWNLOAD_HOST=https://playwright.azureedge.net

# 或使用镜像
export PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright

# 重试安装
playwright install chromium
```

### 问题 3: 权限问题 (macOS/Linux)

```
PermissionError: [Errno 13] Permission denied
```

**解决方案**:
```bash
# 使用虚拟环境避免权限问题
python3 -m venv venv
source venv/bin/activate
pip install -r auto_demo/requirements.txt
```

### 问题 4: 找不到 playwright 命令

```
playwright: command not found
```

**解决方案**:
```bash
# 使用 Python 模块方式调用
python -m playwright install chromium
```

## 验证安装完整性

运行以下命令验证所有组件：

```bash
# 1. 检查 Python 依赖
python -c "import yaml; import playwright; print('✅ 依赖安装成功')"

# 2. 检查 Playwright 浏览器
playwright --version

# 3. 运行快速测试（无需Flask服务器）
python -c "from auto_demo.demo_engine import DemoEngine; print('✅ 演示引擎可用')"
```

## 下一步

安装完成后：

1. **启动 Flask 服务器**:
   ```bash
   python app.py
   ```

2. **运行演示**:
   ```bash
   python start_demo.py --headed
   ```

3. **查看文档**:
   - [使用指南](README.md)
   - [场景示例](scenarios/README.md)

## 卸载

如果需要卸载：

```bash
# 1. 卸载 Python 包
pip uninstall playwright pyyaml -y

# 2. 删除浏览器文件
rm -rf ~/Library/Caches/ms-playwright  # macOS
rm -rf ~/.cache/ms-playwright          # Linux
rmdir /s %USERPROFILE%\AppData\Local\ms-playwright  # Windows
```

## 技术支持

如遇到其他问题：
1. 查看 [README.md](README.md) 的故障排除部分
2. 检查 [Playwright 官方文档](https://playwright.dev/python/)
3. 提交 Issue 到项目仓库
