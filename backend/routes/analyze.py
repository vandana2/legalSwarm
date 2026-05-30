"""
Text-based analysis route.

Accepts raw contract text (no PDF) and delegates to the same orchestration
pipeline used by the PDF route in contract_routes.py.  Both routes share one
implementation path through run_contract_analysis().
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.crew_orchestrator import run_contract_analysis

router = APIRouter(prefix="/api/analyze", tags=["analyze"])


class TextAnalysisRequest(BaseModel):
    contract_text: str


@router.post("/contract")
async def analyze_contract_text(request: TextAnalysisRequest):
    """
    Analyze contract provided as raw text.
    Returns the same response shape as POST /api/contracts/analyze.
    """
    text = request.contract_text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="contract_text must not be empty")

    try:
        result = run_contract_analysis(text)
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/status/{contract_id}")
async def get_analysis_status(contract_id: str):
    """Placeholder – will return job state once async storage is added."""
    return {"contract_id": contract_id, "status": "synchronous_analysis_only"}

