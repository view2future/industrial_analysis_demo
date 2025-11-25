# 全项目UI现代化整改方案（统一风格与图标规范）

## 当前栈与页面范围
- 模板体系：Flask/Jinja，主要页面与布局：
  - 基模板：`templates/base.html`（导航/页脚，已加载 Tailwind 与图标库）
  - 首页（Bootstrap版）：`templates/index_enhanced.html`
  - 报告生成页：`templates/generate_report.html`
  - 流式生成页：`templates/stream_report.html`
  - 报告查看页：`templates/report_view.html`
  - 静态演示首页：`templates/index.html`
- 全局样式：`static/css/styles.css` 与各模板内联 `<style>`；不使用 CSS-in-JS
- 现有图标库：Font Awesome + Bootstrap Icons（混用）

## 改造目标
- 全站统一现代化设计语言（Glass + Neo），统一配色、字体、间距、阴影、动效
- 组件（布局、表单、导航、表格、卡片、弹窗/提示）风格一致且具备完整交互态
- 图标统一风格与语义，大小/颜色/可访问性一致；为特殊功能图标提供 ≥3 个候选
- 保持功能与交互逻辑不变，必要时进行最小 DOM 调整以达成统一图标库

## 设计系统（Design Tokens）
- 颜色：主色 `#4C6FFF`、次色深空灰 `#1F2937`、品牌紫 `#7C3AED`、霓虹点缀 `#00E7FF`
- 渐变：`linear-gradient(135deg, #4C6FFF 0%, #7C3AED 100%)`
- 字体：`Plus Jakarta Sans` → `Inter` → `SF Pro Display` → 系统栈
- 间距：8pt 网格（8/16/24/32/40/48/56/64）
- 阴影与圆角：柔和/增强阴影、新拟态双阴影；圆角 12/16/22px
- 动效：模块级入场（fade-up/scale-in 420ms），微交互悬停上浮与高光

## 组件级统一升级
- 布局与容器：统一卡片/容器圆角、阴影与玻璃质感，Hero 与导航使用品牌渐变
- 表单元素：`input/select/textarea` 焦点发光、边框高亮、禁用态对比增强；按钮统一圆角与梯度
- 导航/面包屑：导航文字与悬停高光统一；面包屑新增一致的层级与分隔符样式
- 数据表格：表头/行悬停/选中/禁用态统一；分页与状态徽章风格一致
- 卡片：标题区与操作区统一间距与字体权重；悬停阴影与轻微位移
- 弹窗与提示：统一圆角、阴影、遮罩透明度；信息层级颜色（info/success/warning/error）

## 图标统一规范与替换策略
- 推荐库：Material Symbols（Rounded）或 Ant Design Icons（二选一）
- 迁移策略（两阶段）：
  1. 快速统一（不改/微改 DOM）：为现有 `.fas/.bi` 图标统一大小/颜色/对比度与可访问性（`aria-hidden` 与 `aria-label` 规则），先消除视觉不一致；提供 CSS 别名类（如 `.icon-24`、`.icon-muted`）。
  2. 正式迁移（小规模 DOM 替换）：将 Font Awesome/Bootstrap Icons 替换为选定库，对应语义核对清单；为特殊功能图标给出 ≥3 个候选（例如“AI生成”“知识图谱”“产业链”等）。
- 点击区域与可访问性：统一最小触达面积 40×40px；键盘焦点可见；图标按钮添加 `aria-label`。

## 实施步骤
### 阶段1：设计系统与全局样式落地（优先级最高）
1. 在 `static/css/theme-modern.css` 统一 Tokens 与基础组件样式（已存在文件将完善扩展）。
2. 在 `templates/base.html` 全局加载主题；对独立模板（`index_enhanced.html`、`report_view.html`、`index.html`）确保引入统一主题。
3. 提取各模板 `:root` 局部变量，改由主题集中管理，减少冲突。

### 阶段2：组件库统一与交互态补齐
1. 表单：统一 `.input-glow`/`.btn` 系列的 `hover/active/focus/disabled`；选择器与下拉菜单对比度增强。
2. 表格：添加 `.table-modern` 统一行高、斑马纹、悬停与选中态；徽章 `.badge-status` 梯度与可读性统一。
3. 卡片/弹窗/提示：统一 `.glass-card/.modal/.alert` 视觉与分层阴影。
4. 面包屑：提供 `.breadcrumb-modern` 样式（不改逻辑，若缺失则按现有结构样式化）。

### 阶段3：图标统一与错误修复
1. 盘点所有图标与语义映射：导出覆盖清单（页面/位置/现用类/建议替换）。
2. 快速统一：CSS 层面统一大小/颜色/对比度；补充 `aria-label` 与辅助说明。
3. 正式迁移：引入选定图标库（Material 或 AntD），按清单替换；每个特殊功能图标提供 ≥3 个候选预览。

### 阶段4：质量保证与测试
1. 跨浏览器：Chrome/Edge/Safari；移动端：iOS Safari、Android Chrome；分辨率断点（320–1920px）。
2. 状态覆盖：`hover/active/focus/disabled/loading/success/error/warning/info` 均有样式并可见。
3. 可访问性：对比度、键盘导航、焦点可见性、语义标签与 `aria-*`。
4. 代码质量：为 `static/js/*.js` 与 `static/css/*.css` 配置 ESLint 与 Stylelint（使用 `eslint:recommended` 与 `stylelint-config-standard`），修复告警。
5. 截图对比：改造前后关键页面模块的对比图文档。

### 阶段5：交付与文档
- UI组件库文档：组件分类、示例、交互态、设计 Tokens、使用方式与覆盖策略。
- 图标规范与替换清单：包含错误图标修复说明与候选方案。
- 测试报告：跨设备与浏览器结果、问题与修复说明。
- 截图对比文档：页面级与组件级对比图。

## 初步时间表（24小时内交付初稿）
- T+6h：完成 Tokens 与全局样式扩展、表单/按钮统一、导航/Hero 统一；提交首页与“生成AI报告”页面初版效果截图。
- T+12h：完成表格/卡片/提示/弹窗统一；提交组件库文档初稿（含交互态）。
- T+18h：输出图标盘点与迁移建议 + 特殊功能图标候选预览；修复明显错误图标。
- T+24h：完成跨浏览器基础测试与截图对比文档，提交初步修改方案与实施清单。

## 高保真设计稿（Figma/Sketch）
- 交付内容：
  - 设计 Tokens（颜色/半径/阴影/间距/字体）作为 Variables/Tokens Studio 文件
  - 组件库：按钮、输入、选择器、表格、卡片、徽章、导航、面包屑、弹窗、提示
  - 页面高保真：首页与“生成AI报告”两张全幅稿；可选扩展“流式生成页”与“报告查看页”
- 链接提供方式：确认方案后，我将在 Figma 创建并上传组件库与页面稿，生成可公开访问的分享链接并回传；如需 Sketch 源文件，同步导出并提供下载。

## 风险与兼容性说明
- 内联 `style` 与重复 `:root` 变量可能造成覆盖冲突，将通过更高优先级选择器或适度 `!important` 解决。
- 图标库迁移涉及类名变更（小型 DOM 调整），将按“清单化替换”进行，确保语义与功能一致，逐页验证。

——请确认是否选择 Material Symbols（Rounded）或 Ant Design Icons 作为统一图标库；确认后我将按上述时间表推进并提交初版效果与文档。