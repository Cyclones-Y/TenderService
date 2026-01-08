import re

from sqlalchemy.ext.asyncio import AsyncSession


from module_tender.dao.tender_dao import TenderDao
from module_tender.entity.structured_entity.win_candidate_entity import WinCandidateEntity
from module_tender.entity.vo.tender_vo import TenderModel
from module_tender.service.integration.structured_output import extract_structured_data
from module_tender.service.public_resources.base import PublicResourcesBase
from utils.html_util import HtmlUtil
from utils.pdf_util import PdfUtil


class WinCandidateFetcher(PublicResourcesBase):
    """中标候选人公示获取与解析"""

    _default_ai_entity = lambda: WinCandidateEntity(
        constructionContent="",
        duration="",
        projectType="",
        bidControlPrice=0.0,
        constructionScale="",
        bidPrice=0.0,
        tendererOrAgency="",
        winner_rank_1="",
        winner_rank_2="",
        winner_rank_3="",
        discountRate="0.00%",
        unitPrice=0.0,
    )

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
            channel_id="123",
            channel_third="jyxxzbhxrgs",
            ext="A98",
            page=page,
            size=size,
            starttime=start_date,
            endtime=end_date,
        )
        inserted = 0
        for item in result:
            parsed = await cls.parse_item_from_content(item)
            tender = TenderModel(
                project_code=parsed.get("projectCode"),
                project_name=parsed.get("projectName"),
                project_type=parsed.get("projectType"),
                district=parsed.get("district"),
                construction_unit=parsed.get("constructionUnit"),
                project_stage="中标候选人",
                bid_control_price=parsed.get("bidControlPrice"),
                construction_scale=parsed.get("constructionScale"),
                construction_content=parsed.get("constructionContent"),
                duration=parsed.get("duration"),
                bid_price=parsed.get("bidPrice"),
                winner_rank_1=parsed.get("winnerRank1"),
                winner_rank_2=parsed.get("winnerRank2"),
                winner_rank_3=parsed.get("winnerRank3"),
                discount_rate=parsed.get("discountRate"),
                unit_price=parsed.get("unitPrice"),
                announcement_website=parsed.get("announcementWebsite"),
                pre_qualification_url=parsed.get("preQualificationUrl"),
                release_time=cls._parse_release_date(item.get("releaseDate")),
                bid_date=cls._parse_release_date(item.get("releaseDate")),
                registration_deadline=cls._parse_release_date(item.get("noticeEndTime")),
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
    def _extract_ai_data(cls, text: str) -> WinCandidateEntity:
        """
        使用 AI 提取中标候选人关键信息
        """
        result = extract_structured_data(
            text=text,
            response_model=WinCandidateEntity,
            instruction="从下述公告和中标详情中提取相关信息：",
            default_factory=cls._default_ai_entity,
            max_retries=2,
            retry_delay=0.5,
        )
        return result if result is not None else cls._default_ai_entity()

    @classmethod
    async def parse_item_from_content(cls, json_item: dict) -> dict:
        content_str = json_item.get("content", "")
        district = json_item.get("region", "")
        html_url = cls._abs_url(json_item.get("link"))
        pdf_links = await HtmlUtil.fetch_target_pdf_links(html_url)
        txt = ""
        if pdf_links:
            try:
                txt = await PdfUtil.fetch_pdf_text(pdf_links[0], headers={"Referer": html_url}, referer=html_url)
            except Exception:
                txt = ""


        # 使用 AI 提取补充字段
        ai_source = "中标候选人公告内容："+ content_str + "中标候选人详细内容："+ (("\n" + txt) if txt else "")
        ai_result = cls._extract_ai_data(ai_source)

        return {
            "projectCode": json_item.get("projectCode"),
            "projectName": json_item.get("title"),
            "projectType": ai_result.projectType,
            "district": district,
            "constructionUnit": ai_result.tendererOrAgency,
            "duration": ai_result.duration,
            "agency": ai_result.tendererOrAgency,
            "bidControlPrice": ai_result.bidControlPrice,
            "bidPrice": ai_result.bidPrice,
            "constructionScale": ai_result.constructionScale,
            "constructionContent": ai_result.constructionContent,
            "winnerRank1": ai_result.winner_rank_1,
            "winnerRank2": ai_result.winner_rank_2,
            "winnerRank3": ai_result.winner_rank_3,
            "discountRate": ai_result.discountRate,
            "unitPrice": ai_result.unitPrice,
            "announcementWebsite": "公共资源",
            "preQualificationUrl": cls._abs_url(json_item.get("link")),
        }
