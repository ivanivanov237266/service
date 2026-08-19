from fastapi import APIRouter, HTTPException
from api.schemas import SummarizeRequest, SummarizeResponse
from services.summarization import SummarizationService
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
service = SummarizationService()

@router.post("/summarize", response_model=SummarizeResponse)
async def summarize(request: SummarizeRequest):
    logger.info(f"Received summarization request, text length={len(request.text)}")
    try:
        result = service.process(request.text)
        return result
    except Exception as e:
        logger.exception(f"Internal error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")