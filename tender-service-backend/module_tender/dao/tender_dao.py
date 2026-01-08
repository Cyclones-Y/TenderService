from typing import Union

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from common.vo import PageModel
from module_tender.entity.do.tender_do import BizTenderInfo
from module_tender.entity.vo.tender_vo import TenderModel, TenderPageQueryModel
from utils.page_util import PageUtil


class TenderDao:
    """
    招标信息管理模块数据库操作层
    """

    @classmethod
    async def get_tender_detail_by_id(cls, db: AsyncSession, tender_id: int) -> Union[BizTenderInfo, None]:
        """
        根据招标信息id获取招标信息详细信息

        :param db: orm对象
        :param tender_id: 招标信息id
        :return: 招标信息信息对象
        """
        tender_info = (
            await db.execute(select(BizTenderInfo).where(BizTenderInfo.tender_id == tender_id))
        ).scalars().first()

        return tender_info

    @classmethod
    async def get_tender_detail_by_project_code(cls, db: AsyncSession, project_code: str) -> Union[BizTenderInfo, None]:
        """
        根据项目编号获取招标信息详细信息

        :param db: orm对象
        :param project_code: 项目编号
        :return: 招标信息信息对象
        """
        tender_info = (
            await db.execute(select(BizTenderInfo).where(BizTenderInfo.project_code == project_code))
        ).scalars().first()

        return tender_info

    @classmethod
    async def get_tender_list(
        cls, db: AsyncSession, query_object: TenderPageQueryModel, is_page: bool = False
    ) -> Union[PageModel, list[BizTenderInfo]]:
        """
        根据查询参数获取招标信息列表信息

        :param db: orm对象
        :param query_object: 查询参数对象
        :param is_page: 是否开启分页
        :return: 招标信息列表信息对象
        """
        query = select(BizTenderInfo)
        if query_object.project_name:
            query = query.where(BizTenderInfo.project_name.like(f'%{query_object.project_name}%'))
        if query_object.project_code:
            query = query.where(BizTenderInfo.project_code.like(f'%{query_object.project_code}%'))
        if query_object.district:
            query = query.where(BizTenderInfo.district == query_object.district)
        if query_object.project_stage:
            query = query.where(BizTenderInfo.project_stage == query_object.project_stage)
        
        query = query.order_by(BizTenderInfo.create_time.desc())
        
        tender_list = await PageUtil.paginate(db, query, query_object.page_num, query_object.page_size, is_page)

        return tender_list

    @classmethod
    async def get_by_code_and_stage(cls, db: AsyncSession, project_code: str, project_stage: str) -> Union[BizTenderInfo, None]:
        """
        根据项目编号与阶段获取招标信息
        """
        tender_info = (
            await db.execute(
                select(BizTenderInfo).where(
                    BizTenderInfo.project_code == project_code,
                    BizTenderInfo.project_stage == project_stage,
                )
            )
        ).scalars().first()
        return tender_info

    @classmethod
    async def add_tender_dao(cls, db: AsyncSession, tender: TenderModel) -> BizTenderInfo:
        """
        新增招标信息数据库操作

        :param db: orm对象
        :param tender: 招标信息对象
        :return:
        """
        db_tender = BizTenderInfo(**tender.model_dump(exclude_unset=True))
        db.add(db_tender)
        await db.flush()

        return db_tender

    @classmethod
    async def edit_tender_dao(cls, db: AsyncSession, tender: dict) -> None:
        """
        编辑招标信息数据库操作

        :param db: orm对象
        :param tender: 需要更新的招标信息字典
        :return:
        """
        await db.execute(update(BizTenderInfo).where(BizTenderInfo.tender_id == tender['tender_id']).values(**tender))

    @classmethod
    async def delete_tender_dao(cls, db: AsyncSession, tender: TenderModel) -> None:
        """
        删除招标信息数据库操作

        :param db: orm对象
        :param tender: 招标信息对象
        :return:
        """
        await db.execute(delete(BizTenderInfo).where(BizTenderInfo.tender_id.in_([tender.tender_id])))
