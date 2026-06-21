from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from ..models import Shipment
from . import shipment_views, carrier_views, pickup_views


@api_view(['GET', 'POST'])
def shipments_list(request):
    if request.method == 'GET':
        return shipment_views.list_shipments(request)
    return shipment_views.create_shipment(request)


@api_view(['GET', 'PUT', 'DELETE'])
def shipments_detail(request, id):
    if request.method == 'GET':
        return shipment_views.shipment_detail(request, id)
    elif request.method == 'PUT':
        return shipment_views.update_shipment(request, id)
    return shipment_views.delete_shipment(request, id)


@api_view(['GET', 'POST'])
def carriers_list(request):
    if request.method == 'GET':
        return carrier_views.list_carriers(request)
    return carrier_views.add_carrier(request)


@api_view(['GET', 'PUT', 'DELETE'])
def carriers_detail(request, code):
    if request.method == 'GET':
        return carrier_views.carrier_detail(request, code)
    elif request.method == 'PUT':
        return carrier_views.update_carrier(request, code)
    return carrier_views.delete_carrier(request, code)


@api_view(['GET', 'POST'])
def pickups_list(request):
    if request.method == 'GET':
        return pickup_views.list_pickups(request)
    return pickup_views.schedule_pickup(request)


@api_view(['GET', 'PUT', 'DELETE'])
def pickups_detail(request, id):
    if request.method == 'GET':
        return pickup_views.pickup_detail(request, id)
    elif request.method == 'PUT':
        return pickup_views.update_pickup(request, id)
    return pickup_views.delete_pickup(request, id)
