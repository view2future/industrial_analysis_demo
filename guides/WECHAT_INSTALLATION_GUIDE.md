# 微信公众号功能安装和配置指南

## 1. wechatsogou 安装

### 1.1 基础安装

```bash
# 激活虚拟环境
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate     # Windows

# 安装 wechatsogou
pip install wechatsogou
```

### 1.2 可能遇到的问题及解决方案

#### 问题1: 安装失败
如果遇到安装失败，尝试以下方法：

```bash
# 升级 pip
pip install --upgrade pip

# 使用国内镜像安装
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple wechatsogou

# 或者尝试安装特定版本
pip install wechatsogou==2023.3.3
```

#### 问题2: 运行时出现验证码或限制
wechatsogou 使用搜狗微信搜索，可能遇到反爬虫限制：

1. **使用代理IP**：
```python
# 在 wechat_scraper.py 中可以配置代理
import wechatsogou
ws = wechatsogou.WechatSogouAPI(
    # 配置代理参数
    # proxies={'http': 'your_proxy', 'https': 'your_proxy'}
)
```

2. **降低请求频率**：
系统已内置请求频率控制，避免过于频繁的请求。

## 2. 微信公众号配置

### 2.1 配置文件位置
配置文件位于：`data/wechat_accounts_config.json`

### 2.2 配置文件结构
```json
[
  {
    "province": "四川省",
    "accounts": [
      "四川发布",
      "天府发布"
    ],
    "cities": [
      {
        "city": "成都市",
        "accounts": [
          "成都发布"
        ],
        "districts": [
          {
            "district": "高新区",
            "accounts": [
              "成都高新"
            ]
          }
        ]
      }
    ]
  }
]
```

### 2.3 配置说明
- `province`: 省份名称
- `accounts`: 省级公众号列表
- `cities`: 城市列表
  - `city`: 城市名称
  - `accounts`: 市级公众号列表
  - `districts`: 区县列表
    - `district`: 区县名称
    - `accounts`: 区县级公众号列表

## 3. 系统运行

### 3.1 启动应用
```bash
# 启动主应用
python app.py

# 启动 Celery 工作进程（处理后台任务）
celery -A src.tasks.celery_app worker --loglevel=info

# 启动 Celery Beat（处理定时任务）
celery -A src.tasks.celery_app beat --loglevel=info
```

### 3.2 自动任务
- 系统启动时：自动运行微信公众号内容抓取
- 每日凌晨2点：定时更新微信公众号内容

## 4. 故障排除

### 4.1 wechatsogou 不可用时的处理
如果 wechatsogou 库无法正常工作，系统会：
1. 记录警告日志："wechatsogou library not available, using mock implementation"
2. 使用预设的模拟数据继续运行
3. 不影响系统其他功能

### 4.2 检查微信功能是否正常
在系统启动日志中查找以下信息：
- "wechatsogou library loaded successfully" - 表示 wechatsogou 正常
- "WeChatSogouAPI initialized successfully" - 表示 API 初始化成功
- "Starting background WeChat articles fetch task..." - 表示后台任务已启动

### 4.3 数据库验证
可以通过以下方式验证微信文章是否正确存储：
1. 检查数据库中 WeChatArticle 表是否有数据
2. 在智能检索中查看是否有来自微信公众号的结果

## 5. 最佳实践

### 5.1 设置合适的公众号列表
- 优先设置政府官方发布类公众号
- 避免设置太多公众号，以免请求频率过高
- 定期更新配置以获取最相关的信息源

### 5.2 监控和维护
- 定期检查日志文件了解抓取情况
- 监控数据库中微信文章的更新频率
- 根据实际使用效果调整公众号列表