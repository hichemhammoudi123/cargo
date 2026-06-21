from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class AddressData:
    company: str = ''
    contact_name: str = ''
    email: str = ''
    phone: str = ''
    country: str = ''
    zip_code: str = ''
    city: str = ''
    address: str = ''
    address2: str = ''


@dataclass
class PackageData:
    reference: str = ''
    description: str = ''
    weight: float = 0.0
    weight_unit: str = 'KG'
    length: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
    dim_unit: str = 'CM'
    declared_value: Optional[float] = None
    declared_currency: str = 'EUR'


@dataclass
class ShipmentInput:
    carrier_code: str = ''
    service_code: str = ''
    reference: str = ''
    sender: AddressData = field(default_factory=AddressData)
    recipient: AddressData = field(default_factory=AddressData)
    packages: list = field(default_factory=list)
    insurance_amount: Optional[float] = None
    insurance_currency: str = 'EUR'
    signature_required: bool = True
    saturday_delivery: bool = False


@dataclass
class CarrierShipmentResponse:
    carrier_tracking_number: str = ''
    carrier_shipment_id: str = ''
    label_url: str = ''
    label_format: str = 'PDF'
    tracking_url: str = ''
    price_total: float = 0.0
    price_currency: str = 'EUR'
    price_breakdown: list = field(default_factory=list)
    estimated_delivery_date: Optional[datetime] = None
    raw_response: dict = field(default_factory=dict)


@dataclass
class RateRequest:
    sender_country: str = ''
    sender_zip: str = ''
    sender_city: str = ''
    recipient_country: str = ''
    recipient_zip: str = ''
    recipient_city: str = ''
    packages: list = field(default_factory=list)
    service_type: str = 'EXPRESS'


@dataclass
class RateOffer:
    carrier_code: str = ''
    carrier_name: str = ''
    service_code: str = ''
    service_name: str = ''
    total_price: float = 0.0
    currency: str = 'EUR'
    estimated_transit_days: int = 0
    estimated_delivery_date: Optional[str] = None
    guaranteed: bool = False
    breakdown: list = field(default_factory=list)


@dataclass
class TrackingEventData:
    code: str = ''
    description: str = ''
    location: str = ''
    timestamp: Optional[datetime] = None
    raw_status: str = ''


@dataclass
class CarrierTrackingData:
    tracking_number: str = ''
    current_status: str = ''
    events: list = field(default_factory=list)
    estimated_delivery_date: Optional[datetime] = None
    raw_response: dict = field(default_factory=dict)


@dataclass
class PickupRequest:
    carrier_code: str = ''
    shipment_ids: list = field(default_factory=list)
    pickup_date: str = ''
    ready_time: str = ''
    close_time: str = ''
    location: AddressData = field(default_factory=AddressData)
    total_packages: int = 1
    total_weight: Optional[float] = None
    weight_unit: str = 'KG'
    special_instructions: str = ''


@dataclass
class CarrierPickupResponse:
    carrier_pickup_id: str = ''
    confirmation_number: str = ''
    status: str = 'CONFIRMED'


@dataclass
class ConnectionTestResult:
    status: str = 'ERROR'
    latency_ms: int = 0
    endpoint: str = ''
    http_status: int = 0
    message: str = ''
    account_valid: bool = False


@dataclass
class WebhookPayload:
    tracking_no: str = ''
    carrier_raw_status: str = ''
    internal_status: str = ''
    customer_name: str = ''
    timestamp: Optional[datetime] = None
    signed_by: str = ''
    location: str = ''


class CarrierAdapter(ABC):
    """Abstract base class for all carrier adapters."""

    @property
    @abstractmethod
    def code(self) -> str: ...
    @property
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def create_shipment(self, input_data: ShipmentInput) -> CarrierShipmentResponse: ...

    @abstractmethod
    def cancel_shipment(self, tracking_number: str) -> dict: ...

    @abstractmethod
    def get_label(self, tracking_number: str, label_format: str = 'PDF') -> dict: ...

    @abstractmethod
    def get_rates(self, request: RateRequest) -> list[RateOffer]: ...

    @abstractmethod
    def track(self, tracking_number: str) -> CarrierTrackingData: ...

    @abstractmethod
    def track_batch(self, tracking_numbers: list[str]) -> dict: ...

    @abstractmethod
    def schedule_pickup(self, request: PickupRequest) -> CarrierPickupResponse: ...

    @abstractmethod
    def cancel_pickup(self, pickup_id: str) -> dict: ...

    @abstractmethod
    def validate_address(self, address: AddressData) -> dict: ...

    @abstractmethod
    def test_connection(self) -> ConnectionTestResult: ...

    @abstractmethod
    def parse_webhook(self, raw_body: dict) -> WebhookPayload: ...

    @abstractmethod
    def validate_webhook_signature(self, payload: str, signature: str, secret: str) -> bool: ...
