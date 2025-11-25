# 区域产业分析小工作台设计规范（V1）

## 目标
- 统一全站配色、字体、间距与交互模式
- 提升可读性与可访问性（对比度、可聚焦、键盘导航）
- 建立可复用的组件样式与设计令牌（CSS变量）

## 设计令牌（CSS Variables）
- 颜色
  - `--brand-primary`: 主色 `#3A86FF`
  - `--brand-secondary`: 辅助色 `#FF6B35`
  - `--brand-purple`: 强调色 `#7c3aed`
  - `--brand-gradient`: 渐变（主色→辅色）
  - `--text-strong`: 正文主色、对比度高
  - `--text-muted`: 次要文字、说明文字
- 间距与圆角
  - `--space-1` ~ `--space-8`: 8px 步进间距系统
  - `--radius-md`/`--radius-lg`/`--radius-xl`: 圆角等级
- 阴影与动效
  - `--shadow-soft`/`--shadow-strong`: 卡片与悬浮阴影
  - `--transition-fast`/`--transition-medium` 与 `--easing`
- 字体与排版
  - `--font-sans`/`--font-serif`/`--font-mono`
  - `--font-size-base`: `16px`
  - `--line-height-base`: `1.7`
  - `--heading-line-height`: `1.3`

## 字体层级系统
- 标题（Sans）：页面标题 `h1` 2.0rem；区块标题 `h2` 1.6rem；小标题 `h3` 1.3rem
- 正文（Serif）：基线 16px，行高 1.7~1.8
- 代码（Mono）：`code`/`pre` 使用 `--font-mono`

## Markdown 渲染规范
- 统一由服务端 `markdown2` 渲染，并启用 extras：
  - `fenced-code-blocks`, `tables`, `strike`, `task_list`, `code-friendly`, `toc`
- 样式类：统一使用 `.markdown-content`
  - 最大宽度 `75ch`，居中
  - 行高 `1.8`，段落间距 `0.8em`
  - 自动断行：`word-break: break-word; overflow-wrap: anywhere;`
  - 代码块深色底、圆角与滚动；行内代码浅色底

## 配色方案与对比度
- 渐变背景：使用 `.gradient-bg`
- 渐变文字：使用 `.gradient-text`
- 文本对比度：正文采用 `--text-strong`；弱化信息采用 `--text-muted`
- 链接悬停与可聚焦：统一使用可见 `outline` 与颜色变化

## 组件样式约定
- 按钮 `.btn` 基础圆角与悬浮动效
  - 主按钮 `.btn-primary` 使用品牌渐变与光晕
  - 浅色按钮 `.btn-light` 用于深色背景的对比显示
- 卡片 `.card` / `.glass-card`：圆角、阴影与悬浮提升
- 输入 `.input-glow`：聚焦高亮与阴影
- 徽章 `.badge-status`：完成/处理中/待定/失败四状态

## 间距与布局网格
- 页面容器：`max-w-7xl` + 适配 `px-4 sm:px-6 lg:px-8`
- 区块间距：大区块 `--space-6~8`；内容内间距 `--space-2~4`

## 导航与交互模式
- 顶部导航统一使用 `.gradient-bg` 与主题切换按钮（`#themeToggle`）
- 所有可交互元素提供 `:focus-visible` 样式与 `aria-label`

## 无障碍与响应式
- 键盘可达：按钮与表单控件必须可聚焦
- 色弱友好：避免仅依赖颜色表达状态；配合图标/文字
- 响应式：图表容器适配 `resize()`；断点布局采用 Tailwind 工具类

## 应用规范
- 所有页面继承 `templates/base.html`
- Markdown 区域使用 `.markdown-content`，避免使用 `.prose`
- 渐变文字请使用全局 `.gradient-text`，不在页面内重复定义

## 版本与维护
- 本规范版本：V1.0（2025-11-13）
- 维护位置：`static/css/theme-modern.css` 与本文档
- 后续扩展：状态色、表单校验样式、数据表组件、图表主题统一等

