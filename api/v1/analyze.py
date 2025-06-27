from fastapi import APIRouter, HTTPException
from models.analysis import SynthesisRequest, SynthesisResult
from services.analyzer import run_synthesis_analysis

router = APIRouter()

@router.post("/synthesize", response_model=SynthesisResult)
async def synthesis_analysis_endpoint(request: SynthesisRequest):
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="Text input cannot be empty")
    
    result = await run_synthesis_analysis(request.text, request.lenses)
    return result
