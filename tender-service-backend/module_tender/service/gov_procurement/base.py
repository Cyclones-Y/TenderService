import datetime
import re
import requests
from bs4 import BeautifulSoup
from sqlalchemy.ext.asyncio import AsyncSession

from module_tender.dao.tender_dao import TenderDao


class GovProcurement:

    @classmethod
    async def get_ccgp_gov_project_list(cls, start_date: str = None, end_date: str = None) -> list[dict]:
        """
        从给定URL获取项目链接列表
        """
        # 默认日期范围 (如果未提供)
        if not start_date:
            start_date = (datetime.date.today() - datetime.timedelta(days=30)).strftime("%Y-%m-%d")
        if not end_date:
            end_date = datetime.date.today().strftime("%Y-%m-%d")

        # 格式化日期为 URL 所需格式 (YYYY:MM:DD)
        start_time_encoded = start_date.replace("-", "%3A")
        end_time_encoded = end_date.replace("-", "%3A")

        list_url: list[str] = [
            f'https://search.ccgp.gov.cn/bxsearch?searchtype=2&page_index=1&bidSort=1&buyerName=&projectId=&pinMu=3&bidType=&dbselect=bidx&kw=%E7%BB%BF%E5%8C%96&start_time={start_time_encoded}&end_time={end_time_encoded}&timeType=5&displayZone=%E5%8C%97%E4%BA%AC&zoneId=11&pppStatus=0&agentName=',
            f'https://search.ccgp.gov.cn/bxsearch?searchtype=2&page_index=1&bidSort=1&buyerName=&projectId=&pinMu=2&bidType=&dbselect=bidx&kw=%E7%BB%BF%E5%8C%96&start_time={start_time_encoded}&end_time={end_time_encoded}&timeType=5&displayZone=%E5%8C%97%E4%BA%AC&zoneId=11&pppStatus=0&agentName='
        ]

        items: list[dict] = []
        for url in list_url:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Referer': 'https://search.ccgp.gov.cn/',
                'Host': 'search.ccgp.gov.cn'
            }
            try:
                response = requests.get(url, headers=headers)
                response.encoding = 'utf-8'
                # 使用 BeautifulSoup 解析网页
                soup = BeautifulSoup(response.text, 'lxml')

                # 查找所有列表项
                srch_result = soup.find('ul', class_='vT-srch-result-list-bid')
                if not srch_result:
                    continue

                list_items = srch_result.find_all('li')

                for li in list_items:
                    a_tag = li.find('a')
                    if not a_tag:
                        continue

                    href = a_tag.get('href')
                    title = a_tag.get_text(strip=True)

                    strong_tag = li.find('strong')
                    project_type = strong_tag.get_text(strip=True) if strong_tag else ""
                    
                    if "招标公告" in title:
                        project_type = "招标公告"

                    span_tag = li.find('span')
                    span_text = span_tag.get_text(strip=True) if span_tag else ""

                    stage_info = await cls.extract_tender_info(span_text)

                    project_dict = {
                        'project_url': href,
                        'project_title': title,
                        'project_type': project_type,
                    }
                    # 合并字典
                    project_dict.update(stage_info)
                    items.append(project_dict)
            except Exception as e:
                # 在实际工程中，这里应该记录日志
                print(f"Error fetching {url}: {e}")
                continue

        return items

    @classmethod
    async def extract_tender_info(cls, text: str) -> dict:
        """
        从公告文本中提取时间、采购人、代理机构、施工类型等信息
        """
        # 提取时间 - 格式为 YYYY.MM.DD HH:MM:SS
        time_pattern = r'(\d{4}\.\d{2}\.\d{2}\s+\d{2}:\d{2}:\d{2})'
        time_match = re.search(time_pattern, text)
        extracted_time = time_match.group(1).replace('.', '-') if time_match else None
        # 如果存在完整的时间，则只保留日期部分
        if extracted_time:
            # 分割字符串并只取日期部分
            date_part = extracted_time.split()[0]  # 只取日期部分，去掉小时分钟秒
            extracted_time = date_part

        # 提取采购人 - "采购人："后的内容
        purchaser_pattern = r'采购人：([^\r\n|]+)'
        purchaser_match = re.search(purchaser_pattern, text)
        purchaser = purchaser_match.group(1).strip() if purchaser_match else None

        # 提取代理机构 - "代理机构："后的内容
        agency_pattern = r'代理机构：([^\r\n|]+)'
        agency_match = re.search(agency_pattern, text)
        agency = agency_match.group(1).strip() if agency_match else None

        # 提取施工类型 - 最后部分的分类信息
        construction_type_pattern = r'(工程/[^|\r\n]+|施工/[^|\r\n]+|[^|\r\n]*施工[^|\r\n]*)'
        construction_matches = re.findall(construction_type_pattern, text)
        construction_type = construction_matches[-1].strip() if construction_matches else None

        return {
            'release_time': extracted_time,
            'construction_unit': purchaser,
            'agency': agency,
            'construction_type': construction_type
        }

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
    async def get_html_detail_content(cls, url: str) -> str:
        """
        获取HTML页面的详细内容
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://search.ccgp.gov.cn/',
        }
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        # 使用 BeautifulSoup 解析网页
        soup = BeautifulSoup(response.text, 'lxml')
        text_element = soup.find('div', class_='vF_detail_content')
        if text_element:
            return text_element.get_text(strip=True)
        else:
            return ""

    @staticmethod
    def _parse_release_date(s: str) -> datetime.date | None:
        if not s:
            return None
        try:
            return datetime.datetime.strptime(str(s).strip(), "%Y-%m-%d").date()
        except ValueError:
            return None

    @staticmethod
    def _get_project_code(text: str) -> str | None:
        """
        从文本中提取项目编号
        """
        # 1. 优先尝试匹配纯 ASCII 字符的编号 (字母、数字、横杠、下划线、点、斜杠)
        # 这种方式最安全，能有效应对 "项目编号：TC2603004项目名称：..." 这种紧凑且无分隔符的情况
        ascii_match = re.search(
            r"项目编号[：:]\s*([A-Za-z0-9\-_./]+)",
            text,
            flags=re.S
        )
        if ascii_match:
            code = ascii_match.group(1).strip()
            # 如果提取到的代码长度合理，优先采用
            if 3 < len(code) < 50:
                return code.strip("。；;，")

        # 2. 如果纯 ASCII 匹配不满足（例如编号含中文），尝试基于常见后继关键词截断
        # 使用 Lookahead 预测后续可能出现的字段名
        keyword_match = re.search(
            r"项目编号[：:]\s*(.*?)(?=\s|项目名称|采购方式|预算金额|采购人|代理机构|$)",
            text,
            flags=re.S
        )
        if keyword_match:
            return re.sub(r"\s+", " ", keyword_match.group(1)).strip().strip("。；;，")

        # 3. 兜底：匹配到行尾
        match = re.search(
            r"项目编号[：:]\s*(.*?)(?:\n|$)",
            text,
            flags=re.S)
        if match:
            return re.sub(r"\s+", " ", match.group(1)).strip().strip("。；;，")
        return ""

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

    @classmethod
    async def check_and_skip_if_exists(cls, item: dict, db: AsyncSession, project_stage: str) -> bool:
        """
        检查项目是否已存在，如果存在则跳过
        """
        project_code = (item.get("projectCode") or "").strip()
        if project_code:
            existed = await TenderDao.get_by_code_and_stage(db, project_code, project_stage)
            if existed:
                return True
        return False
