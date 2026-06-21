from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from ..models import Carrier, CarrierService, CarrierCapability, CarrierStatusEnum
from ..serializers import (
    CarrierListSerializer, CarrierDetailSerializer, CarrierAddSerializer,
    CarrierUpdateSerializer, CarrierToggleSerializer, CredentialsUpdateSerializer,
    CarrierServiceAddSerializer,
)
from ..services.carrier_service import CarrierServiceLogic


def add_carrier(request):
    serializer = CarrierAddSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    if Carrier.objects.filter(code=serializer.validated_data['code'].upper()).exists():
        return Response({'success': False, 'error': {'code': 'DUPLICATE', 'message': 'Carrier already exists'}},
                        status=status.HTTP_409_CONFLICT)
    carrier = CarrierServiceLogic.add_carrier(serializer.validated_data)
    return Response({
        'success': True,
        'data': {
            'code': carrier.code,
            'name': carrier.name,
            'adapterName': carrier.adapter_name,
            'active': carrier.active,
            'status': carrier.status,
            'message': 'Carrier added. Run a connection test before using.',
        }
    }, status=status.HTTP_201_CREATED)


def list_carriers(request):
    queryset = Carrier.objects.prefetch_related('services').all()
    active = request.query_params.get('active')
    if active and active.lower() == 'true':
        queryset = queryset.filter(active=True)
    feature = request.query_params.get('feature')
    if feature:
        queryset = queryset.filter(capabilities__features__icontains=feature)
    serializer = CarrierListSerializer(queryset, many=True)
    return Response({
        'success': True,
        'data': serializer.data,
        'pagination': {'page': 1, 'limit': len(serializer.data), 'total': len(serializer.data)},
    })


def carrier_detail(request, code):
    carrier = get_object_or_404(Carrier.objects.prefetch_related('services'), code=code.upper())
    serializer = CarrierDetailSerializer(carrier)
    return Response({'success': True, 'data': serializer.data})


def update_carrier(request, code):
    carrier = get_object_or_404(Carrier, code=code.upper())
    serializer = CarrierUpdateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data
    if 'active' in data:
        carrier.active = data['active']
    if 'settings' in data:
        s = data['settings']
        if 'timeoutMs' in s:
            carrier.timeout_ms = s['timeoutMs']
        if 'retryMaxAttempts' in s:
            carrier.retry_max_attempts = s['retryMaxAttempts']
    carrier.save()
    return Response({'success': True, 'data': {'code': carrier.code, 'updated': True}})


def delete_carrier(request, code):
    carrier = get_object_or_404(Carrier, code=code.upper())
    carrier.delete()
    return Response({'success': True, 'data': {'deleted': True}})


@api_view(['PATCH'])
def toggle_carrier(request, code):
    carrier = get_object_or_404(Carrier, code=code.upper())
    serializer = CarrierToggleSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    carrier.active = serializer.validated_data['active']
    carrier.save()
    from ..services.adapters.registry import registry
    if carrier.active:
        registry.get(carrier.code)
    return Response({
        'success': True,
        'data': {
            'code': carrier.code,
            'active': carrier.active,
            'deactivatedAt': None if carrier.active else carrier.created_at.isoformat(),
        }
    })


@api_view(['POST'])
def test_carrier_connection(request, code):
    carrier = get_object_or_404(Carrier, code=code.upper())
    try:
        result = CarrierServiceLogic.test_connection(code.upper())
        return Response({
            'success': True,
            'data': {
                'status': result.status,
                'latencyMs': result.latency_ms,
                'testedAt': None,
                'endpoint': result.endpoint,
                'details': {
                    'httpStatus': result.http_status,
                    'message': result.message,
                    'accountValid': result.account_valid,
                },
            }
        })
    except Exception as e:
        return Response({
            'success': False,
            'error': {
                'code': 'CARRIER_CONNECTION_FAILED',
                'message': str(e),
                'details': {'httpStatus': 0, 'reason': str(e)},
            }
        }, status=status.HTTP_502_BAD_GATEWAY)


@api_view(['PUT'])
def update_credentials(request, code):
    carrier = get_object_or_404(Carrier, code=code.upper())
    serializer = CredentialsUpdateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    updated_carrier = CarrierServiceLogic.update_credentials(code.upper(), serializer.validated_data)
    return Response({
        'success': True,
        'data': {
            'code': updated_carrier.code,
            'credentialsUpdatedAt': updated_carrier.credentials_updated_at.isoformat(),
            'message': 'Credentials updated. Re-test connection.',
        }
    })


@api_view(['POST'])
def add_carrier_service(request, code):
    carrier = get_object_or_404(Carrier, code=code.upper())
    serializer = CarrierServiceAddSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data
    svc, created = CarrierService.objects.update_or_create(
        carrier=carrier,
        code=data['code'],
        defaults={
            'name': data['name'],
            'description': data.get('description', ''),
            'max_weight': data.get('maxWeight'),
            'zones': data.get('zones', []),
            'transit_days': data.get('transitDays'),
            'features': data.get('features', []),
            'active': data.get('active', True),
        }
    )
    return Response({'success': True, 'data': {'code': svc.code, 'name': svc.name, 'active': svc.active}},
                    status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
