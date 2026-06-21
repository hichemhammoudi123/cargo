from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..serializers import RateRequestSerializer
from ..services.rate_service import RateService


@api_view(['POST'])
def compare_rates(request):
    serializer = RateRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    result = RateService.get_rates(serializer.validated_data)
    return Response({'success': True, 'data': result['data'], 'errors': result['errors']})
