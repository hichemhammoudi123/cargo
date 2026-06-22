from fastapi import APIRouter
from schemas.rate import RateRequest
from services.rate_service import RateService

router = APIRouter()


@router.post("/rates")
def compare_rates(body: RateRequest):
    result = RateService.get_rates(body.model_dump())
    return {"success": True, "data": result["data"], "errors": result["errors"]}
