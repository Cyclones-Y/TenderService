import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from module_tender.dao.tender_dao import TenderDao
from module_tender.entity.structured_entity.ccgp_gov_entity import CCGPGovEntity
from module_tender.entity.vo.tender_vo import TenderModel
from module_tender.service.gov_procurement.base import GovProcurement
from module_tender.service.integration.structured_output import extract_structured_data


class TenderService(GovProcurement):
    """
    CCGP 政府采购项目服务业务层
    """

    @classmethod
    async def fetch(cls, db: AsyncSession, start_date: str = None, end_date: str = None) -> int:
        """
        获取招标公告数据
        """
        # 调用基类的数据获取能力
        result = await cls.get_ccgp_gov_project_list(start_date, end_date)

        # Concurrency control
        semaphore = asyncio.Semaphore(10)
        db_lock = asyncio.Lock()

        async def process_item(item: dict) -> TenderModel | None:
            async with semaphore:
                url = item.get('project_url')
                if not url:
                    return None

                try:
                    text = await cls.get_html_detail_content(url)
                except Exception:
                    return None


                project_code = cls._get_project_code(text)
                project_stage = item.get('project_type', '')

                # Check existence (Serialized)
                if project_code:
                    async with db_lock:
                        if await cls.check_and_skip_if_exists({"projectCode": project_code}, db, project_stage):
                            return None

                enriched_item = dict(item)
                enriched_item["projectCode"] = project_code

                try:
                    parsed = await cls.parse_item_from_content(enriched_item)
                    tender = TenderModel(
                        project_code=parsed.get("projectCode"),
                        project_name=parsed.get("projectName"),
                        project_type=parsed.get('projectType'),
                        district=parsed.get("district"),
                        construction_unit=parsed.get("constructionUnit"),
                        project_stage=parsed.get("project_stage"),
                        bid_control_price=parsed.get("bidControlPrice"),
                        construction_scale=parsed.get("constructionScale"),
                        duration=parsed.get("duration"),
                        registration_deadline=cls._parse_registration_deadline(parsed.get("registrationDeadline")),
                        agency=parsed.get('agency'),
                        construction_content=parsed.get("constructionContent"),
                        tender_scope=parsed.get("tenderScope"),
                        announcement_website=parsed.get("announcementWebsite"),
                        pre_qualification_url=parsed.get("preQualificationUrl"),
                        bid_announcement_url=parsed.get("bidAnnouncementUrl"),
                        bid_date=cls._parse_release_date(parsed.get("bid_date")),
                        release_time=cls._parse_release_date(parsed.get("releaseTime")),
                        remark=parsed.get("remark"),
                        winner_rank_1=parsed.get("winnerRank1"),
                        winner_rank_2=parsed.get("winnerRank2"),
                        winner_rank_3=parsed.get("winnerRank3"),
                        discount_rate=parsed.get("discountRate"),
                        unit_price=parsed.get("unitPrice")
                    )
                    return tender
                except Exception as e:
                    print(f"Error processing item {url}: {e}")
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

    @classmethod
    def _default_ai_entity(cls) -> CCGPGovEntity:
        return CCGPGovEntity(
            projectCode="",
            district="",
            projectType="",
            bidControlPrice=0.0,
            bidPrice=0.0,
            constructionScale="",
            constructionContent="",
            tenderScope="",
            constructionName="",
            agentName="",
            duration="",
            registrationDeadline="",
            winner_rank_1="",
            winner_rank_2="",
            winner_rank_3="",
            discountRate="",
            unitPrice=0.0,
        )

    @classmethod
    async def _extract_ai_data(cls, text: str) -> tuple[CCGPGovEntity, bool]:
        """
        使用 AI 提取招标公告关键信息
        """
        try:
            result = await asyncio.to_thread(
                extract_structured_data,
                text=text,
                response_model=CCGPGovEntity,
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
    async def parse_item_from_content(cls, json_item: dict = None) -> dict:
        html_url = json_item.get('project_url', "")
        content_str = await cls.get_html_detail_content(html_url)
        project_code = cls._get_project_code(content_str)
        project_name = json_item.get('project_title')
        agency = json_item.get('agency')
        construction_unit = json_item.get('construction_unit')
        project_stage = json_item.get('project_type')
        release_time = json_item.get('release_time')

        # 使用 AI 提取补充字段
        content_str = cls._sanitize_text_for_ai(content_str)
        ai_result, used_default = await cls._extract_ai_data(content_str)
        remark_text = f"数据提取失败请手动打开浏览器查看：{html_url}" if used_default else None

        return {
            "projectCode": project_code,
            "projectName": project_name,
            "projectType": ai_result.projectType,
            "project_stage": project_stage,
            "district": ai_result.district,
            "constructionUnit": construction_unit,
            "duration": ai_result.duration,
            "registrationDeadline": ai_result.registrationDeadline,
            "tenderScope": ai_result.tenderScope,
            "agency": agency,
            "bidControlPrice": ai_result.bidControlPrice,
            "bidPrice": ai_result.bidPrice,
            "constructionScale": ai_result.constructionScale,
            "constructionContent": ai_result.constructionContent,
            "winnerRank1": ai_result.winner_rank_1,
            "winnerRank2": ai_result.winner_rank_2,
            "winnerRank3": ai_result.winner_rank_3,
            "discountRate": ai_result.discountRate,
            "unitPrice": ai_result.unitPrice,
            "announcementWebsite": "政府采购",
            "preQualificationUrl": html_url,
            "bidAnnouncementUrl": html_url if project_stage == "中标公告" else "",
            "bid_date": release_time if project_stage == "中标公告" else "",
            "releaseTime": release_time,
            "remark": remark_text
        }
