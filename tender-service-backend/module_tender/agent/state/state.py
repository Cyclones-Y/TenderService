from typing import TypedDict, Optional, Any
from module_tender.entity.vo.tender_vo import AiTenderAnalysisModel

class AgentState(TypedDict):
    tender_id: int
    tender_data: dict
    project_text: str
    analysis_result: Optional[AiTenderAnalysisModel]
    progress: int
    current_step: str
    error: Optional[str]
    intermediate_data: Optional[dict]
    db_session: Any
