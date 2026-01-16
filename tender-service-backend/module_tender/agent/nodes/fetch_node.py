import asyncio
import requests
from module_tender.agent.state.state import AgentState
from module_tender.dao.tender_dao import TenderDao
from utils.log_util import logger

class FetchNode:
    async def __call__(self, state: AgentState) -> dict:
        tender_id = state['tender_id']
        db = state['db_session']
        
        try:
            tender = await TenderDao.get_tender_detail_by_id(db, tender_id)
            if not tender:
                return {"error": "未找到招标信息", "progress": 100, "current_step": "获取失败"}

            url = tender.pre_qualification_url or tender.bid_announcement_url

            content = ""
            if url:
                def fetch():
                    try:
                        resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=30)
                        resp.encoding = resp.apparent_encoding
                        return resp.text
                    except Exception as e:
                        logger.error(f"Fetch failed: {e}")
                        return ""
                
                content = await asyncio.to_thread(fetch)
            
            if not content:
                # 如果没有URL或抓取失败，尝试使用数据库中已有的内容（如果有）
                # 这里假设必须要有内容才能继续
                if not url:
                     return {"error": "未找到相关链接", "progress": 100, "current_step": "获取失败"}
                return {"error": "无法获取网页内容", "progress": 100, "current_step": "获取失败"}

            return {
                "project_text": content,
                "tender_data": tender.__dict__,
                "progress": 10,
                "current_step": "文件获取中"
            }
            
        except Exception as e:
            logger.error(f"FetchNode error: {e}")
            return {"error": str(e), "progress": 100, "current_step": "系统异常"}
