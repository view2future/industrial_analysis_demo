# 浮动任务面板实现文档

## 概述

实现了一个完整的后台任务管理系统，包括浮动图标和浮动面板UI，用于跟踪和显示AI报告生成任务的实时状态。

## 实现的功能

### 1. 点击"后台运行"按钮后立即返回首页 ✓
- 点击"后台运行"按钮后，模态框立即关闭
- 页面自动重定向到首页 (`/`)
- 任务在后台继续运行

### 2. 右下角浮动图标 ✓
- **位置**: 固定在页面右下角 (bottom: 30px, right: 30px)
- **样式**: 
  - 处理中: 黄色渐变 + 旋转动画
  - 已完成: 红色渐变
- **功能**: 点击图标打开浮动面板，显示任务详情

### 3. 浮动面板显示任务状态 ✓
- **尺寸**: 450px × 650px
- **位置**: 右下角，浮动图标上方
- **内容**:
  - 任务列表（支持多个并发任务）
  - 实时进度条
  - 城市和行业信息
  - 用时统计
  - 当前阶段（初始化/生成大纲/生成内容/分析数据/完成报告）
- **交互**: 
  - 已完成任务显示"查看报告"按钮
  - 处理中任务显示进度条和实时状态

### 4. 模态框布局调整 ✓
- **LLM实时内容区域**: 45vh (约300px最小高度)
- **状态消息区域**: 20vh (overflow-y: auto)
- 布局更加合理，符合用户体验

### 5. 支持多报告同时生成 ✓
- 使用localStorage持久化任务列表
- 每个任务独立跟踪状态
- 页面刷新后自动恢复任务状态
- 自动重新开始未完成任务的轮询

## 技术实现

### 文件结构

```
static/js/floating_task.js       # 浮动任务管理器核心逻辑
templates/base.html              # 在所有页面加载floating_task.js
templates/index_enhanced.html    # 首页也加载floating_task.js
templates/generate_report.html   # 修改后台运行按钮逻辑，调整模态框布局
```

### 核心功能

#### floating_task.js
- **initFloatingIcon()**: 初始化浮动图标
- **addBackgroundTask(taskId, city, industry)**: 添加后台任务
- **startTaskPolling(taskId)**: 开始轮询任务状态 (每2秒)
- **updateFloatingPanelContent()**: 更新浮动面板内容
- **saveBackgroundTasks() / restoreBackgroundTasks()**: 持久化和恢复任务

#### 任务状态管理
```javascript
{
    taskId: 'xxx',              // 任务ID
    city: '成都',               // 目标城市
    industry: '人工智能',       // 目标行业
    startTime: timestamp,       // 开始时间
    reportId: null,             // 报告ID（完成后填充）
    status: 'processing',       // 状态
    stage: 'init'               // 当前阶段
}
```

#### 阶段映射
- **init**: 初始化 (10% 进度)
- **outline**: 生成大纲 (30% 进度)
- **generation**: 生成内容 (60% 进度)
- **analysis**: 分析数据 (85% 进度)
- **finalize**: 完成报告 (95% 进度)
- **completed**: 已完成 (100% 进度)

### API集成

任务状态通过轮询 `/api/task-status/<task_id>` 获取:
```json
{
    "state": "SUCCESS",
    "status": "completed",
    "result": {
        "report_id": "xxx"
    },
    "info": {
        "current_step": 3
    }
}
```

## 修改的文件

### 1. `static/js/floating_task.js` (新增)
- 466行代码
- 完整的任务管理和UI逻辑

### 2. `templates/generate_report.html`
- 移除旧的浮动图标HTML和样式
- 修改"后台运行"按钮逻辑，在点击时调用 `window.addBackgroundTask()`
- 在任务创建后设置 `currentTaskId`, `currentCity`, `currentIndustry`
- 调整模态框布局：LLM区域 45vh，状态区域 20vh
- 引入 `floating_task.js`

### 3. `templates/base.html`
- 在 `</body>` 前引入 `floating_task.js`
- 确保所有页面都能显示浮动图标和面板

### 4. `templates/index_enhanced.html`
- 引入 `floating_task.js`
- 首页也能显示后台任务状态

## 使用流程

1. 用户在 `/generate-report` 页面填写表单并提交
2. 模态框显示，任务开始生成
3. 用户点击"后台运行"按钮
4. 系统调用 `window.addBackgroundTask(taskId, city, industry)`
5. 浮动图标立即显示在右下角（黄色，旋转动画）
6. 页面重定向到首页
7. 浮动图标持续显示，后台轮询任务状态
8. 任务完成后，图标变为红色
9. 点击图标打开浮动面板，显示任务详情
10. 点击"查看报告"按钮跳转到报告页面

## 测试建议

1. **单任务测试**:
   - 生成一个报告
   - 点击"后台运行"
   - 验证立即跳转到首页
   - 验证浮动图标显示
   - 验证点击图标打开面板
   - 验证任务完成后图标变红

2. **多任务测试**:
   - 连续生成多个报告（不同城市/行业）
   - 全部点击"后台运行"
   - 验证面板显示所有任务
   - 验证每个任务独立跟踪状态

3. **持久化测试**:
   - 生成报告并后台运行
   - 刷新页面
   - 验证任务仍在列表中
   - 验证轮询自动恢复

4. **跨页面测试**:
   - 后台运行任务后访问其他页面 (如 `/upload`, `/v3_roadmap`)
   - 验证浮动图标在所有页面都显示
   - 验证点击图标在任何页面都能打开面板

## 注意事项

- 浮动图标使用 z-index: 10000，浮动面板使用 z-index: 9999，确保不被其他元素遮挡
- 任务列表保存在 localStorage 中，浏览器清除数据后任务列表会丢失
- 轮询间隔为2秒，可根据服务器负载调整
- 图标位置固定在右下角，移动端可能需要适配

## 未来改进

1. 添加清除已完成任务的按钮
2. 添加任务失败重试功能
3. 支持拖拽调整浮动面板位置
4. 添加通知功能（任务完成时弹出通知）
5. 优化移动端显示
6. 添加任务取消功能
7. 支持任务队列管理（暂停/恢复）

## 问题排查

### 浮动图标不显示
- 检查浏览器控制台是否有JS错误
- 确认 `floating_task.js` 已正确加载
- 确认任务已成功创建并添加到 `window.backgroundTasks`

### 任务状态不更新
- 检查 `/api/task-status/<task_id>` 是否正常返回
- 确认轮询是否正常运行（控制台会有日志）
- 检查任务ID是否正确

### 页面刷新后任务丢失
- 检查localStorage是否被禁用
- 确认 `restoreBackgroundTasks()` 是否正常执行
- 检查浏览器控制台是否有localStorage相关错误

### 面板样式异常
- 确认Bootstrap 5已正确加载
- 检查Bootstrap Icons是否可用
- 确认没有CSS冲突

## 总结

本次实现完全解决了之前提到的所有问题：
1. ✅ 点击"后台运行"立即返回首页
2. ✅ 右下角浮动图标显示任务状态
3. ✅ 点击图标打开浮动面板而不是跳转页面
4. ✅ 面板显示实时任务状态
5. ✅ 模态框布局调整（上大下小）
6. ✅ 支持多任务并发生成

系统现在具备完整的后台任务管理能力，用户体验得到显著提升。
