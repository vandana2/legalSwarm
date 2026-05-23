from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.agent_service import AgentService

router = APIRouter(prefix="/api/analyze", tags=["analyze"])

class AnalysisRequest(BaseModel):
    contract_path: str
    contract_text: str

@router.post("/contract")
async def analyze_contract(request: AnalysisRequest):
    """
    Analyze contract using AI agent swarm
    """
    try:
        agent_service = AgentService()
        result = await agent_service.analyze(request.contract_text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{contract_id}")
async def get_analysis_status(contract_id: str):
    """
    Get analysis status for a contract
    """
    return {"contract_id": contract_id, "status": "analyzing"}
