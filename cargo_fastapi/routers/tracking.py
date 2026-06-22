from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.shipment import Shipment
from services.tracking_service import TrackingService
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/shipments/{id}/tracking")
def get_tracking(id: str, db: Session = Depends(get_db)):
    shipment = db.query(Shipment).filter(Shipment.id == id).first()
    if not shipment:
        return {"success": False, "error": {"code": "NOT_FOUND", "message": "Shipment not found"}}
    try:
        tracking_data = TrackingService.get_tracking(db, id)
        return {"success": True, "data": tracking_data}
    except Exception as e:
        return {"success": False, "error": {"code": "TRACKING_ERROR", "message": str(e)}}


@router.post("/webhooks/{carrier_code}")
def webhook_receive(carrier_code: str, raw_body: dict, db: Session = Depends(get_db)):
    carrier_code = carrier_code.upper()
    try:
        result = TrackingService.process_webhook(db, carrier_code, raw_body)
        logger.info(f"Webhook processed: {carrier_code} -> {result.get('internalStatus')}")
    except Exception as e:
        logger.error(f"Webhook processing error for {carrier_code}: {e}")
    return {"success": True, "message": "Webhook processed successfully"}
