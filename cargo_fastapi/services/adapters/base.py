"""Adapter base classes and data transfer objects."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from abc import ABC, abstractmethod


@dataclass
class AddressData:
    company: str = ""
    contact_name: str = ""
    email: str = ""
    phone: str = ""
    country: str = ""
    zip_code: str = ""
    city: str = ""
    address: str = ""
    address2: str = ""


@dataclass
class PackageData:
    reference: str = ""
    description: str = ""
    weight: float = 0.0
    weight_unit: str = "KG"
    length: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
    dim_unit: str = "CM"
    declared_value: Optional[float] = None
    declared_currency: str = "EUR"


@dataclass
class ShipmentInput:
    carrier_code: str = ""
    service_code: str = ""
    reference: str = ""
    sender: AddressData = field(default_factory=AddressData)
    recipient: AddressData = field(default_factory=AddressData)
    packages: list = field(default_factory=list)
    insurance_amount: Optional[float] = None
    insurance_currency: str = "EUR"
    signature_required: bool = True
    saturday_delivery: bool = False


@dataclass
class CarrierShipmentResponse:
    carrier_tracking_number: str = ""
    carrier_shipment_id: str = ""
    label_url: str = ""
    label_format: str = "PDF"
    tracking_url: str = ""
    price_total: float = 0.0
    price_currency: str = "EUR"
    price_breakdown: list = field(default_factory=list)
    estimated_delivery_date: Optional[str] = None


@dataclass
class RateRequest:
    sender_country: str = ""
    sender_zip: str = ""
    sender_city: str = ""
    recipient_country: str = ""
    recipient_zip: str = ""
    recipient_city: str = ""
    packages: list = field(default_factory=list)
    service_type: str = "EXPRESS"


@dataclass
class RateOffer:
    carrier_code: str = ""
    carrier_name: str = ""
    service_code: str = ""
    service_name: str = ""
    total_price: float = 0.0
    currency: str = "EUR"
    estimated_transit_days: Optional[int] = None
    estimated_delivery_date: Optional[str] = None
    guaranteed: bool = False
    breakdown: list = field(default_factory=list)


@dataclass
class PickupRequest:
    carrier_code: str = ""
    shipment_ids: list = field(default_factory=list)
    pickup_date: str = ""
    ready_time: str = ""
    close_time: str = ""
    location: Optional[AddressData] = None
    total_packages: int = 1
    total_weight: Optional[float] = None
    weight_unit: str = "KG"
    special_instructions: str = ""


@dataclass
class PickupResponse:
    carrier_pickup_id: str = ""
    confirmation_number: str = ""
    status: str = "CONFIRMED"


@dataclass
class TrackingResult:
    tracking_number: str = ""
    current_status: str = ""
    estimated_delivery_date: Optional[str] = None
    events: list = field(default_factory=list)


@dataclass
class TrackingEvent:
    status: str = ""
    timestamp: str = ""
    location: str = ""


@dataclass
class WebhookParsedEvent:
    tracking_no: str = ""
    carrier_raw_status: str = ""
    timestamp: str = ""
    customer_name: str = ""


@dataclass
class ConnectionTestResult:
    status: str = "CONNECTED"
    latency_ms: int = 0
    endpoint: str = ""
    http_status: int = 200
    message: str = "Connection successful"
    account_valid: bool = True


class CarrierAdapter(ABC):

    @abstractmethod
    def get_adapter_name(self) -> str:
        ...

    @abstractmethod
    def create_shipment(self, input_data: ShipmentInput) -> CarrierShipmentResponse:
        ...

    @abstractmethod
    def cancel_shipment(self, tracking_number: str) -> bool:
        ...

    @abstractmethod
    def get_tracking(self, tracking_number: str) -> TrackingResult:
        ...

    @abstractmethod
    def get_rates(self, request: RateRequest) -> list[RateOffer]:
        ...

    @abstractmethod
    def schedule_pickup(self, request: PickupRequest) -> PickupResponse:
        ...

    @abstractmethod
    def cancel_pickup(self, carrier_pickup_id: str) -> bool:
        ...

    @abstractmethod
    def validate_address(self, address: AddressData) -> dict:
        ...

    @abstractmethod
    def get_label(self, tracking_number: str, fmt: str = "PDF") -> dict:
        ...

    @abstractmethod
    def parse_webhook(self, raw_body: dict) -> WebhookParsedEvent:
        ...

    @abstractmethod
    def validate_webhook_signature(self, payload: str, signature: str, secret: str) -> bool:
        ...

    @abstractmethod
    def test_connection(self) -> ConnectionTestResult:
        ...
