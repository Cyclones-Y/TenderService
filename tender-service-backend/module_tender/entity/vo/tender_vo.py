from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class TenderModel(BaseModel):
    """
    招标信息表对应pydantic模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)

    tender_id: Optional[int] = Field(default=None, description='主键ID')
    project_code: Optional[str] = Field(default=None, description='项目编号')
    project_name: Optional[str] = Field(default=None, description='项目名称')
    district: Optional[str] = Field(default=None, description='所在区县')
    construction_unit: Optional[str] = Field(default=None, description='建设单位')
    project_stage: Optional[str] = Field(default=None, description='所处阶段')
    project_type: Optional[str] = Field(default=None, description='项目类型')
    bid_control_price: Optional[float] = Field(default=None, description='招标控制价（万元）')
    bid_price: Optional[float] = Field(default=None, description='中标价（万元）')
    construction_scale: Optional[str] = Field(default=None, description='建设规模')
    construction_content: Optional[str] = Field(default=None, description='施工内容')
    tender_scope: Optional[str] = Field(default=None, description='招标范围')
    duration: Optional[str] = Field(default=None, description='工期')
    registration_deadline: Optional[datetime] = Field(default=None, description='报名截止时间')
    agency: Optional[str] = Field(default=None, description='代理机构')
    release_time: Optional[date] = Field(default=None, description='信息发布时间')
    expected_announcement_date: Optional[str] = Field(default=None, description='预计招标公告发布时间')
    announcement_website: Optional[str] = Field(default=None, description='公告网站')
    pre_qualification_url: Optional[str] = Field(default=None, description='预审公告收集网址')
    winner_rank_1: Optional[str] = Field(default=None, description='中标排名1')
    winner_rank_2: Optional[str] = Field(default=None, description='中标排名2')
    winner_rank_3: Optional[str] = Field(default=None, description='中标排名3')
    discount_rate: Optional[str] = Field(default=None, description='中标下浮率（%）')
    unit_price: Optional[float] = Field(default=None, description='单方造价（万元/㎡或万元/项）')
    bid_date: Optional[date] = Field(default=None, description='中标日期')
    bid_announcement_url: Optional[str] = Field(default=None, description='中标公告网址')
    create_by: Optional[str] = Field(default=None, description='创建者')
    create_time: Optional[datetime] = Field(default=None, description='创建时间')
    update_by: Optional[str] = Field(default=None, description='更新者')
    update_time: Optional[datetime] = Field(default=None, description='更新时间')
    remark: Optional[str] = Field(default=None, description='备注')


class TenderQueryModel(TenderModel):
    """
    招标信息管理不分页查询模型
    """

    begin_time: Optional[str] = Field(default=None, description='开始时间')
    end_time: Optional[str] = Field(default=None, description='结束时间')


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
