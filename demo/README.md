# 自定义故事线演示系统

这是一个基于Selenium的自动化演示系统，可以根据用户定义的故事线执行特定的演示流程。

## 功能特点

- 🎬 自定义演示故事线
- 🖱️ 精确的鼠标控制和页面交互
- ⏱️ 可配置的演示时间控制
- 🌐 支持Chrome浏览器自动化
- 📋 简单易用的一键启动

## 演示故事线

当前演示包含以下步骤：

1. **系统启动** - 自动启动Flask应用和Chrome浏览器
2. **首页展示** - 从上到下滑动鼠标，完整展示首页，停留2秒钟
3. **上传页面** - 进入文件上传页面，停留3秒钟
4. **演示结束** - 自动清理资源并关闭浏览器

## 使用方法

### 一键启动（推荐）
```bash
python start_custom_demo.py
```

### 使用简化版（不依赖Selenium）
```bash
python start_custom_demo.py --simple
```

### 直接运行
```bash
python demo/custom_story_demo.py
```

### 直接运行简化版
```bash
python demo/simple_custom_demo.py
```

## 自定义演示故事线

要创建自己的演示故事线，请修改 `demo/custom_story_demo.py` 文件：

1. 修改现有方法以调整演示行为
2. 添加新方法以扩展演示功能
3. 在 `run_custom_story_demo()` 方法中调整执行顺序

## 系统要求

- Python 3.8+
- Chrome浏览器（完整版）
- Selenium WebDriver（完整版）

## 安装依赖

```bash
pip install -r demo/demo_requirements.txt
```

## 测试系统

```bash
python tests/test_custom_demo.py
```