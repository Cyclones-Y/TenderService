import re

from sqlalchemy.ext.asyncio import AsyncSession

from exceptions.exception import ServiceException
from module_tender.dao.tender_dao import TenderDao
from module_tender.entity.vo.tender_vo import TenderModel
from module_tender.service.public_resources.base import PublicResourcesBase


class WinCandidateFetcher(PublicResourcesBase):
    """中标候选人公示获取与解析"""

    @classmethod
    async def fetch(
        cls,
        start_date: str,
        end_date: str,
        db: AsyncSession,
        page: int = 1,
        size: int = 100,
    ) -> int:
        result = await cls.request_list(
            channel_id="284",
            channel_third="jyxxgcjszhbxh",
            ext="A98",
            page=page,
            size=size,
            starttime=start_date,
            endtime=end_date,
        )
        inserted = 0
        for item in result:
            parsed = cls.parse_item_from_content(item)
            tender = TenderModel(
                project_code=parsed.get("projectCode"),
                project_name=parsed.get("projectName"),
                district=parsed.get("district"),
                project_stage="中标候选人",
                winner_rank_1=parsed.get("winnerRank1"),
                winner_rank_2=parsed.get("winnerRank2"),
                winner_rank_3=parsed.get("winnerRank3"),
                announcement_website=parsed.get("announcementWebsite"),
                pre_qualification_url=parsed.get("preQualificationUrl"),
                release_time=cls._parse_release_date(item.get("releaseDate")),
            )
            try:
                await TenderDao.add_tender_dao(db, tender)
                await db.commit()
                inserted += 1
            except Exception:
                await db.rollback()
                continue
        return inserted

    @staticmethod
    def _extract_rank_candidate(content_str: str, rank: int) -> str | None:
        # 示例：第一中标候选人：XXX公司
        rank_chinese = {1: "一", 2: "二", 3: "三"}.get(rank, "")
        if not rank_chinese:
            return None
        
        pattern = rf"第{rank_chinese}中标候选人[：:]\s*(.*?)(?:；|;|第|$)"
        match = re.search(pattern, content_str, flags=re.S)
        if match:
             return re.sub(r"\s+", " ", match.group(1)).strip().strip("。；;")
        return None

    @classmethod
    def parse_item_from_content(cls, json_item: dict) -> dict:
        content_str = json_item.get("content", "")
        district = json_item.get("region", "")
        
        return {
            "projectCode": json_item.get("projectCode"),
            "projectName": json_item.get("title"),
            "district": district,
            "winnerRank1": cls._extract_rank_candidate(content_str, 1),
            "winnerRank2": cls._extract_rank_candidate(content_str, 2),
            "winnerRank3": cls._extract_rank_candidate(content_str, 3),
            "announcementWebsite": "公共资源",
            "preQualificationUrl": cls._abs_url(json_item.get("link")),
        }
