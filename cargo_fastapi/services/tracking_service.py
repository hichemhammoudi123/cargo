from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from models.shipment import Shipment
from models.tracking import TrackingEvent
from services.status_map import StatusMapperEngine
from services.adapters.registry import registry


class TrackingService:

    @staticmethod
    def get_tracking(db: Session, shipment_id: str) -> dict:
        shipment = db.query(Shipment).filter(Shipment.id == shipment_id).first()
        if not shipment:
            raise ValueError("Shipment not found")

        adapter = registry.get(shipment.carrier_code)
        events_list = []
        current_status = "PENDING"
        current_label = "Pending"

        if adapter and shipment.carrier_tracking_number:
            result = adapter.get_tracking(shipment.carrier_tracking_number)
            current_status = StatusMapperEngine.map(shipment.carrier_code, result.current_status)
            for evt in result.events:
                mapped = StatusMapperEngine.map(shipment.carrier_code, evt.status)
                events_list.append({
                    "status": evt.status,
                    "mapped": mapped,
                    "timestamp": evt.timestamp,
                    "location": evt.location,
                })

        db_events = db.query(TrackingEvent).filter(
            TrackingEvent.shipment_id == shipment_id
        ).order_by(TrackingEvent.timestamp.asc()).all()

        for evt in db_events:
            events_list.append({
                "eventId": evt.id,
                "internalCode": evt.internal_code,
                "carrierCode": evt.carrier_code,
                "carrierRawStatus": evt.carrier_raw_status,
                "label": evt.label,
                "location": evt.location,
                "timestamp": evt.timestamp.isoformat() if evt.timestamp else "",
            })

        return {
            "shipmentId": shipment.id,
            "carrierCode": shipment.carrier_code,
            "carrierTrackingNumber": shipment.carrier_tracking_number,
            "currentStatus": {
                "internalCode": shipment.internal_status or current_status,
                "carrierCode": shipment.carrier_code,
                "carrierRawStatus": shipment.carrier_status or "",
                "label": current_label,
                "timestamp": datetime.utcnow().isoformat(),
            },
            "estimatedDeliveryDate": shipment.estimated_delivery_date.isoformat() if shipment.estimated_delivery_date else None,
            "events": events_list,
        }

    @staticmethod
    def process_webhook(db: Session, carrier_code: str, raw_body: dict) -> dict:
        adapter = registry.get_or_raise(carrier_code)
        parsed = adapter.parse_webhook(raw_body)
        mapped_status = StatusMapperEngine.map(carrier_code, parsed.carrier_raw_status)

        from models.tracking import TrackingEvent as TrackingEventModel
        tracking_no = parsed.tracking_no
        shipment = db.query(Shipment).filter(
            Shipment.carrier_tracking_number == tracking_no
        ).first()

        if not shipment:
            raise ValueError(f"No shipment found with tracking number {tracking_no}")

        shipment.internal_status = mapped_status
        shipment.carrier_status = parsed.carrier_raw_status

        if mapped_status == "DELIVERED":
            shipment.status = "DELIVERED"
        elif mapped_status == "CANCELLED":
            shipment.status = "CANCELLED"
        elif mapped_status == "PICKED_UP":
            shipment.status = "PICKED_UP"

        try:
            ts = datetime.fromisoformat(parsed.timestamp.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            ts = datetime.utcnow()

        event = TrackingEventModel(
            shipment_id=shipment.id,
            internal_code=mapped_status,
            carrier_code=carrier_code,
            carrier_raw_status=parsed.carrier_raw_status,
            label=mapped_status.replace("_", " ").title(),
            location="",
            timestamp=ts,
        )
        db.add(event)
        db.commit()

        return {"internalStatus": mapped_status, "carrierRawStatus": parsed.carrier_raw_status}
