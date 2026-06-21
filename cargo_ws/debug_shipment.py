import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'cargo_service.settings'
import django
django.setup()
from django.test.utils import setup_test_environment
setup_test_environment()
from django.test import Client
c = Client()

body = '{"carrierCode":"DHL","serviceCode":"DHL_EXP","reference":"CMD-2026-001234","sender":{"company":"TechCorp SAS","contactName":"Jean Dupont","email":"jean@techcorp.fr","phone":"+33123456789","country":"FR","zipCode":"75001","city":"Paris","address":"12 Rue de Rivoli"},"recipient":{"company":"Berlin GmbH","contactName":"Hans Schmidt","email":"hans@berlin.de","phone":"+4930123456","country":"DE","zipCode":"10115","city":"Berlin","address":"Friedrichstraße 100"},"packages":[{"reference":"COLIS-001","description":"Composants électroniques","weight":2.5,"weightUnit":"KG","length":30,"width":20,"height":15,"dimUnit":"CM","declaredValue":500.00,"declaredCurrency":"EUR"}],"options":{"insurance":{"amount":500.00,"currency":"EUR"},"signatureRequired":true,"saturdayDelivery":false}}'
r = c.post('/api/v1/cargo/shipments', body, content_type='application/json')
import json
print('Status:', r.status_code)
data = json.loads(r.content)
print(json.dumps(data, indent=2, ensure_ascii=False))
