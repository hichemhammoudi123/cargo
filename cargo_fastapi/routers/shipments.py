from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.shipment import Shipment, Package
from models.address import Address as AddressModel
from schemas.shipment import ShipmentCreate, ShipmentUpdate, ShipmentLabelRequest
from services.shipment_service import ShipmentService
from datetime import datetime

router = APIRouter()


@router.get("/shipments")
def list_shipments(
    status: str = "",
    carrier: str = "",
    from_date: str = "",
    to_date: str = "",
    q: str = "",
    page: int = 1,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    query = db.query(Shipment)
    if status:
        query = query.filter(Shipment.internal_status == status.upper())
    if carrier:
        query = query.filter(Shipment.carrier_code == carrier.upper())
    if from_date:
        query = query.filter(Shipment.created_at >= from_date)
    if to_date:
        query = query.filter(Shipment.created_at <= to_date)
    if q:
        query = query.filter(Shipment.reference.ilike(f"%{q}%"))
    total = query.count()
    shipments = query.order_by(Shipment.created_at.desc()).offset((page - 1) * limit).limit(limit).all()
    data = []
    for s in shipments:
        recip = {}
        if s.recipient:
            recip = {"company": s.recipient.company, "country": s.recipient.country}
        data.append({
            "id": s.id, "internalStatus": s.internal_status, "carrierStatus": s.carrier_status,
            "carrierCode": s.carrier_code, "carrierTrackingNumber": s.carrier_tracking_number,
            "reference": s.reference, "recipient": recip,
            "createdAt": s.created_at.isoformat() if s.created_at else "",
        })
    return {"success": True, "data": data, "pagination": {"page": page, "limit": limit, "total": total}}


@router.post("/shipments")
def create_shipment(body: ShipmentCreate, db: Session = Depends(get_db)):
    try:
        shipment = ShipmentService.create_shipment(db, body.model_dump())
    except ValueError as e:
        return {"success": False, "error": {"code": "VALIDATION_ERROR", "message": str(e)}}
    return _shipment_detail_response(shipment, db)


@router.get("/shipments/{id}")
def shipment_detail(id: str, db: Session = Depends(get_db)):
    shipment = db.query(Shipment).filter(Shipment.id == id).first()
    if not shipment:
        return {"success": False, "error": {"code": "NOT_FOUND", "message": "Shipment not found"}}
    return _shipment_detail_response(shipment, db)


@router.put("/shipments/{id}")
def update_shipment(id: str, body: ShipmentUpdate, db: Session = Depends(get_db)):
    shipment = db.query(Shipment).filter(Shipment.id == id).first()
    if not shipment:
        return {"success": False, "error": {"code": "NOT_FOUND", "message": "Shipment not found"}}
    if shipment.status != "SUBMITTED":
        return {"success": False, "error": {"code": "INVALID_STATUS", "message": "Can only update shipments in SUBMITTED status"}}
    data = body.model_dump(exclude_unset=True)
    if data.get("reference"):
        shipment.reference = data["reference"]
    if data.get("options"):
        opts = data["options"]
        if "signatureRequired" in opts:
            shipment.signature_required = opts["signatureRequired"]
    db.commit()
    return {
        "success": True,
        "data": {"id": shipment.id, "reference": shipment.reference, "updatedAt": datetime.utcnow().isoformat()},
    }


@router.delete("/shipments/{id}")
def delete_shipment(id: str, db: Session = Depends(get_db)):
    shipment = db.query(Shipment).filter(Shipment.id == id).first()
    if not shipment:
        return {"success": False, "error": {"code": "NOT_FOUND", "message": "Shipment not found"}}
    if shipment.status not in ("SUBMITTED", "DRAFT"):
        return {"success": False, "error": {"code": "INVALID_STATUS", "message": "Can only delete shipments in DRAFT or SUBMITTED status"}}
    db.delete(shipment)
    db.commit()
    return {"success": True, "data": {"deleted": True}}


@router.post("/shipments/{id}/cancel")
def cancel_shipment(id: str, db: Session = Depends(get_db)):
    shipment = db.query(Shipment).filter(Shipment.id == id).first()
    if not shipment:
        return {"success": False, "error": {"code": "NOT_FOUND", "message": "Shipment not found"}}
    if shipment.status == "DELIVERED":
        return {"success": False, "error": {"code": "ALREADY_DELIVERED", "message": "Cannot cancel a delivered shipment"}}
    if shipment.status == "CANCELLED":
        return {"success": False, "error": {"code": "ALREADY_CANCELLED", "message": "Shipment is already cancelled"}}
    try:
        shipment = ShipmentService.cancel_shipment(db, id)
    except ValueError as e:
        return {"success": False, "error": {"code": "CANCEL_FAILED", "message": str(e)}}
    return {
        "success": True,
        "data": {
            "id": shipment.id, "internalStatus": shipment.internal_status,
            "carrierStatus": shipment.carrier_status,
            "cancelledAt": shipment.cancelled_at.isoformat() if shipment.cancelled_at else None,
        },
    }


@router.post("/shipments/{id}/label")
def generate_label(id: str, body: ShipmentLabelRequest, db: Session = Depends(get_db)):
    shipment = db.query(Shipment).filter(Shipment.id == id).first()
    if not shipment:
        return {"success": False, "error": {"code": "NOT_FOUND", "message": "Shipment not found"}}
    from services.adapters.registry import registry
    adapter = registry.get(shipment.carrier_code)
    label = adapter.get_label(shipment.carrier_tracking_number, body.format) if adapter else {}
    return {
        "success": True,
        "data": {
            "labelUrl": label.get("labelUrl", ""),
            "format": label.get("format", body.format),
            "size": label.get("size", "A6"),
            "generatedAt": datetime.utcnow().isoformat(),
        },
    }


def _shipment_detail_response(shipment: Shipment, db: Session = None) -> dict:
    packages = [
        {"reference": p.reference, "weight": float(p.weight), "trackingNumber": p.tracking_number}
        for p in (shipment.packages or [])
    ]
    price = None
    if shipment.price_total is not None:
        price = {"total": float(shipment.price_total), "currency": shipment.price_currency, "breakdown": shipment.price_breakdown or []}
    sender = {}
    if shipment.sender:
        sender = {"company": shipment.sender.company, "country": shipment.sender.country, "zipCode": shipment.sender.zip_code}
    recipient = {}
    if shipment.recipient:
        recipient = {"company": shipment.recipient.company, "country": shipment.recipient.country, "zipCode": shipment.recipient.zip_code}
    from models.carrier import Carrier
    carrier = shipment.carrier
    if not carrier and db:
        carrier = db.query(Carrier).filter(Carrier.code == shipment.carrier_code).first()
    return {
        "success": True,
        "data": {
            "id": shipment.id, "internalStatus": shipment.internal_status,
            "carrierStatus": shipment.carrier_status,
            "statusHistory": [],
            "carrierCode": shipment.carrier_code,
            "carrierName": carrier.name if carrier else "",
            "carrierTrackingNumber": shipment.carrier_tracking_number,
            "carrierShipmentId": shipment.carrier_shipment_id,
            "labelUrl": shipment.label_url, "labelFormat": shipment.label_format,
            "trackingUrl": shipment.tracking_url, "reference": shipment.reference,
            "price": price, "sender": sender, "recipient": recipient,
            "packages": packages,
            "createdAt": shipment.created_at.isoformat() if shipment.created_at else "",
            "estimatedDeliveryDate": shipment.estimated_delivery_date.isoformat() if shipment.estimated_delivery_date else None,
        },
    }
