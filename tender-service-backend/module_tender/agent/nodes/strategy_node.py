import asyncio
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel
from module_tender.agent.state.state import AgentState
from module_tender.service.integration.structured_output import extract_structured_data
from module_tender.entity.vo.tender_vo import AiTenderAnalysisModel, CompetitorModel, PriceStatsModel
from module_tender.agent.prompts.analysis_prompts import STRATEGY_PROMPT

class StrategyAnalysisResult(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    risks: list[str] = Field(description='风险列表')
    strategy: str = Field(description='投标响应策略建议')
    competitors: list[CompetitorModel] = Field(description='潜在竞争对手预测')
    price_stats: PriceStatsModel = Field(description='同类项目报价分布')

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
            # Create a default result if extraction fails, matching the new structure but with empty/default values
            from module_tender.entity.vo.tender_vo import PriceStatsModel, CompetitorModel
            result = StrategyAnalysisResult(
                risks=[], 
                strategy="无法生成策略",
                competitors=[],
                price_stats=PriceStatsModel(avg_discount="0%", max_discount="0%", distribution=[])
            )
        
        final_model = AiTenderAnalysisModel(
            score=intermediate.get('score', 0),
            summary=intermediate.get('summary', ''),
            requirements=intermediate.get('requirements', []),
            profitability=intermediate.get('profitability', 'N/A'),
            difficulty=intermediate.get('difficulty', '未知'),
            radar_data=intermediate.get('radar_data', []),
            features=intermediate.get('features', []),
            decision_conclusion=intermediate.get('decision_conclusion',''),
            focus_points=intermediate.get('focus_points', []),
            risks=result.risks,
            strategy=result.strategy,
            competitors=result.competitors,
            price_stats=result.price_stats
        )
        print("输出重点关注事项：" + str(final_model.focus_points))
        
        return {
            "progress": 90,
            "current_step": "建议生成中",
            "analysis_result": final_model
        }
