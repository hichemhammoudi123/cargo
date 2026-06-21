from .adapters.registry import registry
from .adapters.base import RateRequest, PackageData


def _to_snake(d: dict) -> dict:
    import re
    return {re.sub(r'(?<!^)(?=[A-Z])', '_', k).lower(): v for k, v in d.items()}


class RateService:

    @staticmethod
    def get_rates(data: dict) -> list:
        sender = data.get('sender', {})
        recipient = data.get('recipient', {})
        packages_data = data.get('packages', [])
        carrier_codes = data.get('options', {}).get('carrierCodes', [])
        service_type = data.get('options', {}).get('serviceType', 'EXPRESS')

        request = RateRequest(
            sender_country=sender.get('country', ''),
            sender_zip=sender.get('zipCode', ''),
            sender_city=sender.get('city', ''),
            recipient_country=recipient.get('country', ''),
            recipient_zip=recipient.get('zipCode', ''),
            recipient_city=recipient.get('city', ''),
            packages=[PackageData(**_to_snake(p)) for p in packages_data],
            service_type=service_type,
        )

        carriers = registry.get_active()
        if carrier_codes:
            carriers = [c for c in carriers if c.code.upper() in [cc.upper() for cc in carrier_codes]]

        all_offers = []
        errors = []

        for adapter in carriers:
            try:
                offers = adapter.get_rates(request)
                all_offers.extend(offers)
            except Exception as e:
                errors.append({'carrierCode': adapter.code, 'message': str(e)})

        all_offers.sort(key=lambda o: o.total_price)

        result = [
            {
                'carrierCode': o.carrier_code,
                'carrierName': o.carrier_name,
                'serviceCode': o.service_code,
                'serviceName': o.service_name,
                'totalPrice': o.total_price,
                'currency': o.currency,
                'estimatedTransitDays': o.estimated_transit_days,
                'estimatedDeliveryDate': o.estimated_delivery_date,
                'guaranteed': o.guaranteed,
                'breakdown': o.breakdown,
            }
            for o in all_offers
        ]

        return {'data': result, 'errors': errors if errors else None}
