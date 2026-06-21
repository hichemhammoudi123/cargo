from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from ..models import Pickup
from ..serializers import PickupCreateSerializer, PickupListSerializer, PickupDetailSerializer, PickupUpdateSerializer
from ..services.pickup_service import PickupService


def schedule_pickup(request):
    serializer = PickupCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    try:
        pickup = PickupService.schedule_pickup(serializer.validated_data)
    except ValueError as e:
        return Response({'success': False, 'error': {'code': 'PICKUP_ERROR', 'message': str(e)}},
                        status=status.HTTP_400_BAD_REQUEST)

    return Response({
        'success': True,
        'data': {
            'id': pickup.id,
            'carrierCode': pickup.carrier.code,
            'carrierPickupId': pickup.carrier_pickup_id,
            'status': pickup.status,
            'pickupDate': pickup.pickup_date.isoformat(),
            'confirmationNumber': pickup.confirmation_number,
        }
    }, status=status.HTTP_201_CREATED)


def list_pickups(request):
    queryset = Pickup.objects.select_related('carrier').all().order_by('-created_at')
    page = int(request.query_params.get('page', 1))
    limit = int(request.query_params.get('limit', 20))
    start = (page - 1) * limit
    end = start + limit
    total = queryset.count()
    page_qs = queryset[start:end]
    serializer = PickupListSerializer(page_qs, many=True)
    return Response({
        'success': True,
        'data': serializer.data,
        'pagination': {'page': page, 'limit': limit, 'total': total},
    })


def pickup_detail(request, id):
    pickup = get_object_or_404(Pickup.objects.select_related('carrier'), id=id)
    serializer = PickupDetailSerializer(pickup)
    return Response({'success': True, 'data': serializer.data})


def update_pickup(request, id):
    pickup = get_object_or_404(Pickup.objects.select_related('carrier'), id=id)
    if pickup.status == 'CANCELLED':
        return Response({'success': False, 'error': {'code': 'ALREADY_CANCELLED',
                        'message': 'Cannot update a cancelled pickup'}},
                        status=status.HTTP_409_CONFLICT)
    serializer = PickupUpdateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data
    if 'pickupDate' in data:
        pickup.pickup_date = data['pickupDate']
    if 'readyTime' in data:
        pickup.ready_time = data['readyTime']
    if 'closeTime' in data:
        pickup.close_time = data['closeTime']
    if 'specialInstructions' in data:
        pickup.special_instructions = data['specialInstructions']
    pickup.save()
    detail_serializer = PickupDetailSerializer(pickup)
    return Response({'success': True, 'data': detail_serializer.data})


def delete_pickup(request, id):
    pickup = get_object_or_404(Pickup.objects.select_related('carrier'), id=id)
    if pickup.status == 'CANCELLED':
        return Response({'success': False, 'error': {'code': 'ALREADY_CANCELLED',
                        'message': 'Pickup is already cancelled'}},
                        status=status.HTTP_409_CONFLICT)
    try:
        pickup = PickupService.cancel_pickup(id)
    except ValueError as e:
        return Response({'success': False, 'error': {'code': 'CANCEL_ERROR', 'message': str(e)}},
                        status=status.HTTP_400_BAD_REQUEST)
    return Response({
        'success': True,
        'data': {
            'id': pickup.id,
            'status': pickup.status,
            'cancelledAt': pickup.cancelled_at.isoformat() if pickup.cancelled_at else None,
        }
    })


@api_view(['POST'])
def cancel_pickup(request, id):
    pickup = get_object_or_404(Pickup.objects.select_related('carrier'), id=id)
    try:
        pickup = PickupService.cancel_pickup(id)
    except ValueError as e:
        return Response({'success': False, 'error': {'code': 'CANCEL_ERROR', 'message': str(e)}},
                        status=status.HTTP_400_BAD_REQUEST)

    return Response({
        'success': True,
        'data': {
            'id': pickup.id,
            'status': pickup.status,
            'cancelledAt': pickup.cancelled_at.isoformat() if pickup.cancelled_at else None,
        }
    })
