from typing import Union

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from common.response import Response
from common.router import APIRouterPro
from common.vo import PageModel
from config.get_db import get_db
from module_tender.entity.do.tender_do import BizTenderInfo
from module_tender.entity.vo.tender_vo import (
    DeleteTenderModel,
    TenderModel,
    TenderPageQueryModel,
)
from module_tender.service.tender_service import TenderService

# 实例化路由对象
tenderController = APIRouterPro(prefix='/tender', tags=['招标信息管理'])


@tenderController.get(
    '/list', response_model=PageModel, summary='获取招标信息列表', description='获取招标信息列表'
)
async def get_tender_list(
    page_num: int = Query(1, description='页码'),
    page_size: int = Query(10, description='每页记录数'),
    project_name: str = Query(None, description='项目名称'),
    project_code: str = Query(None, description='项目编号'),
    district: str = Query(None, description='所在区县'),
    project_stage: str = Query(None, description='所处阶段'),
    begin_time: str = Query(None, description='开始时间'),
    end_time: str = Query(None, description='结束时间'),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """
    获取招标信息列表
    """
    tender_page_query = TenderPageQueryModel(
        page_num=page_num,
        page_size=page_size,
        project_name=project_name,
        project_code=project_code,
        district=district,
        project_stage=project_stage,
        begin_time=begin_time,
        end_time=end_time,
    )
    tender_list = await TenderService.get_tender_list(tender_page_query, db)
    return Response.success(tender_list)


@tenderController.get(
    '/{tender_id}', response_model=Union[BizTenderInfo, None], summary='获取招标信息详细信息', description='获取招标信息详细信息'
)
async def get_tender_detail(
    tender_id: int, db: AsyncSession = Depends(get_db)
) -> Response:
    """
    获取招标信息详细信息
    """
    tender_info = await TenderService.get_tender_detail(tender_id, db)
    return Response.success(tender_info)


@tenderController.post(
    '', response_model=BizTenderInfo, summary='新增招标信息', description='新增招标信息'
)
async def add_tender(
    tender: TenderModel, db: AsyncSession = Depends(get_db)
) -> Response:
    """
    新增招标信息
    """
    new_tender = await TenderService.add_tender(tender, db)
    return Response.success(new_tender)


@tenderController.put(
    '', summary='修改招标信息', description='修改招标信息'
)
async def update_tender(
    tender: TenderModel, db: AsyncSession = Depends(get_db)
) -> Response:
    """
    修改招标信息
    """
    await TenderService.update_tender(tender, db)
    return Response.success(msg='修改成功')


@tenderController.delete(
    '/{tender_ids}', summary='删除招标信息', description='删除招标信息'
)
async def delete_tender(
    tender_ids: str, db: AsyncSession = Depends(get_db)
) -> Response:
    """
    删除招标信息
    """
    delete_tender_model = DeleteTenderModel(tender_ids=tender_ids)
    await TenderService.delete_tender(delete_tender_model, db)
    return Response.success(msg='删除成功')
