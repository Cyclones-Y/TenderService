from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class TenderModel(BaseModel):
    """
    招标信息表对应pydantic模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)

    tender_id: int | None = Field(default=None, description='主键ID')
    project_code: str | None = Field(default=None, description='项目编号')
    project_name: str | None = Field(default=None, description='项目名称')
    district: str | None = Field(default=None, description='所在区县')
    construction_unit: str | None = Field(default=None, description='建设单位')
    project_stage: str | None = Field(default=None, description='所处阶段')
    project_type: str | None = Field(default=None, description='项目类型')
    bid_control_price: float | None = Field(default=None, description='招标控制价（万元）')
    bid_price: float | None = Field(default=None, description='中标价（万元）')
    construction_scale: str | None = Field(default=None, description='建设规模')
    construction_content: str | None = Field(default=None, description='施工内容')
    tender_scope: str | None = Field(default=None, description='招标范围')
    duration: str | None = Field(default=None, description='工期')
    registration_deadline: datetime | None = Field(default=None, description='报名截止时间')
    agency: str | None = Field(default=None, description='代理机构')
    release_time: date | None = Field(default=None, description='信息发布时间')
    expected_announcement_date: str | None = Field(default=None, description='预计招标公告发布时间')
    announcement_website: str | None = Field(default=None, description='公告网站')
    pre_qualification_url: str | None = Field(default=None, description='预审公告收集网址')
    winner_rank_1: str | None = Field(default=None, description='中标排名1')
    winner_rank_2: str | None = Field(default=None, description='中标排名2')
    winner_rank_3: str | None = Field(default=None, description='中标排名3')
    discount_rate: str | None = Field(default=None, description='中标下浮率（%）')
    unit_price: float | None = Field(default=None, description='单方造价（万元/㎡或万元/项）')
    evaluation_report_1: str | None = Field(default=None, description='评标报告_1')
    evaluation_report_2: str | None = Field(default=None, description='评标报告_2')
    evaluation_report_3: str | None = Field(default=None, description='评标报告_3')
    bid_date: date | None = Field(default=None, description='中标日期')
    bid_announcement_url: str | None = Field(default=None, description='中标公告网址')
    create_by: str | None = Field(default=None, description='创建者')
    create_time: datetime | None = Field(default=None, description='创建时间')
    update_by: str | None = Field(default=None, description='更新者')
    update_time: datetime | None = Field(default=None, description='更新时间')
    remark: str | None = Field(default=None, description='备注')


class TenderQueryModel(TenderModel):
    """
    招标信息管理不分页查询模型
    """

    begin_time: str | None = Field(default=None, description='开始时间')
    end_time: str | None = Field(default=None, description='结束时间')
    tender_ids: str | None = Field(default=None, description='选中的招标信息ID集合，逗号分隔')


class TenderPageQueryModel(TenderQueryModel):
    """
    招标信息管理分页查询模型
    """

    page_num: int = Field(default=1, description='当前页码')
    page_size: int = Field(default=10, description='每页记录数')


class DeleteTenderModel(BaseModel):
    """
    删除招标信息模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    tender_ids: str = Field(description='需要删除的招标信息ID')


class DistrictStatModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    name: str = Field(description='名称')
    value: int = Field(description='数值')


class StageStatModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    name: str = Field(description='名称')
    value: int = Field(description='数值')


class TrendStatModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    date: str = Field(description='日期')
    count: int = Field(description='数量')


class TenderDashboardModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    total_projects: int = Field(description='总招标项目数')
    month_new: int = Field(description='本月新增')
    total_amount_billion: float = Field(description='涉及金额（亿元）')
    top_district: str = Field(description='活跃区县')
    last_sync_minutes_ago: int = Field(description='上次同步时间（分钟前）')
    last_sync_hours_ago: float = Field(description='上次同步时间（小时前）')
    last_sync_time: str | None = Field(description='上次同步具体时间')
    district_stats: list[DistrictStatModel] = Field(description='区域分布统计')
    stage_stats: list[StageStatModel] = Field(description='项目阶段分布统计')
    trend_stats: list[TrendStatModel] = Field(description='趋势统计')
