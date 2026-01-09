from typing import Union

from sqlalchemy.ext.asyncio import AsyncSession

from common.vo import PageModel
from exceptions.exception import ServiceException
from module_tender.dao.tender_dao import TenderDao
from module_tender.entity.do.tender_do import BizTenderInfo
from module_tender.entity.vo.tender_vo import (
    DeleteTenderModel,
    TenderModel,
    TenderPageQueryModel,
)
from module_tender.service.orchestrator.public_resources_service import PublicResourcesService
from utils.common_util import SqlalchemyUtil
from utils.excel_util import ExcelUtil


class TenderService:
    """
    招标信息管理模块业务层
    """

    @classmethod
    async def get_tender_list(
        cls, query_object: TenderPageQueryModel, db: AsyncSession, is_page: bool = True
    ) -> Union[PageModel, list]:
        """
        获取招标信息列表信息

        :param query_object: 查询参数对象
        :param db: orm对象
        :return: 招标信息列表信息对象
        """
        tender_list = await TenderDao.get_tender_list(db, query_object, is_page=is_page)

        return tender_list

    @classmethod
    async def get_tender_detail(cls, tender_id: int, db: AsyncSession) -> Union[BizTenderInfo, None]:
        """
        获取招标信息详细信息

        :param tender_id: 招标信息id
        :param db: orm对象
        :return: 招标信息信息对象
        """
        tender_info = await TenderDao.get_tender_detail_by_id(db, tender_id)

        return tender_info

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
            'evaluation_report_1': '评标报告_1',
            'evaluation_report_2': '评标报告_2',
            'evaluation_report_3': '评标报告_3',
            'bid_date': '中标日期',
            'bid_announcement_url': '中标公告网址',
            'remark': '备注',
        }
        list_data = [SqlalchemyUtil.base_to_dict(item, transform_case='camel_to_snake') for item in tender_list]
        return ExcelUtil.export_list2excel(list_data, mapping_dict)


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
