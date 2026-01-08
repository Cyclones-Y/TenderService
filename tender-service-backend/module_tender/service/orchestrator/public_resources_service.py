import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from config.database import AsyncSessionLocal
from module_tender.service.public_resources.correction_notice import CorrectionNoticeFetcher
from module_tender.service.public_resources.tender_notice import TenderNoticeFetcher
from module_tender.service.public_resources.tender_plan import TenderPlanFetcher
from module_tender.service.public_resources.win_candidate import WinCandidateFetcher


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


async def test_fetch_tender_data() -> None:
    async with AsyncSessionLocal() as db:
        print("Fetching Tender Data...")
        # count_plan = await PublicResourcesService.fetch_tender_plan(
        #     start_date="2025-12-05",
        #     end_date="2026-01-05",
        #     db=db,
        #     page=1,
        #     size=10,
        # )
        # count_notice = await PublicResourcesService.fetch_tender_notice(
        #     start_date="2025-12-05",
        #     end_date="2026-01-05",
        #     db=db,
        #     page=1,
        #     size=10,
        # )
        count_win_candidate = await PublicResourcesService.fetch_win_candidate(
            start_date="2025-12-05",
            end_date="2026-01-05",
            db=db,
            page=1,
            size=100,
        )
        print(f"Fetched {count_win_candidate} tender notice.")


if __name__ == "__main__":
    asyncio.run(test_fetch_tender_data())
