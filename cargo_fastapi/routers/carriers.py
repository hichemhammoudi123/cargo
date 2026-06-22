from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.carrier import Carrier, CarrierService, CarrierCapability
from schemas.carrier import (
    CarrierList, CarrierDetail, CarrierAdd, CarrierUpdate, CarrierToggle,
    CredentialsUpdate, CarrierServiceAdd, CarrierServiceOut, CarrierCapabilityOut,
)
from services.carrier_service import CarrierServiceLogic
from typing import Optional
from datetime import datetime

router = APIRouter()


@router.get("/carriers")
def list_carriers(db: Session = Depends(get_db)):
    carriers = db.query(Carrier).all()
    data = []
    for c in carriers:
        services_list = [
            CarrierServiceOut(
                code=s.code, name=s.name, description=s.description,
                maxWeight=float(s.max_weight) if s.max_weight else None,
                maxWeightUnit=s.max_weight_unit, zones=s.zones or [],
                transitDays=s.transit_days, features=s.features or [], active=s.active,
            )
            for s in c.services
        ] if c.services else []
        data.append(CarrierList(
            code=c.code, name=c.name, adapterName=c.adapter_name,
            active=c.active, status=c.status, services=services_list,
        ).model_dump())
    return {"success": True, "data": data, "pagination": {"page": 1, "limit": len(data), "total": len(data)}}


@router.post("/carriers")
def add_carrier(body: CarrierAdd, db: Session = Depends(get_db)):
    existing = db.query(Carrier).filter(Carrier.code == body.code.upper()).first()
    if existing:
        return {"success": False, "error": {"code": "DUPLICATE", "message": "Carrier already exists"}}
    carrier = Carrier(
        code=body.code.upper(),
        name=body.name,
        adapter_name=body.adapterName or body.code.lower().capitalize(),
        active=body.active,
        status="PENDING_TEST",
        website=body.website,
    )
    db.add(carrier)
    db.commit()
    return {"success": True, "data": {"code": carrier.code, "name": carrier.name, "active": carrier.active}}


@router.get("/carriers/{code}")
def carrier_detail(code: str, db: Session = Depends(get_db)):
    carrier = db.query(Carrier).filter(Carrier.code == code.upper()).first()
    if not carrier:
        return {"success": False, "error": {"code": "NOT_FOUND", "message": "Carrier not found"}}
    services_list = [
        CarrierServiceOut(
            code=s.code, name=s.name, description=s.description,
            maxWeight=float(s.max_weight) if s.max_weight else None,
            maxWeightUnit=s.max_weight_unit, zones=s.zones or [],
            transitDays=s.transit_days, features=s.features or [], active=s.active,
        ).model_dump()
        for s in (carrier.services or [])
    ]
    caps = None
    if carrier.capabilities:
        caps = CarrierCapabilityOut(
            labelFormats=carrier.capabilities.label_formats or [],
            features=carrier.capabilities.features or [],
        ).model_dump()
    settings = {
        "timeoutMs": carrier.timeout_ms,
        "retryMaxAttempts": carrier.retry_max_attempts,
        "retryDelayMs": carrier.retry_delay_ms,
        "rateLimitPerMin": carrier.rate_limit_per_min,
    }
    return {"success": True, "data": {
        "code": carrier.code, "name": carrier.name,
        "adapterName": carrier.adapter_name, "active": carrier.active,
        "status": carrier.status,
        "lastTestedAt": carrier.last_tested_at.isoformat() if carrier.last_tested_at else None,
        "services": services_list, "capabilities": caps,
        "settings": settings,
        "credentialsUpdatedAt": carrier.credentials_updated_at.isoformat() if carrier.credentials_updated_at else None,
    }}


@router.put("/carriers/{code}")
def update_carrier(code: str, body: CarrierUpdate, db: Session = Depends(get_db)):
    carrier = db.query(Carrier).filter(Carrier.code == code.upper()).first()
    if not carrier:
        return {"success": False, "error": {"code": "NOT_FOUND", "message": "Carrier not found"}}
    if body.active is not None:
        carrier.active = body.active
    if body.settings:
        if "timeoutMs" in body.settings:
            carrier.timeout_ms = body.settings["timeoutMs"]
        if "retryMaxAttempts" in body.settings:
            carrier.retry_max_attempts = body.settings["retryMaxAttempts"]
    db.commit()
    return {"success": True, "data": {"code": carrier.code, "active": carrier.active}}


@router.delete("/carriers/{code}")
def delete_carrier(code: str, db: Session = Depends(get_db)):
    carrier = db.query(Carrier).filter(Carrier.code == code.upper()).first()
    if not carrier:
        return {"success": False, "error": {"code": "NOT_FOUND", "message": "Carrier not found"}}
    db.delete(carrier)
    db.commit()
    return {"success": True, "data": {"deleted": True}}


@router.patch("/carriers/{code}/toggle")
def toggle_carrier(code: str, body: CarrierToggle, db: Session = Depends(get_db)):
    carrier = db.query(Carrier).filter(Carrier.code == code.upper()).first()
    if not carrier:
        return {"success": False, "error": {"code": "NOT_FOUND", "message": "Carrier not found"}}
    carrier.active = body.active
    db.commit()
    return {
        "success": True,
        "data": {
            "code": carrier.code,
            "active": carrier.active,
            "deactivatedAt": None if carrier.active else datetime.utcnow().isoformat(),
        },
    }


@router.get("/carriers/{code}/services")
def get_carrier_services(code: str, db: Session = Depends(get_db)):
    carrier = db.query(Carrier).filter(Carrier.code == code.upper()).first()
    if not carrier:
        return {"success": False, "error": {"code": "NOT_FOUND", "message": "Carrier not found"}}
    services_list = [
        CarrierServiceOut(
            code=s.code, name=s.name, description=s.description,
            maxWeight=float(s.max_weight) if s.max_weight else None,
            maxWeightUnit=s.max_weight_unit, zones=s.zones or [],
            transitDays=s.transit_days, features=s.features or [], active=s.active,
        ).model_dump()
        for s in (carrier.services or [])
    ]
    return {"success": True, "data": services_list}


@router.get("/carriers/{code}/capabilities")
def get_carrier_capabilities(code: str, db: Session = Depends(get_db)):
    carrier = db.query(Carrier).filter(Carrier.code == code.upper()).first()
    if not carrier:
        return {"success": False, "error": {"code": "NOT_FOUND", "message": "Carrier not found"}}
    caps = None
    if carrier.capabilities:
        caps = CarrierCapabilityOut(
            labelFormats=carrier.capabilities.label_formats or [],
            features=carrier.capabilities.features or [],
        ).model_dump()
    return {"success": True, "data": caps or {"labelFormats": [], "features": []}}


@router.post("/carriers/{code}/test")
def test_carrier(code: str, db: Session = Depends(get_db)):
    carrier = db.query(Carrier).filter(Carrier.code == code.upper()).first()
    if not carrier:
        return {"success": False, "error": {"code": "NOT_FOUND", "message": "Carrier not found"}}
    try:
        result = CarrierServiceLogic.test_connection(code.upper())
        carrier.status = result.status
        carrier.last_tested_at = datetime.utcnow()
        db.commit()
        return {
            "success": True,
            "data": {
                "status": result.status, "latencyMs": result.latency_ms,
                "testedAt": carrier.last_tested_at.isoformat(),
                "endpoint": result.endpoint,
                "details": {"httpStatus": result.http_status, "message": result.message, "accountValid": result.account_valid},
            },
        }
    except Exception as e:
        return {"success": False, "error": {"code": "CARRIER_CONNECTION_FAILED", "message": str(e)}}


@router.put("/carriers/{code}/credentials")
def update_credentials(code: str, body: CredentialsUpdate, db: Session = Depends(get_db)):
    carrier = db.query(Carrier).filter(Carrier.code == code.upper()).first()
    if not carrier:
        return {"success": False, "error": {"code": "NOT_FOUND", "message": "Carrier not found"}}
    if body.authType:
        carrier.auth_type = body.authType
    if body.apiKey:
        carrier.api_key_enc = body.apiKey
    if body.apiSecret:
        carrier.api_secret_enc = body.apiSecret
    if body.webhookSecret:
        carrier.webhook_secret_enc = body.webhookSecret
    carrier.credentials_updated_at = datetime.utcnow()
    db.commit()
    return {"success": True, "data": {"code": carrier.code, "credentialsUpdatedAt": carrier.credentials_updated_at.isoformat()}}


@router.post("/carriers/{code}/services")
def add_carrier_service(code: str, body: CarrierServiceAdd, db: Session = Depends(get_db)):
    carrier = db.query(Carrier).filter(Carrier.code == code.upper()).first()
    if not carrier:
        return {"success": False, "error": {"code": "NOT_FOUND", "message": "Carrier not found"}}
    svc, created = db.query(CarrierService).filter(
        CarrierService.carrier_code == code.upper(),
        CarrierService.code == body.code,
    ).first(), None
    if svc:
        for key, val in body.model_dump(exclude={"code"}).items():
            setattr(svc, key, val)
    else:
        svc = CarrierService(carrier_code=code.upper(), code=body.code, name=body.name)
        db.add(svc)
    db.commit()
    return {"success": True, "data": {"code": svc.code, "name": svc.name, "active": svc.active}}
