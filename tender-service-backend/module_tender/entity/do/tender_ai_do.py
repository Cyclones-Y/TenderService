from sqlalchemy import BigInteger, Column, JSON, Integer, DateTime, func
from config.database import Base

class BizTenderAiAnalysis(Base):
    """
    招标信息AI分析结果表
    """
    __tablename__ = 'biz_tender_ai_analysis'
    __table_args__ = ({'comment': '招标AI分析结果表'},)

    analysis_id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True, comment='主键ID')
    tender_id = Column(BigInteger, nullable=False, unique=True, index=True, comment='招标信息ID')
    analysis_result = Column(JSON, nullable=True, comment='AI分析结果JSON')
    create_time = Column(DateTime, server_default=func.now(), comment='创建时间')
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')
