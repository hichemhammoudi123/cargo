import hashlib
import hmac
import time
from datetime import datetime
from .base import (CarrierAdapter, ShipmentInput, CarrierShipmentResponse, RateRequest, RateOffer,
                   CarrierTrackingData, TrackingEventData, PickupRequest, CarrierPickupResponse,
                   ConnectionTestResult, WebhookPayload, AddressData)
from .registry import registry


class YurticiAdapter(CarrierAdapter):
    @property
    def code(self) -> str: return 'YURTICI'
    @property
    def name(self) -> str: return 'Yurtiçi Kargo'

    def create_shipment(self, input_data: ShipmentInput) -> CarrierShipmentResponse:
        return CarrierShipmentResponse(
            carrier_tracking_number='YT' + str(int(time.time()))[-12:],
            carrier_shipment_id='YT-' + str(int(time.time()))[-8:],
            label_url='https://api.yurticikargo.com/labels/dummy.pdf',
            tracking_url='https://www.yurticikargo.com/track/dummy',
            price_total=35.00, price_currency='TRY',
            price_breakdown=[{'type': 'BASE', 'amount': 30.00}, {'type': 'FUEL', 'amount': 5.00}],
        )

    def cancel_shipment(self, tracking_number: str) -> dict:
        return {'status': 'CANCELLED', 'trackingNumber': tracking_number}

    def get_label(self, tracking_number: str, label_format: str = 'PDF') -> dict:
        return {'labelUrl': f'https://api.yurticikargo.com/labels/{tracking_number}.pdf',
                'format': label_format, 'size': 'A6', 'generatedAt': datetime.now().isoformat()}

    def get_rates(self, request: RateRequest) -> list[RateOffer]:
        return [
            RateOffer(carrier_code='YURTICI', carrier_name='Yurtiçi Kargo',
                      service_code='YURTICI_STANDARD', service_name='Standart Kargo',
                      total_price=35.00, currency='TRY', estimated_transit_days=3,
                      breakdown=[{'type': 'BASE', 'amount': 30.00}, {'type': 'FUEL', 'amount': 5.00}])
        ]

    def track(self, tracking_number: str) -> CarrierTrackingData:
        return CarrierTrackingData(
            tracking_number=tracking_number, current_status='IN_PROGRESS',
            events=[
                TrackingEventData(code='PENDING', description='Kayıt oluşturuldu', raw_status='Kayıt oluşturuldu'),
                TrackingEventData(code='PICKED_UP', description='Teslim Alındı', raw_status='Teslim Alındı'),
                TrackingEventData(code='IN_PROGRESS', description='Yolda', raw_status='Yolda',
                                  location='İstanbul, Türkiye'),
            ],
        )

    def track_batch(self, tracking_numbers: list[str]) -> dict:
        return {tn: self.track(tn) for tn in tracking_numbers}

    def schedule_pickup(self, request: PickupRequest) -> CarrierPickupResponse:
        return CarrierPickupResponse(
            carrier_pickup_id='YT-PICKUP-' + str(int(time.time()))[-5:],
            confirmation_number='CONF-YT-' + str(int(time.time()))[-6:],
        )

    def cancel_pickup(self, pickup_id: str) -> dict:
        return {'status': 'CANCELLED', 'pickupId': pickup_id}

    def validate_address(self, address: AddressData) -> dict:
        return {'valid': True, 'normalizedAddress': {'country': address.country, 'zipCode': address.zip_code,
                                                      'city': address.city.upper(), 'address': address.address.upper()},
                'suggestions': []}

    def test_connection(self) -> ConnectionTestResult:
        return ConnectionTestResult(status='CONNECTED', latency_ms=150,
                                    endpoint='https://api.yurticikargo.com/health',
                                    http_status=200, message='API ulaşılabilir', account_valid=True)

    def parse_webhook(self, raw_body: dict) -> WebhookPayload:
        import pytz
        return WebhookPayload(
            tracking_no=raw_body.get('takipNo', ''),
            carrier_raw_status=raw_body.get('durum', ''),
            customer_name=raw_body.get('alici', ''),
            timestamp=datetime.now(),
        )

    def validate_webhook_signature(self, payload: str, signature: str, secret: str) -> bool:
        expected = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature)


registry.register('YURTICI', YurticiAdapter())
