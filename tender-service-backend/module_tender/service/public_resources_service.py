import asyncio
import json
import re

from curl_cffi import requests as curl_requests
from sqlalchemy.ext.asyncio import AsyncSession

from config.database import AsyncSessionLocal
from exceptions.exception import ServiceException
from module_tender.dao.tender_dao import TenderDao
from module_tender.entity.vo.tender_vo import TenderModel


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
        url = "https://ggzyfw.beijing.gov.cn/elasticsearch/searchList"
        payload = {
            "channel_id": "284",
            "channel_first": "jyxx",
            "channel_second": "jyxxgcjs",
            "channel_third": "jyxxgcjszbjh",
            "channel_fourth": "",
            "ext": "A98",
            "ext8": "",
            "starttime": start_date,
            "endtime": end_date,
            "sort": "time",
            "page": str(page),
            "size": str(size),
        }
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        try:
            resp = await asyncio.to_thread(
                curl_requests.post,
                url,
                data=payload,
                headers=headers,
                timeout=30,
                verify=False,
                impersonate="chrome",
            )
            resp.raise_for_status()
        except Exception as e:
            raise ServiceException(message=f"招标计划数据获取失败: {e}") from e
        try:
            text = resp.content.decode("utf-8", errors="replace")
            data = json.loads(text)
        except Exception:
            try:
                data = resp.json()
            except Exception as e:
                raise ServiceException(message=f"招标计划数据解析失败: {e}") from e
        result = data.get("result") or []
        if isinstance(result, str):
            try:
                result = json.loads(result)
            except Exception:
                result = []
        inserted = 0
        for item in result:
            parsed = cls.parse_plan_item_from_content(item)
            tender = TenderModel(
                project_code=parsed.get("projectCode"),
                project_name=parsed.get("projectName"),
                district=parsed.get("district"),
                construction_unit=parsed.get("constructionUnit"),
                project_stage="招标计划",
                # project_type=parsed.get("projectType"),
                bid_control_price=parsed.get("bidControlPrice"),
                construction_scale=parsed.get("constructionScale"),
                construction_content=parsed.get("constructionContent"),
                tender_scope=parsed.get("tenderScope"),
                announcement_website=parsed.get("announcementWebsite"),
                pre_qualification_url=parsed.get("preQualificationUrl"),
                expected_announcement_date=parsed.get("expectedAnnouncementDate"),
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
    def _abs_url(link: str) -> str:
        if not link:
            return ""
        if str(link).startswith("http"):
            return str(link)
        return f"https://ggzyfw.beijing.gov.cn{link}"

    @staticmethod
    def _parse_release_date(s: str) -> None | __import__("datetime").date:
        if not s:
            return None
        try:
            return __import__("datetime").datetime.strptime(str(s).strip(), "%Y-%m-%d").date()
        except ValueError:
            return None

    @staticmethod
    def _extract_construction_unit(content_str: str) -> str:
        unit_match = re.search(
            r"招标人[：:]\s*(.*?)(?:。|；|;|项目概况|投资估算|招标范围|建设规模|预计招标公告发布时间|招标公告发布时间|其他说明|项目名称|$)",
            content_str,
            flags=re.S,
        )
        if unit_match:
            return re.sub(r"\s+", " ", unit_match.group(1)).strip().strip("。；;")
        return ""

    @staticmethod
    def _extract_construction_content(content_str: str) -> str:
        overview_match = re.search(r"项目概况[：:]\s*(.*?)(?=投资估算(?:[：:]|\\s))", content_str, flags=re.S)
        if overview_match:
            return re.sub(r"\s+", " ", overview_match.group(1)).strip()
        return ""

    @staticmethod
    def _extract_bid_control_price(content_str: str) -> float | None:
        price_match = re.search(r"(?:招标控制价|投资估算)[：:]\s*([\d\.]+)\s*万元", content_str)
        if price_match:
            try:
                return float(price_match.group(1))
            except ValueError:
                return None
        return None

    @staticmethod
    def _extract_construction_scale(content_str: str) -> str:
        def _extract_scale_text(text: str) -> str | None:
            if not text:
                return None
            t = re.sub(r"\s+", " ", str(text)).strip().replace("，", ",")
            return t or None

        scale_match = re.search(
            r"建设规模[：:]\s*(.*?)(?=(?:预计)?招标公告发布时间|招标公告发布时间|其他说明|$)",
            content_str,
            flags=re.S,
        )
        if scale_match:
            val = _extract_scale_text(scale_match.group(1))
            if val is not None:
                return val
        scale_fallback = re.search(
            r"(?:建设规模|建设面积|施工面积)[：: ]?\s*(.*?)(?=(?:预计)?招标公告发布时间|招标公告发布时间|其他说明|$)",
            content_str,
            flags=re.S,
        )
        if scale_fallback:
            val = _extract_scale_text(scale_fallback.group(1))
            if val is not None:
                return val
        return ""

    @staticmethod
    def _extract_tender_scope(content_str: str) -> str:
        scope_match = re.search(
            r"招标范围[：:]\s*(.*?)(?=建设规模[：:]|建设面积[：:]|施工面积[：:])",
            content_str,
            flags=re.S,
        )
        if scope_match:
            return re.sub(r"\s+", " ", scope_match.group(1)).strip()
        return ""

    @staticmethod
    def _extract_expected_announcement_date(content_str: str) -> str | None:
        expected_match = re.search(
            r"预计招标公告发布时间[：:]\s*(.*?)(?=其他说明|$)",
            content_str,
            flags=re.S,
        )
        if expected_match:
            tmp = re.sub(r"\s+", " ", expected_match.group(1)).strip()
            return tmp or None
        return None

    @classmethod
    def parse_plan_item_from_content(cls, json_item: dict) -> dict:
        content_str = json_item.get("content", "")
        district = json_item.get("region", "")
        construction_unit = cls._extract_construction_unit(content_str)
        construction_content = cls._extract_construction_content(content_str)
        bid_control_price = cls._extract_bid_control_price(content_str)
        construction_scale = cls._extract_construction_scale(content_str)
        tender_scope = cls._extract_tender_scope(content_str)
        expected_announcement_date = cls._extract_expected_announcement_date(content_str)
        return {
            "projectCode": json_item.get("projectCode"),
            "projectName": json_item.get("title"),
            "district": district,
            "constructionUnit": construction_unit,
            # "projectType": PublicResourcesService.extract_project_type(json_item.get("title")),
            "bidControlPrice": bid_control_price,
            "constructionScale": construction_scale,
            "constructionContent": construction_content,
            "tenderScope": tender_scope,
            "announcementWebsite": "公共资源",
            "preQualificationUrl": cls._abs_url(json_item.get("link")),
            "expectedAnnouncementDate": expected_announcement_date,
        }


async def test_fetch_tender_plan() -> None:
    async with AsyncSessionLocal() as db:
        count = await PublicResourcesService.fetch_tender_plan(
            start_date="2025-12-05",
            end_date="2026-01-05",
            db=db,
            page=1,
            size=100,
        )
        print(count)


if __name__ == "__main__":
    asyncio.run(test_fetch_tender_plan())
