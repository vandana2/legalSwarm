from fastapi import APIRouter, UploadFile, File, HTTPException
from services.pdf_parser import PDFParser
import os

router = APIRouter(prefix="/api/upload", tags=["upload"])

@router.post("/contract")
async def upload_contract(file: UploadFile = File(...)):
    """
    Upload a contract PDF for analysis
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")
    
    try:
        # Save uploaded file
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, file.filename)
        
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())
        
        # Parse PDF
        parser = PDFParser(file_path)
        text = parser.extract_text()
        chunks = parser.chunk_text(text)
        
        return {
            "filename": file.filename,
            "path": file_path,
            "text_length": len(text),
            "chunks_count": len(chunks),
            "status": "uploaded"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
