import asyncio
import datetime
import json
import re

from curl_cffi import requests as curl_requests
from exceptions.exception import ServiceException

class PublicResourcesBase:
    @staticmethod
    def _abs_url(link: str) -> str:
        if not link:
            return ""
        if str(link).startswith("http"):
            return str(link)
        return f"https://ggzyfw.beijing.gov.cn{link}"

    @staticmethod
    def _parse_release_date(s: str) -> datetime.date | None:
        if not s:
            return None
        try:
            return datetime.datetime.strptime(str(s).strip(), "%Y-%m-%d").date()
        except ValueError:
            return None

    @classmethod
    async def request_list(
        cls,
        channel_id: str,
        channel_third: str,
        ext: str,
        page: int,
        size: int,
        starttime: str,
        endtime: str,
    ) -> list:
        url = "https://ggzyfw.beijing.gov.cn/elasticsearch/searchList"
        payload = {
            "channel_id": str(channel_id),
            "channel_first": "jyxx",
            "channel_second": "jyxxgcjs",
            "channel_third": str(channel_third),
            "channel_fourth": "",
            "ext": str(ext),
            "ext8": "",
            "starttime": starttime,
            "endtime": endtime,
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
            raise ServiceException(message=f"数据获取失败: {e}") from e
        try:
            text = resp.content.decode("utf-8", errors="replace")
            data = json.loads(text)
        except Exception:
            try:
                data = resp.json()
            except Exception as e:
                raise ServiceException(message=f"数据解析失败: {e}") from e
        result = data.get("result") or []
        if isinstance(result, str):
            try:
                result = json.loads(result)
            except Exception:
                result = []
        return result
