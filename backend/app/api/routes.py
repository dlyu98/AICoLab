"""FastAPI routes for health agent endpoints."""
from fastapi import APIRouter

from app.agent.service import HealthAgentService
from app.models.schemas import ApiResponse, HealthRequest

router = APIRouter()
service = HealthAgentService()


@router.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/v1/agent/respond", response_model=ApiResponse)
async def respond(request: HealthRequest) -> ApiResponse:
    response, raw = await service.handle(request)
    return ApiResponse(session_id=request.session_id, response=response, raw_model_output=raw)
