from typing import Optional

class PdfUtil:
    @staticmethod
    async def fetch_pdf_text(
        pdf_url: str,
        *,
        impersonate: str = "chrome124",
        timeout: int = 20,
        headers: Optional[dict] = None,
        referer: Optional[str] = None,
        session: Optional[object] = None,
    ) -> str:
        """
        从 PDF 文件中提取文本

        :param pdf_url: PDF 文件的 URL
        :param impersonate: 模拟的浏览器类型
        :param timeout: 请求超时时间（秒）
        :param headers: 请求头信息
        :param referer: 引用来源 URL
        :param session: 异步 HTTP 会话对象
        :return: 提取到的文本内容
        """
        from curl_cffi.requests import AsyncSession
        ext = session
        created = False
        if ext is None:
            ext = AsyncSession()
            created = True
        try:
            req_headers = dict(headers or {})
            if referer and "Referer" not in req_headers:
                req_headers["Referer"] = referer
            if "Accept" not in req_headers:
                req_headers["Accept"] = "application/pdf,*/*"
            if referer:
                try:
                    await ext.get(referer, impersonate=impersonate, timeout=timeout)
                except Exception:
                    pass
            resp = await ext.get(pdf_url, impersonate=impersonate, timeout=timeout, headers=req_headers)
            if resp.status_code != 200:
                return ""
            ct = (resp.headers or {}).get("Content-Type", "")
            data = resp.content
            if (not ct.lower().startswith("application/pdf")) or (data is None) or (len(data) < 1024):
                if referer:
                    req_headers["Referer"] = referer
                resp = await ext.get(pdf_url, impersonate=impersonate, timeout=timeout, headers=req_headers)
                if resp.status_code != 200:
                    return ""
                data = resp.content
            return PdfUtil.extract_text_from_bytes(data)
        finally:
            if created:
                await ext.close()



    @staticmethod
    def extract_text_from_bytes(data: bytes) -> str:
        """
        从 PDF 文件的字节数据中提取文本

        :param data: PDF 文件的字节数据
        :return: 提取到的文本内容
        """
        try:
            import fitz
        except Exception:
            return ""
        try:
            with fitz.open(stream=data, filetype="pdf") as doc:
                texts = []
                for page in doc:
                    txt = page.get_text("text") or ""
                    if not txt:
                        txt = page.get_text("raw") or ""
                    if not txt:
                        blocks = page.get_text("blocks") or []
                        if blocks:
                            blocks_sorted = sorted(blocks, key=lambda b: (b[1], b[0]))
                            txt = "\n".join(b[4] for b in blocks_sorted if isinstance(b[4], str) and b[4].strip())
                    if txt:
                        texts.append(txt)
                return "\n".join(texts).strip()
        except Exception:
            return ""

    @staticmethod
    def analyze_pdf_bytes(data: bytes, max_pages: int = 10) -> dict:
        """
        分析 PDF 文件的字节数据，判断是否为扫描件

        :param data: PDF 文件的字节数据
        :param max_pages: 最多检查的页面数
        :return: 包含分析结果的字典，包括是否为扫描件、检查的页面数、总页数、文本总长度、图片总数量
        """
        try:
            import fitz
        except Exception:
            return {"is_probably_scanned": False, "pages_checked": 0, "total_pages": 0, "text_total_len": 0, "image_total_count": 0}
        try:
            with fitz.open(stream=data, filetype="pdf") as doc:
                total_pages = len(doc)
                pages_checked = 0
                text_total_len = 0
                image_total_count = 0
                for i, page in enumerate(doc):
                    if i >= max_pages:
                        break
                    txt = page.get_text("text") or ""
                    if not txt:
                        txt = page.get_text("raw") or ""
                    text_total_len += len(txt or "")
                    imgs = page.get_images(full=True)
                    image_total_count += len(imgs or [])
                    pages_checked += 1
                is_probably_scanned = (text_total_len < 50) and (image_total_count >= pages_checked)
                return {
                    "is_probably_scanned": is_probably_scanned,
                    "pages_checked": pages_checked,
                    "total_pages": total_pages,
                    "text_total_len": text_total_len,
                    "image_total_count": image_total_count,
                }
        except Exception:
            return {"is_probably_scanned": False, "pages_checked": 0, "total_pages": 0, "text_total_len": 0, "image_total_count": 0}

    @staticmethod
    async def analyze_pdf_url(
        pdf_url: str,
        *,
        impersonate: str = "chrome124",
        timeout: int = 20,
        headers: Optional[dict] = None,
        max_pages: int = 10,
        referer: Optional[str] = None,
        session: Optional[object] = None,
    ) -> dict:
        """
        分析 PDF 文件的 URL，判断是否为扫描件

        :param pdf_url: PDF 文件的 URL
        :param impersonate: 模拟的浏览器类型
        :param timeout: 请求超时时间（秒）
        :param headers: 请求头信息
        :param max_pages: 最多检查的页面数
        :param referer: 引用来源 URL
        :param session: 异步 HTTP 会话对象
        :return: 包含分析结果的字典，包括是否为扫描件、检查的页面数、总页数、文本总长度、图片总数量
        """
        from curl_cffi.requests import AsyncSession
        ext = session
        created = False
        if ext is None:
            ext = AsyncSession()
            created = True
        try:
            req_headers = dict(headers or {})
            if referer and "Referer" not in req_headers:
                req_headers["Referer"] = referer
            if "Accept" not in req_headers:
                req_headers["Accept"] = "application/pdf,*/*"
            if referer:
                try:
                    await ext.get(referer, impersonate=impersonate, timeout=timeout)
                except Exception:
                    pass
            resp = await ext.get(pdf_url, impersonate=impersonate, timeout=timeout, headers=req_headers)
            if resp.status_code != 200:
                return {"is_probably_scanned": False, "pages_checked": 0, "total_pages": 0, "text_total_len": 0, "image_total_count": 0}
            ct = (resp.headers or {}).get("Content-Type", "")
            data = resp.content
            if (not ct.lower().startswith("application/pdf")) or (data is None) or (len(data) < 1024):
                if referer:
                    req_headers["Referer"] = referer
                resp = await ext.get(pdf_url, impersonate=impersonate, timeout=timeout, headers=req_headers)
                if resp.status_code != 200:
                    return {"is_probably_scanned": False, "pages_checked": 0, "total_pages": 0, "text_total_len": 0, "image_total_count": 0}
                data = resp.content
            return PdfUtil.analyze_pdf_bytes(data, max_pages=max_pages)
        finally:
            if created:
                await ext.close()
