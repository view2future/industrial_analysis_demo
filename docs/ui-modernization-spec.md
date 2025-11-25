# UI现代化设计规范（仅CSS覆写，DOM不变）

## 设计语言
- 风格：Glassmorphism + Neumorphism，科技蓝与深空灰基调，霓虹点缀
- 原则：外观替换与动效增强，不改变页面的DOM结构与业务逻辑

## 品牌与配色
- 主色 `--brand-primary`: #4C6FFF
- 次色 `--brand-secondary`: #1F2937（深空灰/深夜蓝）
- 紫色 `--brand-purple`: #7C3AED
- 霓虹点缀 `--accent-neon`: #00E7FF
- 渐变 `--brand-gradient`: linear-gradient(135deg, #4C6FFF 0%, #7C3AED 100%)
- 背景柔和 `--bg-soft`: #F6F8FA

状态色（覆盖示例）
- 完成：绿色梯度（#22C55E → #16A34A）
- 处理中：琥珀梯度（#FDE68A → #F59E0B）
- 待处理：灰蓝梯度（#94A3B8 → #64748B）
- 失败：红色梯度（#F87171 → #DC2626）

## 字体系统
- 首选：`Inter`、`SF Pro Display`
- 回退：`-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica Neue, Arial, Google Sans, Noto Sans, PingFang SC, Microsoft YaHei, sans-serif`
- 全局已通过 `static/css/theme-modern.css` 应用

## 间距系统（8pt网格）
- `--space-1: 8px`、`--space-2: 16px`、`--space-3: 24px`、`--space-4: 32px`、`--space-5: 40px`、`--space-6: 48px`、`--space-7: 56px`、`--space-8: 64px`
- 卡片与区块建议：内边距 24–32px；区块间距 24–40px

## 阴影与圆角
- 阴影：`--shadow-soft`、`--shadow-strong`；新拟态双阴影：`--neu-shadow-top`、`--neu-shadow-bottom`
- 圆角：`--radius-md: 12px`、`--radius-lg: 16px`、`--radius-xl: 22px`

## 组件外观规范（基于现有类名）
- 导航与Hero：`.gradient-bg`、`.navbar`、`.hero-section` 使用 `--brand-gradient` 与霓虹高光
- 卡片：`.card`、`.feature-card`、`.glass-card` 统一圆角、玻璃质感、柔和阴影
- 按钮：`.btn` 系列统一圆角与动效；`.btn-primary` 使用品牌渐变；`.btn-light/.btn-outline-light` 使用半透明玻璃样式
- 输入：`.input-glow` 边框与发光焦点
- 徽章：`.badge-status` 各状态赋色梯度
- 进度：`.progress-glow` 霓虹内发光
- 图标：`.fas/.bi` 统一霓虹色 `--accent-neon`

## 动效规范
- 进入：`fade-up`（420ms）与 `scale-in`（420ms）默认应用到 `.card/.glass-card/.feature-card/.report-card`
- 微交互：悬停上浮（2–6px）、阴影增强、色彩高光
- 缓动：`--easing: cubic-bezier(0.22, 1, 0.36, 1)`

## 覆盖策略与兼容性
- 全局CSS位于 `static/css/theme-modern.css`，在 `templates/base.html` 引入，覆盖不需改DOM
- 针对页面内联样式与重复的 `:root` 变量，通过 `!important` 提升优先级，确保品牌色一致
- 保留现有Bootstrap/Tailwind工具类，避免破坏布局与交互
- 若页面出现局部冲突，优先编写更具体的选择器覆盖（避免改模板）

## 渐进式替换建议
- 新功能或页面统一使用上述CSS变量，不再在页面局部重新定义颜色/字体
- 逐步将内联 `style` 的色值替换为类或变量（在后续维护周期进行，不在本次交付中强制）

## 交付清单与位置
- CSS主题与变量：`static/css/theme-modern.css`
- 全局引用：`templates/base.html` 引入 `<link rel="stylesheet" ...>`
- 设计规范：本文件 `docs/ui-modernization-spec.md`

## 注意事项
- 仅通过CSS覆写实现外观变更，未修改任何页面DOM结构或业务逻辑
- 如需更高级的页面转场与序列动效，可在不改DOM的前提下追加CSS关键帧；JS类库（如Framer Motion）不在本次交付范围内

