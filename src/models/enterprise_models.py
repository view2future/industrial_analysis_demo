from datetime import datetime

# This file will be imported dynamically in the routes to avoid circular imports
# The db instance will be imported when the models are actually needed
def get_models(db_ref):
    """
    Dynamic function to create models with the provided db reference
    This avoids circular imports by creating models at runtime
    """

    # Check if model already exists to avoid conflicts
    if hasattr(db_ref, 'models') and 'Enterprise' in db_ref.models:
        # Return existing models if they already exist
        return db_ref.models['Enterprise'], db_ref.models['EnterpriseMeeting']

    class Enterprise(db_ref.Model):
        """Enterprise model to store enterprise information."""
        __tablename__ = 'enterprises'
        __table_args__ = {'extend_existing': True}  # This allows redefinition of table

        id = db_ref.Column(db_ref.Integer, primary_key=True)
        # 企业名称 - Text (unique)
        enterprise_name = db_ref.Column(db_ref.String(200), unique=True, nullable=False, comment='企业唯一标识')

        # 飞桨/文心 - Enum (PaddlePaddle/Wenxin)
        ai_platform = db_ref.Column(db_ref.String(50), nullable=False, comment='使用的核心AI技术')

        # 线索入库时间 - Text (quarter format)
        lead_inbound_time = db_ref.Column(db_ref.String(20), nullable=False, comment='线索获取时间，格式为2025Q4')

        # 线索更新时间 - DateTime (auto updated)
        lead_update_time = db_ref.Column(db_ref.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='数据最新变动时间')

        # 伙伴等级 - Enum (Certified/Preferred/None)
        partner_level = db_ref.Column(db_ref.String(50), nullable=True, comment='合作深度等级')

        # 生态AI产品 - Text
        ai_products = db_ref.Column(db_ref.Text, comment='记录合作成果')

        # 优先级 - Enum (P0/P1/P2)
        priority = db_ref.Column(db_ref.String(10), nullable=False, comment='跟进优先级')

        # base - Text (location)
        base_location = db_ref.Column(db_ref.Text, comment='企业地理位置')

        # 注册资本 - Integer (in units of 10,000)
        registered_capital = db_ref.Column(db_ref.Integer, comment='注册资本，单位为万')

        # 参保人数 - Integer
        employee_count = db_ref.Column(db_ref.Integer, comment='参保人数')

        # 企业背景 - Text
        enterprise_background = db_ref.Column(db_ref.Text, comment='核心业务与合作基础')

        # 行业 - Text (JSON format for multiple industries)
        industry = db_ref.Column(db_ref.Text, comment='所属领域，JSON格式存储多个行业')

        # 任务方向 - Text
        task_direction = db_ref.Column(db_ref.Text, comment='企业使用飞桨或文心所运用的技术')

        # 联系人信息 - Text
        contact_info = db_ref.Column(db_ref.Text, comment='对接人信息')

        # 使用场景 - Text
        usage_scenario = db_ref.Column(db_ref.Text, comment='核心业务数据')

        # 进展 - JSON (for storing multiple version records)
        progress = db_ref.Column(db_ref.JSON, comment='跟进情况，包含历史记录')

        # Timestamps
        created_at = db_ref.Column(db_ref.DateTime, default=datetime.utcnow)
        updated_at = db_ref.Column(db_ref.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

        def to_dict(self):
            """Convert model instance to dictionary for JSON serialization."""
            return {
                'id': self.id,
                'enterprise_name': self.enterprise_name,
                'ai_platform': self.ai_platform,
                'lead_inbound_time': self.lead_inbound_time,
                'lead_update_time': self.lead_update_time.isoformat() if self.lead_update_time else None,
                'partner_level': self.partner_level,
                'ai_products': self.ai_products,
                'priority': self.priority,
                'base_location': self.base_location,
                'registered_capital': self.registered_capital,
                'employee_count': self.employee_count,
                'enterprise_background': self.enterprise_background,
                'industry': self.industry.split(',') if self.industry else [],
                'task_direction': self.task_direction,
                'contact_info': self.contact_info,
                'usage_scenario': self.usage_scenario,
                'progress': self.progress or [],
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'updated_at': self.updated_at.isoformat() if self.updated_at else None
            }

    class EnterpriseMeeting(db_ref.Model):
        """Meeting model to store enterprise meeting records."""
        __tablename__ = 'enterprise_meetings'
        __table_args__ = {'extend_existing': True}  # This allows redefinition of table

        id = db_ref.Column(db_ref.Integer, primary_key=True)
        meeting_type = db_ref.Column(db_ref.String(50), nullable=False, comment='会议类型：内部会议/外部会议')  # 'internal' or 'external'

        # For external meetings
        enterprise_id = db_ref.Column(db_ref.Integer, db_ref.ForeignKey('enterprises.id'), nullable=True, comment='关联企业ID')
        enterprise_name = db_ref.Column(db_ref.String(200), comment='参会企业名称')  # For new customers not in DB

        # Meeting details
        attendees = db_ref.Column(db_ref.Text, comment='参会人信息')  # JSON format
        meeting_time = db_ref.Column(db_ref.DateTime, nullable=False, comment='会议时间')
        meeting_location = db_ref.Column(db_ref.Text, comment='会议地点')
        meeting_summary = db_ref.Column(db_ref.Text, comment='会议纪要')

        created_at = db_ref.Column(db_ref.DateTime, default=datetime.utcnow)
        updated_at = db_ref.Column(db_ref.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

        def to_dict(self):
            """Convert model instance to dictionary for JSON serialization."""
            return {
                'id': self.id,
                'meeting_type': self.meeting_type,
                'enterprise_id': self.enterprise_id,
                'enterprise_name': self.enterprise_name,
                'attendees': self.attendees.split(',') if self.attendees else [],
                'meeting_time': self.meeting_time.isoformat() if self.meeting_time else None,
                'meeting_location': self.meeting_location,
                'meeting_summary': self.meeting_summary,
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'updated_at': self.updated_at.isoformat() if self.updated_at else None
            }

    return Enterprise, EnterpriseMeeting