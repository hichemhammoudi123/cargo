"""Mock UPS adapter."""
from datetime import datetime, timedelta
from .base import (
    CarrierAdapter, ShipmentInput, CarrierShipmentResponse, RateRequest, RateOffer,
    PickupRequest, PickupResponse, TrackingResult, TrackingEvent, WebhookParsedEvent,
    ConnectionTestResult, AddressData,
)
from .registry import registry
import random


class UpsAdapter(CarrierAdapter):

    def get_adapter_name(self) -> str:
        return "Ups"

    def create_shipment(self, input_data: ShipmentInput) -> CarrierShipmentResponse:
        tn = f"1Z{random.randint(100, 999)}AA{random.randint(10000000, 99999999)}"
        return CarrierShipmentResponse(
            carrier_tracking_number=tn,
            carrier_shipment_id=f"UPS-SHIP-{random.randint(10000, 99999)}",
            label_url="https://www.ups.com/labels/dummy.pdf",
            label_format="PDF",
            tracking_url=f"https://www.ups.com/track/dummy",
            price_total=42.50,
            price_currency="EUR",
            price_breakdown=[
                {"type": "BASE", "label": "Transport", "amount": 38.00},
                {"type": "FUEL", "label": "Fuel surcharge", "amount": 4.50},
            ],
        )

    def cancel_shipment(self, tracking_number: str) -> bool:
        return True

    def get_tracking(self, tracking_number: str) -> TrackingResult:
        return TrackingResult(
            tracking_number=tracking_number,
            current_status="IN_PROGRESS",
            estimated_delivery_date=(datetime.utcnow() + timedelta(days=2)).isoformat(),
            events=[],
        )

    def get_rates(self, request: RateRequest) -> list[RateOffer]:
        return [RateOffer(
            carrier_code="UPS",
            carrier_name="UPS United Parcel Service",
            service_code="UPS_EXP",
            service_name="UPS Express Plus",
            total_price=48.00,
            currency="EUR",
            estimated_transit_days=2,
            guaranteed=False,
        )]

    def schedule_pickup(self, request: PickupRequest) -> PickupResponse:
        return PickupResponse(
            carrier_pickup_id=f"UPS-PU-{random.randint(10000, 99999)}",
            confirmation_number=f"UPS-CONF-{random.randint(100000, 999999)}",
        )

    def cancel_pickup(self, carrier_pickup_id: str) -> bool:
        return True

    def validate_address(self, address: AddressData) -> dict:
        return {"valid": True, "normalizedAddress": {}, "suggestions": []}

    def get_label(self, tracking_number: str, fmt: str = "PDF") -> dict:
        return {"labelUrl": f"https://www.ups.com/labels/{tracking_number}.pdf", "format": fmt, "size": "A6"}

    def parse_webhook(self, raw_body: dict) -> WebhookParsedEvent:
        return WebhookParsedEvent(
            tracking_no=raw_body.get("shipment_id", ""),
            carrier_raw_status=raw_body.get("state", ""),
            timestamp=raw_body.get("timestamp", ""),
            customer_name=raw_body.get("customer", ""),
        )

    def validate_webhook_signature(self, payload: str, signature: str, secret: str) -> bool:
        return True

    def test_connection(self) -> ConnectionTestResult:
        return ConnectionTestResult(latency_ms=random.randint(50, 200), endpoint="https://www.ups.com/api/test")


registry.register("UPS", UpsAdapter())
