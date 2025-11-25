# API 错误处理和通知系统指南

## 概述

本系统提供了全面的 API 错误处理机制，能够智能检测和处理 Kimi、Google Gemini、豆包大模型等 AI 服务的配额超限、连接问题等错误，并通过用户友好的通知系统及时告知用户。

## 功能特性

### 🎯 核心功能
- **智能错误检测**: 自动识别 API 配额超限、连接超时、服务不可用等错误
- **服务回退机制**: 当主要服务失败时，自动切换到备用服务
- **用户通知系统**: 及时向用户发送友好的错误通知和解决方案
- **错误分析和建议**: 提供详细的错误分析和可操作的建议
- **系统监控**: 实时监控 API 服务状态和错误趋势

### 🔧 支持的 API 服务
- **Kimi (月之暗面)**: 中文 AI 大模型服务
- **Google Gemini**: Google 的多模态 AI 服务
- **豆包大模型**: 字节跳动的 AI 服务

## 系统架构

### 核心组件

```
src/utils/
├── api_error_handler.py      # API 错误处理核心逻辑
├── notification_service.py   # 用户通知服务
└── __init__.py

src/ai/
└── llm_generator.py          # 增强版 LLM 生成器（支持回退）

api_notification_routes.py    # Flask API 路由（通知和状态）
```

### 错误处理流程

```
API 调用失败
    ↓
错误检测和分类
    ↓
┌─────────────────────────────────────────────────┐
│ 配额超限？ → 通知用户配额不足 → 尝试回退到其他服务 │
│ 连接问题？ → 通知用户网络问题 → 建议检查网络设置   │
│ 认证失败？ → 通知用户密钥问题 → 建议检查配置      │
│ 其他错误？ → 通用错误处理 → 记录日志和通知        │
└─────────────────────────────────────────────────┘
    ↓
服务回退（如果启用）
    ↓
结果通知（成功/失败）
```

## 使用方法

### 1. 基本配置

在 `config.json` 中配置 API 密钥：

```json
{
  "api_keys": {
    "kimi_api_key": "your-kimi-api-key",
    "google_gemini_api_key": "your-gemini-api-key",
    "doubao_api_key": "your-doubao-api-key"
  }
}
```

### 2. 使用 LLM 生成器

```python
from src.ai.llm_generator import LLMReportGenerator

# 创建支持回退的生成器
generator = LLMReportGenerator(
    llm_service='kimi',  # 首选服务
    enable_fallback=True  # 启用回退机制
)

# 生成报告
result = generator.generate_report(
    city='成都',
    industry='人工智能',
    additional_context='重点关注 AI 芯片产业'
)

# 检查结果
if result['success']:
    print(f"报告生成成功！使用服务: {result.get('used_service', 'unknown')}")
    print(f"尝试过的服务: {result.get('attempted_services', [])}")
else:
    print(f"报告生成失败: {result.get('error', '未知错误')}")
    if 'api_error' in result:
        api_error = result['api_error']
        print(f"错误类型: {api_error['type']}")
        print(f"用户消息: {api_error['user_message']}")
        print(f"建议操作: {api_error['suggested_action']}")
```

### 3. 处理 API 错误

```python
from src.utils.api_error_handler import handle_api_error, APIService

try:
    # 你的 API 调用代码
    result = api_client.generate_content(prompt)
except Exception as e:
    # 智能错误处理
    api_error = handle_api_error(e, 'kimi', "报告生成")
    
    # 获取错误信息
    print(f"错误类型: {api_error.error_type.value}")
    print(f"用户消息: {api_error.user_friendly_message}")
    print(f"建议操作: {api_error.suggested_action}")
    print(f"重试等待: {api_error.retry_after} 秒")
    
    # 根据错误类型采取相应措施
    if api_error.error_type.value == 'quota_exceeded':
        # 切换到其他服务
        fallback_service = api_error_handler.get_fallback_service(
            APIService.KIMI, available_services
        )
    elif api_error.error_type.value == 'connection_timeout':
        # 等待后重试
        time.sleep(api_error.retry_after or 30)
```

### 4. 发送用户通知

```python
from src.utils.notification_service import notification_service

# API 配额超限通知
notification = notification_service.notify_api_quota_exceeded(
    service_name='kimi',
    user_id='user123',
    suggested_action='建议切换到 Gemini 服务或等待下个月配额重置'
)

# 连接错误通知
notification = notification_service.notify_api_connection_error(
    service_name='gemini',
    error_message='连接超时',
    user_id='user123'
)

# 服务回退通知
notification = notification_service.notify_service_fallback(
    original_service='kimi',
    fallback_service='gemini',
    success=True,
    user_id='user123'
)

# 报告生成结果通知
notification = notification_service.notify_report_generation_result(
    success=True,
    city='成都',
    industry='人工智能',
    service_used='kimi',
    user_id='user123'
)
```

### 5. API 状态查询

```javascript
// 获取用户通知
fetch('/api/notifications')
    .then(response => response.json())
    .then(data => {
        console.log('通知:', data.notifications);
        console.log('未读数:', data.unread_count);
    });

// 获取通知统计
fetch('/api/notifications/stats')
    .then(response => response.json())
    .then(data => {
        console.log('通知统计:', data.stats);
    });

// 获取 API 状态
fetch('/api/api-status')
    .then(response => response.json())
    .then(data => {
        console.log('API 状态:', data.error_summary);
        console.log('最近错误:', data.recent_errors);
    });

// 标记通知为已读
fetch('/api/notifications/notification_id/read', {method: 'POST'})
    .then(response => response.json());
```

## 错误类型和处理

### 配额超限 (quota_exceeded)
- **检测关键词**: `quota exceeded`, `rate limit exceeded`, `余额不足`, `配额已用完`
- **处理方式**: 自动切换到其他可用服务，通知用户配额不足
- **用户建议**: 切换到其他 AI 服务，或等待配额重置

### 连接问题
- **连接超时** (connection_timeout): 网络连接超时
- **连接拒绝** (connection_refused): 服务拒绝连接
- **服务不可用** (service_unavailable): 服务暂时不可用
- **处理方式**: 等待后重试，或切换到其他服务
- **用户建议**: 检查网络连接，稍后重试

### 认证错误 (authentication_error)
- **检测关键词**: `authentication failed`, `invalid api key`, `认证失败`
- **处理方式**: 通知用户检查 API 密钥配置
- **用户建议**: 检查 config.json 文件中的 API 密钥

### 请求频率限制 (rate_limited)
- **检测关键词**: `too many requests`, `rate limit`
- **处理方式**: 等待后重试，使用指数退避策略
- **用户建议**: 降低请求频率，稍后重试

## 用户界面集成

### 通知显示
在页面模板中添加通知组件：

```html
<!-- 通知徽章 -->
<div class="notification-badge" id="notificationBadge">
    <span id="notificationCount">0</span>
</div>

<!-- 通知面板 -->
<div class="notification-panel" id="notificationPanel">
    <div class="notification-header">
        <h3>通知中心</h3>
        <button onclick="markAllAsRead()">全部已读</button>
    </div>
    <div class="notification-content" id="notificationContent">
        <!-- 通知列表 -->
    </div>
</div>
```

### API 状态显示
```html
<div class="api-status-panel">
    <div class="api-status-header">
        <div class="api-status-title">API 服务状态</div>
        <div class="status-indicator" id="overallStatus">
            <div class="status-dot status-healthy"></div>
            <span>系统正常</span>
        </div>
    </div>
    <div class="api-services" id="apiServices">
        <!-- 服务状态卡片 -->
    </div>
</div>
```

### JavaScript 集成
```javascript
// 定期更新通知
function updateNotifications() {
    fetch('/api/notifications')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateNotificationUI(data.notifications, data.unread_count);
            }
        });
}

// 定期更新 API 状态
function updateAPIStatus() {
    fetch('/api/api-status')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateAPIStatusUI(data.error_summary, data.has_recent_issues);
            }
        });
}

// 每 30 秒更新一次
setInterval(() => {
    updateNotifications();
    updateAPIStatus();
}, 30000);
```

## 测试和验证

### 运行测试脚本
```bash
# 运行 API 错误处理测试
python test_api_error_handling.py
```

### 模拟 API 错误
```bash
# 使用演示页面测试通知系统
# 访问: http://localhost:5000/notification_demo.html
```

### 验证功能
1. **配额超限处理**: 测试当 API 配额用完时的自动回退
2. **连接问题处理**: 模拟网络问题，验证错误处理和重试
3. **通知系统**: 验证用户通知的创建、显示和管理
4. **服务回退**: 测试主要服务失败时的备用服务切换

## 最佳实践

### 1. 错误处理
- 始终使用 `try-except` 块包装 API 调用
- 使用错误处理器获取用户友好的错误信息
- 根据错误类型采取适当的处理措施

### 2. 用户通知
- 及时发送通知，但不要过于频繁
- 提供清晰的错误描述和解决建议
- 允许用户管理通知（标记已读、删除）

### 3. 服务回退
- 配置多个 API 服务以提高可靠性
- 优先使用响应速度快、稳定性高的服务
- 记录实际使用的服务以便分析

### 4. 监控和日志
- 记录所有 API 错误和回退事件
- 定期分析错误模式和服务性能
- 设置警报监控关键错误

## 故障排除

### 常见问题

**Q: 通知不显示**
A: 检查通知服务是否正确初始化，用户 ID 是否匹配

**Q: 服务回退失败**
A: 确认 config.json 中配置了多个 API 密钥

**Q: 错误检测不准确**
A: 检查错误模式配置，可以添加新的错误关键词

**Q: API 状态不更新**
A: 确认前端 JavaScript 正确调用 API 端点

### 调试技巧
1. 查看详细日志：`logs/` 目录下的日志文件
2. 使用测试脚本验证各个组件
3. 检查浏览器控制台的前端错误
4. 验证配置文件格式和 API 密钥

## 更新和维护

### 添加新的 API 服务
1. 在 `api_error_handler.py` 中添加服务配置
2. 在 `llm_generator.py` 中实现服务调用逻辑
3. 更新通知服务中的服务显示名称
4. 添加相应的错误模式

### 更新错误模式
根据实际遇到的错误，更新 `ERROR_PATTERNS` 配置：

```python
ERROR_PATTERNS = {
    APIService.NEWSERVICE: {
        APIErrorType.QUOTA_EXCEEDED: [
            r'new.*quota.*pattern',
            r'another.*pattern'
        ],
        # ... 其他错误类型
    }
}
```

### 性能优化
- 定期清理过期的通知和错误历史
- 使用缓存减少 API 状态查询
- 优化错误检测算法以提高准确性

---

这个 API 错误处理和通知系统为您的区域产业分析小工作台提供了强大的容错能力，确保即使在 API 服务出现问题时，用户也能获得良好的体验。通过智能的错误检测、服务回退和用户通知，系统能够保持稳定运行并及时向用户提供反馈。