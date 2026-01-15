import asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from module_tender.dao.tender_dao import TenderDao
from module_tender.entity.structured_entity.gov_tender_notice_entity import GovTenderNoticeEntity
from module_tender.entity.vo.tender_vo import TenderModel
from module_tender.service.gov_procurement.base import GovProcurementBase, Landscaping
from module_tender.service.integration.structured_output import extract_structured_data


from prompts.prompts import get_classify_landscaping_prompt


class GovTenderNoticeFetcher(GovProcurementBase):
    """政府采购公告获取与解析"""
    PROJECT_STAGE = "招标公告"

    @classmethod
    async def fetch(cls, db: AsyncSession, start_date: str, end_date: str) -> int:
        city_result = await cls.get_html_project_list(
            level="city",
            start_date=start_date,
            end_date=end_date,
        )

        area_result = await cls.get_html_project_list(
            level="area",
            start_date=start_date,
            end_date=end_date,
        )

        result = city_result + area_result

        # Concurrency control
        semaphore = asyncio.Semaphore(10)
        db_lock = asyncio.Lock()

        async def process_item(item: dict) -> TenderModel | None:
            async with semaphore:
                url = item.get('project_url')
                if not url:
                    return None

                try:
                    text = await GovProcurementBase.get_html_detail_content(url)
                except Exception:
                    return None

                matched_keywords_count = sum(1 for k in cls.include_keywords if k in text[:500])
                if matched_keywords_count < 2:
                    return None

                project_code = cls._get_project_code(text)

                # Check existence (Serialized)
                if project_code:
                    async with db_lock:
                        if await cls.check_and_skip_if_exists({"projectCode": project_code}, db, cls.PROJECT_STAGE):
                            return None

                try:
                    response = await asyncio.to_thread(
                        extract_structured_data,
                        text="",
                        response_model=Landscaping,
                        instruction=get_classify_landscaping_prompt(text[:500]),
                        max_retries=2,
                        retry_delay=0.5,
                    )
                except Exception:
                    return None

                if not response.is_landscaping_industry:
                    return None

                enriched_item = dict(item)
                enriched_item["projectCode"] = project_code

                try:
                    parsed = await cls.parse_item_from_content(enriched_item, text)
                    tender = TenderModel(
                            project_code=parsed.get("projectCode"),
                            project_name=parsed.get("projectName"),
                            project_type=parsed.get('projectType'),
                            district=parsed.get("district"),
                            construction_unit=parsed.get("constructionUnit"),
                            project_stage=cls.PROJECT_STAGE,
                            bid_control_price=parsed.get("bidControlPrice"),
                            construction_scale=parsed.get("constructionScale"),
                            duration=parsed.get("duration"),
                            registration_deadline=cls._parse_registration_deadline(parsed.get("registrationDeadline")),
                            agency=parsed.get('agency'),
                            construction_content=parsed.get("constructionContent"),
                            tender_scope=parsed.get("tenderScope"),
                            announcement_website=parsed.get("announcementWebsite"),
                            pre_qualification_url=parsed.get("preQualificationUrl"),
                            release_time=cls._parse_release_date(item.get("project_time")),
                            remark=parsed.get("remark")
                        )
                    return tender
                except Exception:
                    return None

        tasks = [process_item(item) for item in result]
        tenders = await asyncio.gather(*tasks)

        inserted = 0
        for tender in tenders:
            if tender:
                try:
                    await TenderDao.add_tender_dao(db, tender)
                    await db.commit()
                    inserted += 1
                except Exception:
                    await db.rollback()
                    continue
        return inserted


    @staticmethod
    def _default_ai_entity() -> GovTenderNoticeEntity:
        return GovTenderNoticeEntity(
            district="市级",
            projectType="其他",
            bidControlPrice=0.0,
            constructionScale="",
            tenderScope="",
            constructionContent="",
            duration="",
            registrationDeadline="",
        )

    @classmethod
    async def _extract_ai_data(cls, text: str) -> tuple[GovTenderNoticeEntity, bool]:
        """
        使用 AI 提取招标公告关键信息
        """
        try:
            result = await asyncio.to_thread(
                extract_structured_data,
                text=text,
                response_model=GovTenderNoticeEntity,
                instruction="从下述公告中提取相关信息：",
                default_factory=cls._default_ai_entity,
                max_retries=2,
                retry_delay=0.5,
            )
            if result is not None:
                return result, False
            return cls._default_ai_entity(), True
        except Exception:
            return cls._default_ai_entity(), True


    @classmethod
    async def parse_item_from_content(cls, json_item: dict, content_str: str | None = None) -> dict:
        if content_str is None:
            content_str = await GovProcurementBase.get_html_detail_content(json_item.get('project_url'))
        html_url = json_item.get('project_url')

        # 使用 AI 提取补充字段
        content_str = cls._sanitize_text_for_ai(content_str)
        ai_result, used_default = await cls._extract_ai_data(content_str)
        remark_text = f"数据提取失败请手动打开浏览器查看：{html_url}" if used_default else None

        return {
            "projectCode": json_item.get("projectCode"),
            "projectName": json_item.get("project_title"),
            "projectType": ai_result.projectType,
            "district": ai_result.district,
            "constructionUnit": ai_result.constructionName,
            "duration": ai_result.duration,
            "agency": ai_result.agentName,
            "bidControlPrice": ai_result.bidControlPrice,
            "registrationDeadline": ai_result.registrationDeadline,
            "constructionScale": ai_result.constructionScale,
            "constructionContent": ai_result.constructionContent,
            "tenderScope": ai_result.tenderScope,
            "announcementWebsite": "政府采购",
            "preQualificationUrl": html_url,
            "remark": remark_text
        }




