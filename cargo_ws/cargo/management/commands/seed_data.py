from django.core.management.base import BaseCommand
from cargo.models import Carrier, CarrierService, CarrierCapability
from cargo.services.adapters.registry import registry


CARRIERS = [
    {
        'code': 'DHL',
        'name': 'DHL Express',
        'website': 'https://www.dhl.com',
        'status': 'CONNECTED',
        'timeout_ms': 30000,
        'services': [
            {'code': 'DHL_EXP', 'name': 'DHL Express Worldwide', 'description': 'Express international shipping', 'maxWeight': 70, 'transitDays': 2},
            {'code': 'DHL_ECO', 'name': 'DHL Economy Select', 'description': 'Economy international shipping', 'maxWeight': 70, 'transitDays': 5},
            {'code': 'DHL_DOM', 'name': 'DHL Domestic Express', 'description': 'Domestic express delivery', 'maxWeight': 50, 'transitDays': 1},
        ],
        'capabilities': {'label_formats': ['PDF', 'ZPL', 'PNG'], 'features': ['insurance', 'signature', 'saturday_delivery']},
    },
    {
        'code': 'UPS',
        'name': 'UPS United Parcel Service',
        'website': 'https://www.ups.com',
        'status': 'CONNECTED',
        'timeout_ms': 30000,
        'services': [
            {'code': 'UPS_EXP', 'name': 'UPS Express Plus', 'description': 'Express international shipping', 'maxWeight': 70, 'transitDays': 2},
            {'code': 'UPS_SAV', 'name': 'UPS Saver', 'description': 'Economy international shipping', 'maxWeight': 70, 'transitDays': 4},
            {'code': 'UPS_DOM', 'name': 'UPS Domestic', 'description': 'Domestic delivery', 'maxWeight': 50, 'transitDays': 1},
        ],
        'capabilities': {'label_formats': ['PDF', 'ZPL'], 'features': ['insurance', 'signature']},
    },
    {
        'code': 'FEDEX',
        'name': 'FedEx Corporation',
        'website': 'https://www.fedex.com',
        'status': 'CONNECTED',
        'timeout_ms': 30000,
        'services': [
            {'code': 'FDX_INTL', 'name': 'FedEx International Priority', 'description': 'International priority shipping', 'maxWeight': 68, 'transitDays': 2},
            {'code': 'FDX_ECO', 'name': 'FedEx Economy', 'description': 'International economy shipping', 'maxWeight': 68, 'transitDays': 5},
            {'code': 'FDX_DOM', 'name': 'FedEx Domestic', 'description': 'Domestic delivery', 'maxWeight': 50, 'transitDays': 1},
        ],
        'capabilities': {'label_formats': ['PDF', 'ZPL', 'PNG'], 'features': ['insurance', 'signature', 'weekend_delivery']},
    },
    {
        'code': 'YURTICI',
        'name': 'Yurtiçi Kargo',
        'website': 'https://www.yurticikargo.com',
        'status': 'CONNECTED',
        'timeout_ms': 20000,
        'services': [
            {'code': 'YT_STD', 'name': 'Standart Teslimat', 'description': 'Standard domestic delivery', 'maxWeight': 50, 'transitDays': 2},
            {'code': 'YT_FAST', 'name': 'Hızlı Teslimat', 'description': 'Express domestic delivery', 'maxWeight': 30, 'transitDays': 1},
        ],
        'capabilities': {'label_formats': ['PDF'], 'features': ['signature']},
    },
    {
        'code': 'MNG',
        'name': 'MNG Kargo',
        'website': 'https://www.mngkargo.com',
        'status': 'CONNECTED',
        'timeout_ms': 20000,
        'services': [
            {'code': 'MNG_STD', 'name': 'Standart Teslimat', 'description': 'Standard domestic delivery', 'maxWeight': 50, 'transitDays': 2},
            {'code': 'MNG_FAST', 'name': 'Ekspres Teslimat', 'description': 'Express domestic delivery', 'maxWeight': 30, 'transitDays': 1},
        ],
        'capabilities': {'label_formats': ['PDF'], 'features': ['signature']},
    },
    {
        'code': 'ARAMEX',
        'name': 'Aramex International',
        'website': 'https://www.aramex.com',
        'status': 'CONNECTED',
        'timeout_ms': 30000,
        'services': [
            {'code': 'ARAM_DOM', 'name': 'Aramex Domestic', 'description': 'Domestic delivery', 'maxWeight': 50, 'transitDays': 1},
            {'code': 'ARAM_INTL', 'name': 'Aramex International', 'description': 'International shipping', 'maxWeight': 70, 'transitDays': 3},
        ],
        'capabilities': {'label_formats': ['PDF', 'ZPL'], 'features': ['insurance', 'signature']},
    },
]


class Command(BaseCommand):
    help = 'Seed database with 6 carriers, their services, and capabilities'

    def handle(self, *args, **options):
        for data in CARRIERS:
            code = data['code']
            carrier, created = Carrier.objects.update_or_create(
                code=code,
                defaults={
                    'name': data['name'],
                    'adapter_name': code.lower().capitalize(),
                    'website': data['website'],
                    'active': True,
                    'status': data['status'],
                    'timeout_ms': data['timeout_ms'],
                }
            )
            if created:
                self.stdout.write(f'  Created carrier: {code}')
            else:
                self.stdout.write(f'  Updated carrier: {code}')

            for svc in data['services']:
                CarrierService.objects.update_or_create(
                    carrier=carrier,
                    code=svc['code'],
                    defaults={
                        'name': svc['name'],
                        'description': svc['description'],
                        'max_weight': svc['maxWeight'],
                        'transit_days': svc['transitDays'],
                        'active': True,
                    }
                )
                self.stdout.write(f'    Service: {svc["code"]}')

            CarrierCapability.objects.update_or_create(
                carrier=carrier,
                defaults=data['capabilities']
            )

        total = Carrier.objects.count()
        self.stdout.write(self.style.SUCCESS(f'Done. {total} carriers seeded.'))
