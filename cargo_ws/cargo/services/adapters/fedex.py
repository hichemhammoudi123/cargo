import hashlib
import hmac
import time
from datetime import datetime
from .base import (CarrierAdapter, ShipmentInput, CarrierShipmentResponse, RateRequest, RateOffer,
                   CarrierTrackingData, TrackingEventData, PickupRequest, CarrierPickupResponse,
                   ConnectionTestResult, WebhookPayload, AddressData)
from .registry import registry


class FedExAdapter(CarrierAdapter):
    @property
    def code(self) -> str: return 'FEDEX'
    @property
    def name(self) -> str: return 'FedEx'

    def create_shipment(self, input_data: ShipmentInput) -> CarrierShipmentResponse:
        return CarrierShipmentResponse(
            carrier_tracking_number=str(int(time.time()))[-12:],
            carrier_shipment_id='FX' + str(int(time.time()))[-8:],
            label_url='https://api.fedex.com/labels/dummy.pdf',
            tracking_url='https://www.fedex.com/track/dummy',
            price_total=48.50, price_currency='EUR',
            price_breakdown=[{'type': 'BASE', 'amount': 41.00}, {'type': 'FUEL', 'amount': 5.50}],
        )

    def cancel_shipment(self, tracking_number: str) -> dict:
        return {'status': 'CANCELLED', 'trackingNumber': tracking_number}

    def get_label(self, tracking_number: str, label_format: str = 'PDF') -> dict:
        return {'labelUrl': f'https://api.fedex.com/labels/{tracking_number}.pdf',
                'format': label_format, 'size': 'A6', 'generatedAt': datetime.now().isoformat()}

    def get_rates(self, request: RateRequest) -> list[RateOffer]:
        return [
            RateOffer(carrier_code='FEDEX', carrier_name='FedEx',
                      service_code='FEDEX_PRIORITY', service_name='FedEx Priority',
                      total_price=48.50, currency='EUR', estimated_transit_days=1,
                      breakdown=[{'type': 'BASE', 'amount': 41.00}, {'type': 'FUEL', 'amount': 5.50}])
        ]

    def track(self, tracking_number: str) -> CarrierTrackingData:
        return CarrierTrackingData(
            tracking_number=tracking_number, current_status='IN_PROGRESS',
            events=[
                TrackingEventData(code='PENDING', description='Label created', raw_status='Label created'),
                TrackingEventData(code='PICKED_UP', description='Picked up', raw_status='PICKED UP'),
                TrackingEventData(code='IN_PROGRESS', description='En route', raw_status='EN_ROUTE',
                                  location='Memphis, TN'),
            ],
        )

    def track_batch(self, tracking_numbers: list[str]) -> dict:
        return {tn: self.track(tn) for tn in tracking_numbers}

    def schedule_pickup(self, request: PickupRequest) -> CarrierPickupResponse:
        return CarrierPickupResponse(
            carrier_pickup_id='FX-PICKUP-' + str(int(time.time()))[-5:],
            confirmation_number='CONF-FX-' + str(int(time.time()))[-6:],
        )

    def cancel_pickup(self, pickup_id: str) -> dict:
        return {'status': 'CANCELLED', 'pickupId': pickup_id}

    def validate_address(self, address: AddressData) -> dict:
        return {'valid': True, 'normalizedAddress': {'country': address.country, 'zipCode': address.zip_code},
                'suggestions': []}

    def test_connection(self) -> ConnectionTestResult:
        return ConnectionTestResult(status='CONNECTED', latency_ms=180,
                                    endpoint='https://api.fedex.com/health',
                                    http_status=200, message='API is reachable', account_valid=True)

    def parse_webhook(self, raw_body: dict) -> WebhookPayload:
        return WebhookPayload(
            tracking_no=raw_body.get('tracking_number', ''),
            carrier_raw_status=raw_body.get('current_status', ''),
            customer_name=raw_body.get('recipient', {}).get('name', ''),
            timestamp=datetime.now(),
        )

    def validate_webhook_signature(self, payload: str, signature: str, secret: str) -> bool:
        expected = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature)


registry.register('FEDEX', FedExAdapter())
