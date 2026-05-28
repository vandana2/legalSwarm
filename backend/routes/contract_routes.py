"""
Backend API Routes for Contract Analysis using CrewAI Orchestration
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Any
import os
import tempfile

from services.pdf_parser import PDFParser
from services.crew_orchestrator import run_contract_analysis

router = APIRouter(prefix="/api/contracts", tags=["contracts"])


@router.post("/analyze")
async def analyze_contract(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Upload and analyze a contract using the full CrewAI agent swarm
    
    Flow:
    1. Extract text from PDF
    2. Parser Agent - Structure clauses
    3. Risk Detector - Identify risks
    4. Explainer - Translate to plain English
    5. Redline - Suggest alternatives
    6. Compliance - Check laws
    7. Verdict Agent - Final score & recommendation
    
    Args:
        file: PDF contract file
    
    Returns:
        Complete analysis with all agent outputs
    """
    
    try:
        # Validate file
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            contents = await file.read()
            temp_file.write(contents)
            temp_file_path = temp_file.name
        
        try:
            # Extract text from PDF
            pdf_parser = PDFParser(temp_file_path)
            contract_text = pdf_parser.extract_text()
            
            if not contract_text:
                raise HTTPException(status_code=400, detail="Could not extract text from PDF")
            
            # Run CrewAI analysis
            analysis_result = run_contract_analysis(contract_text)
            
            # Return results
            return {
                'status': 'success',
                'filename': file.filename,
                'file_size': len(contents),
                'analysis': analysis_result
            }
            
        finally:
            # Clean up temp file
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/analyze-text")
async def analyze_contract_text(contract_data: Dict[str, str]) -> Dict[str, Any]:
    """
    Analyze contract provided as raw text (for testing)
    
    Args:
        contract_data: {"text": "contract text here"}
    
    Returns:
        Complete analysis with all agent outputs
    """
    
    try:
        contract_text = contract_data.get('text', '').strip()
        
        if not contract_text:
            raise HTTPException(status_code=400, detail="Contract text is required")
        
        # Run CrewAI analysis
        analysis_result = run_contract_analysis(contract_text)
        
        return {
            'status': 'success',
            'text_length': len(contract_text),
            'analysis': analysis_result
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint"""
    return {
        'status': 'healthy',
        'service': 'Contract Analysis API',
        'agents_available': [
            'Parser Agent',
            'Risk Detector Agent',
            'Explainer Agent',
            'Redline Agent',
            'Compliance Agent',
            'Verdict Agent (CrewAI)'
        ]
    }


@router.get("/analysis/{analysis_id}")
async def get_analysis(analysis_id: str) -> Dict[str, Any]:
    """Retrieve saved analysis results (when database integration added)"""
    # TODO: Implement database storage and retrieval
    return {
        'status': 'not_implemented',
        'message': 'Database integration coming soon'
    }
