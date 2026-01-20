from bs4 import BeautifulSoup, Tag
import requests
import asyncio

from pydantic import BaseModel, Field

from module_tender.service.beijing_gov_procurement.base import GovProcurementBase
from module_tender.service.beijing_gov_procurement.tender_notice import GovTenderNoticeFetcher
from module_tender.service.integration.structured_output import extract_structured_data
from prompts.prompts import  get_classify_landscaping_prompt


class Landscaping(BaseModel):
    is_landscaping_industry: bool = Field(default=False, description="是否为园林行业相关")


def get_html_project_list(url):
    """
    从给定URL获取项目链接列表
    """
    response = requests.get(url)
    response.encoding = 'utf-8'
    # 首先检查页面是否成功加载
    print(f"HTTP状态码: {response.status_code}")
    # 使用 BeautifulSoup 解析网页
    soup = BeautifulSoup(response.text, 'lxml')

    # 查找所有列表项
    list_items = soup.find_all('li')
    project_list = []

    if list_items:
        # 获取该页的14个列表项
        for li in list_items[:14]:
            # 提取链接和文本
            link_element = li.find('a')
            # 提取时间
            time_element = li.find('span', class_='datetime')

            if link_element:
                # 获取href属性（链接）
                href = link_element.get('href')
                if href.startswith('//'):
                    href = 'http://' + href[2:]

                # 构建包含链接、文本和时间的字典
                item_data = {
                    'href': href,
                    'text': link_element.get_text(strip=True),
                    'time': time_element.get_text(strip=True) if time_element else '无时间信息'
                }
                project_list.append(item_data)
    else:
        print("未能找到目标元素")

    return project_list



def get_html_detail_content(url):
    response = requests.get(url)
    response.encoding = 'utf-8'

    # 使用 BeautifulSoup 解析网页
    soup = BeautifulSoup(response.text, 'lxml')

    # 首先检查页面是否成功加载
    print(f"HTTP状态码: {response.status_code}")
    full_text = ""
    html_detail = soup.find("div", id="BodyLabel").find_all('p')
    for p in html_detail:
        full_text += p.get_text(strip=True) + "\n"
    print(full_text)
    return full_text


def main():
    # 使用 requests 获取网页内容
    url = 'http://www.ccgp-beijing.gov.cn/xxgg/qjxxgg/A002004002index_4.htm'


    # 查找正文内容 - 根据实际页面结构调整选择器
    list_items = get_html_project_list(url)

    if list_items:
        # 获取该页的14个列表项
        for li in list_items:
            # 提取链接和文本
            url = li.get('href')
            text = li.get('text')
            time = li.get('time')
            print(f"{text} - {time} - {url}")
            response = extract_structured_data("", Landscaping, get_classify_landscaping_prompt(text))
            if response.is_landscaping_industry:
                print(get_html_detail_content(url))
                print("-" * 50)
            else:
                print("未找到")
    else:
        print("未能找到目标元素，获取整个页面文本:")
        # 备用：获取整个页面文本并清理
        full_text = get_html_project_list(url).get_text()
        cleaned_text = ''.join(full_text.split())
        print(cleaned_text)
    return 0

if __name__ == "__main__":
    start_date ="2025-12-05"
    end_date = "2026-01-14"
    include_keywords = ['园林', '景观', '森林', '绿化', '养护', '林业', '花园', '绿地', '公园', '生态', '树木', '喷灌', '植被', '环境']

    async def _run():
        result_1 = await GovProcurementBase.get_html_project_list(
            info_type="win",
            level="city",
            start_date=start_date,
            end_date=end_date,
        )
        result_2 = await GovProcurementBase.get_html_project_list(
            info_type="win",
            level="111",
            start_date=start_date,
            end_date=end_date,
        )
        result = result_1 + result_2
        for li in result:
            url = li.get('project_url')
            title = li.get('project_title')
            time = li.get('project_time')
            if not url:
                continue
            text = await GovProcurementBase.get_html_detail_content(url)
            matched_keywords_count = sum(1 for k in include_keywords if k in text[:400])
            if matched_keywords_count < 2:
                continue
            print(GovTenderNoticeFetcher._get_project_code(text))
            print(GovTenderNoticeFetcher._get_project_name(text))

        print(f"一共有：{len(result)} 个项目")

    asyncio.run(_run())
