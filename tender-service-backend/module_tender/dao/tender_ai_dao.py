from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from module_tender.entity.do.tender_ai_do import BizTenderAiAnalysis
from module_tender.entity.do.tender_do import BizTenderInfo

class TenderAiDao:
    """
    招标AI分析结果DAO
    """

    @classmethod
    async def get_analysis_by_tender_id(cls, db: AsyncSession, tender_id: int) -> BizTenderAiAnalysis | None:
        """
        根据tender_id获取分析结果
        """
        query = select(BizTenderAiAnalysis).where(BizTenderAiAnalysis.tender_id == tender_id)
        result = await db.execute(query)
        return result.scalars().first()

    @classmethod
    async def save_or_update_analysis(cls, db: AsyncSession, tender_id: int, result_data: dict) -> BizTenderAiAnalysis:
        """
        保存或更新分析结果
        """
        # 检查是否存在
        existing = await cls.get_analysis_by_tender_id(db, tender_id)
        if existing:
            existing.analysis_result = result_data
            # update_time 会自动更新
            await db.flush()
            return existing
        else:
            new_analysis = BizTenderAiAnalysis(
                tender_id=tender_id,
                analysis_result=result_data
            )
            db.add(new_analysis)
            await db.flush()
            return new_analysis

    @classmethod
    async def list_analysis_history(cls, db: AsyncSession, limit: int = 50) -> list[tuple[BizTenderAiAnalysis, str | None]]:
        query = (
            select(BizTenderAiAnalysis, BizTenderInfo.project_name)
            .join(BizTenderInfo, BizTenderInfo.tender_id == BizTenderAiAnalysis.tender_id)
            .order_by(BizTenderAiAnalysis.update_time.desc())
            .limit(limit)
        )
        result = await db.execute(query)
        return result.all()
