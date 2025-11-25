# UI组件库文档（统一风格与交互态）

## 设计Tokens
- 颜色/渐变/间距/阴影/圆角/字体见 `static/css/theme-modern.css` 与 `docs/figma-tokens.json`

## 组件清单与类名
- 布局与容器：`.glass-card`, `.card`, `.container`, `.gradient-bg`
- 表单元素：`.input-glow`, `.btn`, `.btn-primary`, `.btn-light`, `.btn-outline-light`
- 导航与面包屑：`.navbar`, `.breadcrumb`, `.breadcrumb-item`
- 表格：`.table`, `.table-striped`, `.badge-status.*`
- 卡片：`.feature-card`, `.report-card`
- 弹窗与提示：`.modal-content`, `.alert`, `.alert-info/success/warning/danger`
- 图标工具：`.icon-20`, `.icon-24`, `.icon-muted`, `.icon-primary`, `.icon-button`
- 进度与阶段：`.progress-glow`, `.stage-circle`
- 滚动条与焦点：`.custom-scrollbar`, `*:focus-visible`

## 交互态规范
- `hover`：轻微上浮与阴影增强；浅色按钮高光；表格行背景加强
- `active`：位移回落；阴影略减；主按钮亮度提升
- `focus`：强可见焦点边（3px）、偏移（2px）；输入框发光边框
- `disabled`：对比度降低、指针禁用、阴影移除
- `loading`：图标或按钮显示旋转指示；保持可见焦点态

## 使用示例
- 将按钮升级为品牌主色：`<a class="btn btn-primary">...</a>`
- 输入框发光焦点：`<input class="input-glow">`
- 卡片玻璃质感：`<div class="glass-card p-6">...</div>`
- 图标按钮可达区域：`<button class="icon-button"><i class="bi bi-gear icon-24"></i></button>`

## 图标统一与迁移
- 快速统一：对现有 `.fas/.bi` 应用 `.icon-24` 与颜色类
- 正式迁移建议：Material Symbols 或 Ant Design Icons；提供语义映射与候选方案清单

## 注意事项
- 不修改业务逻辑与路由，尽可能避免 DOM 改动；如需更换图标库，采取清单化最小替换
- 若冲突源于内联样式，优先使用更具体选择器或 `!important` 进行覆盖
