import asyncio
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from utils.html_util import HtmlUtil
from utils.pdf_util import PdfUtil


async def extract_pdf_link(html_url: str):
    print(f"正在获取页面: {html_url}")
    links = await HtmlUtil.fetch_target_pdf_links(html_url)
    print("\n--- 提取结果 ---")
    if links:
        for href in links:
            print(f"目标文件: {href}")
        first = links[0]
        print("\n--- PDF 文本片段 ---")
        txt = await PdfUtil.fetch_pdf_text(first, headers={"Referer": html_url})
        print((txt or ""))
    else:
        print("未找到符合'中标候选人公示'相关命名规则的 PDF 文件。")

if __name__ == "__main__":
    html_url = "https://ggzyfw.beijing.gov.cn/jyxxzbhxrgs/20251230/5388880.html"
    asyncio.run(extract_pdf_link(html_url))
