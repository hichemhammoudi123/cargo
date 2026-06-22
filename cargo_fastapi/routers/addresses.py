from fastapi import APIRouter
from schemas.address import AddressValidate
from services.address_service import AddressService

router = APIRouter()


@router.post("/addresses/validate")
def validate_address(body: AddressValidate):
    try:
        result = AddressService.validate_address(body.model_dump())
        return {"success": True, "data": result}
    except ValueError as e:
        return {"success": False, "error": {"code": "VALIDATION_ERROR", "message": str(e)}}
