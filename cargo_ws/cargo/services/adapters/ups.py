import hashlib
import hmac
import time
from datetime import datetime
from .base import (CarrierAdapter, ShipmentInput, CarrierShipmentResponse, RateRequest, RateOffer,
                   CarrierTrackingData, TrackingEventData, PickupRequest, CarrierPickupResponse,
                   ConnectionTestResult, WebhookPayload, AddressData)
from .registry import registry


class UpsAdapter(CarrierAdapter):
    @property
    def code(self) -> str: return 'UPS'
    @property
    def name(self) -> str: return 'UPS'

    def create_shipment(self, input_data: ShipmentInput) -> CarrierShipmentResponse:
        ups_payload = {
            'shipment_id': 'UPS' + str(int(time.time()))[-10:],
            'customer': input_data.recipient.contact_name,
        }
        return CarrierShipmentResponse(
            carrier_tracking_number='1Z' + str(int(time.time()))[-14:],
            carrier_shipment_id=ups_payload['shipment_id'],
            label_url='https://www.ups.com/labels/dummy.pdf',
            tracking_url='https://www.ups.com/track/dummy',
            price_total=42.00, price_currency='EUR',
            price_breakdown=[{'type': 'BASE', 'amount': 36.00}, {'type': 'FUEL', 'amount': 4.50}],
            raw_response=ups_payload,
        )

    def cancel_shipment(self, tracking_number: str) -> dict:
        return {'status': 'CANCELLED', 'trackingNumber': tracking_number}

    def get_label(self, tracking_number: str, label_format: str = 'PDF') -> dict:
        return {'labelUrl': f'https://www.ups.com/labels/{tracking_number}.pdf',
                'format': label_format, 'size': 'A6', 'generatedAt': datetime.now().isoformat()}

    def get_rates(self, request: RateRequest) -> list[RateOffer]:
        return [
            RateOffer(carrier_code='UPS', carrier_name='UPS',
                      service_code='UPS_EXPRESS_SAVER', service_name='UPS Express Saver',
                      total_price=42.00, currency='EUR', estimated_transit_days=3,
                      breakdown=[{'type': 'BASE', 'amount': 36.00}, {'type': 'FUEL', 'amount': 4.50}])
        ]

    def track(self, tracking_number: str) -> CarrierTrackingData:
        return CarrierTrackingData(
            tracking_number=tracking_number, current_status='IN_PROGRESS',
            events=[
                TrackingEventData(code='PENDING', description='Label created', raw_status='Label created'),
                TrackingEventData(code='PICKED_UP', description='Collected', raw_status='Collected'),
                TrackingEventData(code='IN_PROGRESS', description='OnTheWay', raw_status='OnTheWay',
                                  location='Frankfurt, Germany'),
            ],
            raw_response={'shipment_id': tracking_number},
        )

    def track_batch(self, tracking_numbers: list[str]) -> dict:
        return {tn: self.track(tn) for tn in tracking_numbers}

    def schedule_pickup(self, request: PickupRequest) -> CarrierPickupResponse:
        return CarrierPickupResponse(
            carrier_pickup_id='UPS-PICKUP-' + str(int(time.time()))[-5:],
            confirmation_number='CONF-UPS-' + str(int(time.time()))[-6:],
        )

    def cancel_pickup(self, pickup_id: str) -> dict:
        return {'status': 'CANCELLED', 'pickupId': pickup_id}

    def validate_address(self, address: AddressData) -> dict:
        return {'valid': True, 'normalizedAddress': {'country': address.country, 'zipCode': address.zip_code},
                'suggestions': []}

    def test_connection(self) -> ConnectionTestResult:
        return ConnectionTestResult(status='CONNECTED', latency_ms=200,
                                    endpoint='https://onlinetools.ups.com/api/health',
                                    http_status=200, message='API is reachable', account_valid=True)

    def parse_webhook(self, raw_body: dict) -> WebhookPayload:
        return WebhookPayload(
            tracking_no=raw_body.get('shipment_id', ''),
            carrier_raw_status=raw_body.get('state', ''),
            customer_name=raw_body.get('customer', ''),
            signed_by=raw_body.get('signed_by', ''),
            timestamp=datetime.now(),
        )

    def validate_webhook_signature(self, payload: str, signature: str, secret: str) -> bool:
        expected = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature)


registry.register('UPS', UpsAdapter())
