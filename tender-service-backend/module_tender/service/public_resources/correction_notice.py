import re

from sqlalchemy.ext.asyncio import AsyncSession

from config.database import AsyncSessionLocal
from exceptions.exception import ServiceException
from module_tender.dao.tender_dao import TenderDao
from module_tender.entity.vo.tender_vo import TenderModel
from module_tender.service.public_resources.base import PublicResourcesBase


class CorrectionNoticeFetcher(PublicResourcesBase):
    """更正公告获取与解析"""

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
            channel_id="121",
            channel_third="jyxxggjtbyqs",
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
                project_stage="更正公告",
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

    @classmethod
    def parse_item_from_content(cls, json_item: dict) -> dict:
        district = json_item.get("region", "")
        
        return {
            "projectCode": json_item.get("projectCode"),
            "projectName": json_item.get("title"),
            "district": district,
            "announcementWebsite": "公共资源",
            "preQualificationUrl": cls._abs_url(json_item.get("link")),
        }
