import re
from typing import List, Optional

from parsel import Selector


class HtmlUtil:
    """
    HTML 解析与数据提取工具类 (基于 parsel/lxml)
    """

    @staticmethod
    def get_text(
        html: str,
        css: Optional[str] = None,
        xpath: Optional[str] = None,
        default: str = "",
        strip: bool = True,
    ) -> str:
        """
        提取单个元素的文本内容

        :param html: HTML 源码
        :param css: CSS 选择器 (例如: 'div.content > p::text')
        :param xpath: XPath 选择器 (例如: '//div[@class="content"]/p/text()')
        :param default: 未找到时的默认值
        :param strip: 是否去除首尾空白
        :return: 提取的文本
        """
        if not html:
            return default

        sel = Selector(text=html)
        result = None

        if css:
            result = sel.css(css).get()
        elif xpath:
            result = sel.xpath(xpath).get()
        else:
            # 如果没有提供选择器，则清理整个 HTML 的标签，返回纯文本
            # 类似 BeautifulSoup.get_text()
            return HtmlUtil.clean_tags(html)

        if result is None:
            return default

        return result.strip() if strip else result

    @staticmethod
    def get_list(
        html: str,
        css: Optional[str] = None,
        xpath: Optional[str] = None,
        strip: bool = True,
    ) -> List[str]:
        """
        提取多个元素的文本列表
        """
        if not html:
            return []

        sel = Selector(text=html)
        results = []

        if css:
            results = sel.css(css).getall()
        elif xpath:
            results = sel.xpath(xpath).getall()

        if strip:
            return [r.strip() for r in results if r and r.strip()]
        return results

    @staticmethod
    def clean_tags(html: str) -> str:
        """
        移除 HTML 标签，仅保留文本，并规范化空白字符
        适用于将富文本转为纯文本给 LLM 处理
        """
        if not html:
            return ""
        
        # 使用 XPath string() 获取纯文本，性能极佳
        sel = Selector(text=html)
        # //body//text() 会获取所有子节点文本，但 string(.) 会拼接得更好
        text = sel.xpath("string(.)").get() or ""
        
        # 规范化空白：将连续的换行/空格替换为单个空格，但保留段落感通常需要更复杂的处理
        # 这里简单做一下清理，保留换行可能对 LLM 更有利，视情况而定
        # 下面策略：将连续空白(包括换行)替换为单个空格
        return re.sub(r'\s+', ' ', text).strip()

    @staticmethod
    def clean_tags_preserve_structure(html: str) -> str:
        """
        移除标签但保留一定的结构（如换行），更适合 LLM 阅读
        """
        if not html:
            return ""
            
        # 简单的正则去除 script 和 style
        html = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', html, flags=re.S|re.I)
        
        # 将块级元素替换为换行
        html = re.sub(r'</?(div|p|br|h\d|tr|li)[^>]*>', '\n', html, flags=re.I)
        
        # 去除其余标签
        text = re.sub(r'<[^>]+>', '', html)
        
        # 压缩多余空行
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        return '\n'.join(lines)

    @staticmethod
    def find_target_pdf_links(
        html: str,
        keywords: Optional[List[str]] = None,
        html_url: Optional[str] = None,
        base_url: Optional[str] = "https://ggzyfw.beijing.gov.cn",
    ) -> List[str]:
        """
        从 HTML 中寻找目标 PDF 文件链接

        :param html: HTML 源码
        :param keywords: 关键字列表，用于匹配文件名或链接
        :param html_url: HTML 页面的 URL，用于生成链接
        :param base_url: 基础 URL，用于生成链接
        :return: 目标 PDF 文件链接列表
        """
        if not html:
            return []
        if keywords is None:
            keywords = ["候选人", "公示", "中标"]
        sel = Selector(text=html)
        links = sel.xpath('//a[contains(translate(@href, "PDF", "pdf"), ".pdf")]')
        found: List[str] = []
        for link in links:
            href = link.xpath('@href').get()
            href = (href or "").strip()
            text = (link.xpath('string(.)').get() or "").strip()
            file_name = href.split('/')[-1] if href else ""
            is_target = any((kw in text) or (kw in file_name) for kw in keywords)
            if not is_target:
                continue
            if href and not href.startswith('http'):
                if href.startswith('/'):
                    if base_url:
                        href = f"{base_url}{href}"
                else:
                    from urllib.parse import urljoin
                    if html_url:
                        href = urljoin(html_url, href)
                    elif base_url:
                        href = urljoin(base_url + '/', href)
            if href and href not in found:
                found.append(href)
        return found

    @staticmethod
    async def fetch_target_pdf_links(
        html_url: str,
        keywords: Optional[List[str]] = None,
        impersonate: str = "chrome110",
        timeout: int = 10,
        base_url: Optional[str] = "https://ggzyfw.beijing.gov.cn",
    ) -> List[str]:
        from curl_cffi.requests import AsyncSession
        async with AsyncSession() as session:
            response = await session.get(
                html_url,
                impersonate=impersonate,
                timeout=timeout,
            )
            if response.status_code != 200:
                return []
            html_content = response.text
        return HtmlUtil.find_target_pdf_links(
            html_content,
            keywords=keywords,
            html_url=html_url,
            base_url=base_url,
        )
