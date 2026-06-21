from datetime import datetime
from ..models import Shipment, TrackingEvent, ShipmentStatus, InternalStatus
from .adapters.registry import registry
from ..status_map import mapper


class TrackingService:

    @staticmethod
    def get_tracking(shipment_id: str) -> dict:
        shipment = Shipment.objects.get(id=shipment_id)
        adapter = registry.get(shipment.carrier.code)

        if not adapter:
            return TrackingService._build_from_db(shipment)

        carrier_data = adapter.track(shipment.carrier_tracking_number)

        # Map each event through StatusMapper
        events = []
        for evt in carrier_data.events:
            internal_code = mapper.map(shipment.carrier.code, evt.raw_status or evt.description)
            events.append({
                'eventId': f'evt_{len(events) + 1}',
                'internalCode': internal_code.value,
                'carrierCode': evt.code,
                'carrierRawStatus': evt.raw_status or evt.description,
                'label': evt.description,
                'location': evt.location or '',
                'timestamp': evt.timestamp.isoformat() if evt.timestamp else '',
            })

        current_internal = mapper.map(shipment.carrier.code, carrier_data.current_status)

        return {
            'shipmentId': shipment_id,
            'carrierCode': shipment.carrier.code,
            'carrierTrackingNumber': shipment.carrier_tracking_number,
            'currentStatus': {
                'internalCode': current_internal.value,
                'carrierCode': carrier_data.current_status,
                'label': carrier_data.current_status,
                'location': events[-1]['location'] if events else '',
                'timestamp': events[-1]['timestamp'] if events else '',
            },
            'estimatedDeliveryDate': shipment.estimated_delivery_date.isoformat() if shipment.estimated_delivery_date else None,
            'events': events,
        }

    @staticmethod
    def process_webhook(carrier_code: str, raw_body: dict) -> dict:
        adapter = registry.get_or_raise(carrier_code)
        parsed = adapter.parse_webhook(raw_body)
        internal_status = mapper.map(carrier_code, parsed.carrier_raw_status)

        # Find shipment by tracking number
        shipment = Shipment.objects.filter(carrier_tracking_number=parsed.tracking_no).first()
        if not shipment:
            raise ValueError(f"Shipment with tracking '{parsed.tracking_no}' not found")

        # Create tracking event
        TrackingEvent.objects.create(
            shipment=shipment,
            internal_code=internal_status.value,
            carrier_code=carrier_code,
            carrier_raw_status=parsed.carrier_raw_status,
            label=parsed.carrier_raw_status,
            location=parsed.location or '',
            signed_by=parsed.signed_by or parsed.customer_name,
            carrier_raw_data=raw_body,
            timestamp=parsed.timestamp or datetime.now(),
        )

        # Update shipment status
        shipment.internal_status = internal_status.value
        shipment.carrier_status = parsed.carrier_raw_status
        shipment.save()

        return {
            'tracking_no': parsed.tracking_no,
            'carrier_raw_status': parsed.carrier_raw_status,
            'internalStatus': internal_status.value,
            'customer_name': parsed.customer_name,
        }

    @staticmethod
    def _build_from_db(shipment: Shipment) -> dict:
        events_qs = shipment.tracking_events.all()[:10]
        events = [
            {
                'eventId': e.id,
                'internalCode': e.internal_code,
                'carrierCode': e.carrier_code,
                'carrierRawStatus': e.carrier_raw_status,
                'label': e.label,
                'location': e.location,
                'timestamp': e.timestamp.isoformat(),
            }
            for e in events_qs
        ]
        return {
            'shipmentId': shipment.id,
            'carrierCode': shipment.carrier.code,
            'carrierTrackingNumber': shipment.carrier_tracking_number,
            'currentStatus': {
                'internalCode': shipment.internal_status,
                'carrierCode': shipment.carrier_status,
                'label': shipment.carrier_status,
                'timestamp': shipment.updated_at.isoformat(),
            },
            'events': events,
        }
