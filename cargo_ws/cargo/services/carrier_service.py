from ..models import Carrier, CarrierService, CarrierCapability, CarrierStatusEnum
from .adapters.registry import registry
from .adapters.base import ConnectionTestResult


class CarrierServiceLogic:
    """Business logic for carrier CRUD and management."""

    @staticmethod
    def add_carrier(data: dict) -> Carrier:
        carrier = Carrier(
            code=data['code'], name=data['name'],
            adapter_name=data.get('adapterName', data['code'] + 'Adapter'),
            active=data.get('active', True),
            website=data.get('website', ''),
            auth_type=data.get('credentials', {}).get('authType', 'API_KEY'),
            api_key_enc=data.get('credentials', {}).get('apiKey', ''),
            api_secret_enc=data.get('credentials', {}).get('apiSecret', ''),
            account_number=data.get('credentials', {}).get('accountNumber', ''),
            endpoint=data.get('credentials', {}).get('endpoint', ''),
            webhook_secret_enc=data.get('credentials', {}).get('webhookSecret', ''),
            timeout_ms=data.get('settings', {}).get('timeoutMs', 10000),
            retry_max_attempts=data.get('settings', {}).get('retryMaxAttempts', 3),
            retry_delay_ms=data.get('settings', {}).get('retryDelayMs', 1000),
            rate_limit_per_min=data.get('settings', {}).get('rateLimitPerMinute', 50),
        )
        carrier.save()

        for svc in data.get('services', []):
            CarrierService.objects.create(
                carrier=carrier, code=svc['code'], name=svc['name'],
                description=svc.get('description', ''),
                max_weight=svc.get('maxWeight'), zones=svc.get('zones', []),
                transit_days=svc.get('transitDays'), features=svc.get('features', []),
                active=svc.get('active', True),
            )

        caps = data.get('capabilities', {})
        CarrierCapability.objects.create(
            carrier=carrier,
            label_formats=caps.get('labelFormats', ['PDF']),
            features=caps.get('features', []),
        )
        return carrier

    @staticmethod
    def test_connection(carrier_code: str) -> ConnectionTestResult:
        adapter = registry.get(carrier_code)
        if not adapter:
            raise ValueError(f"Adapter for '{carrier_code}' not found")
        result = adapter.test_connection()
        Carrier.objects.filter(code=carrier_code).update(
            status=result.status, last_tested_at=result.tested_at if hasattr(result, 'tested_at') else None)
        return result

    @staticmethod
    def update_credentials(carrier_code: str, data: dict) -> Carrier:
        carrier = Carrier.objects.get(code=carrier_code)
        if 'apiKey' in data:
            carrier.api_key_enc = data['apiKey']
        if 'apiSecret' in data:
            carrier.api_secret_enc = data['apiSecret']
        if 'webhookSecret' in data:
            carrier.webhook_secret_enc = data['webhookSecret']
        carrier.status = CarrierStatusEnum.PENDING_TEST
        carrier.save()
        return carrier
