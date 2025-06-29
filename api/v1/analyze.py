from fastapi import APIRouter, HTTPException, Header, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from models.analysis import SynthesisRequest, SynthesisResult
from services.analyzer import run_synthesis_analysis
from core import config
from typing import Optional

router = APIRouter()
# Don't auto-error so we can handle it ourselves
security = HTTPBearer(auto_error=False)


def verify_api_key(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> bool:
    """
    Verify API key for protected endpoints.
    Only required when USE_DUMMY_DATA is False and API_KEY is set.
    """
    if config.USE_DUMMY_DATA:
        # No API key required when using dummy data
        return True

    if not config.API_KEY:
        # No API key configured, allow access
        return True

    if not credentials or credentials.credentials != config.API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key. Contact the administrator for access."
        )
    return True


@router.get("/config")
async def get_config():
    """Get frontend configuration."""
    return {
        "use_dummy_data": config.USE_DUMMY_DATA,
        "requires_api_key": bool(config.API_KEY and not config.USE_DUMMY_DATA),
        "demo_mode_enabled": config.USE_DUMMY_DATA
    }


@router.post("/synthesize", response_model=SynthesisResult)
async def synthesis_analysis_endpoint(
    request: SynthesisRequest,
    api_key_valid: bool = Depends(verify_api_key)
):
    """
    Perform synthesis analysis on the provided text.

    - If USE_DUMMY_DATA=True: Returns dummy data without API key requirements
    - If USE_DUMMY_DATA=False and API_KEY is set: Requires valid API key
    """
    if not request.text or not request.text.strip():
        raise HTTPException(
            status_code=400, detail="Text input cannot be empty")

    result = await run_synthesis_analysis(request.text)
    return result
