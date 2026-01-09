from datetime import date, datetime

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from common.vo import PageModel
from module_tender.entity.do.tender_do import BizTenderInfo
from module_tender.entity.vo.tender_vo import TenderModel, TenderPageQueryModel
from utils.page_util import PageUtil
from utils.time_format_util import TimeFormatUtil

BEIJING_DISTRICTS = (
    '东城区',
    '西城区',
    '朝阳区',
    '丰台区',
    '石景山区',
    '海淀区',
    '顺义区',
    '通州区',
    '大兴区',
    '房山区',
    '门头沟区',
    '昌平区',
    '平谷区',
    '密云区',
    '怀柔区',
    '延庆区',
)
OTHER_DISTRICT_LABEL = '其他'


class TenderDao:
    """
    招标信息管理模块数据库操作层
    """

    @classmethod
    async def get_tender_detail_by_id(cls, db: AsyncSession, tender_id: int) -> BizTenderInfo | None:
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
    async def get_tender_detail_by_project_code(cls, db: AsyncSession, project_code: str) -> BizTenderInfo | None:
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
    ) -> PageModel | list[BizTenderInfo]:
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
        if query_object.begin_time and query_object.end_time:
            start_date = TimeFormatUtil.parse_date(query_object.begin_time)
            end_date = TimeFormatUtil.parse_date(query_object.end_time)
            if start_date and end_date:
                query = query.where(BizTenderInfo.release_time.between(start_date, end_date))

        query = query.order_by(BizTenderInfo.release_time.desc(), BizTenderInfo.create_time.desc())

        tender_list = await PageUtil.paginate(db, query, query_object.page_num, query_object.page_size, is_page)

        return tender_list

    @classmethod
    async def get_by_code_and_stage(cls, db: AsyncSession, project_code: str, project_stage: str) -> BizTenderInfo | None:
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

    @classmethod
    async def get_dashboard_total_projects(cls, db: AsyncSession) -> int:
        result = await db.execute(
            select(func.count(func.distinct(BizTenderInfo.project_code))).where(
                BizTenderInfo.project_code.is_not(None),
                BizTenderInfo.project_code != '',
            )
        )
        return int(result.scalar() or 0)

    @classmethod
    async def get_dashboard_month_new(cls, db: AsyncSession, month_start: datetime) -> int:
        result = await db.execute(select(func.count(BizTenderInfo.tender_id)).where(BizTenderInfo.create_time >= month_start))
        return int(result.scalar() or 0)

    @classmethod
    async def get_dashboard_total_amount_wan(cls, db: AsyncSession) -> float:
        result = await db.execute(select(func.sum(BizTenderInfo.bid_control_price)))
        value = result.scalar()
        return float(value or 0)

    @classmethod
    async def get_dashboard_top_district(cls, db: AsyncSession) -> str:
        result = await db.execute(
            select(BizTenderInfo.district, func.count(func.distinct(BizTenderInfo.project_code)).label('cnt'))
            .where(
                BizTenderInfo.district.is_not(None),
                BizTenderInfo.district != '',
            )
            .group_by(BizTenderInfo.district)
            .order_by(func.count(func.distinct(BizTenderInfo.project_code)).desc())
        )
        rows = [(str(r[0]), int(r[1] or 0)) for r in result.all() if r[0]]
        if not rows:
            return ''

        count_by_district = dict(rows)
        other_sum = sum(count for district, count in rows if district not in BEIJING_DISTRICTS)

        best_name = ''
        best_count = 0
        for district in BEIJING_DISTRICTS:
            count = count_by_district.get(district, 0)
            if count > best_count:
                best_count = count
                best_name = district
        if other_sum > best_count:
            best_name = OTHER_DISTRICT_LABEL

        return best_name

    @classmethod
    async def get_dashboard_last_sync_time(cls, db: AsyncSession) -> datetime | None:
        result = await db.execute(select(func.max(BizTenderInfo.update_time)))
        return result.scalar()

    @classmethod
    async def get_dashboard_district_stats(cls, db: AsyncSession) -> list[tuple[str, int]]:
        result = await db.execute(
            select(BizTenderInfo.district, func.count(func.distinct(BizTenderInfo.project_code)).label('cnt'))
            .where(
                BizTenderInfo.district.is_not(None),
                BizTenderInfo.district != '',
            )
            .group_by(BizTenderInfo.district)
            .order_by(func.count(func.distinct(BizTenderInfo.project_code)).desc())
        )
        rows = [(str(r[0]), int(r[1] or 0)) for r in result.all() if r[0]]
        count_by_district = dict(rows)
        other_sum = sum(count for district, count in rows if district not in BEIJING_DISTRICTS)

        stats = [(d, count_by_district[d]) for d in BEIJING_DISTRICTS if count_by_district.get(d, 0) > 0]
        if other_sum > 0:
            stats.append((OTHER_DISTRICT_LABEL, other_sum))
        return stats

    @classmethod
    async def get_dashboard_stage_stats(cls, db: AsyncSession) -> list[tuple[str, int]]:
        result = await db.execute(
            select(BizTenderInfo.project_stage, func.count(BizTenderInfo.tender_id).label('cnt'))
            .where(BizTenderInfo.project_stage.is_not(None), BizTenderInfo.project_stage != '')
            .group_by(BizTenderInfo.project_stage)
            .order_by(func.count(BizTenderInfo.tender_id).desc())
        )
        return [(str(r[0]), int(r[1] or 0)) for r in result.all() if r[0]]

    @classmethod
    async def get_dashboard_trend(cls, db: AsyncSession, start_date: date, end_date: date) -> list[tuple[date, int]]:
        date_expr = func.coalesce(BizTenderInfo.release_time, func.date(BizTenderInfo.create_time)).label('d')
        result = await db.execute(
            select(date_expr, func.count(BizTenderInfo.tender_id).label('cnt'))
            .where(date_expr.between(start_date, end_date))
            .group_by(date_expr)
            .order_by(date_expr.asc())
        )
        return [(r[0], int(r[1] or 0)) for r in result.all() if r[0]]
