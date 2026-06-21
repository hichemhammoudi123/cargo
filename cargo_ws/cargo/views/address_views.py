from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..serializers import AddressValidateSerializer
from ..services.address_service import AddressService


@api_view(['POST'])
def validate_address(request):
    serializer = AddressValidateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    try:
        result = AddressService.validate_address(serializer.validated_data)
        return Response({'success': True, 'data': result})
    except ValueError as e:
        return Response({'success': False, 'error': {'code': 'VALIDATION_ERROR', 'message': str(e)}},
                        status=status.HTTP_400_BAD_REQUEST)
