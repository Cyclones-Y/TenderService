import requests
from bs4 import BeautifulSoup
import datetime
import re
import asyncio


from exceptions.exception import ServiceException


class GovProcurementBase:


    @staticmethod
    def _parse_release_date(s: str) -> datetime.date | None:
        if not s:
            return None
        try:
            return datetime.datetime.strptime(str(s).strip(), "%Y-%m-%d").date()
        except ValueError:
            return None



    @staticmethod
    def _parse_registration_deadline(s: str) -> datetime.datetime | None:
        if not s:
            return None

        try:
            # Support Chinese date format: 2026年01月19日16时00分
            dt = datetime.datetime.strptime(str(s).strip(), "%Y年%m月%d日%H时%M分")
            return dt.replace(second=0, microsecond=0)
        except ValueError:
            try:
                dt = datetime.datetime.strptime(str(s).strip(), "%Y-%m-%d %H:%M")
                return dt.replace(second=0, microsecond=0)
            except ValueError:
                return None

    @staticmethod
    def _sanitize_text_for_ai(text: str, max_len: int = 6000) -> str:
        """
        排除敏感信息
        """
        t = text or ""
        t = re.sub(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}', '', t)
        t = re.sub(r'\b1[3-9]\d{9}\b', '', t)
        t = re.sub(r'\b0\d{2,3}-\d{7,8}\b', '', t)
        return t[:max_len]

    @classmethod
    async def check_and_skip_if_exists(cls, item: dict, db, project_stage: str) -> bool:
        """
        检查项目是否已存在，如果存在则跳过
        :param item: 项目数据
        :param db: 数据库会话
        :param project_stage: 项目阶段
        :return: 如果项目已存在返回True，否则返回False
        """
        from module_tender.dao.tender_dao import TenderDao

        project_code = (item.get("projectCode") or "").strip()
        if project_code:
            existed = await TenderDao.get_by_code_and_stage(db, project_code, project_stage)
            if existed:
                return True
        return False

    @classmethod
    async def get_html_project_list(
        cls,
        level: str = "city",
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> list[dict] | None:
        """
        从给定URL获取项目链接列表
        """
        if start_date and end_date:
            start_date = cls._parse_release_date(start_date)
            end_date = cls._parse_release_date(end_date)
            base_tpl = (
                "http://www.ccgp-beijing.gov.cn/xxgg/sjxxgg/zbgg/A002004001001index_{page}.htm"
                if str(level).lower() == "city"
                else "http://www.ccgp-beijing.gov.cn/xxgg/qjxxgg/qjzbgg/A002004002001index_{page}.htm"
            )
            page = 1
            results: list[dict] = []
            while True:
                page_url = base_tpl.format(page=page)
                try:
                    resp = await asyncio.to_thread(
                        requests.get,
                        page_url,
                        timeout=30,
                        verify=False,
                    )
                    resp.raise_for_status()
                except Exception as e:
                    raise ServiceException(message=f"列表页获取失败: {e}") from e
                try:
                    resp.encoding = "utf-8"
                    soup = BeautifulSoup(resp.text, "lxml")
                    list_items = soup.find_all("li")
                    if not list_items:
                        break
                    page_dates: list[datetime.date] = []
                    for li in list_items:
                        link_element = li.find("a")
                        time_element = li.find("span", class_="datetime")
                        date_str = time_element.get_text(strip=True) if time_element else None
                        if not date_str:
                            m = re.search(r"(\d{4}-\d{2}-\d{2})", li.get_text())
                            date_str = m.group(1) if m else None
                        dt = cls._parse_release_date(date_str or "")
                        if not dt:
                            continue
                        page_dates.append(dt)
                        if start_date <= dt <= end_date:
                            href = link_element.get("href") if link_element else ""
                            if href:
                                if href.startswith("//"):
                                    href = "http://" + href[2:]
                                elif href.startswith("/"):
                                    href = "http://www.ccgp-beijing.gov.cn" + href
                            item = {
                                "project_url": href,
                                "project_title": link_element.get_text(strip=True) if link_element else "",
                                "project_time": date_str or "",
                            }
                            results.append(item)
                    if page_dates and min(page_dates) < start_date:
                        break
                    page += 1
                except Exception as e:
                    raise ServiceException(message=f"列表页解析失败: {e}") from e

            return results


    @classmethod
    async def get_html_detail_content(cls, url: str | None) -> str:
        """
        从给定URL获取项目详情内容
        """
        if not url:
            raise ServiceException(message="详情页获取失败: 缺少有效URL")
        try:
            response = await asyncio.to_thread(
                requests.get,
                url,
                timeout=30,
                verify=False
            )
            response.raise_for_status()
        except Exception as e:
            raise ServiceException(message=f"详情页获取失败: {e}") from e

        try:
            # 使用 BeautifulSoup 解析网页
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'lxml')

            # 首先检查页面是否成功加载
            full_text = ""
            # 这里的查找逻辑保留用户原有的，但添加判空
            body_label = soup.find("div", id="BodyLabel")
            if body_label:
                html_detail = body_label.find_all('p')
                for p in html_detail:
                    full_text += p.get_text(strip=True) + "\n"
            return full_text
        except Exception as e:
            raise ServiceException(message=f"详情页解析失败: {e}") from e

