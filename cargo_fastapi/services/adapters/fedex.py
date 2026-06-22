"""Mock FedEx adapter."""
from datetime import datetime, timedelta
from .base import (
    CarrierAdapter, ShipmentInput, CarrierShipmentResponse, RateRequest, RateOffer,
    PickupRequest, PickupResponse, TrackingResult, TrackingEvent, WebhookParsedEvent,
    ConnectionTestResult, AddressData,
)
from .registry import registry
import random


class FedExAdapter(CarrierAdapter):

    def get_adapter_name(self) -> str:
        return "FedEx"

    def create_shipment(self, input_data: ShipmentInput) -> CarrierShipmentResponse:
        tn = f"FDX{random.randint(1000000000, 9999999999)}"
        return CarrierShipmentResponse(
            carrier_tracking_number=tn,
            carrier_shipment_id=f"FDX-{tn}",
            label_url="https://api.fedex.com/labels/dummy.pdf",
            label_format="PDF",
            tracking_url=f"https://www.fedex.com/track/dummy",
            price_total=47.80,
            price_currency="EUR",
            price_breakdown=[
                {"type": "BASE", "label": "Transport", "amount": 40.00},
                {"type": "FUEL", "label": "Fuel surcharge", "amount": 5.80},
                {"type": "INSURANCE", "label": "Insurance", "amount": 2.00},
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
            carrier_code="FEDEX",
            carrier_name="FedEx Corporation",
            service_code="FDX_INTL",
            service_name="FedEx International Priority",
            total_price=47.80,
            currency="EUR",
            estimated_transit_days=2,
            guaranteed=True,
        )]

    def schedule_pickup(self, request: PickupRequest) -> PickupResponse:
        return PickupResponse(carrier_pickup_id=f"FDX-PU-{random.randint(10000, 99999)}", confirmation_number="")

    def cancel_pickup(self, carrier_pickup_id: str) -> bool:
        return True

    def validate_address(self, address: AddressData) -> dict:
        return {"valid": True, "normalizedAddress": {}, "suggestions": []}

    def get_label(self, tracking_number: str, fmt: str = "PDF") -> dict:
        return {"labelUrl": f"https://api.fedex.com/labels/{tracking_number}.pdf", "format": fmt, "size": "A6"}

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
        return ConnectionTestResult(latency_ms=random.randint(50, 200), endpoint="https://api.fedex.com/test")


registry.register("FEDEX", FedExAdapter())
