import hashlib
import hmac
import time
from datetime import datetime
from .base import (CarrierAdapter, ShipmentInput, CarrierShipmentResponse, RateRequest, RateOffer,
                   CarrierTrackingData, TrackingEventData, PickupRequest, CarrierPickupResponse,
                   ConnectionTestResult, WebhookPayload, AddressData)
from .registry import registry


class AramexAdapter(CarrierAdapter):
    @property
    def code(self) -> str: return 'ARAMEX'
    @property
    def name(self) -> str: return 'Aramex'

    def create_shipment(self, input_data: ShipmentInput) -> CarrierShipmentResponse:
        return CarrierShipmentResponse(
            carrier_tracking_number=str(int(time.time()))[-10:],
            carrier_shipment_id='AX-' + str(int(time.time()))[-8:],
            label_url='https://api.aramex.com/labels/dummy.pdf',
            tracking_url='https://www.aramex.com/track/dummy',
            price_total=40.00, price_currency='USD',
            price_breakdown=[{'type': 'BASE', 'amount': 34.00}, {'type': 'FUEL', 'amount': 4.00},
                             {'type': 'INSURANCE', 'amount': 2.00}],
        )

    def cancel_shipment(self, tracking_number: str) -> dict:
        return {'status': 'CANCELLED', 'trackingNumber': tracking_number}

    def get_label(self, tracking_number: str, label_format: str = 'PDF') -> dict:
        return {'labelUrl': f'https://api.aramex.com/labels/{tracking_number}.pdf',
                'format': label_format, 'size': 'A6', 'generatedAt': datetime.now().isoformat()}

    def get_rates(self, request: RateRequest) -> list[RateOffer]:
        return [
            RateOffer(carrier_code='ARAMEX', carrier_name='Aramex',
                      service_code='ARAMEX_EXPRESS', service_name='Aramex Express',
                      total_price=40.00, currency='USD', estimated_transit_days=3,
                      breakdown=[{'type': 'BASE', 'amount': 34.00}, {'type': 'FUEL', 'amount': 4.00}])
        ]

    def track(self, tracking_number: str) -> CarrierTrackingData:
        return CarrierTrackingData(
            tracking_number=tracking_number, current_status='IN_PROGRESS',
            events=[
                TrackingEventData(code='PENDING', description='Shipment created', raw_status='Shipment created'),
                TrackingEventData(code='PICKED_UP', description='Picked up', raw_status='PICKED UP'),
                TrackingEventData(code='IN_PROGRESS', description='In transit', raw_status='IN TRANSIT',
                                  location='Dubai, UAE'),
            ],
        )

    def track_batch(self, tracking_numbers: list[str]) -> dict:
        return {tn: self.track(tn) for tn in tracking_numbers}

    def schedule_pickup(self, request: PickupRequest) -> CarrierPickupResponse:
        return CarrierPickupResponse(
            carrier_pickup_id='AX-PICKUP-' + str(int(time.time()))[-5:],
            confirmation_number='CONF-AX-' + str(int(time.time()))[-6:],
        )

    def cancel_pickup(self, pickup_id: str) -> dict:
        return {'status': 'CANCELLED', 'pickupId': pickup_id}

    def validate_address(self, address: AddressData) -> dict:
        return {'valid': True, 'normalizedAddress': {'country': address.country, 'zipCode': address.zip_code},
                'suggestions': []}

    def test_connection(self) -> ConnectionTestResult:
        return ConnectionTestResult(status='CONNECTED', latency_ms=220,
                                    endpoint='https://api.aramex.com/health',
                                    http_status=200, message='API is reachable', account_valid=True)

    def parse_webhook(self, raw_body: dict) -> WebhookPayload:
        return WebhookPayload(
            tracking_no=raw_body.get('awb', ''),
            carrier_raw_status=raw_body.get('event', ''),
            customer_name=raw_body.get('consignee', ''),
            timestamp=datetime.now(),
        )

    def validate_webhook_signature(self, payload: str, signature: str, secret: str) -> bool:
        expected = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature)


registry.register('ARAMEX', AramexAdapter())
