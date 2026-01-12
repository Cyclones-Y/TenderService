from datetime import datetime

from sqlalchemy import BigInteger, Column, Date, DateTime, Numeric, String, UniqueConstraint

from config.database import Base
from config.env import DataBaseConfig
from utils.common_util import SqlalchemyUtil


class BizTenderInfo(Base):
    """
    招标信息表
    """

    __tablename__ = 'biz_tender_info'
    __table_args__ = (
        UniqueConstraint('project_code', 'project_stage', name='uq_biz_tender_info_code_stage'),
        {'comment': '招标信息表'},
    )

    tender_id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True, comment='主键ID')

    project_code = Column(
        String(64),
        unique=False,
        nullable=True,
        server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type),
        comment='项目编号',
    )
    project_name = Column(
        String(200),
        nullable=True,
        server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type),
        comment='项目名称',
    )
    district = Column(
        String(100),
        nullable=True,
        server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type),
        comment='所在区县',
    )
    construction_unit = Column(
        String(200),
        nullable=True,
        server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type),
        comment='建设单位',
    )
    project_stage = Column(
        String(50),
        nullable=True,
        server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type),
        comment='所处阶段',
    )
    project_type = Column(
        String(100),
        nullable=True,
        server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type),
        comment='项目类型',
    )

    bid_control_price = Column(
        Numeric(18, 6),
        nullable=True,
        server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type),
        comment='招标控制价（万元）',
    )
    bid_price = Column(
        Numeric(18, 6),
        nullable=True,
        server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type),
        comment='中标价（万元）',
    )

    construction_scale = Column(
        String(500),
        nullable=True,
        server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type),
        comment='建设规模',
    )
    construction_content = Column(
        String(500),
        nullable=True,
        server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type),
        comment='施工内容',
    )
    tender_scope = Column(
        String(500),
        nullable=True,
        server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type),
        comment='招标范围',
    )
    duration = Column(
        String(50),
        nullable=True,
        server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type),
        comment='工期',
    )
    registration_deadline = Column(
        DateTime,
        nullable=True,
        server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type),
        comment='报名截止时间',
    )
    agency = Column(
        String(200),
        nullable=True,
        server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type),
        comment='代理机构',
    )

    release_time = Column(Date, nullable=True, comment='信息发布时间')
    expected_announcement_date = Column(
        String(100),
        nullable=True,
        server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type),
        comment='预计招标公告发布时间',
    )
    announcement_website = Column(
        String(100),
        nullable=True,
        server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type),
        comment='公告网站',
    )
    pre_qualification_url = Column(
        String(255),
        nullable=True,
        server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type),
        comment='预审公告收集网址',
    )

    winner_rank_1 = Column(
        String(100),
        nullable=True,
        server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type),
        comment='中标排名1',
    )
    winner_rank_2 = Column(
        String(100),
        nullable=True,
        server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type),
        comment='中标排名2',
    )
    winner_rank_3 = Column(
        String(100),
        nullable=True,
        server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type),
        comment='中标排名3',
    )
    evaluation_report_1 = Column(
        String(255),
        nullable=True,
        server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type),
        comment='评标报告_1',
    )
    evaluation_report_2 = Column(
        String(255),
        nullable=True,
        server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type),
        comment='评标报告_2',
    )
    evaluation_report_3 = Column(
        String(255),
        nullable=True,
        server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type),
        comment='评标报告_3',
    )

    discount_rate = Column(
        String(20),
        nullable=True,
        server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type),
        comment='中标下浮率（%）',
    )
    unit_price = Column(
        Numeric(18, 2),
        nullable=True,
        server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type),
        comment='单方造价（万元/㎡或万元/项）',
    )
    bid_date = Column(
        DateTime,
        nullable=True,
        server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type),
        comment='中标日期',
    )
    bid_announcement_url = Column(
        String(255),
        nullable=True,
        server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type),
        comment='中标公告网址',
    )

    create_by = Column(String(64), nullable=True, server_default="''", comment='创建者')
    create_time = Column(DateTime, nullable=True, default=datetime.now(), comment='创建时间')
    update_by = Column(String(64), nullable=True, server_default="''", comment='更新者')
    update_time = Column(DateTime, nullable=True, default=datetime.now(), comment='更新时间')
    remark = Column(
        String(500),
        nullable=True,
        server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type),
        comment='备注',
    )
