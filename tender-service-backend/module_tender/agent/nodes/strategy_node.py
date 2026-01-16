import asyncio
from pydantic import BaseModel, Field
from module_tender.agent.state.state import AgentState
from module_tender.service.integration.structured_output import extract_structured_data
from module_tender.entity.vo.tender_vo import AiTenderAnalysisModel
from module_tender.agent.prompts.analysis_prompts import STRATEGY_PROMPT

class StrategyAnalysisResult(BaseModel):
    risks: list[str] = Field(description='风险列表')
    strategy: str = Field(description='投标响应策略建议')

class StrategyNode:
    async def __call__(self, state: AgentState) -> dict:
        text = state.get("project_text", "")
        intermediate = state.get("intermediate_data", {})
        
        def run_strategy():
            return extract_structured_data(
                text,
                StrategyAnalysisResult,
                instruction=STRATEGY_PROMPT
            )
            
        result = await asyncio.to_thread(run_strategy)
        
        if not result:
            result = StrategyAnalysisResult(risks=[], strategy="无法生成策略")
        # Merge
        final_model = AiTenderAnalysisModel(
            score=intermediate.get('score', 0),
            summary=intermediate.get('summary', ''),
            requirements=intermediate.get('requirements', []),
            risks=result.risks,
            strategy=result.strategy
        )
        
        return {
            "progress": 90,
            "current_step": "建议生成中",
            "analysis_result": final_model
        }
