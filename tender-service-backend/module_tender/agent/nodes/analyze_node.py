import asyncio
from pydantic import BaseModel, Field
from module_tender.agent.state.state import AgentState
from module_tender.service.integration.structured_output import extract_structured_data
from module_tender.entity.vo.tender_vo import AiRequirementItemModel
from module_tender.agent.prompts.analysis_prompts import ANALYSIS_PROMPT

class CoreAnalysisResult(BaseModel):
    summary: str = Field(description='核心解读与摘要')
    requirements: list[AiRequirementItemModel] = Field(description='关键/硬性要求列表')
    score: int = Field(description='AI 推荐指数（0-100）')

class AnalyzeNode:
    async def __call__(self, state: AgentState) -> dict:
        text = state.get("project_text", "")
        
        def run_analysis():
            return extract_structured_data(
                text, 
                CoreAnalysisResult, 
                instruction=ANALYSIS_PROMPT
            )
            
        result = await asyncio.to_thread(run_analysis)
        
        if not result:
            return {"error": "分析失败", "progress": 100, "current_step": "分析失败"}
            
        return {
            "progress": 60,
            "current_step": "核心分析中",
            "analysis_result": None,
            "intermediate_data": result.model_dump()
        }
