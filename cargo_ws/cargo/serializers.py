from rest_framework import serializers
from .models import Carrier, CarrierService, CarrierCapability, Shipment, Package, TrackingEvent, Pickup, Address


# ─── Address ────────────────────────────────────────────────────────────

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'


class AddressValidateSerializer(serializers.Serializer):
    country = serializers.CharField(max_length=2)
    zipCode = serializers.CharField(source='zip_code', max_length=20)
    city = serializers.CharField(max_length=100)
    address = serializers.CharField()
    carrierCode = serializers.CharField(max_length=20, default='DHL')


# ─── Package ────────────────────────────────────────────────────────────

class PackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        exclude = ['shipment']


class PackageInputSerializer(serializers.Serializer):
    reference = serializers.CharField(required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True)
    weight = serializers.FloatField()
    weightUnit = serializers.ChoiceField(choices=['KG', 'LB'], default='KG')
    length = serializers.FloatField(required=False)
    width = serializers.FloatField(required=False)
    height = serializers.FloatField(required=False)
    dimUnit = serializers.ChoiceField(choices=['CM', 'IN'], default='CM')
    declaredValue = serializers.FloatField(required=False)
    declaredCurrency = serializers.CharField(max_length=3, default='EUR')


# ─── Carrier ────────────────────────────────────────────────────────────

class CarrierServiceSerializer(serializers.ModelSerializer):
    maxWeight = serializers.FloatField(source='max_weight', read_only=True)
    maxWeightUnit = serializers.CharField(source='max_weight_unit', read_only=True)
    transitDays = serializers.IntegerField(source='transit_days', read_only=True)

    class Meta:
        model = CarrierService
        fields = ['code', 'name', 'description', 'maxWeight', 'maxWeightUnit',
                  'zones', 'transitDays', 'features', 'active']


class CarrierCapabilitySerializer(serializers.ModelSerializer):
    labelFormats = serializers.JSONField(source='label_formats', read_only=True)

    class Meta:
        model = CarrierCapability
        fields = ['labelFormats', 'features']


class CarrierListSerializer(serializers.ModelSerializer):
    adapterName = serializers.CharField(source='adapter_name', read_only=True)
    services = CarrierServiceSerializer(many=True, read_only=True)

    class Meta:
        model = Carrier
        fields = ['code', 'name', 'adapterName', 'active', 'status', 'services']


class CarrierDetailSerializer(serializers.ModelSerializer):
    adapterName = serializers.CharField(source='adapter_name', read_only=True)
    lastTestedAt = serializers.DateTimeField(source='last_tested_at', read_only=True)
    credentialsUpdatedAt = serializers.DateTimeField(source='credentials_updated_at', read_only=True)
    services = CarrierServiceSerializer(many=True, read_only=True)
    capabilities = CarrierCapabilitySerializer(read_only=True)
    settings = serializers.SerializerMethodField()

    class Meta:
        model = Carrier
        fields = ['code', 'name', 'adapterName', 'active', 'status', 'lastTestedAt',
                  'services', 'capabilities', 'settings', 'credentialsUpdatedAt']

    def get_settings(self, obj):
        return {
            'timeoutMs': obj.timeout_ms,
            'retryMaxAttempts': obj.retry_max_attempts,
            'retryDelayMs': obj.retry_delay_ms,
            'rateLimitPerMin': obj.rate_limit_per_min,
        }


class CarrierAddSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=20)
    name = serializers.CharField(max_length=100)
    adapterName = serializers.CharField(max_length=100, required=False)
    active = serializers.BooleanField(default=True)
    website = serializers.URLField(required=False, allow_blank=True)
    contact = serializers.DictField(required=False, default=dict)
    services = serializers.ListField(required=False, default=list)
    capabilities = serializers.DictField(required=False, default=dict)
    credentials = serializers.DictField(required=False, default=dict)
    settings = serializers.DictField(required=False, default=dict)


class CarrierUpdateSerializer(serializers.Serializer):
    active = serializers.BooleanField(required=False)
    settings = serializers.DictField(required=False)


class CarrierToggleSerializer(serializers.Serializer):
    active = serializers.BooleanField()
    reason = serializers.CharField(required=False, allow_blank=True)


class CredentialsUpdateSerializer(serializers.Serializer):
    authType = serializers.CharField(required=False)
    apiKey = serializers.CharField(required=False)
    apiSecret = serializers.CharField(required=False)
    webhookSecret = serializers.CharField(required=False)


class CarrierServiceAddSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=50)
    name = serializers.CharField(max_length=100)
    description = serializers.CharField(required=False, allow_blank=True)
    maxWeight = serializers.FloatField(required=False)
    maxWeightUnit = serializers.ChoiceField(choices=['KG', 'LB'], default='KG')
    zones = serializers.ListField(child=serializers.CharField(), default=list)
    transitDays = serializers.IntegerField(required=False)
    features = serializers.ListField(child=serializers.CharField(), default=list)
    active = serializers.BooleanField(default=True)


# ─── Shipment ───────────────────────────────────────────────────────────

class SenderRecipientSerializer(serializers.Serializer):
    company = serializers.CharField(required=False, allow_blank=True)
    contactName = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    country = serializers.CharField(max_length=2)
    zipCode = serializers.CharField(max_length=20)
    city = serializers.CharField(max_length=100)
    address = serializers.CharField()


class InsuranceSerializer(serializers.Serializer):
    amount = serializers.FloatField(required=False)
    currency = serializers.CharField(max_length=3, default='EUR')


class ShipmentOptionsSerializer(serializers.Serializer):
    insurance = InsuranceSerializer(required=False)
    signatureRequired = serializers.BooleanField(default=True)
    saturdayDelivery = serializers.BooleanField(default=False)


class ShipmentCreateSerializer(serializers.Serializer):
    carrierCode = serializers.CharField(max_length=20)
    serviceCode = serializers.CharField(max_length=50)
    reference = serializers.CharField(required=False, allow_blank=True)
    sender = SenderRecipientSerializer()
    recipient = SenderRecipientSerializer()
    packages = PackageInputSerializer(many=True)
    options = ShipmentOptionsSerializer(required=False)


class ShipmentUpdateSerializer(serializers.Serializer):
    reference = serializers.CharField(required=False)
    options = ShipmentOptionsSerializer(required=False)


class ShipmentListSerializer(serializers.ModelSerializer):
    internalStatus = serializers.CharField(source='internal_status', read_only=True)
    carrierStatus = serializers.CharField(source='carrier_status', read_only=True)
    carrierCode = serializers.CharField(source='carrier.code', read_only=True)
    carrierTrackingNumber = serializers.CharField(source='carrier_tracking_number', read_only=True)
    recipient = serializers.SerializerMethodField()
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)

    class Meta:
        model = Shipment
        fields = ['id', 'internalStatus', 'carrierStatus', 'carrierCode',
                  'carrierTrackingNumber', 'reference', 'recipient', 'createdAt']

    def get_recipient(self, obj):
        if obj.recipient:
            return {'company': obj.recipient.company, 'country': obj.recipient.country}
        return {}


class PackageOutSerializer(serializers.ModelSerializer):
    trackingNumber = serializers.CharField(source='tracking_number', read_only=True)

    class Meta:
        model = Package
        fields = ['reference', 'weight', 'trackingNumber']


class PriceBreakdownSerializer(serializers.Serializer):
    type = serializers.CharField()
    label = serializers.CharField()
    amount = serializers.FloatField()


class ShipmentDetailSerializer(serializers.ModelSerializer):
    internalStatus = serializers.CharField(source='internal_status', read_only=True)
    carrierStatus = serializers.CharField(source='carrier_status', read_only=True)
    carrierCode = serializers.CharField(source='carrier.code', read_only=True)
    carrierName = serializers.CharField(source='carrier.name', read_only=True)
    carrierTrackingNumber = serializers.CharField(source='carrier_tracking_number', read_only=True)
    carrierShipmentId = serializers.CharField(source='carrier_shipment_id', read_only=True)
    labelUrl = serializers.CharField(source='label_url', read_only=True)
    labelFormat = serializers.CharField(source='label_format', read_only=True)
    trackingUrl = serializers.CharField(source='tracking_url', read_only=True)
    statusHistory = serializers.SerializerMethodField(method_name='get_status_history')
    price = serializers.SerializerMethodField(method_name='get_price')
    sender = serializers.SerializerMethodField(method_name='get_sender')
    recipient = serializers.SerializerMethodField(method_name='get_recipient')
    packages = PackageOutSerializer(many=True, read_only=True)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    estimatedDeliveryDate = serializers.DateTimeField(source='estimated_delivery_date', read_only=True)

    class Meta:
        model = Shipment
        fields = ['id', 'internalStatus', 'carrierStatus', 'statusHistory',
                  'carrierCode', 'carrierName', 'carrierTrackingNumber', 'carrierShipmentId',
                  'labelUrl', 'labelFormat', 'trackingUrl', 'reference', 'price',
                  'sender', 'recipient', 'packages', 'createdAt', 'estimatedDeliveryDate']

    def get_status_history(self, obj):
        events = obj.tracking_events.all()[:10]
        return [
            {'status': e.carrier_code, 'internalStatus': e.internal_code, 'timestamp': e.timestamp.isoformat()}
            for e in events
        ]

    def get_price(self, obj):
        if obj.price_total is None:
            return None
        return {
            'total': float(obj.price_total),
            'currency': obj.price_currency,
            'breakdown': obj.price_breakdown,
        }

    def get_sender(self, obj):
        if obj.sender:
            return {'company': obj.sender.company, 'country': obj.sender.country, 'zipCode': obj.sender.zip_code}
        return {}

    def get_recipient(self, obj):
        if obj.recipient:
            return {'company': obj.recipient.company, 'country': obj.recipient.country, 'zipCode': obj.recipient.zip_code}
        return {}


class CancelShipmentSerializer(serializers.Serializer):
    pass


# ─── Label ──────────────────────────────────────────────────────────────

class LabelRequestSerializer(serializers.Serializer):
    format = serializers.ChoiceField(choices=['PDF', 'ZPL', 'PNG'], default='PDF')


# ─── Tracking ───────────────────────────────────────────────────────────

class TrackingEventOutSerializer(serializers.Serializer):
    eventId = serializers.CharField()
    internalCode = serializers.CharField()
    carrierCode = serializers.CharField()
    carrierRawStatus = serializers.CharField()
    label = serializers.CharField()
    location = serializers.CharField()
    timestamp = serializers.CharField()


class TrackingResponseSerializer(serializers.Serializer):
    shipmentId = serializers.CharField()
    carrierCode = serializers.CharField()
    carrierTrackingNumber = serializers.CharField()
    currentStatus = serializers.DictField()
    estimatedDeliveryDate = serializers.CharField(allow_null=True)
    events = TrackingEventOutSerializer(many=True)


# ─── Webhook ────────────────────────────────────────────────────────────

class WebhookResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField(default=True)
    message = serializers.CharField(default='Webhook processed successfully')


# ─── Rates ──────────────────────────────────────────────────────────────

class RatePackageSerializer(serializers.Serializer):
    weight = serializers.FloatField()
    weightUnit = serializers.ChoiceField(choices=['KG', 'LB'], default='KG')
    length = serializers.FloatField(required=False)
    width = serializers.FloatField(required=False)
    height = serializers.FloatField(required=False)
    dimUnit = serializers.ChoiceField(choices=['CM', 'IN'], default='CM')


class RateOptionsSerializer(serializers.Serializer):
    carrierCodes = serializers.ListField(child=serializers.CharField(), required=False)
    serviceType = serializers.CharField(required=False)


class RateRequestSerializer(serializers.Serializer):
    sender = SenderRecipientSerializer()
    recipient = SenderRecipientSerializer()
    packages = RatePackageSerializer(many=True)
    options = RateOptionsSerializer(required=False)


# ─── Pickup ─────────────────────────────────────────────────────────────

class PickupListSerializer(serializers.ModelSerializer):
    carrierCode = serializers.CharField(source='carrier.code', read_only=True)
    pickupDate = serializers.DateField(source='pickup_date', read_only=True)

    class Meta:
        model = Pickup
        fields = ['id', 'carrierCode', 'status', 'pickupDate', 'confirmationNumber', 'createdAt']


class PickupDetailSerializer(serializers.ModelSerializer):
    carrierCode = serializers.CharField(source='carrier.code', read_only=True)
    carrierPickupId = serializers.CharField(source='carrier_pickup_id', read_only=True)
    pickupDate = serializers.DateField(source='pickup_date', read_only=True)
    readyTime = serializers.TimeField(source='ready_time', read_only=True)
    closeTime = serializers.TimeField(source='close_time', read_only=True)
    totalPackages = serializers.IntegerField(source='total_packages', read_only=True)
    totalWeight = serializers.FloatField(source='total_weight', read_only=True)
    weightUnit = serializers.CharField(source='weight_unit', read_only=True)
    confirmationNumber = serializers.CharField(source='confirmation_number', read_only=True)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    cancelledAt = serializers.DateTimeField(source='cancelled_at', read_only=True)

    class Meta:
        model = Pickup
        fields = ['id', 'carrierCode', 'carrierPickupId', 'status',
                  'pickupDate', 'readyTime', 'closeTime',
                  'totalPackages', 'totalWeight', 'weightUnit',
                  'confirmationNumber', 'createdAt', 'cancelledAt']


class PickupUpdateSerializer(serializers.Serializer):
    pickupDate = serializers.DateField(required=False)
    readyTime = serializers.TimeField(required=False)
    closeTime = serializers.TimeField(required=False)
    specialInstructions = serializers.CharField(required=False, allow_blank=True)


class PickupLocationSerializer(serializers.Serializer):
    company = serializers.CharField(required=False, allow_blank=True)
    contactName = serializers.CharField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    country = serializers.CharField(max_length=2)
    zipCode = serializers.CharField(max_length=20)
    city = serializers.CharField(max_length=100)
    address = serializers.CharField()


class PickupCreateSerializer(serializers.Serializer):
    carrierCode = serializers.CharField(max_length=20)
    shipmentIds = serializers.ListField(child=serializers.CharField())
    pickupDate = serializers.DateField()
    readyTime = serializers.TimeField()
    closeTime = serializers.TimeField()
    location = PickupLocationSerializer()
    totalPackages = serializers.IntegerField(default=1)
    totalWeight = serializers.FloatField(required=False)
    weightUnit = serializers.ChoiceField(choices=['KG', 'LB'], default='KG')
    specialInstructions = serializers.CharField(required=False, allow_blank=True)


# ─── Tracking Event (for webhook) ───────────────────────────────────────

class TrackingEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackingEvent
        fields = '__all__'
