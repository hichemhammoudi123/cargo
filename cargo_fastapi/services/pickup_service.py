from datetime import datetime, date
from sqlalchemy.orm import Session
from models.pickup import Pickup
from models.carrier import Carrier
from models.address import Address as AddressModel
from services.adapters.registry import registry
from services.adapters.base import PickupRequest, AddressData


class PickupService:

    @staticmethod
    def schedule_pickup(db: Session, data: dict) -> Pickup:
        carrier_code = data["carrierCode"]
        adapter = registry.get_or_raise(carrier_code)
        loc = data.get("location", {})

        address = AddressModel(
            company=loc.get("company", ""),
            contact_name=loc.get("contactName", ""),
            phone=loc.get("phone", ""),
            country=loc.get("country", ""),
            zip_code=loc.get("zipCode", ""),
            city=loc.get("city", ""),
            address=loc.get("address", ""),
        )
        db.add(address)
        db.flush()

        req = PickupRequest(
            carrier_code=carrier_code,
            shipment_ids=data.get("shipmentIds", []),
            pickup_date=str(data.get("pickupDate", "")),
            ready_time=str(data.get("readyTime", "")),
            close_time=str(data.get("closeTime", "")),
            location=AddressData(
                company=loc.get("company", ""),
                contact_name=loc.get("contactName", ""),
                phone=loc.get("phone", ""),
                country=loc.get("country", ""),
                zip_code=loc.get("zipCode", ""),
                city=loc.get("city", ""),
                address=loc.get("address", ""),
            ),
            total_packages=data.get("totalPackages", 1),
            total_weight=data.get("totalWeight"),
            weight_unit=data.get("weightUnit", "KG"),
            special_instructions=data.get("specialInstructions", ""),
        )

        resp = adapter.schedule_pickup(req)

        from datetime import time as time_type
        pickup = Pickup(
            carrier_code=carrier_code,
            carrier_pickup_id=resp.carrier_pickup_id,
            status="CONFIRMED",
            pickup_date=data["pickupDate"],
            ready_time=data["readyTime"],
            close_time=data["closeTime"],
            location_id=address.id,
            total_packages=data.get("totalPackages", 1),
            total_weight=data.get("totalWeight"),
            weight_unit=data.get("weightUnit", "KG"),
            special_instructions=data.get("specialInstructions", ""),
            confirmation_number=resp.confirmation_number,
        )
        db.add(pickup)
        db.commit()
        db.refresh(pickup)
        return pickup

    @staticmethod
    def cancel_pickup(db: Session, pickup_id: str) -> Pickup:
        pickup = db.query(Pickup).filter(Pickup.id == pickup_id).first()
        if not pickup:
            raise ValueError("Pickup not found")
        if pickup.status == "CANCELLED":
            raise ValueError("Pickup is already cancelled")
        adapter = registry.get(pickup.carrier_code)
        if adapter and pickup.carrier_pickup_id:
            adapter.cancel_pickup(pickup.carrier_pickup_id)
        pickup.status = "CANCELLED"
        pickup.cancelled_at = datetime.utcnow()
        db.commit()
        db.refresh(pickup)
        return pickup
