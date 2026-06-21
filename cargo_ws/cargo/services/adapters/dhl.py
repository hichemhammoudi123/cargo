import hashlib
import hmac
import time
from datetime import datetime
from .base import (CarrierAdapter, ShipmentInput, CarrierShipmentResponse, RateRequest, RateOffer,
                   CarrierTrackingData, TrackingEventData, PickupRequest, CarrierPickupResponse,
                   ConnectionTestResult, WebhookPayload, AddressData)
from .registry import registry


class DhlAdapter(CarrierAdapter):
    @property
    def code(self) -> str: return 'DHL'
    @property
    def name(self) -> str: return 'DHL Express'

    def create_shipment(self, input_data: ShipmentInput) -> CarrierShipmentResponse:
        dhl_payload = {
            'product': input_data.service_code,
            'sender': {
                'addressStreet': input_data.sender.address,
                'postalCode': input_data.sender.zip_code,
                'city': input_data.sender.city,
                'countryCode': input_data.sender.country,
            },
            'recipient': {
                'addressStreet': input_data.recipient.address,
                'postalCode': input_data.recipient.zip_code,
                'city': input_data.recipient.city,
                'countryCode': input_data.recipient.country,
            },
            'pieces': [{'weight': p.weight, 'weightUnit': p.weight_unit} for p in input_data.packages],
        }
        # Simulate API call
        return CarrierShipmentResponse(
            carrier_tracking_number='DHL' + str(int(time.time()))[-8:],
            carrier_shipment_id='DE-' + str(int(time.time())),
            label_url='https://api.dhl.com/labels/dummy.pdf',
            tracking_url='https://www.dhl.com/track/dummy',
            price_total=45.30,
            price_currency='EUR',
            price_breakdown=[
                {'type': 'BASE', 'label': 'Transport', 'amount': 38.00},
                {'type': 'FUEL', 'label': 'Fuel surcharge', 'amount': 5.30},
                {'type': 'INSURANCE', 'label': 'Insurance', 'amount': 2.00},
            ],
            estimated_delivery_date=datetime.now(),
            raw_response=dhl_payload,
        )

    def cancel_shipment(self, tracking_number: str) -> dict:
        return {'status': 'CANCELLED', 'trackingNumber': tracking_number}

    def get_label(self, tracking_number: str, label_format: str = 'PDF') -> dict:
        return {
            'labelUrl': f'https://api.dhl.com/labels/{tracking_number}.pdf',
            'format': label_format,
            'size': 'A6',
            'generatedAt': datetime.now().isoformat(),
        }

    def get_rates(self, request: RateRequest) -> list[RateOffer]:
        return [
            RateOffer(carrier_code='DHL', carrier_name='DHL Express',
                      service_code='DHL_EXPRESS_WORLDWIDE', service_name='Express Worldwide',
                      total_price=45.30, currency='EUR', estimated_transit_days=2,
                      breakdown=[{'type': 'BASE', 'amount': 38.00}, {'type': 'FUEL', 'amount': 5.30}])
        ]

    def track(self, tracking_number: str) -> CarrierTrackingData:
        return CarrierTrackingData(
            tracking_number=tracking_number,
            current_status='IN_PROGRESS',
            events=[
                TrackingEventData(code='PENDING', description='Shipment information received',
                                  location='Paris, France', timestamp=datetime.now(), raw_status='Shipment information received'),
                TrackingEventData(code='PICKED_UP', description='Pickup scanned',
                                  location='Paris, France', timestamp=datetime.now(), raw_status='Pickup scanned'),
                TrackingEventData(code='IN_PROGRESS', description='Departed from transit hub',
                                  location='Frankfurt, Germany', timestamp=datetime.now(), raw_status='Departed from transit hub'),
            ],
            raw_response={'trackingNumber': tracking_number},
        )

    def track_batch(self, tracking_numbers: list[str]) -> dict:
        return {tn: self.track(tn) for tn in tracking_numbers}

    def schedule_pickup(self, request: PickupRequest) -> CarrierPickupResponse:
        return CarrierPickupResponse(
            carrier_pickup_id='DHL-PICKUP-' + str(int(time.time()))[-5:],
            confirmation_number='CONF-DHL-' + str(int(time.time()))[-6:],
        )

    def cancel_pickup(self, pickup_id: str) -> dict:
        return {'status': 'CANCELLED', 'pickupId': pickup_id}

    def validate_address(self, address: AddressData) -> dict:
        return {
            'valid': True,
            'normalizedAddress': {'country': address.country, 'zipCode': address.zip_code,
                                  'city': address.city.upper(), 'address': address.address.upper()},
            'suggestions': [],
        }

    def test_connection(self) -> ConnectionTestResult:
        return ConnectionTestResult(status='CONNECTED', latency_ms=120, endpoint='https://api.dhl.com/health',
                                    http_status=200, message='API is reachable', account_valid=True)

    def parse_webhook(self, raw_body: dict) -> WebhookPayload:
        return WebhookPayload(
            tracking_no=raw_body.get('trackingNumber', ''),
            carrier_raw_status=raw_body.get('status', ''),
            customer_name=raw_body.get('signedBy', ''),
            timestamp=datetime.now(),
            location=raw_body.get('location', {}).get('city', ''),
        )

    def validate_webhook_signature(self, payload: str, signature: str, secret: str) -> bool:
        expected = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature)


registry.register('DHL', DhlAdapter())
