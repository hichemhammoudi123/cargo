from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from ..models import Shipment, ShipmentStatus
from ..serializers import (
    ShipmentCreateSerializer, ShipmentUpdateSerializer, ShipmentListSerializer,
    ShipmentDetailSerializer, LabelRequestSerializer,
)
from ..services.shipment_service import ShipmentService
import datetime


def create_shipment(request):
    serializer = ShipmentCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    try:
        shipment = ShipmentService.create_shipment(serializer.validated_data)
    except ValueError as e:
        return Response({'success': False, 'error': {'code': 'VALIDATION_ERROR', 'message': str(e)}},
                        status=status.HTTP_400_BAD_REQUEST)

    detail_serializer = ShipmentDetailSerializer(shipment)
    return Response({'success': True, 'data': detail_serializer.data}, status=status.HTTP_201_CREATED)


def list_shipments(request):
    queryset = Shipment.objects.select_related('carrier', 'sender', 'recipient').all()

    status_filter = request.query_params.get('status')
    if status_filter:
        queryset = queryset.filter(internal_status=status_filter.upper())

    carrier = request.query_params.get('carrier')
    if carrier:
        queryset = queryset.filter(carrier__code=carrier.upper())

    from_date = request.query_params.get('from')
    if from_date:
        queryset = queryset.filter(created_at__gte=from_date)

    to_date = request.query_params.get('to')
    if to_date:
        queryset = queryset.filter(created_at__lte=to_date)

    q = request.query_params.get('q')
    if q:
        queryset = queryset.filter(reference__icontains=q)

    page = int(request.query_params.get('page', 1))
    limit = int(request.query_params.get('limit', 20))
    start = (page - 1) * limit
    end = start + limit
    total = queryset.count()

    page_qs = queryset[start:end]
    serializer = ShipmentListSerializer(page_qs, many=True)
    return Response({
        'success': True,
        'data': serializer.data,
        'pagination': {'page': page, 'limit': limit, 'total': total},
    })


def shipment_detail(request, id):
    shipment = get_object_or_404(Shipment.objects.select_related('carrier', 'sender', 'recipient'), id=id)
    serializer = ShipmentDetailSerializer(shipment)
    return Response({'success': True, 'data': serializer.data})


def update_shipment(request, id):
    shipment = get_object_or_404(Shipment, id=id)
    if shipment.status != ShipmentStatus.SUBMITTED:
        return Response({'success': False, 'error': {'code': 'INVALID_STATUS',
                        'message': 'Can only update shipments in SUBMITTED status'}},
                        status=status.HTTP_409_CONFLICT)

    serializer = ShipmentUpdateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    if 'reference' in data:
        shipment.reference = data['reference']
    if 'options' in data:
        opts = data['options']
        if 'signatureRequired' in opts:
            shipment.signature_required = opts['signatureRequired']
    shipment.save()

    return Response({'success': True, 'data': {'id': shipment.id, 'reference': shipment.reference,
                                                'updatedAt': shipment.updated_at.isoformat()}})


def delete_shipment(request, id):
    shipment = get_object_or_404(Shipment, id=id)
    if shipment.status not in (ShipmentStatus.SUBMITTED, ShipmentStatus.DRAFT):
        return Response({'success': False, 'error': {'code': 'INVALID_STATUS',
                        'message': 'Can only delete shipments in DRAFT or SUBMITTED status'}},
                        status=status.HTTP_409_CONFLICT)
    shipment.delete()
    return Response({'success': True, 'data': {'deleted': True}})


@api_view(['POST'])
def cancel_shipment(request, id):
    shipment = get_object_or_404(Shipment, id=id)
    if shipment.status == ShipmentStatus.DELIVERED:
        return Response({'success': False, 'error': {'code': 'ALREADY_DELIVERED',
                        'message': 'Cannot cancel a delivered shipment'}},
                        status=status.HTTP_409_CONFLICT)
    if shipment.status in (ShipmentStatus.CANCELLED,):
        return Response({'success': False, 'error': {'code': 'ALREADY_CANCELLED',
                        'message': 'Shipment is already cancelled'}},
                        status=status.HTTP_409_CONFLICT)

    try:
        shipment = ShipmentService.cancel_shipment(id)
    except ValueError as e:
        return Response({'success': False, 'error': {'code': 'CANCEL_FAILED', 'message': str(e)}},
                        status=status.HTTP_400_BAD_REQUEST)

    return Response({
        'success': True,
        'data': {
            'id': shipment.id,
            'internalStatus': shipment.internal_status,
            'carrierStatus': shipment.carrier_status,
            'cancelledAt': shipment.cancelled_at.isoformat() if shipment.cancelled_at else None,
        }
    })


@api_view(['POST'])
def generate_label(request, id):
    shipment = get_object_or_404(Shipment, id=id)
    serializer = LabelRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    fmt = serializer.validated_data.get('format', 'PDF')

    from ..services.adapters.registry import registry
    adapter = registry.get(shipment.carrier.code)
    if adapter:
        label = adapter.get_label(shipment.carrier_tracking_number, fmt)
    else:
        label = {'labelUrl': '', 'format': fmt, 'size': 'A6'}

    return Response({
        'success': True,
        'data': {
            'labelUrl': label.get('labelUrl', ''),
            'format': label.get('format', fmt),
            'size': label.get('size', 'A6'),
            'generatedAt': datetime.datetime.now().isoformat(),
        }
    })
