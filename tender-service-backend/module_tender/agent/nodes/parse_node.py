from bs4 import BeautifulSoup
from module_tender.agent.state.state import AgentState

class ParseNode:
    async def __call__(self, state: AgentState) -> dict:
        html = state.get("project_text", "")
        if not html:
            return {"error": "无内容解析"}
            
        def parse(h):
            soup = BeautifulSoup(h, 'lxml')
            for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
                tag.decompose()
            return soup.get_text(separator="\n", strip=True)
            
        text = parse(html)
        # Simple cleanup
        text = "\n".join([line for line in text.splitlines() if len(line) > 5])
        
        return {
            "project_text": text[:25000],
            "progress": 30,
            "current_step": "解析进行中"
        }
