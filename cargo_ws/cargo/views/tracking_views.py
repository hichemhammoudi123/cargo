import hashlib
import hmac
import logging
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from ..models import Shipment, Carrier
from ..services.tracking_service import TrackingService
from ..services.adapters.registry import registry

logger = logging.getLogger(__name__)


@api_view(['GET'])
def get_tracking(request, id):
    shipment = get_object_or_404(Shipment.objects.select_related('carrier'), id=id)
    try:
        tracking_data = TrackingService.get_tracking(id)
        return Response({'success': True, 'data': tracking_data})
    except Exception as e:
        return Response({
            'success': False,
            'error': {'code': 'TRACKING_ERROR', 'message': str(e)},
        }, status=status.HTTP_502_BAD_GATEWAY)


@api_view(['POST'])
def webhook_receive(request, carrier_code):
    """
    Inbound webhook from carriers.
    Always returns 200 to the carrier (non-200 = retry).
    """
    carrier_code = carrier_code.upper()
    raw_body = request.data

    # HMAC signature validation
    signature = request.META.get('HTTP_X_SIGNATURE', '')
    try:
        carrier = Carrier.objects.get(code=carrier_code)
        secret = carrier.webhook_secret_enc
        if secret and signature:
            adapter = registry.get(carrier_code)
            if adapter:
                payload_str = request.body.decode('utf-8') if hasattr(request, 'body') else str(raw_body)
                if not adapter.validate_webhook_signature(payload_str, signature, secret):
                    logger.warning(f"Invalid webhook signature for {carrier_code}")
    except Carrier.DoesNotExist:
        pass

    try:
        result = TrackingService.process_webhook(carrier_code, raw_body)
        logger.info(f"Webhook processed: {carrier_code} -> {result.get('internalStatus')}")
    except Exception as e:
        logger.error(f"Webhook processing error for {carrier_code}: {e}")
        # Always return 200 to carrier
        pass

    return Response({'success': True, 'message': 'Webhook processed successfully'})
