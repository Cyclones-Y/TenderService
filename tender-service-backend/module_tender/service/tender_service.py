from collections.abc import AsyncIterable
from datetime import datetime, timedelta
import json
import asyncio
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from config.database import AsyncSessionLocal
from common.vo import PageModel
from exceptions.exception import ServiceException
from module_admin.entity.do.job_do import SysJobLog
from module_tender.dao.tender_dao import TenderDao
from module_tender.dao.tender_ai_dao import TenderAiDao
from module_tender.entity.do.tender_do import BizTenderInfo
from module_tender.entity.vo.tender_vo import (
    AiTenderAnalysisModel,
    AiAnalysisHistoryItemModel,
    DeleteTenderModel,
    DistrictStatModel,
    StageStatModel,
    TenderDashboardModel,
    TenderModel,
    TenderPageQueryModel,
    TrendStatModel,
)
from module_tender.service.orchestrator.public_resources_service import PublicResourcesService
from module_tender.agent.agent import tender_agent
from utils.common_util import SqlalchemyUtil
from utils.log_util import logger
from utils.excel_util import ExcelUtil


class TenderService:
    """
    招标信息管理模块业务层
    """

    @classmethod
    async def get_tender_list(
        cls, query_object: TenderPageQueryModel, db: AsyncSession, is_page: bool = True
    ) -> PageModel | list:
        """
        获取招标信息列表信息

        :param query_object: 查询参数对象
        :param db: orm对象
        :return: 招标信息列表信息对象
        """
        tender_list = await TenderDao.get_tender_list(db, query_object, is_page=is_page)

        return tender_list

    @classmethod
    async def get_tender_detail(cls, tender_id: int, db: AsyncSession) -> BizTenderInfo | None:
        """
        获取招标信息详细信息

        :param tender_id: 招标信息id
        :param db: orm对象
        :return: 招标信息信息对象
        """
        tender_info = await TenderDao.get_tender_detail_by_id(db, tender_id)

        return tender_info

    @staticmethod
    def _build_ai_context(tender: BizTenderInfo) -> str:
        """
        构建用于 AI 分析的项目上下文文本
        """
        parts: list[str] = []

        def add(label: str, value: object | None) -> None:
            if value is None:
                return
            text = str(value).strip()
            if not text:
                return
            parts.append(f"{label}: {text}")

        add("项目名称", tender.project_name)
        add("项目编号", tender.project_code)
        add("所在区县", tender.district)
        add("建设单位", tender.construction_unit)
        add("项目阶段", tender.project_stage)
        add("项目类型", tender.project_type)
        add("招标控制价（万元）", tender.bid_control_price)
        add("中标价（万元）", tender.bid_price)
        add("建设规模", tender.construction_scale)
        add("施工内容", tender.construction_content)
        add("招标范围", tender.tender_scope)
        add("工期", tender.duration)
        add("报名截止时间", tender.registration_deadline)
        add("代理机构", tender.agency)
        add("信息发布时间", tender.release_time)
        add("公告网站", tender.announcement_website)
        add("预审公告收集网址", tender.pre_qualification_url)
        add("中标公告网址", tender.bid_announcement_url)
        add("备注", tender.remark)

        return "\n".join(parts)

    @staticmethod
    def _default_ai_analysis() -> AiTenderAnalysisModel:
        """
        AI 分析失败时的默认结果
        """
        return AiTenderAnalysisModel(
            score=60,
            summary="",
            risks=[],
            requirements=[],
            strategy="",
        )

    @classmethod
    async def analyze_tender_ai(cls, tender_id: int, db: AsyncSession) -> AiTenderAnalysisModel:
        """
        使用大模型对招标项目进行 AI 分析
        
        :param tender_id: 招标信息id
        :param db: orm对象
        :return: AI 分析结果
        """
        history = await TenderAiDao.get_analysis_by_tender_id(db, tender_id)
        if history and history.analysis_result:
            try:
                return AiTenderAnalysisModel.model_validate(history.analysis_result)
            except Exception as e:
                logger.warning(f"Failed to parse cached analysis result: {e}")
        last_result = None
        async for state in tender_agent.run(tender_id, db, None):
            if state.get('analysis_result'):
                last_result = state['analysis_result']
        
        if last_result:
            return last_result
            
        return cls._default_ai_analysis()

    @classmethod
    async def get_ai_analysis_history(cls, db: AsyncSession, limit: int = 50) -> list[AiAnalysisHistoryItemModel]:
        rows = await TenderAiDao.list_analysis_history(db, limit=limit)
        history: list[AiAnalysisHistoryItemModel] = []
        for analysis, project_name in rows:
            analysis_result = analysis.analysis_result or {}
            risks = analysis_result.get("risks") or []
            if isinstance(risks, list) and len(risks) > 0:
                risk_tag = str(risks[0])
            else:
                risk_tag = "无"
            decision_conclusion = analysis_result.get("decisionConclusion") or analysis_result.get("decision_conclusion") or ""
            analysis_time = analysis.update_time or analysis.create_time
            analysis_time_str = analysis_time.strftime("%Y-%m-%d %H:%M") if analysis_time else ""
            history.append(
                AiAnalysisHistoryItemModel(
                    analysis_id=analysis.analysis_id,
                    tender_id=analysis.tender_id,
                    project_name=project_name or "未知项目",
                    analysis_time=analysis_time_str,
                    score=analysis_result.get("score") or 0,
                    risk_tag=risk_tag,
                    decision_conclusion=decision_conclusion,
                )
            )
        return history

    @classmethod
    async def analyze_tender_ai_stream(
        cls, tender_id: int, db: AsyncSession, qualifications: list[str] | None = None
    ) -> AsyncIterable[str]:
        """
        流式执行 AI 分析，返回进度和结果
        """
        # 1. Check for historical analysis
        history = await TenderAiDao.get_analysis_by_tender_id(db, tender_id)
        if history and history.analysis_result:
            output = {
                "progress": 100,
                "message": "已加载历史分析结果",
                "result": history.analysis_result,
            }
            yield f"data: {json.dumps(output, ensure_ascii=False)}\n\n"
            return

        # 2. Run Agent
        final_result = None
        saved_result = False
        try:
            async for state in tender_agent.run(tender_id, db, qualifications or []):
                output = {
                    "progress": state.get("progress", 0),
                    "message": state.get("current_step", ""),
                    "result": None,
                }

                if state.get("analysis_result"):
                    final_result = state["analysis_result"].model_dump(by_alias=True)
                    if not saved_result:
                        try:
                            async with AsyncSessionLocal() as new_db:
                                await TenderAiDao.save_or_update_analysis(new_db, tender_id, final_result)
                                await new_db.commit()
                            saved_result = True
                        except Exception as e:
                            logger.warning(f"Failed to save analysis result: {e}")
                    output["result"] = final_result

                yield f"data: {json.dumps(output, ensure_ascii=False)}\n\n"
            
            # 3. Save result (Normal completion)
            if final_result and not saved_result:
                try:
                    await TenderAiDao.save_or_update_analysis(db, tender_id, final_result)
                    await db.commit()
                except Exception as e:
                    await db.rollback()
                    logger.warning(f"Failed to save analysis result: {e}")
                
        except asyncio.CancelledError:
            # Handle client disconnection gracefully
            logger.info(f"Stream cancelled by client for tender {tender_id}")
            # Try to save if we already have the result (e.g. cancelled during the last yield)
            if final_result:
                try:
                    # Create a new session to save the result, as the original session might be cancelled/rolled back
                    async with AsyncSessionLocal() as new_db:
                        await TenderAiDao.save_or_update_analysis(new_db, tender_id, final_result)
                        await new_db.commit()
                except Exception as e:
                    logger.warning(f"Failed to save result after cancellation: {e}")
            raise
        except Exception as e:
            logger.error(f"Error during AI analysis stream: {e}")
            await db.rollback()
            # Yield error message to client
            error_output = {
                "progress": 0,
                "message": f"分析出错: {str(e)}",
                "error": True
            }
            yield f"data: {json.dumps(error_output, ensure_ascii=False)}\n\n"

    @classmethod
    async def add_tender(cls, tender: TenderModel, db: AsyncSession) -> BizTenderInfo:
        """
        新增招标信息

        :param tender: 招标信息对象
        :param db: orm对象
        :return: 新增的招标信息对象
        """
        try:
            db_tender = await TenderDao.add_tender_dao(db, tender)
            await db.commit()
            return db_tender
        except Exception as e:
            await db.rollback()
            raise e

    @classmethod
    async def update_tender(cls, tender: TenderModel, db: AsyncSession) -> None:
        """
        更新招标信息

        :param tender: 招标信息对象
        :param db: orm对象
        :return:
        """
        tender_info = await TenderDao.get_tender_detail_by_id(db, tender.tender_id)
        if not tender_info:
            raise ServiceException(message=f'招标信息ID {tender.tender_id} 不存在')

        try:
            await TenderDao.edit_tender_dao(db, tender.model_dump(exclude_unset=True))
            await db.commit()
        except Exception as e:
            await db.rollback()
            raise e

    @classmethod
    async def delete_tender(cls, delete_tender: DeleteTenderModel, db: AsyncSession) -> None:
        """
        删除招标信息

        :param delete_tender: 删除招标信息对象
        :param db: orm对象
        :return:
        """
        tender_ids = delete_tender.tender_ids.split(',')
        try:
            for tender_id in tender_ids:
                tender = await TenderDao.get_tender_detail_by_id(db, int(tender_id))
                if tender:
                    await TenderDao.delete_tender_dao(db, tender)
            await db.commit()
        except Exception as e:
            await db.rollback()
            raise e

    @staticmethod
    async def export_tender_list_services(tender_list: list) -> bytes:
        mapping_dict = {
            'project_code': '项目编号',
            'project_name': '项目名称',
            'district': '所在区县',
            'construction_unit': '建设单位',
            'project_stage': '所处阶段',
            'project_type': '项目类型',
            'bid_control_price': '招标控制价（万元）',
            'bid_price': '中标价（万元）',
            'construction_scale': '建设面积（㎡）',
            'construction_content': '施工内容',
            'duration': '工期',
            'registration_deadline': '报名截止时间',
            'agency': '代理机构',
            'create_time': '采集时间',
            'announcement_website': '公告网站',
            'pre_qualification_url': '预审公告收集网址',
            'winner_rank_1': '中标排名1',
            'winner_rank_2': '中标排名2',
            'winner_rank_3': '中标排名3',
            'discount_rate': '中标下浮率',
            'unit_price': '单方造价',
            'evaluation_report_1': '评标报告',
            'bid_date': '中标日期',
            'bid_announcement_url': '中标公告网址',
            'remark': '备注',
        }
        list_data = [SqlalchemyUtil.base_to_dict(item, transform_case='camel_to_snake') for item in tender_list]
        return ExcelUtil.export_list2excel(list_data, mapping_dict)

    @classmethod
    async def get_dashboard_stats(cls, db: AsyncSession) -> TenderDashboardModel:
        now = datetime.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        start_date = (now - timedelta(days=29)).date()
        end_date = now.date()

        total_projects = await TenderDao.get_dashboard_total_projects(db)
        month_new = await TenderDao.get_dashboard_month_new(db, month_start)
        total_amount_wan = await TenderDao.get_dashboard_total_amount_wan(db)
        top_district = await TenderDao.get_dashboard_top_district(db)
        
        # 获取上次同步时间（从sys_job_log获取最新的一条记录）
        last_sync_job = (await db.execute(select(SysJobLog).order_by(desc(SysJobLog.create_time)).limit(1))).scalars().first()
        last_sync_time = last_sync_job.create_time if last_sync_job else None
        
        last_sync_minutes_ago = 0
        last_sync_hours_ago = 0.0
        last_sync_time_str = None
        if last_sync_time:
            diff_seconds = (now - last_sync_time).total_seconds()
            last_sync_minutes_ago = max(0, int(diff_seconds // 60))
            last_sync_hours_ago = max(0.0, round(diff_seconds / 3600, 1))
            last_sync_time_str = last_sync_time.strftime('%Y-%m-%d %H:%M')

        district_rows = await TenderDao.get_dashboard_district_stats(db)
        stage_rows = await TenderDao.get_dashboard_stage_stats(db)
        trend_rows = await TenderDao.get_dashboard_trend(db, start_date, end_date)

        trend_map = {d.isoformat(): c for d, c in trend_rows}
        trend_stats = []
        for i in range(30):
            d = (now - timedelta(days=29 - i)).date().isoformat()
            trend_stats.append(TrendStatModel(date=d, count=int(trend_map.get(d, 0))))

        return TenderDashboardModel(
            total_projects=total_projects,
            month_new=month_new,
            total_amount_billion=round(total_amount_wan / 10000, 2),
            top_district=top_district or '-',
            last_sync_minutes_ago=last_sync_minutes_ago,
            last_sync_hours_ago=last_sync_hours_ago,
            last_sync_time=last_sync_time_str,
            district_stats=[DistrictStatModel(name=n, value=v) for n, v in district_rows],
            stage_stats=[StageStatModel(name=n, value=v) for n, v in stage_rows],
            trend_stats=trend_stats,
        )


    @classmethod
    def extract_project_type(cls, title: str) -> str:
        """
        根据标题提取项目类型
        """
        if not title:
            return "其他"

        types = {
            "施工": ["施工", "建设", "工程"],
            "监理": ["监理"],
            "设计": ["设计"],
            "勘察": ["勘察"],
            "采购": ["采购", "供货"],
            "服务": ["服务", "咨询"]
        }

        for type_name, keywords in types.items():
            for keyword in keywords:
                if keyword in title:
                    return type_name

        return "其他"

    @classmethod
    def determine_stage(cls, item: dict) -> str:
        """
        判断项目阶段
        """
        title = item.get('title', '')
        if '中标' in title or '结果' in title:
            return '中标结果'
        if '候选人' in title:
            return '中标候选人'
        if '招标' in title or '公告' in title:
            return '招标公告'
        if '资格预审' in title:
            return '资格预审'
        return "其他"

    @classmethod
    async def fetch_tender_plan(
        cls,
        start_date: str,
        end_date: str,
        db: AsyncSession,
        page: int = 1,
        size: int = 100,
    ) -> int:
        return await PublicResourcesService.fetch_tender_plan(
            start_date=start_date,
            end_date=end_date,
            db=db,
            page=page,
            size=size,
        )
