# 🎬 区域产业分析小工作台 - 自动演示系统

## 🚀 快速开始

### 一键启动演示
```bash
python3 start_demo.py
```

### 系统要求检查
```bash
python3 test_demo_quick.py
```

## 📋 系统功能

✅ **全自动演示**: 从系统启动到功能演示完全自动化  
✅ **智能录屏**: 自动录制演示过程生成视频  
✅ **多平台支持**: 支持macOS、Linux、Windows  
✅ **一键操作**: 简单启动，无需复杂配置  
✅ **完整流程**: 展示项目所有核心功能  

## 🎯 演示内容（2分钟）

### 第1阶段：系统启动 (0-15秒)
- 🚀 自动启动Flask应用
- 🌐 打开Chrome浏览器
- 📹 开始录屏

### 第2阶段：首页展示 (15-30秒)
- 🏠 展示项目标题和简介
- 📖 滚动展示主要功能特性
- 🎨 展示现代化UI设计

### 第3阶段：文件上传 (30-60秒)
- 📤 导航到上传页面
- 📋 展示支持的文件格式
- 🔄 自动上传示例产业分析报告

### 第4阶段：智能分析 (60-90秒)
- ⚡ 展示实时分析进度
- 🤖 AI智能文本处理
- 📊 多维度数据分析

### 第5阶段：结果展示 (90-120秒)
- 📈 交互式可视化图表
  - 饼图：内容分类分布
  - 雷达图：AI应用潜力
  - 柱状图：关键词频次
  - 条形图：文档统计
- 📑 分类分析详情
- 💡 AI应用机会识别

## 📦 包含组件

### 核心文件
- `start_demo.py` - 一键启动主程序
- `demo_system.py` - 完整演示系统
- `demo_simple.py` - macOS简化版
- `demo_requirements.txt` - 依赖包列表
- `demo_guide.md` - 详细使用指南

### 测试和验证
- `test_demo_quick.py` - 快速系统检测
- `test_demo_system.py` - 完整功能测试

## 🔧 安装步骤

### 1. 系统检测
```bash
python3 test_demo_quick.py
```

### 2. 安装依赖（如需要）
```bash
pip3 install -r demo_requirements.txt
```

### 3. 启动演示
```bash
python3 start_demo.py
```

## 📁 输出文件

### 视频文件
- 📍 位置：`demo_output/demo_YYYYMMDD_HHMMSS.mp4`
- ⏱️ 时长：约2分钟
- 📐 分辨率：屏幕原始分辨率
- 🎯 帧率：10fps

### 日志文件
- 📍 位置：`demo_system.log`
- 📝 内容：详细运行记录和错误信息

## ⚡ 高级用法

### macOS简化版
```bash
python3 demo_simple.py
```

### 手动运行完整版
```bash
python3 demo_system.py
```

### 自定义演示
编辑`demo_system.py`修改：
- 演示时长和步骤
- 示例文件选择
- 录屏参数设置

## 🛠️ 系统要求

### 必需环境
- 🐍 Python 3.8+
- 🌐 Chrome浏览器
- 💾 8GB+ RAM
- 💽 2GB+ 可用磁盘空间

### 支持平台
- ✅ macOS（推荐）
- ✅ Linux
- ✅ Windows

## 🔍 故障排除

### 常见问题

#### ❌ Chrome驱动问题
```bash
# 自动安装Chrome驱动
python3 -c "from webdriver_manager.chrome import ChromeDriverManager; ChromeDriverManager().install()"
```

#### ❌ 端口被占用
```bash
# 检查端口占用
lsof -i :5000  # macOS/Linux
netstat -ano | findstr :5000  # Windows
```

#### ❌ 权限问题（macOS）
系统偏好设置 → 安全性与隐私 → 屏幕录制 → 添加终端

#### ❌ 依赖包缺失
```bash
# 重新安装依赖
pip3 install selenium pyautogui opencv-python numpy webdriver-manager
```

### 详细调试
查看日志文件：`demo_system.log`

## 📞 技术支持

### 测试系统
```bash
python3 test_demo_quick.py  # 快速检测
python3 test_demo_system.py # 完整测试
```

### 手动验证
访问测试地址：
- 主页：http://localhost:5000
- 上传：http://localhost:5000/upload
- 设置：http://localhost:5000/settings

## 🎉 成功标志

✅ **测试通过**：`所有测试通过！演示系统可以正常运行`  
✅ **演示完成**：`🎉 演示成功完成！`  
✅ **视频生成**：`视频文件保存在: demo_output/demo_*.mp4`  

---

## 🚀 现在就开始！

```bash
# 1. 系统检测
python3 test_demo_quick.py

# 2. 启动演示
python3 start_demo.py

# 3. 等待2分钟，获得完整演示视频
```

**🎬 您的专业演示视频即将生成！**