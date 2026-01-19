import asyncio
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel
from module_tender.agent.prompts.analysis_prompts import ANALYSIS_PROMPT
from module_tender.agent.state.state import AgentState
from module_tender.service.integration.structured_output import extract_structured_data
from module_tender.entity.vo.tender_vo import AiRequirementItemModel, RadarItemModel

class CoreAnalysisResult(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    summary: str = Field(description='核心解读与摘要')
    requirements: list[AiRequirementItemModel] = Field(description='关键/硬性要求列表')
    score: int = Field(description='AI 推荐指数（0-100）')
    profitability: str = Field(description='预估利润率，例如 "12% - 15%"')
    difficulty: str = Field(description='实施难度，例如 "高 (管网复杂)"')
    radar_data: list[RadarItemModel] = Field(description='能力维度雷达图数据，包含：资质匹配、资金风险、技术难度、竞争程度、利润空间')
    features: list[str] = Field(description='项目特征标签')
    decision_conclusion: str = Field(description='决策建议结论')
    focus_points: list[str] = Field(description='重点关注事项，建议3-5条')

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
