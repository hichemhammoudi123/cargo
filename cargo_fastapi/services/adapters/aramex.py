"""Mock Aramex adapter."""
from datetime import datetime, timedelta
from .base import (
    CarrierAdapter, ShipmentInput, CarrierShipmentResponse, RateRequest, RateOffer,
    PickupRequest, PickupResponse, TrackingResult, TrackingEvent, WebhookParsedEvent,
    ConnectionTestResult, AddressData,
)
from .registry import registry
import random


class AramexAdapter(CarrierAdapter):

    def get_adapter_name(self) -> str:
        return "Aramex"

    def create_shipment(self, input_data: ShipmentInput) -> CarrierShipmentResponse:
        tn = f"ARAM{random.randint(10000000, 99999999)}"
        return CarrierShipmentResponse(
            carrier_tracking_number=tn,
            carrier_shipment_id=f"ARAM-{tn}",
            label_url="https://api.aramex.com/labels/dummy.pdf",
            label_format="PDF",
            tracking_url=f"https://www.aramex.com/track/dummy",
            price_total=35.00,
            price_currency="USD",
            price_breakdown=[],
        )

    def cancel_shipment(self, tracking_number: str) -> bool:
        return True

    def get_tracking(self, tracking_number: str) -> TrackingResult:
        return TrackingResult(
            tracking_number=tracking_number,
            current_status="IN_PROGRESS",
            estimated_delivery_date=(datetime.utcnow() + timedelta(days=3)).isoformat(),
            events=[],
        )

    def get_rates(self, request: RateRequest) -> list[RateOffer]:
        return [RateOffer(
            carrier_code="ARAMEX",
            carrier_name="Aramex International",
            service_code="ARAM_INTL",
            service_name="Aramex International",
            total_price=35.00,
            currency="USD",
            estimated_transit_days=3,
        )]

    def schedule_pickup(self, request: PickupRequest) -> PickupResponse:
        return PickupResponse(carrier_pickup_id=f"ARAM-PU-{random.randint(10000, 99999)}", confirmation_number="")

    def cancel_pickup(self, carrier_pickup_id: str) -> bool:
        return True

    def validate_address(self, address: AddressData) -> dict:
        return {"valid": True, "normalizedAddress": {}, "suggestions": []}

    def get_label(self, tracking_number: str, fmt: str = "PDF") -> dict:
        return {"labelUrl": f"https://api.aramex.com/labels/{tracking_number}.pdf", "format": fmt, "size": "A6"}

    def parse_webhook(self, raw_body: dict) -> WebhookParsedEvent:
        return WebhookParsedEvent(
            tracking_no=raw_body.get("trackingNumber", ""),
            carrier_raw_status=raw_body.get("status", ""),
            timestamp=raw_body.get("timestamp", ""),
            customer_name=raw_body.get("signedBy", ""),
        )

    def validate_webhook_signature(self, payload: str, signature: str, secret: str) -> bool:
        return True

    def test_connection(self) -> ConnectionTestResult:
        return ConnectionTestResult(latency_ms=random.randint(50, 200), endpoint="https://api.aramex.com/test")


registry.register("ARAMEX", AramexAdapter())
