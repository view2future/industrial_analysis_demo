# Google Gemini API 网络配置指南

## 问题诊断

当前检测到**网络连接问题**:
- Google API 端点 `generativelanguage.googleapis.com` 无法访问
- 错误: `Connection timeout` / `UNAVAILABLE`

## 解决方案

### 方案1: 配置代理 (推荐)

如果你使用代理访问国际网络,需要配置环境变量:

```bash
# 在 start.sh 或 终端中设置
export HTTP_PROXY="http://your-proxy:port"
export HTTPS_PROXY="http://your-proxy:port"
export http_proxy="http://your-proxy:port"
export https_proxy="http://your-proxy:port"

# 或者如果有认证
export HTTP_PROXY="http://username:password@your-proxy:port"
export HTTPS_PROXY="http://username:password@your-proxy:port"
```

**修改 start.sh 文件:**

```bash
#!/bin/bash

# 配置代理 (根据你的实际代理设置)
# export HTTP_PROXY="http://127.0.0.1:7890"
# export HTTPS_PROXY="http://127.0.0.1:7890"

# 其他启动命令...
python app_enhanced.py
```

### 方案2: 检查防火墙

确保防火墙允许访问:
- `generativelanguage.googleapis.com:443`
- `*.googleapis.com:443`

### 方案3: 测试连通性

```bash
# 测试能否访问 Google API
curl -I https://generativelanguage.googleapis.com

# 如果上面失败,尝试 ping
ping generativelanguage.googleapis.com

# 检查DNS解析
nslookup generativelanguage.googleapis.com
```

### 方案4: 使用代理的 Python 配置

如果需要在 Python 代码中配置代理:

```python
import os

# 在导入 google.generativeai 之前设置
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'

import google.generativeai as genai
```

## 验证 API 密钥

确保你的 API Key 有效:

```bash
curl "https://generativelanguage.googleapis.com/v1beta/models?key=YOUR_API_KEY"
```

## 已实施的代码优化

已更新 `src/ai/llm_generator.py`:

1. ✅ **添加重试逻辑** - 3次重试,指数退避
2. ✅ **增加超时设置** - 600秒主报告,300秒摘要/SWOT
3. ✅ **优化模型配置** - 添加 generation_config 和 safety_settings
4. ✅ **更好的错误处理** - 详细日志记录

## 测试 API 连接

```bash
cd /Users/wangyu94/regional-industrial-dashboard

# 简单测试
python3 << 'EOF'
import google.generativeai as genai
import json

with open('config.json') as f:
    api_key = json.load(f)['api_keys']['google_gemini_api_key']

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-pro')

try:
    response = model.generate_content("你好")
    print(f"✓ API 工作正常: {response.text[:50]}")
except Exception as e:
    print(f"✗ API 错误: {e}")
EOF
```

## 常见错误及解决

### 错误 1: `ServiceUnavailable: 503`
**原因**: 网络无法访问 Google 服务器  
**解决**: 配置代理 (见方案1)

### 错误 2: `PERMISSION_DENIED: 403`
**原因**: API Key 无效或没有权限  
**解决**: 
1. 检查 `config.json` 中的 API Key
2. 到 https://makersuite.google.com/app/apikey 重新生成

### 错误 3: `RESOURCE_EXHAUSTED: 429`
**原因**: API 配额用尽  
**解决**: 等待配额重置或升级配额

### 错误 4: `DeadlineExceeded`
**原因**: 请求超时  
**解决**: 已在代码中增加超时时间到 600 秒

## 推荐配置

对于中国大陆用户:

1. **使用代理服务** (必需)
2. **检查 API Key 区域限制**
3. **考虑使用其他端点** (如果 Google 提供备用端点)

## 下一步

1. 配置你的网络代理
2. 重启系统: `./start.sh`
3. 测试报告生成功能
4. 查看日志确认连接成功

如果问题持续,检查:
- `/Users/wangyu94/regional-industrial-dashboard/logs/celery.log`
- Flask 应用日志
