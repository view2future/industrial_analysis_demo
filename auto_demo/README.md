# 自动化演示系统 (Auto Demo System)

基于 Playwright 的浏览器自动化演示系统，用于区域产业分析小工作台的功能演示。

## 特性

- 🎬 **YAML驱动** - 通过简单的YAML配置文件定义演示场景
- 🚀 **高性能** - 优化的浏览器自动化，快速响应，低延迟
- 📹 **可选录屏** - 支持高清屏幕录制，生成演示视频
- 🎨 **灵活配置** - 支持 headless/headed 模式，可自定义滚动速度、动作延迟等
- 🔄 **回退机制** - 支持多重选择器回退，提高成功率
- 📝 **详细日志** - 实时输出每个步骤的执行状态

## 快速开始

### 1. 安装依赖

```bash
# 安装 Python 依赖
pip install -r auto_demo/requirements.txt

# 安装 Playwright浏览器（Chromium）
playwright install chromium
```

### 2. 启动 Flask 服务器

在一个终端中启动应用：

```bash
python app.py
```

确保服务器运行在 `http://localhost:5000`

### 3. 运行默认演示

```bash
# Headless 模式（默认）
python start_demo.py

# 可视化模式（显示浏览器窗口）
python start_demo.py --headed

# 启用屏幕录制
python start_demo.py --headed --record
```

## 使用说明

### 命令行选项

```bash
python start_demo.py [选项]

选项:
  --scenario PATH     指定YAML场景文件路径（默认: auto_demo/scenarios/default_demo.yaml）
  --headed            使用可视化浏览器模式
  --headless          使用无头模式（默认）
  --record            启用屏幕录制
  --no-prompt         跳过交互式提示

示例:
  python start_demo.py --headed
  python start_demo.py --scenario auto_demo/scenarios/quick_demo.yaml
  python start_demo.py --headed --record
```

### 创建自定义场景

在 `auto_demo/scenarios/` 目录下创建新的 YAML 文件：

```yaml
name: "My Custom Demo"
description: "Demo description"
base_url: "http://localhost:5000"

config:
  scroll_duration: 10
  action_delay: 1.5
  slow_motion: 50

steps:
  - action: navigate
    url: "/"
    description: "打开首页"
  
  - action: scroll_smooth
    direction: "down"
    duration: 5
    description: "向下滚动"
  
  - action: click
    selector: "button.submit"
    description: "点击提交按钮"
```

## 支持的动作 (Actions)

### navigate - 导航

跳转到指定URL

```yaml
- action: navigate
  url: "/report/123"
  description: "打开报告页面"
```

### click - 点击

点击页面元素

```yaml
- action: click
  selector: "text=生成AI报告"
  description: "点击按钮"
  optional: false  # 可选，失败时是否继续
  fallback:  # 备选选择器
    - selector: ".btn-primary"
    - selector: "#generateBtn"
```

### fill - 填充输入

在输入框中输入文本

```yaml
- action: fill
  selector: "#city"
  value: "成都"
  description: "填写城市"
```

### scroll_smooth - 平滑滚动

平滑滚动页面

```yaml
- action: scroll_smooth
  direction: "down"  # 或 "up"
  duration: 10  # 秒
  description: "向下滚动10秒"
```

### wait - 等待

等待指定时间

```yaml
- action: wait
  duration: 2  # 秒
  description: "等待加载"
```

### message - 显示消息

在控制台显示消息（不影响浏览器）

```yaml
- action: message
  text: "演示完成！"
  description: "显示完成消息"
```

## 选择器 (Selectors)

Playwright 支持多种选择器类型：

- **文本选择器**: `text=生成AI报告` 或 `text="完整匹配"`
- **CSS选择器**: `#id`, `.class`, `button.btn-primary`
- **XPath**: `//button[contains(text(), '提交')]`
- **组合选择器**: `button:has-text('生成')`
- **属性选择器**: `[name="city"]`, `input[type="text"]`

## 配置选项

在YAML文件的 `config` 部分可以设置：

```yaml
config:
  scroll_duration: 10    # 默认滚动持续时间（秒）
  action_delay: 1.5      # 动作之间的延迟（秒）
  slow_motion: 50        # 慢动作延迟，便于观察（毫秒）
```

## 屏幕录制

启用录制后，视频文件将保存在 `auto_demo/recordings/` 目录：

- 格式：WebM (VP9编码)
- 分辨率：1920x1080
- 文件名：包含时间戳

```bash
# 查看录制的视频
ls -lh auto_demo/recordings/
```

## 性能优化

为确保演示流畅高效：

1. **快速页面加载** - 使用 `domcontentloaded` 等待策略
2. **智能等待** - 自动等待元素可见和可交互
3. **平滑滚动** - 20fps的滚动动画，自然流畅
4. **合理超时** - 30秒的默认超时，避免长时间卡住

## 故障排除

### 问题：Flask服务器未运行

```
⚠️ Flask 服务器未运行在 http://localhost:5000
```

**解决方案**: 在另一个终端运行 `python app.py`

### 问题：Playwright未安装

```
playwright._impl._api_types.Error: Executable doesn't exist
```

**解决方案**: 运行 `playwright install chromium`

### 问题：元素未找到

```
Timeout 30000ms exceeded
```

**解决方案**:
1. 检查选择器是否正确
2. 增加等待时间
3. 使用 fallback 选择器
4. 将步骤标记为 `optional: true`

### 问题：录制视频无法播放

**解决方案**: 使用支持WebM的播放器（VLC、Chrome浏览器等）

## 最佳实践

1. **使用描述性步骤名称** - 便于理解和调试
2. **合理设置等待时间** - 避免过快导致失败
3. **使用回退选择器** - 提高鲁棒性
4. **标记可选步骤** - 避免因非关键步骤失败而中断
5. **测试场景** - 在 headless 和 headed 模式下都测试
6. **模块化场景** - 创建可复用的小场景文件

## 示例场景

查看 `auto_demo/scenarios/` 目录下的示例：

- `default_demo.yaml` - 完整的AI报告生成演示
- `quick_demo.yaml` - 30秒快速概览（待创建）
- `upload_demo.yaml` - 文件上传功能演示（待创建）

## 技术栈

- **Playwright** - 现代浏览器自动化框架
- **PyYAML** - YAML配置文件解析
- **Python 3.8+** - 异步编程支持
- **Chromium** - 自动化浏览器

## 开发

### 添加新动作

在 `demo_engine.py` 中添加新的动作处理器：

```python
async def _action_custom(self, step: Dict[str, Any]) -> bool:
    """Custom action implementation"""
    # Your logic here
    return True
```

然后在 `execute_action` 方法中注册：

```python
elif action == 'custom':
    return await self._action_custom(step)
```

### 调试技巧

1. 使用 `--headed` 查看浏览器行为
2. 检查日志输出了解每步执行情况
3. 在YAML中增加 `wait` 步骤观察状态
4. 使用浏览器开发者工具验证选择器

## 许可证

与主项目相同

## 支持

如有问题，请查看项目文档或提交Issue。
