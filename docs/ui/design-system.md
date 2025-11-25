# 设计系统

## 色彩体系
- 基础表面渐变：`#F5F7FA → #E1E8ED`（变量：`--surface-gradient`）
- 主色（科技蓝）：`#3A86FF`（变量：`--brand-primary`）
- 辅色（活力橙）：`#FF6B35`（变量：`--brand-secondary`）
- 文字主色：`#2D3748`（变量：`--text-strong`）
- 文字次色：`#475569`（变量：`--text-muted`）
- 玻璃拟态：背景 `rgba(255,255,255,0.72)`，边框 `rgba(255,255,255,0.35)`，`backdrop-filter: blur(10px)`
- 按钮微光晕：`box-shadow: 0 0 15px rgba(58, 134, 255, 0.3)`

## 间距与圆角
- 间距规模：`--space-1: 8px`、`--space-2: 16px`、`--space-3: 24px`、`--space-4: 32px`、`--space-5: 40px`、`--space-6: 48px`、`--space-7: 56px`、`--space-8: 64px`
- 圆角：`--radius-md: 12px`、`--radius-lg: 16px`、`--radius-xl: 22px`
- 阴影：`--shadow-soft`、`--shadow-strong`

## 字体层级
- 标题：Sans（`Inter`/`SF Pro Display`），`--font-sans`
- 正文：Serif（`Lora`/`Noto Serif`），`--font-serif`
- 代码：Mono（`Fira Code`），`--font-mono`

### 建议字号
- H1：32px（桌面）/ 24px（移动）
- H2：24px / 20px
- 正文：16px / 15px
- 辅助文字：14px

## 组件规范
- 按钮：`btn btn-primary` 使用品牌渐变与微光晕；`btn-light` 采用玻璃拟态风格
- 输入框：`input-glow` 聚焦光晕与主色描边
- 卡片：`glass-card` 具备背景透明与模糊，悬停提升阴影层级

## 无障碍
- 焦点可见：使用 `*:focus-visible` 的 3px 轮廓（与品牌色相关）
- 对比度：确保文本与背景对比达到 AA 标准；图表与装饰性元素避免成为唯一信息载体
