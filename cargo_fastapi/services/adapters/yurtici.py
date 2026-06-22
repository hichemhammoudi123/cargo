"""Mock Yurtici Kargo adapter."""
from datetime import datetime, timedelta
from .base import (
    CarrierAdapter, ShipmentInput, CarrierShipmentResponse, RateRequest, RateOffer,
    PickupRequest, PickupResponse, TrackingResult, TrackingEvent, WebhookParsedEvent,
    ConnectionTestResult, AddressData,
)
from .registry import registry
import random


class YurticiAdapter(CarrierAdapter):

    def get_adapter_name(self) -> str:
        return "Yurtici"

    def create_shipment(self, input_data: ShipmentInput) -> CarrierShipmentResponse:
        tn = f"YT{datetime.utcnow().year}{random.randint(100000000, 999999999)}"
        return CarrierShipmentResponse(
            carrier_tracking_number=tn,
            carrier_shipment_id=f"YT-{tn}",
            label_url="",
            label_format="PDF",
            tracking_url=f"https://www.yurticikargo.com/track/dummy",
            price_total=25.00,
            price_currency="TRY",
            price_breakdown=[],
        )

    def cancel_shipment(self, tracking_number: str) -> bool:
        return True

    def get_tracking(self, tracking_number: str) -> TrackingResult:
        return TrackingResult(
            tracking_number=tracking_number,
            current_status="IN_PROGRESS",
            estimated_delivery_date=(datetime.utcnow() + timedelta(days=1)).isoformat(),
            events=[],
        )

    def get_rates(self, request: RateRequest) -> list[RateOffer]:
        return [RateOffer(
            carrier_code="YURTICI",
            carrier_name="Yurtici Kargo",
            service_code="YT_STD",
            service_name="Standart Teslimat",
            total_price=25.00,
            currency="TRY",
            estimated_transit_days=2,
        )]

    def schedule_pickup(self, request: PickupRequest) -> PickupResponse:
        return PickupResponse(carrier_pickup_id=f"YT-PU-{random.randint(10000, 99999)}", confirmation_number="")

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
        return ConnectionTestResult(latency_ms=random.randint(50, 200), endpoint="https://api.yurticikargo.com/test")


registry.register("YURTICI", YurticiAdapter())
