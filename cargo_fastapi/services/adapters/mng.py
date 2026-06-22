"""Mock MNG Kargo adapter."""
from datetime import datetime, timedelta
from .base import (
    CarrierAdapter, ShipmentInput, CarrierShipmentResponse, RateRequest, RateOffer,
    PickupRequest, PickupResponse, TrackingResult, TrackingEvent, WebhookParsedEvent,
    ConnectionTestResult, AddressData,
)
from .registry import registry
import random


class MngAdapter(CarrierAdapter):

    def get_adapter_name(self) -> str:
        return "Mng"

    def create_shipment(self, input_data: ShipmentInput) -> CarrierShipmentResponse:
        tn = f"MNG{random.randint(100000000, 999999999)}"
        return CarrierShipmentResponse(
            carrier_tracking_number=tn,
            carrier_shipment_id=f"MNG-{tn}",
            label_url="",
            label_format="PDF",
            tracking_url="",
            price_total=22.00,
            price_currency="TRY",
            price_breakdown=[],
        )

    def cancel_shipment(self, tracking_number: str) -> bool:
        return True

    def get_tracking(self, tracking_number: str) -> TrackingResult:
        return TrackingResult(tracking_number=tracking_number, current_status="PENDING", events=[])

    def get_rates(self, request: RateRequest) -> list[RateOffer]:
        return [RateOffer(
            carrier_code="MNG",
            carrier_name="MNG Kargo",
            service_code="MNG_STD",
            service_name="Standart Teslimat",
            total_price=22.00,
            currency="TRY",
            estimated_transit_days=2,
        )]

    def schedule_pickup(self, request: PickupRequest) -> PickupResponse:
        return PickupResponse(carrier_pickup_id=f"MNG-PU-{random.randint(10000, 99999)}", confirmation_number="")

    def cancel_pickup(self, carrier_pickup_id: str) -> bool:
        return True

    def validate_address(self, address: AddressData) -> dict:
        return {"valid": True, "normalizedAddress": {}, "suggestions": []}

    def get_label(self, tracking_number: str, fmt: str = "PDF") -> dict:
        return {"labelUrl": "", "format": fmt, "size": "A6"}

    def parse_webhook(self, raw_body: dict) -> WebhookParsedEvent:
        return WebhookParsedEvent(
            tracking_no=raw_body.get("takipNo", ""),
            carrier_raw_status=raw_body.get("durum", ""),
            timestamp=raw_body.get("tarih", ""),
            customer_name=raw_body.get("alici", ""),
        )

    def validate_webhook_signature(self, payload: str, signature: str, secret: str) -> bool:
        return True

    def test_connection(self) -> ConnectionTestResult:
        return ConnectionTestResult(latency_ms=random.randint(50, 200), endpoint="https://api.mngkargo.com/test")


registry.register("MNG", MngAdapter())
