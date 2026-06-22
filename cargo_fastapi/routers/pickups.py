from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.pickup import Pickup
from schemas.pickup import PickupCreate, PickupUpdate
from services.pickup_service import PickupService

router = APIRouter()


@router.get("/pickups")
def list_pickups(page: int = 1, limit: int = 20, db: Session = Depends(get_db)):
    query = db.query(Pickup).order_by(Pickup.created_at.desc())
    total = query.count()
    pickups = query.offset((page - 1) * limit).limit(limit).all()
    data = []
    for p in pickups:
        data.append({
            "id": p.id, "carrierCode": p.carrier_code, "status": p.status,
            "pickupDate": p.pickup_date.isoformat() if p.pickup_date else "",
            "confirmationNumber": p.confirmation_number,
            "createdAt": p.created_at.isoformat() if p.created_at else "",
        })
    return {"success": True, "data": data, "pagination": {"page": page, "limit": limit, "total": total}}


@router.post("/pickups")
def schedule_pickup(body: PickupCreate, db: Session = Depends(get_db)):
    try:
        pickup = PickupService.schedule_pickup(db, body.model_dump())
    except ValueError as e:
        return {"success": False, "error": {"code": "PICKUP_ERROR", "message": str(e)}}
    return {
        "success": True,
        "data": {
            "id": pickup.id, "carrierCode": pickup.carrier_code,
            "carrierPickupId": pickup.carrier_pickup_id, "status": pickup.status,
            "pickupDate": pickup.pickup_date.isoformat() if pickup.pickup_date else "",
            "confirmationNumber": pickup.confirmation_number,
        },
    }


@router.get("/pickups/{id}")
def pickup_detail(id: str, db: Session = Depends(get_db)):
    pickup = db.query(Pickup).filter(Pickup.id == id).first()
    if not pickup:
        return {"success": False, "error": {"code": "NOT_FOUND", "message": "Pickup not found"}}
    return {
        "success": True,
        "data": {
            "id": pickup.id, "carrierCode": pickup.carrier_code,
            "carrierPickupId": pickup.carrier_pickup_id, "status": pickup.status,
            "pickupDate": pickup.pickup_date.isoformat() if pickup.pickup_date else "",
            "readyTime": str(pickup.ready_time) if pickup.ready_time else "",
            "closeTime": str(pickup.close_time) if pickup.close_time else "",
            "totalPackages": pickup.total_packages,
            "totalWeight": float(pickup.total_weight) if pickup.total_weight else None,
            "weightUnit": pickup.weight_unit,
            "confirmationNumber": pickup.confirmation_number,
            "createdAt": pickup.created_at.isoformat() if pickup.created_at else "",
            "cancelledAt": pickup.cancelled_at.isoformat() if pickup.cancelled_at else None,
        },
    }


@router.put("/pickups/{id}")
def update_pickup(id: str, body: PickupUpdate, db: Session = Depends(get_db)):
    pickup = db.query(Pickup).filter(Pickup.id == id).first()
    if not pickup:
        return {"success": False, "error": {"code": "NOT_FOUND", "message": "Pickup not found"}}
    if pickup.status == "CANCELLED":
        return {"success": False, "error": {"code": "ALREADY_CANCELLED", "message": "Cannot update a cancelled pickup"}}
    data = body.model_dump(exclude_unset=True)
    if "pickupDate" in data:
        pickup.pickup_date = data["pickupDate"]
    if "readyTime" in data:
        pickup.ready_time = data["readyTime"]
    if "closeTime" in data:
        pickup.close_time = data["closeTime"]
    if "specialInstructions" in data:
        pickup.special_instructions = data["specialInstructions"]
    db.commit()
    return {
        "success": True,
        "data": {
            "id": pickup.id, "carrierCode": pickup.carrier_code,
            "carrierPickupId": pickup.carrier_pickup_id, "status": pickup.status,
            "pickupDate": pickup.pickup_date.isoformat() if pickup.pickup_date else "",
        },
    }


@router.delete("/pickups/{id}")
def delete_pickup(id: str, db: Session = Depends(get_db)):
    pickup = db.query(Pickup).filter(Pickup.id == id).first()
    if not pickup:
        return {"success": False, "error": {"code": "NOT_FOUND", "message": "Pickup not found"}}
    if pickup.status == "CANCELLED":
        return {"success": False, "error": {"code": "ALREADY_CANCELLED", "message": "Pickup is already cancelled"}}
    try:
        pickup = PickupService.cancel_pickup(db, id)
    except ValueError as e:
        return {"success": False, "error": {"code": "CANCEL_ERROR", "message": str(e)}}
    return {
        "success": True,
        "data": {
            "id": pickup.id, "status": pickup.status,
            "cancelledAt": pickup.cancelled_at.isoformat() if pickup.cancelled_at else None,
        },
    }


@router.post("/pickups/{id}/cancel")
def cancel_pickup(id: str, db: Session = Depends(get_db)):
    pickup = db.query(Pickup).filter(Pickup.id == id).first()
    if not pickup:
        return {"success": False, "error": {"code": "NOT_FOUND", "message": "Pickup not found"}}
    try:
        pickup = PickupService.cancel_pickup(db, id)
    except ValueError as e:
        return {"success": False, "error": {"code": "CANCEL_ERROR", "message": str(e)}}
    return {
        "success": True,
        "data": {
            "id": pickup.id, "status": pickup.status,
            "cancelledAt": pickup.cancelled_at.isoformat() if pickup.cancelled_at else None,
        },
    }
