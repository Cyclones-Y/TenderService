import asyncio
from curl_cffi import requests as curl_requests
from module_tender.agent.state.state import AgentState
from module_tender.dao.tender_dao import TenderDao
from utils.log_util import logger

class FetchNode:
    def _build_context(self, tender) -> str:
        parts = []

        def add(label: str, value: object | None) -> None:
            if value is None:
                return
            text = str(value).strip()
            if not text:
                return
            parts.append(f"{label}: {text}")

        add("项目名称", tender.project_name)
        add("项目编号", tender.project_code)
        add("所在区县", tender.district)
        add("建设单位", tender.construction_unit)
        add("项目阶段", tender.project_stage)
        add("项目类型", tender.project_type)
        add("招标控制价（万元）", tender.bid_control_price)
        add("中标价（万元）", tender.bid_price)
        add("建设规模", tender.construction_scale)
        add("施工内容", tender.construction_content)
        add("招标范围", tender.tender_scope)
        add("工期", tender.duration)
        add("报名截止时间", tender.registration_deadline)
        add("代理机构", tender.agency)
        add("信息发布时间", tender.release_time)
        add("公告网站", tender.announcement_website)
        add("预审公告收集网址", tender.pre_qualification_url)
        add("中标公告网址", tender.bid_announcement_url)
        add("备注", tender.remark)

        return "\n".join(parts)

    async def __call__(self, state: AgentState) -> dict:
        tender_id = state['tender_id']
        db = state['db_session']
        
        try:
            tender = await TenderDao.get_tender_detail_by_id(db, tender_id)
            if not tender:
                return {"error": "未找到招标信息", "progress": 100, "current_step": "获取失败"}

            url = tender.pre_qualification_url or tender.bid_announcement_url
            context = self._build_context(tender)
            qualifications = state.get("qualifications") or []
            if qualifications:
                context = f"{context}\n企业资质: {', '.join(qualifications)}"

            content = ""
            if url:
                def fetch():
                    try:
                        resp = curl_requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=30, impersonate="chrome")
                        return resp.text
                    except Exception as e:
                        logger.error(f"Fetch failed: {e}")
                        return ""
                
                content = await asyncio.to_thread(fetch)
            
            if not content:
                if context:
                    content = context
                else:
                    if not url:
                        return {"error": "未找到相关链接", "progress": 100, "current_step": "获取失败"}
                    return {"error": "无法获取网页内容", "progress": 100, "current_step": "获取失败"}

            if context and content != context:
                content = f"{context}\n\n{content}"

            return {
                "project_text": content,
                "tender_data": tender.__dict__,
                "progress": 10,
                "current_step": "文件获取中"
            }
            
        except Exception as e:
            logger.error(f"FetchNode error: {e}")
            return {"error": str(e), "progress": 100, "current_step": "系统异常"}
