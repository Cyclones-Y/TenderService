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
from module_tender.service.public_resources_service import PublicResourcesService


class TenderService:
    """
    招标信息管理模块业务层
    """

    @classmethod
    async def get_tender_list(
        cls, query_object: TenderPageQueryModel, db: AsyncSession
    ) -> Union[PageModel, list[BizTenderInfo]]:
        """
        获取招标信息列表信息

        :param query_object: 查询参数对象
        :param db: orm对象
        :return: 招标信息列表信息对象
        """
        tender_list = await TenderDao.get_tender_list(db, query_object, is_page=True)

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
