import re
from decimal import Decimal
from ..models import Shipment, Package, Address, ShipmentStatus, InternalStatus
from .adapters.base import ShipmentInput, AddressData, PackageData
from .adapters.registry import registry


def _to_snake(d: dict) -> dict:
    return {re.sub(r'(?<!^)(?=[A-Z])', '_', k).lower(): v for k, v in d.items()}


class ShipmentService:
    """Business logic for shipment lifecycle."""

    @staticmethod
    def create_shipment(data: dict) -> Shipment:
        carrier_code = data['carrierCode']
        adapter = registry.get_or_raise(carrier_code)

        # Build input
        sender_data = data.get('sender', {})
        recipient_data = data.get('recipient', {})

        sender = Address.objects.create(
            company=sender_data.get('company', ''),
            contact_name=sender_data.get('contactName', ''),
            email=sender_data.get('email', ''),
            phone=sender_data.get('phone', ''),
            country=sender_data.get('country', ''),
            zip_code=sender_data.get('zipCode', ''),
            city=sender_data.get('city', ''),
            address=sender_data.get('address', ''),
        )
        recipient = Address.objects.create(
            company=recipient_data.get('company', ''),
            contact_name=recipient_data.get('contactName', ''),
            email=recipient_data.get('email', ''),
            phone=recipient_data.get('phone', ''),
            country=recipient_data.get('country', ''),
            zip_code=recipient_data.get('zipCode', ''),
            city=recipient_data.get('city', ''),
            address=recipient_data.get('address', ''),
        )

        options = data.get('options', {})
        insurance = options.get('insurance', {})

        input_data = ShipmentInput(
            carrier_code=carrier_code,
            service_code=data.get('serviceCode', ''),
            reference=data.get('reference', ''),
            sender=AddressData(**_to_snake(sender_data)),
            recipient=AddressData(**_to_snake(recipient_data)),
            packages=[PackageData(**_to_snake(pkg)) for pkg in data.get('packages', [])],
            insurance_amount=insurance.get('amount'),
            insurance_currency=insurance.get('currency', 'EUR'),
            signature_required=options.get('signatureRequired', True),
            saturday_delivery=options.get('saturdayDelivery', False),
        )

        # Call adapter
        response = adapter.create_shipment(input_data)

        # Persist
        shipment = Shipment.objects.create(
            status=ShipmentStatus.SUBMITTED,
            internal_status=InternalStatus.PENDING,
            carrier_status='Shipment information received',
            carrier_id=carrier_code,
            reference=data.get('reference', ''),
            carrier_tracking_number=response.carrier_tracking_number,
            carrier_shipment_id=response.carrier_shipment_id,
            label_url=response.label_url,
            label_format=response.label_format,
            tracking_url=response.tracking_url,
            price_total=Decimal(str(response.price_total)) if response.price_total else None,
            price_currency=response.price_currency,
            price_breakdown=response.price_breakdown,
            sender=sender,
            recipient=recipient,
            insurance_amount=Decimal(str(insurance.get('amount', 0))) if insurance.get('amount') else None,
            insurance_currency=insurance.get('currency', 'EUR'),
            signature_required=options.get('signatureRequired', True),
            saturday_delivery=options.get('saturdayDelivery', False),
        )

        for pkg_data in data.get('packages', []):
            Package.objects.create(
                shipment=shipment,
                reference=pkg_data.get('reference', ''),
                description=pkg_data.get('description', ''),
                weight=Decimal(str(pkg_data['weight'])),
                weight_unit=pkg_data.get('weightUnit', 'KG'),
                length=Decimal(str(pkg_data.get('length', 0))) if pkg_data.get('length') else None,
                width=Decimal(str(pkg_data.get('width', 0))) if pkg_data.get('width') else None,
                height=Decimal(str(pkg_data.get('height', 0))) if pkg_data.get('height') else None,
                dim_unit=pkg_data.get('dimUnit', 'CM'),
                declared_value=Decimal(str(pkg_data.get('declaredValue', 0))) if pkg_data.get('declaredValue') else None,
                declared_currency=pkg_data.get('declaredCurrency', 'EUR'),
                tracking_number=response.carrier_tracking_number,
            )

        return shipment

    @staticmethod
    def cancel_shipment(shipment_id: str) -> Shipment:
        shipment = Shipment.objects.get(id=shipment_id)
        if shipment.status in (ShipmentStatus.DELIVERED, ShipmentStatus.CANCELLED):
            raise ValueError(f"Cannot cancel shipment in status '{shipment.status}'")

        adapter = registry.get(shipment.carrier.code)
        if adapter and shipment.carrier_tracking_number:
            adapter.cancel_shipment(shipment.carrier_tracking_number)

        shipment.status = ShipmentStatus.CANCELLED
        shipment.internal_status = InternalStatus.CANCELLED
        shipment.carrier_status = 'Cancelled'
        shipment.save()
        return shipment
