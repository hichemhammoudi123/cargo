"""Mock DHL adapter."""
from datetime import datetime, timedelta
from .base import (
    CarrierAdapter, ShipmentInput, CarrierShipmentResponse, RateRequest, RateOffer,
    PickupRequest, PickupResponse, TrackingResult, TrackingEvent, WebhookParsedEvent,
    ConnectionTestResult, AddressData,
)
from .registry import registry
import random


class DhlAdapter(CarrierAdapter):

    def get_adapter_name(self) -> str:
        return "Dhl"

    def create_shipment(self, input_data: ShipmentInput) -> CarrierShipmentResponse:
        tn = f"DHL{random.randint(10000000, 99999999)}"
        return CarrierShipmentResponse(
            carrier_tracking_number=tn,
            carrier_shipment_id=f"DE-{tn}",
            label_url="https://api.dhl.com/labels/dummy.pdf",
            label_format="PDF",
            tracking_url=f"https://www.dhl.com/track/dummy",
            price_total=45.30,
            price_currency="EUR",
            price_breakdown=[
                {"type": "BASE", "label": "Transport", "amount": 38.00},
                {"type": "FUEL", "label": "Fuel surcharge", "amount": 5.30},
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
            events=[
                TrackingEvent(status="PICKED_UP", timestamp=(datetime.utcnow() - timedelta(days=1)).isoformat(), location="Paris, FR"),
                TrackingEvent(status="IN_PROGRESS", timestamp=datetime.utcnow().isoformat(), location="Transit"),
            ],
        )

    def get_rates(self, request: RateRequest) -> list[RateOffer]:
        return [RateOffer(
            carrier_code="DHL",
            carrier_name="DHL Express",
            service_code="DHL_EXP",
            service_name="DHL Express Worldwide",
            total_price=45.30,
            currency="EUR",
            estimated_transit_days=2,
            estimated_delivery_date=(datetime.utcnow() + timedelta(days=2)).strftime("%Y-%m-%d"),
            guaranteed=True,
            breakdown=[{"type": "BASE", "label": "Transport", "amount": 38.00}, {"type": "FUEL", "label": "Fuel", "amount": 5.30}],
        )]

    def schedule_pickup(self, request: PickupRequest) -> PickupResponse:
        return PickupResponse(
            carrier_pickup_id=f"DHL-PICKUP-{random.randint(10000, 99999)}",
            confirmation_number=f"CONF-{random.randint(100, 999)}-{random.randint(100, 999)}",
        )

    def cancel_pickup(self, carrier_pickup_id: str) -> bool:
        return True

    def validate_address(self, address: AddressData) -> dict:
        return {
            "valid": True,
            "normalizedAddress": {
                "country": address.country,
                "zipCode": address.zip_code,
                "city": address.city.upper(),
                "address": address.address.upper(),
            },
            "suggestions": [],
        }

    def get_label(self, tracking_number: str, fmt: str = "PDF") -> dict:
        return {"labelUrl": f"https://api.dhl.com/labels/{tracking_number}.{fmt.lower()}", "format": fmt, "size": "A6"}

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
        return ConnectionTestResult(latency_ms=random.randint(50, 200), endpoint="https://api.dhl.com/test")


registry.register("DHL", DhlAdapter())
