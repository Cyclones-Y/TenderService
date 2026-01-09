import asyncio
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from config.database import AsyncSessionLocal
from module_tender.service.public_resources.correction_notice import CorrectionNoticeFetcher
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
    async def fetch_correction_notice(
        cls,
        start_date: str,
        end_date: str,
        db: AsyncSession,
        page: int = 1,
        size: int = 100,
    ) -> int:
        """
        获取更正公告
        """
        return await CorrectionNoticeFetcher.fetch(start_date, end_date, db, page, size)

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
    async def fetch_all(
        cls,
        start_date: str,
        end_date: str,
        db: AsyncSession,
        page: int = 1,
        size: int = 100,
        *,
        include_plan: bool = True,
        include_notice: bool = True,
        include_win_candidate: bool = True,
    ) -> dict[str, int]:
        result: dict[str, int] = {"plan": 0, "notice": 0, "correction": 0, "win_candidate": 0, "total": 0}

        if include_plan:
            result["plan"] = await cls.fetch_tender_plan(
                start_date=start_date, end_date=end_date, db=db, page=page, size=size
            )
        if include_notice:
            result["notice"] = await cls.fetch_tender_notice(
                start_date=start_date, end_date=end_date, db=db, page=page, size=size
            )
        if include_win_candidate:
            result["win_candidate"] = await cls.fetch_win_candidate(
                start_date=start_date, end_date=end_date, db=db, page=page, size=size
            )

        result["total"] = result["plan"] + result["notice"] + result["correction"] + result["win_candidate"]
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
        )
    logger.info(f"public_resources_tender_sync_job done: {result}")


async def test_fetch_tender_data() -> None:
    async with AsyncSessionLocal() as db:
        print("Fetching Tender Data...")
        count_plan = await PublicResourcesService.fetch_tender_plan(
            start_date="2025-12-05",
            end_date="2026-01-05",
            db=db,
            page=1,
            size=200,
        )
        count_notice = await PublicResourcesService.fetch_tender_notice(
            start_date="2025-12-05",
            end_date="2026-01-05",
            db=db,
            page=1,
            size=200,
        )
        count_win_candidate = await PublicResourcesService.fetch_win_candidate(
            start_date="2025-12-01",
            end_date="2026-01-09",
            db=db,
            page=1,
            size=200,
        )
        print(f"Fetched {count_win_candidate + count_plan + count_notice} tender notice.")


if __name__ == "__main__":
    asyncio.run(test_fetch_tender_data())
