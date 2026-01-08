import re

from sqlalchemy.ext.asyncio import AsyncSession

from module_tender.dao.tender_dao import TenderDao
from module_tender.entity.structured_entity.tender_notice_fetcher import (
    TenderNoticeFetcher as TenderNoticeEntity,
)
from module_tender.entity.vo.tender_vo import TenderModel
from module_tender.service.integration.structured_output import extract_structured_data
from module_tender.service.public_resources.base import PublicResourcesBase


class TenderNoticeFetcher(PublicResourcesBase):
    """招标公告获取与解析"""
    PROJECT_STAGE = "招标公告"
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
            # 检查项目是否已存在
            if await cls.check_and_skip_if_exists(item, db, cls.PROJECT_STAGE):
                continue
            parsed = cls.parse_item_from_content(item)
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
                registration_deadline=cls._parse_release_date(item.get("noticeEndTime")),
                agency=parsed.get('agency'),
                construction_content=parsed.get("constructionContent"),
                tender_scope=parsed.get("tenderScope"),
                announcement_website=parsed.get("announcementWebsite"),
                pre_qualification_url=parsed.get("preQualificationUrl"),
                release_time=cls._parse_release_date(item.get("releaseDate")),
                remark=parsed.get("remark")
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
    def _extract_construction_unit(content_str: str) -> str:
        unit_match = re.search(
            r"招标人[：:]\s*(.*?)(?:。|；|;|地址|$)",
            content_str,
            flags=re.S,
        )
        if unit_match:
            return re.sub(r"\s+", " ", unit_match.group(1)).strip().strip("。；;")
        return ""

    @staticmethod
    def _extract_agent_unit(content_str: str) -> str:
        unit_match = re.search(
            r"(?:招标代理|招标代理机构)[：:]\s*(.*?)(?:。|；|;|地址|$)",
            content_str,
            flags=re.S,
        )
        if unit_match:
            return re.sub(r"\s+", " ", unit_match.group(1)).strip().strip("。；;")
        return ""

    @staticmethod
    def _extract_duration(content_str: str) -> str:
        # 匹配"工期"、"工期要求"等关键词，提取天数
        duration_match = re.search(
            r"(?:工期|计划工期|施工工期)(?:要求|为|：|:)?\s*(\d+)\s*(?:日历天|天|个日历天)",
            content_str,
            flags=re.S,
        )
        if duration_match:
            return duration_match.group(1)
        # 备选模式：匹配"本工程的工期要求XXX日历天"这种格式
        alt_match = re.search(
            r"本工程的工期要求(\d+)日历天",
            content_str,
            flags=re.S,
        )
        if alt_match:
            return alt_match.group(1)
        return ""

    @staticmethod
    def _extract_investment_amount(content_str: str) -> str:
        # 匹配"计划投资总额"、"投资总额"、"项目投资"等关键词，提取金额
        amount_match = re.search(
            r"(?:计划投资总额|投资总额|项目投资|总投资|工程投资)[：:]\s*([0-9,，.]+\s*(?:万元|元|亿|亿元)?)",
            content_str,
            flags=re.S,
        )
        if amount_match:
            amount_text = amount_match.group(1)
            # 提取数字部分
            number_match = re.search(r"([0-9,，.]+)", amount_text)
            if number_match:
                # 清理数字格式，移除逗号
                cleaned_number = number_match.group(1).replace(',', '').replace('，', '')
                return cleaned_number
        # 备选模式：匹配"计划投资总额 2092 （万元）"这种格式
        alt_match = re.search(
            r"计划投资总额\s+([0-9,，.]+)\s*（?(?:万元|元|亿|亿元)?）?",
            content_str,
            flags=re.S,
        )
        if alt_match:
            return alt_match.group(1).replace(',', '').replace('，', '')
        return ""

    @staticmethod
    def _extract_tender_scope(content_str: str) -> str:
        # 匹配从"范围"到"2.6其他"之间的内容
        scope_match = re.search(
            r"本工程招标范围(.*?)(?:2\.6其他|2\.6\s*其他)",
            content_str,
            flags=re.S,
        )
        if scope_match:
            extracted = scope_match.group(1).strip()
            # 去除开头的冒号或分隔符
            extracted = re.sub(r'^[：:]\s*', '', extracted)
            return re.sub(r"\s+", " ", extracted).strip().strip("。；;，")

        # 备选模式：匹配"招标范围"关键词
        alt_match = re.search(
            r"(?:招标范围|范围)[：:]\s*(.*?)(?:2\.6其他|2\.6\s*其他)",
            content_str,
            flags=re.S,
        )
        if alt_match:
            return re.sub(r"\s+", " ", alt_match.group(1)).strip().strip("。；;，")

        return ""

    @staticmethod
    def _extract_construction_scale(content_str: str) -> str:
        # 匹配"建设规模"关键词，提取规模描述
        scale_match = re.search(
            r"2.2本工程的建设规模\s*(.*?)2.3计划投资总额",
            content_str,
            flags=re.S,
        )
        if scale_match:
            return re.sub(r"\s+", " ", scale_match.group(1)).strip().strip("。；;，")
        return ""

    @staticmethod
    def _default_ai_entity() -> TenderNoticeEntity:
        return TenderNoticeEntity(
            projectType="其他",
            bidControlPrice=0.0,
            constructionScale="",
            tenderScope="",
            constructionContent="",
            duration="",
            registrationDeadline="",
        )

    @classmethod
    def _extract_ai_data(cls, text: str) -> tuple[TenderNoticeEntity, bool]:
        """
        使用 AI 提取招标公告关键信息
        """
        try:
            result = extract_structured_data(
                text=text,
                response_model=TenderNoticeEntity,
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
    def parse_item_from_content(cls, json_item: dict) -> dict:
        content_str = json_item.get("content", "")
        district = json_item.get("region", "")
        construction_unit = cls._extract_construction_unit(content_str)
        agent_unit = cls._extract_agent_unit(content_str)
        duration = cls._extract_duration(content_str)
        investment_amount = cls._extract_investment_amount(content_str)
        tender_scope = cls._extract_tender_scope(content_str)
        construction_scale = cls._extract_construction_scale(content_str)
        html_url = cls._abs_url(json_item.get("link"))

        # 使用 AI 提取补充字段
        content_str = cls._sanitize_text_for_ai(content_str)
        ai_result, used_default = cls._extract_ai_data(content_str)
        remark_text = f"数据提取失败请手动打开浏览器查看：{html_url}" if used_default else None
        
        return {
            "projectCode": json_item.get("projectCode"),
            "projectName": json_item.get("title"),
            "projectType": ai_result.projectType,
            "district": district,
            "constructionUnit": construction_unit,
            "duration": ai_result.duration or duration,  # 优先用 AI 提取的，如果为空则用正则兜底（或反之，视准确率而定）
            "agency": agent_unit,
            "bidControlPrice": ai_result.bidControlPrice,
            "constructionScale": ai_result.constructionScale or construction_scale,
            "constructionContent": ai_result.constructionContent,
            "tenderScope": ai_result.tenderScope or tender_scope,
            "announcementWebsite": "公共资源",
            "preQualificationUrl": html_url,
            "remark": remark_text
        }
