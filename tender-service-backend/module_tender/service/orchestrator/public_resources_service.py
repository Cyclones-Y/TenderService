import asyncio
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from config.database import AsyncSessionLocal
from module_tender.service.beijing_gov_procurement.tender_notice import GovTenderNoticeFetcher
from module_tender.service.beijing_gov_procurement.win_candidate import GovWinCandidateFetcher
from module_tender.service.gov_procurement.tender_service import TenderService
from module_tender.service.public_resources.tender_notice import TenderNoticeFetcher
from module_tender.service.public_resources.tender_plan import TenderPlanFetcher
from module_tender.service.public_resources.win_candidate import WinCandidateFetcher
from utils.log_util import logger


class PublicResourcesService:
    """
    公共资源交易服务平台招标数据获取
    """

    @classmethod
    async def fetch_tender_plan(
        cls,
        start_date: str,
        end_date: str,
        db: AsyncSession,
        page: int = 1,
        size: int = 100,
    ) -> int:
        """
        获取招标计划
        """
        return await TenderPlanFetcher.fetch(start_date, end_date, db, page, size)

    @classmethod
    async def fetch_tender_notice(
        cls,
        start_date: str,
        end_date: str,
        db: AsyncSession,
        page: int = 1,
        size: int = 100,
    ) -> int:
        """
        获取招标公告
        """
        return await TenderNoticeFetcher.fetch(start_date, end_date, db, page, size)

    @classmethod
    async def fetch_gov_tender_notice(
        cls,
        start_date: str,
        end_date: str,
        db: AsyncSession,
    ) -> int:
        """
        获取政府采购网招标公告
        """
        return await GovTenderNoticeFetcher.fetch(db=db, start_date=start_date, end_date=end_date)

    @classmethod
    async def fetch_win_candidate(
        cls,
        start_date: str,
        end_date: str,
        db: AsyncSession,
        page: int = 1,
        size: int = 100,
    ) -> int:
        """
        获取中标候选人
        """
        return await WinCandidateFetcher.fetch(start_date, end_date, db, page, size)

    @classmethod
    async def fetch_gov_win_candidate(
            cls,
            start_date: str,
            end_date: str,
            db: AsyncSession,
    ) -> int:
        """
        获取政府采购网中标公告
        """
        return await GovWinCandidateFetcher.fetch(db=db, start_date=start_date, end_date=end_date)

    @classmethod
    async def fetch_ccgp_tender_notice(
        cls,
        start_date: str,
        end_date: str,
        db: AsyncSession,
    ) -> int:
        """
        获取CCGP政府采购网招标公告
        """
        return await TenderService.fetch(db=db, start_date=start_date, end_date=end_date)

    @classmethod
    async def fetch_all(
        cls,
        start_date: str,
        end_date: str,
        db: AsyncSession,  # 此处的 db 在并行模式下将作为基准，子任务会创建自己的 session
        page: int = 1,
        size: int = 100,
        *,
        include_plan: bool = True,
        include_notice: bool = True,
        include_win_candidate: bool = True,
        include_gov_notice: bool = True,
        include_gov_win_candidate: bool = True,
        include_ccgp_notice: bool = True,
    ) -> dict[str, int]:
        result: dict[str, int] = {
            "plan": 0,
            "notice": 0,
            "win_candidate": 0,
            "gov_notice": 0,
            "gov_win_candidate": 0,
            "ccgp_notice": 0,
            "total": 0,
        }

        # 定义一个包装函数，为每个并行任务创建独立的数据库会话
        async def run_task(task_key, task_func, **kwargs):
            async with AsyncSessionLocal() as task_db:
                try:
                    count = await task_func(db=task_db, **kwargs)
                    return task_key, count
                except Exception as e:
                    logger.error(f"Error in parallel task {task_key}: {e}")
                    return task_key, 0

        coroutines = []

        if include_plan:
            coroutines.append(run_task("plan", cls.fetch_tender_plan, start_date=start_date, end_date=end_date, page=page, size=size))

        if include_notice:
            coroutines.append(run_task("notice", cls.fetch_tender_notice, start_date=start_date, end_date=end_date, page=page, size=size))

        if include_win_candidate:
            coroutines.append(run_task("win_candidate", cls.fetch_win_candidate, start_date=start_date, end_date=end_date, page=page, size=size))

        if include_gov_notice:
            coroutines.append(run_task("gov_notice", cls.fetch_gov_tender_notice, start_date=start_date, end_date=end_date))

        if include_gov_win_candidate:
            coroutines.append(run_task("gov_win_candidate", cls.fetch_gov_win_candidate, start_date=start_date, end_date=end_date))

        if include_ccgp_notice:
            coroutines.append(run_task("ccgp_notice", cls.fetch_ccgp_tender_notice, start_date=start_date, end_date=end_date))

        if coroutines:
            # 并行执行所有任务
            task_results = await asyncio.gather(*coroutines)
            for key, count in task_results:
                result[key] = count

        result["total"] = (
            result["plan"]
            + result["notice"]
            + result["win_candidate"]
            + result["gov_notice"]
            + result["gov_win_candidate"]
            + result["ccgp_notice"]
        )
        return result


def _to_int(value: int | str | None, default: int) -> int:
    if value is None:
        return default
    if isinstance(value, int):
        return value
    try:
        return int(value)
    except ValueError:
        return default


async def public_resources_tender_sync_job(
    *,
    days_back: int | str | None = 7,
    page: int | str | None = 1,
    size: int | str | None = 200,
    include_plan: bool = True,
    include_notice: bool = True,
    include_win_candidate: bool = True,
    include_gov_notice: bool = True,
    include_ccgp_notice: bool = True,
    **kwargs,
) -> None:
    days_back_int = max(0, _to_int(days_back, 7))
    page_int = max(1, _to_int(page, 1))
    size_int = max(1, _to_int(size, 200))

    now = datetime.now()
    end_date = now.date()
    start_date = (end_date - timedelta(days=days_back_int)).isoformat()
    end_date_str = end_date.isoformat()

    logger.info(
        f"public_resources_tender_sync_job start: {start_date}~{end_date_str}, page={page_int}, size={size_int}"
    )
    if kwargs:
        logger.info(f"public_resources_tender_sync_job ignored kwargs: {sorted(kwargs.keys())}")
    async with AsyncSessionLocal() as db:
        result = await PublicResourcesService.fetch_all(
            start_date=start_date,
            end_date=end_date_str,
            db=db,
            page=page_int,
            size=size_int,
            include_plan=include_plan,
            include_notice=include_notice,
            include_win_candidate=include_win_candidate,
            include_gov_notice=include_gov_notice,
            include_ccgp_notice=include_ccgp_notice,
        )
    logger.info(f"public_resources_tender_sync_job done: {result}")


async def test_fetch_tender_data() -> None:
    async with AsyncSessionLocal() as db:
        print("Fetching Tender Data...")
        result = await PublicResourcesService.fetch_all(
            start_date="2026-01-01",
            end_date="2026-01-15",
            db=db,
            page=1,
            size=200,
            include_plan=False,
            include_notice=False,
            include_win_candidate=False,
            include_gov_notice=False,
            include_gov_win_candidate=False,
            include_ccgp_notice=True,
        )
        print(f"Fetched gov tender notice: {result}")


if __name__ == "__main__":
    asyncio.run(test_fetch_tender_data())
