from django.contrib import admin
from .models import Carrier, CarrierService, CarrierCapability, Shipment, Package, TrackingEvent, Pickup, Address

admin.site.register(Carrier)
admin.site.register(CarrierService)
admin.site.register(CarrierCapability)
admin.site.register(Shipment)
admin.site.register(Package)
admin.site.register(TrackingEvent)
admin.site.register(Pickup)
admin.site.register(Address)
