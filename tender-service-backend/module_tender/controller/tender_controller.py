from typing import Annotated
import json

from fastapi import Depends, Form, Query, Request, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from common.router import APIRouterPro
from common.vo import DataResponseModel, PageModel
from config.get_db import get_db
from module_tender.entity.vo.tender_vo import (
    AiTenderAnalysisModel,
    AiAnalysisHistoryItemModel,
    DeleteTenderModel,
    TenderDashboardModel,
    TenderModel,
    TenderPageQueryModel,
)
from module_tender.service.tender_service import TenderService
from utils.common_util import bytes2file_response
from utils.response_util import ResponseUtil

# 实例化路由对象
tender_controller = APIRouterPro(prefix='/tenders', tags=['招标信息管理'])


@tender_controller.get(
    '', response_model=PageModel, summary='获取招标信息列表', description='获取招标信息列表'
)
async def get_tender_list(
    page_num: int = Query(1, description='页码'),
    page_size: int = Query(10, description='每页记录数'),
    project_name: str = Query(None, description='项目名称'),
    project_code: str = Query(None, description='项目编号'),
    district: str = Query(None, description='所在区县'),
    project_stage: str = Query(None, description='所处阶段'),
    project_type: str = Query(None, description='项目类型'),
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
        project_type=project_type,
        begin_time=begin_time,
        end_time=end_time,
    )
    tender_list = await TenderService.get_tender_list(tender_page_query, db)
    return ResponseUtil.success(model_content=tender_list)


@tender_controller.get(
    '/dashboard',
    response_model=DataResponseModel[TenderDashboardModel],
    summary='获取招标数据概览',
    description='用于获取数据概览页面所需的统计数据',
)
async def get_tender_dashboard(db: AsyncSession = Depends(get_db)) -> Response:
    dashboard = await TenderService.get_dashboard_stats(db)
    return ResponseUtil.success(data=dashboard)


@tender_controller.get(
    '/{tender_id}', response_model=DataResponseModel[TenderModel], summary='获取招标信息详细信息', description='获取招标信息详细信息'
)
async def get_tender_detail(
    tender_id: int, db: AsyncSession = Depends(get_db)
) -> Response:
    """
    获取招标信息详细信息
    """
    tender_info = await TenderService.get_tender_detail(tender_id, db)
    if tender_info:
        return ResponseUtil.success(data=TenderModel.model_validate(tender_info))
    return ResponseUtil.failure(msg='未找到该招标信息')


@tender_controller.get(
    '/{tender_id}/ai-analysis',
    response_model=DataResponseModel[AiTenderAnalysisModel],
    summary='AI 智能参谋分析',
    description='对指定招标项目进行AI分析，返回摘要、风险与策略建议',
)
async def analyze_tender_ai(
    tender_id: int, db: AsyncSession = Depends(get_db)
) -> Response:
    """
    对单个招标项目进行 AI 智能分析
    """
    analysis = await TenderService.analyze_tender_ai(tender_id, db)
    return ResponseUtil.success(data=analysis)


@tender_controller.get(
    '/{tender_id}/ai-analysis/stream',
    summary='AI 智能参谋分析（流式）',
    description='返回 Server-Sent Events 流，包含进度和最终结果',
)
async def analyze_tender_ai_stream(
    tender_id: int,
    qualifications: str | None = Query(None, description='企业资质列表JSON字符串'),
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    """
    流式返回 AI 分析进度
    """
    parsed_qualifications: list[str] | None = None
    if qualifications:
        try:
            parsed = json.loads(qualifications)
            if isinstance(parsed, list):
                parsed_qualifications = [str(item) for item in parsed if str(item).strip()]
        except Exception:
            parsed_qualifications = [q.strip() for q in qualifications.split(",") if q.strip()]

    return StreamingResponse(
        TenderService.analyze_tender_ai_stream(tender_id, db, parsed_qualifications),
        media_type="text/event-stream"
    )


@tender_controller.get(
    '/ai-analysis/history',
    response_model=DataResponseModel[list[AiAnalysisHistoryItemModel]],
    summary='AI 分析历史记录',
    description='获取AI分析历史记录列表',
)
async def get_ai_analysis_history(
    limit: int = Query(50, description='返回条数'),
    db: AsyncSession = Depends(get_db),
) -> Response:
    history = await TenderService.get_ai_analysis_history(db, limit=limit)
    return ResponseUtil.success(data=history)


@tender_controller.post(
    '', response_model=DataResponseModel[TenderModel], summary='新增招标信息', description='新增招标信息'
)
async def add_tender(
    tender: TenderModel, db: AsyncSession = Depends(get_db)
) -> Response:
    """
    新增招标信息
    """
    new_tender = await TenderService.add_tender(tender, db)
    return ResponseUtil.success(data=TenderModel.model_validate(new_tender))


@tender_controller.put(
    '', summary='修改招标信息', description='修改招标信息'
)
async def update_tender(
    tender: TenderModel, db: AsyncSession = Depends(get_db)
) -> Response:
    """
    修改招标信息
    """
    await TenderService.update_tender(tender, db)
    return ResponseUtil.success(msg='修改成功')


@tender_controller.delete(
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
    return ResponseUtil.success(msg='删除成功')


@tender_controller.post(
    '/export',
    summary='导出招标信息列表接口',
    description='用于导出当前符合查询条件的招标信息列表数据',
    response_class=StreamingResponse,
    responses={
        200: {
            'description': '流式返回招标信息列表excel文件',
            'content': {
                'application/octet-stream': {},
            },
        }
    },
)
async def export_tender_list(
    request: Request,
    tender_page_query: Annotated[TenderPageQueryModel, Form()],
    db: AsyncSession = Depends(get_db),
) -> Response:
    tender_query_result = await TenderService.get_tender_list(tender_page_query, db, is_page=False)
    tender_export_result = await TenderService.export_tender_list_services(tender_query_result)
    return ResponseUtil.streaming(data=bytes2file_response(tender_export_result))
