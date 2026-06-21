from .adapters.registry import registry
from .adapters.base import AddressData


class AddressService:

    @staticmethod
    def validate_address(data: dict) -> dict:
        carrier_code = data.get('carrierCode', 'DHL')
        adapter = registry.get_or_raise(carrier_code)

        address = AddressData(
            country=data.get('country', ''),
            zip_code=data.get('zipCode', ''),
            city=data.get('city', ''),
            address=data.get('address', ''),
        )

        result = adapter.validate_address(address)

        return {
            'valid': result.get('valid', False),
            'normalizedAddress': result.get('normalizedAddress', {}),
            'suggestions': result.get('suggestions', []),
            'carrierValidation': {
                'code': 'VALID' if result.get('valid') else 'INVALID',
                'message': 'Address is valid' if result.get('valid') else 'Address is invalid',
            },
        }
