from datetime import datetime
from ..models import Pickup, Address, Shipment, ShipmentStatus
from .adapters.registry import registry
from .adapters.base import PickupRequest, AddressData


class PickupService:

    @staticmethod
    def schedule_pickup(data: dict) -> Pickup:
        carrier_code = data['carrierCode']
        adapter = registry.get_or_raise(carrier_code)

        loc = data.get('location', {})
        address = Address.objects.create(
            company=loc.get('company', ''),
            contact_name=loc.get('contactName', ''),
            phone=loc.get('phone', ''),
            country=loc.get('country', ''),
            zip_code=loc.get('zipCode', ''),
            city=loc.get('city', ''),
            address=loc.get('address', ''),
        )

        request = PickupRequest(
            carrier_code=carrier_code,
            shipment_ids=data.get('shipmentIds', []),
            pickup_date=data.get('pickupDate', ''),
            ready_time=data.get('readyTime', ''),
            close_time=data.get('closeTime', ''),
            location=AddressData(**loc),
            total_packages=data.get('totalPackages', 1),
            total_weight=data.get('totalWeight'),
            weight_unit=data.get('weightUnit', 'KG'),
            special_instructions=data.get('specialInstructions', ''),
        )

        response = adapter.schedule_pickup(request)

        pickup = Pickup.objects.create(
            carrier_id=carrier_code,
            carrier_pickup_id=response.carrier_pickup_id,
            status='CONFIRMED',
            pickup_date=data['pickupDate'],
            ready_time=data['readyTime'],
            close_time=data['closeTime'],
            location=address,
            total_packages=data.get('totalPackages', 1),
            total_weight=data.get('totalWeight'),
            weight_unit=data.get('weightUnit', 'KG'),
            special_instructions=data.get('specialInstructions', ''),
            confirmation_number=response.confirmation_number,
        )

        for sid in data.get('shipmentIds', []):
            try:
                shipment = Shipment.objects.get(id=sid)
                pickup.shipments.add(shipment)
            except Shipment.DoesNotExist:
                pass

        return pickup

    @staticmethod
    def cancel_pickup(pickup_id: str) -> Pickup:
        pickup = Pickup.objects.get(id=pickup_id)
        adapter = registry.get(pickup.carrier.code)
        if adapter and pickup.carrier_pickup_id:
            adapter.cancel_pickup(pickup.carrier_pickup_id)
        pickup.status = 'CANCELLED'
        pickup.cancelled_at = datetime.now()
        pickup.save()
        return pickup
