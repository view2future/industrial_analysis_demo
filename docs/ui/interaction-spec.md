# 交互动效说明

## 时长与缓动曲线
- 标准过渡：`300ms cubic-bezier(0.22, 1, 0.36, 1)`（变量：`--transition-medium`）
- 快速过渡：`180ms cubic-bezier(0.22, 1, 0.36, 1)`（变量：`--transition-fast`）
- 骨架屏闪动：`1.6s` 循环 `@keyframes shimmer`
- 粒子动画：每帧 60FPS，持续运行（在加载容器显示期间）

## 触发条件
- 悬停（hover）：应用于 `.interactive`、`.btn`、`.card-hover`、`.glass-card`，触发轻微位移与阴影增强
- 聚焦（focus-visible）：`*:focus-visible` 使用 3px 可见焦点轮廓，符合 WCAG 2.1 AA
- 表单聚焦：`.input-glow:focus` 触发外扩光晕与主色描边
- 加载：在需要的容器添加 `.skeleton-block`；同时通过 `initParticleLoader('<containerId>')` 在容器上叠加粒子动画

## 动态图标
- 图标库：Remix Icon（线性风格），通过 CDN 加载
- 形变动画：通过 `interactive` 类触发颜色与位移过渡；如需更复杂形变，建议使用 SVG 路径动画（后续可扩展）

## 性能建议
- 限制阴影层级与模糊半径，避免在低端设备产生明显卡顿
- 粒子数量根据容器面积自适应（最少 24）；在移动端建议禁用粒子层

## 可访问性
- 对比度遵循 WCAG 2.1 AA；文本颜色使用 `#2D3748`，按钮与链接在 hover/active 时保持充足对比
- 键盘导航：所有按钮与链接均可获得可见焦点轮廓；图标按钮具备 `aria-label` 或伴随文本
