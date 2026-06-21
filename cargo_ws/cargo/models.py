import uuid
from django.db import models


def gen_id(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:12]}"

def default_shp_id():
    return gen_id('shp')
def default_pkg_id():
    return gen_id('pkg')
def default_evt_id():
    return gen_id('evt')
def default_pck_id():
    return gen_id('pck')
def default_addr_id():
    return gen_id('addr')


# ─── Status Choices ─────────────────────────────────────────────────────

class InternalStatus(models.TextChoices):
    PENDING     = 'PENDING',     'Pending'
    PICKED_UP   = 'PICKED_UP',   'Picked Up'
    IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
    DELIVERED   = 'DELIVERED',   'Delivered'
    RETURNED    = 'RETURNED',    'Returned'
    CANCELLED   = 'CANCELLED',   'Cancelled'


class ShipmentStatus(models.TextChoices):
    DRAFT       = 'DRAFT',        'Draft'
    VALIDATED   = 'VALIDATED',    'Validated'
    SUBMITTED   = 'SUBMITTED',    'Submitted'
    PICKED_UP   = 'PICKED_UP',    'Picked Up'
    IN_TRANSIT  = 'IN_TRANSIT',   'In Transit'
    CUSTOMS_HELD = 'CUSTOMS_HELD', 'Customs Held'
    OUT_FOR_DELIVERY = 'OUT_FOR_DELIVERY', 'Out for Delivery'
    DELIVERED   = 'DELIVERED',    'Delivered'
    DELIVERY_ATTEMPTED = 'DELIVERY_ATTEMPTED', 'Delivery Attempted'
    FAILED      = 'FAILED',       'Failed'
    RETURNED    = 'RETURNED',     'Returned'
    CANCELLED   = 'CANCELLED',    'Cancelled'


class CarrierStatusEnum(models.TextChoices):
    CONNECTED     = 'CONNECTED',      'Connected'
    PENDING_TEST  = 'PENDING_TEST',   'Pending Test'
    DISCONNECTED  = 'DISCONNECTED',   'Disconnected'
    ERROR         = 'ERROR',          'Error'


class PickupStatus(models.TextChoices):
    CONFIRMED = 'CONFIRMED', 'Confirmed'
    CANCELLED = 'CANCELLED', 'Cancelled'


class LabelFormat(models.TextChoices):
    PDF = 'PDF', 'PDF'
    ZPL = 'ZPL', 'ZPL'
    PNG = 'PNG', 'PNG'


class WeightUnit(models.TextChoices):
    KG = 'KG', 'Kilogram'
    LB = 'LB', 'Pound'


class DimUnit(models.TextChoices):
    CM = 'CM', 'Centimeter'
    IN = 'IN', 'Inch'


# ─── Carrier ────────────────────────────────────────────────────────────

class Carrier(models.Model):
    code        = models.CharField(max_length=20, primary_key=True)
    name        = models.CharField(max_length=100)
    name_fr     = models.CharField(max_length=100, blank=True)
    name_tr     = models.CharField(max_length=100, blank=True)
    name_ar     = models.CharField(max_length=100, blank=True)
    adapter_name = models.CharField(max_length=100)
    active      = models.BooleanField(default=True)
    status      = models.CharField(max_length=20, choices=CarrierStatusEnum.choices, default=CarrierStatusEnum.PENDING_TEST)
    website     = models.URLField(blank=True)
    last_tested_at = models.DateTimeField(null=True, blank=True)
    credentials_updated_at = models.DateTimeField(auto_now=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    # Encrypted credentials (simplified — use django-fernet-fields in production)
    auth_type   = models.CharField(max_length=20, default='API_KEY')
    api_key_enc = models.TextField(blank=True)
    api_secret_enc = models.TextField(blank=True)
    account_number = models.CharField(max_length=50, blank=True)
    endpoint    = models.URLField(blank=True)
    webhook_secret_enc = models.TextField(blank=True)

    # Settings
    timeout_ms         = models.IntegerField(default=10000)
    retry_max_attempts = models.IntegerField(default=3)
    retry_delay_ms     = models.IntegerField(default=1000)
    rate_limit_per_min = models.IntegerField(default=50)

    class Meta:
        db_table = 'cargo_carriers'
        verbose_name = 'Carrier'
        verbose_name_plural = 'Carriers'

    def __str__(self):
        return f"{self.code} - {self.name}"


class CarrierService(models.Model):
    carrier     = models.ForeignKey(Carrier, on_delete=models.CASCADE, related_name='services')
    code        = models.CharField(max_length=50)
    name        = models.CharField(max_length=100)
    name_fr     = models.CharField(max_length=100, blank=True)
    name_tr     = models.CharField(max_length=100, blank=True)
    name_ar     = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    description_fr = models.TextField(blank=True)
    description_tr = models.TextField(blank=True)
    description_ar = models.TextField(blank=True)
    max_weight  = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    max_weight_unit = models.CharField(max_length=2, choices=WeightUnit.choices, default=WeightUnit.KG)
    zones       = models.JSONField(default=list, blank=True)
    transit_days = models.IntegerField(null=True, blank=True)
    features    = models.JSONField(default=list, blank=True)
    active      = models.BooleanField(default=True)

    class Meta:
        db_table = 'cargo_carrier_services'
        unique_together = [['carrier', 'code']]

    def __str__(self):
        return f"{self.carrier.code} - {self.code}"


class CarrierCapability(models.Model):
    carrier      = models.OneToOneField(Carrier, on_delete=models.CASCADE, related_name='capabilities')
    label_formats = models.JSONField(default=list, blank=True)
    features     = models.JSONField(default=list, blank=True)

    class Meta:
        db_table = 'cargo_carrier_capabilities'


# ─── Address (value object, stored as JSON in Shipment) ─────────────────

class Address(models.Model):
    id          = models.CharField(max_length=30, primary_key=True, default=default_addr_id)
    company     = models.CharField(max_length=200, blank=True)
    contact_name = models.CharField(max_length=200, blank=True)
    email       = models.EmailField(blank=True)
    phone       = models.CharField(max_length=30, blank=True)
    country     = models.CharField(max_length=2)
    zip_code    = models.CharField(max_length=20)
    city        = models.CharField(max_length=100)
    address     = models.TextField()
    address2    = models.TextField(blank=True)

    class Meta:
        db_table = 'cargo_addresses'

    def __str__(self):
        return f"{self.city}, {self.country}"


# ─── Shipment ───────────────────────────────────────────────────────────

class Shipment(models.Model):
    id          = models.CharField(max_length=30, primary_key=True, default=default_shp_id)
    status      = models.CharField(max_length=30, choices=ShipmentStatus.choices, default=ShipmentStatus.DRAFT)
    internal_status = models.CharField(max_length=20, choices=InternalStatus.choices, default=InternalStatus.PENDING)
    carrier_status  = models.CharField(max_length=200, blank=True)
    carrier     = models.ForeignKey(Carrier, on_delete=models.SET_NULL, null=True, related_name='shipments')
    carrier_service = models.ForeignKey(CarrierService, on_delete=models.SET_NULL, null=True, blank=True)
    reference   = models.CharField(max_length=200, blank=True)
    carrier_tracking_number = models.CharField(max_length=100, blank=True)
    carrier_shipment_id = models.CharField(max_length=100, blank=True)
    label_url   = models.URLField(blank=True)
    label_format = models.CharField(max_length=5, choices=LabelFormat.choices, blank=True)
    tracking_url = models.URLField(blank=True)

    # Price
    price_total   = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    price_currency = models.CharField(max_length=3, default='EUR')
    price_breakdown = models.JSONField(default=list, blank=True)

    # Linked addresses
    sender    = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, related_name='sender_shipments')
    recipient = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, related_name='recipient_shipments')

    # Options
    insurance_amount      = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    insurance_currency    = models.CharField(max_length=3, blank=True, default='EUR')
    signature_required    = models.BooleanField(default=True)
    saturday_delivery     = models.BooleanField(default=False)

    estimated_delivery_date = models.DateTimeField(null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'cargo_shipments'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.id} - {self.reference}"


class Package(models.Model):
    id          = models.CharField(max_length=30, primary_key=True, default=default_pkg_id)
    shipment    = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='packages')
    reference   = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    description_fr = models.TextField(blank=True)
    description_tr = models.TextField(blank=True)
    description_ar = models.TextField(blank=True)
    weight      = models.DecimalField(max_digits=10, decimal_places=2)
    weight_unit = models.CharField(max_length=2, choices=WeightUnit.choices, default=WeightUnit.KG)
    length      = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    width       = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    height      = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    dim_unit    = models.CharField(max_length=2, choices=DimUnit.choices, default=DimUnit.CM)
    declared_value    = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    declared_currency = models.CharField(max_length=3, blank=True, default='EUR')
    tracking_number   = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = 'cargo_packages'

    def __str__(self):
        return f"{self.reference or self.id} ({self.weight}{self.weight_unit})"


# ─── Tracking ───────────────────────────────────────────────────────────

class TrackingEvent(models.Model):
    id              = models.CharField(max_length=30, primary_key=True, default=default_evt_id)
    shipment        = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='tracking_events')
    internal_code   = models.CharField(max_length=30)
    carrier_code    = models.CharField(max_length=30, blank=True)
    carrier_raw_status = models.TextField(blank=True)
    label           = models.CharField(max_length=200)
    label_fr        = models.CharField(max_length=200, blank=True)
    label_tr        = models.CharField(max_length=200, blank=True)
    label_ar        = models.CharField(max_length=200, blank=True)
    location        = models.CharField(max_length=200, blank=True)
    signed_by       = models.CharField(max_length=200, blank=True)
    photo_url       = models.URLField(blank=True)
    carrier_raw_data = models.JSONField(default=dict, blank=True)
    timestamp       = models.DateTimeField()
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'cargo_tracking_events'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.shipment.id} - {self.internal_code} @ {self.timestamp}"


# ─── Pickup ─────────────────────────────────────────────────────────────

class Pickup(models.Model):
    id                  = models.CharField(max_length=30, primary_key=True, default=default_pck_id)
    carrier             = models.ForeignKey(Carrier, on_delete=models.SET_NULL, null=True)
    shipments           = models.ManyToManyField(Shipment, related_name='pickups')
    carrier_pickup_id   = models.CharField(max_length=100, blank=True)
    status              = models.CharField(max_length=20, choices=PickupStatus.choices, default=PickupStatus.CONFIRMED)
    pickup_date         = models.DateField()
    ready_time          = models.TimeField()
    close_time          = models.TimeField()
    location            = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)
    total_packages      = models.IntegerField(default=1)
    total_weight        = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    weight_unit         = models.CharField(max_length=2, choices=WeightUnit.choices, default=WeightUnit.KG)
    special_instructions = models.TextField(blank=True)
    special_instructions_fr = models.TextField(blank=True)
    special_instructions_tr = models.TextField(blank=True)
    special_instructions_ar = models.TextField(blank=True)
    confirmation_number = models.CharField(max_length=100, blank=True)
    created_at          = models.DateTimeField(auto_now_add=True)
    cancelled_at        = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'cargo_pickups'

    def __str__(self):
        return f"{self.id} - {self.carrier.code} @ {self.pickup_date}"
