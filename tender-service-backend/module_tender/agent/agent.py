from langgraph.graph import StateGraph, END
from module_tender.agent.state.state import AgentState
from module_tender.agent.nodes.fetch_node import FetchNode
from module_tender.agent.nodes.parse_node import ParseNode
from module_tender.agent.nodes.analyze_node import AnalyzeNode
from module_tender.agent.nodes.strategy_node import StrategyNode

class TenderAgent:
    def __init__(self):
        self.workflow = StateGraph(AgentState)
        
        self.workflow.add_node("fetch", FetchNode())
        self.workflow.add_node("parse", ParseNode())
        self.workflow.add_node("analyze", AnalyzeNode())
        self.workflow.add_node("strategy", StrategyNode())
        
        self.workflow.set_entry_point("fetch")
        
        self.workflow.add_edge("fetch", "parse")
        self.workflow.add_edge("parse", "analyze")
        self.workflow.add_edge("analyze", "strategy")
        self.workflow.add_edge("strategy", END)
        
        self.app = self.workflow.compile()
        
    async def run(self, tender_id: int, db_session, qualifications: list[str] | None = None):
        initial_state = AgentState(
            tender_id=tender_id,
            db_session=db_session,
            progress=0,
            current_step="开始分析",
            tender_data={},
            project_text="",
            analysis_result=None,
            error=None,
            intermediate_data={},
            qualifications=qualifications or [],
        )

        last_state: AgentState | None = initial_state

        async for event in self.app.astream(initial_state):
            for node, state in event.items():
                merged = {**last_state, **state}  # type: ignore[arg-type]
                last_state = merged  # type: ignore[assignment]
                yield merged

        if last_state is not None:
            final = dict(last_state)
            final["progress"] = max(final.get("progress", 0), 100)
            final["current_step"] = final.get("current_step") or "分析完成"
            yield final

# Singleton instance
tender_agent = TenderAgent()
