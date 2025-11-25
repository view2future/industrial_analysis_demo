# 区域产业分析小工作台 - 自动演示系统

## 系统概述

自动演示系统可以：
- 🎬 自动启动应用并执行完整演示流程
- 📹 自动录屏生成演示视频（2分钟内）
- 🔄 一键启动，无需人工干预
- 📊 展示项目的主要功能和特色

## 系统要求

### 基础要求
- Python 3.8+
- Chrome浏览器
- 8GB+ RAM
- 2GB+ 可用磁盘空间

### 操作系统
- ✅ macOS（支持完整版和简化版）
- ✅ Linux（支持完整版）
- ✅ Windows（支持完整版）

## 安装步骤

### 1. 安装Chrome浏览器
访问 https://www.google.com/chrome/ 下载并安装

### 2. 安装演示系统依赖
```bash
# 安装演示系统依赖
pip install -r demo_requirements.txt

# 或者分别安装
pip install selenium pyautogui opencv-python numpy webdriver-manager
```

### 3. 确保项目依赖已安装
```bash
# 安装项目依赖
pip install -r requirements.txt
```

## 使用方法

### 一键启动（推荐）
```bash
python start_demo.py
```

### 简化版（macOS专用）
```bash
python demo_simple.py
```

### 自定义故事线演示
```bash
python start_custom_demo.py
```

### 手动运行完整版
```bash
python demo_system.py
```

## 演示流程

### 自动演示包含以下步骤：

### 自定义故事线演示步骤：
1. **系统启动** (0-5秒)
   - 启动Flask应用
   - 打开Chrome浏览器

2. **首页展示** (5-10秒)
   - 从上到下滑动鼠标，完整展示首页
   - 停留2秒钟时间

3. **上传页面展示** (10-15秒)
   - 进入文件上传页面
   - 停留3秒钟

4. **演示结束**
   - 自动关闭浏览器和应用

1. **系统启动** (0-10秒)
   - 启动Flask应用
   - 打开Chrome浏览器
   - 开始录屏

2. **首页展示** (10-25秒)
   - 展示项目标题和简介
   - 滚动展示主要功能
   - 展示界面设计

3. **上传功能演示** (25-45秒)
   - 导航到上传页面
   - 展示文件上传区域
   - 自动上传示例文件

4. **分析过程展示** (45-75秒)
   - 展示分析进度
   - 等待分析完成
   - 过渡到结果页面

5. **分析结果展示** (75-120秒)
   - 核心要点展示
   - 可视化图表展示
   - 分类分析详情
   - AI应用机会展示

6. **高级功能展示** (可选)
   - 设置页面
   - 地图可视化
   - 知识图谱

## 输出文件

### 视频文件
- 格式：MP4 (完整版) / MOV (简化版)
- 分辨率：屏幕原始分辨率
- 帧率：10fps
- 时长：约2分钟
- 保存位置：`demo_output/demo_YYYYMMDD_HHMMSS.mp4`

### 日志文件
- `demo_system.log` - 详细运行日志
- `demo_output/` - 演示输出目录

## 常见问题

### Q: Chrome驱动安装失败
**A:** 确保已安装Chrome浏览器，然后手动安装驱动：
```bash
pip install webdriver-manager
```

### Q: 录屏权限问题（macOS）
**A:** 系统偏好设置 → 安全性与隐私 → 屏幕录制 → 添加终端

### Q: 演示过程中出现错误
**A:** 检查`demo_system.log`获取详细错误信息

### Q: 视频文件太大
**A:** 可以调整录屏参数，降低分辨率或帧率

### Q: Flask应用启动失败
**A:** 检查5000端口是否被占用：
```bash
lsof -i :5000  # macOS/Linux
netstat -ano | findstr :5000  # Windows
```

## 自定义演示

### 创建自定义故事线
可以通过修改`demo/custom_story_demo.py`文件来自定义演示故事线：
1. 修改`demo_homepage`方法来自定义首页演示
2. 修改`demo_upload_page`方法来自定义上传页面演示
3. 添加新的演示方法并将其添加到`run_custom_story_demo`方法中

### 自定义演示开发
创建新的自定义演示脚本：
```python
# 在custom_story_demo.py中添加新方法
def demo_custom_page(self):
    # 实现自定义页面演示逻辑
    pass

# 在run_custom_story_demo方法中调用
self.demo_custom_page()
```

## 技术支持

### 日志文件位置
- 演示日志：`demo_system.log`
- 应用日志：`logs/`目录

### 调试模式
修改日志级别为DEBUG：
```python
logging.basicConfig(level=logging.DEBUG)
```

### 手动测试
可以手动访问以下地址测试功能：
- 主页：http://localhost:5000
- 上传：http://localhost:5000/upload
- 设置：http://localhost:5000/settings
- 地图：http://localhost:5000/map_visualization
- 知识图谱：http://localhost:5000/knowledge_graph

### 自定义故事线测试
- 自定义演示：http://localhost:5000
- 上传页面：http://localhost:5000/upload

## 最佳实践

### 演示前准备
1. 关闭不必要的应用程序
2. 清理桌面和通知
3. 确保网络连接稳定
4. 调整屏幕分辨率到合适大小
5. 关闭系统通知

### 演示设置
1. 使用外接显示器（可选）
2. 确保充足的光线
3. 关闭屏幕保护程序
4. 调整音量到合适水平

### 后期处理
1. 检查视频质量和完整性
2. 可以添加背景音乐或解说
3. 压缩视频文件（如需要）
4. 添加标题和结尾

## 更新日志

### v1.0.0 (2025-01-05)
- ✨ 初始版本发布
- 🎬 自动演示功能
- 📹 自动录屏功能
- 🔄 一键启动系统
- 📊 完整流程演示

---

**注意**: 首次运行可能需要授权屏幕录制权限，请按系统提示操作。