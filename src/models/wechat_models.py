from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# 在 app.py 中已经初始化了 db，这里只是定义模型
# 以下模型将被添加到 app.py 中


class WeChatArticle(db.Model):
    """WeChat article model to store articles from specified WeChat accounts."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    content = db.Column(db.Text)  # 存储完整文章内容
    publish_date = db.Column(db.String(20))  # 发布日期，格式：YYYY-MM-DD
    author = db.Column(db.String(100))  # 作者
    source_account = db.Column(db.String(200), nullable=False)  # 公众号名称
    url = db.Column(db.String(500))  # 文章链接
    summary = db.Column(db.Text)  # 文章摘要
    keywords = db.Column(db.Text)  # 关键词，JSON格式存储
    industry_relevance = db.Column(db.Text)  # 相关产业，JSON格式存储
    content_html = db.Column(db.Text)  # 原始HTML内容
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 创建时间
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间
    
    def to_dict(self):
        """Convert model instance to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'publish_date': self.publish_date,
            'author': self.author,
            'source_account': self.source_account,
            'url': self.url,
            'summary': self.summary,
            'keywords': self.keywords.split(',') if self.keywords else [],
            'industry_relevance': self.industry_relevance.split(',') if self.industry_relevance else [],
            'content_html': self.content_html,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }