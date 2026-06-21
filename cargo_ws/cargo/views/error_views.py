from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
import traceback


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        if isinstance(exc, ValidationError):
            code = 'VALIDATION_ERROR'
        else:
            code = getattr(exc, 'default_code', 'UNKNOWN_ERROR')
        return Response({
            'success': False,
            'error': {
                'code': code,
                'message': str(exc),
            }
        }, status=response.status_code)

    # Handle unhandled exceptions
    traceback.print_exc()
    return Response({
        'success': False,
        'error': {
            'code': 'INTERNAL_ERROR',
            'message': 'An internal error occurred',
        }
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
