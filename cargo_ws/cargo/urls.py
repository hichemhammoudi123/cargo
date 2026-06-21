from django.urls import path
from .views import shipment_views, tracking_views, rate_views, pickup_views, carrier_views, address_views, combined_views

urlpatterns = [
    # ── Shipments ───────────────────────────────────────────────────────
    path('shipments', combined_views.shipments_list, name='shipments-list'),
    path('shipments/<str:id>', combined_views.shipments_detail, name='shipments-detail'),
    path('shipments/<str:id>/cancel', shipment_views.cancel_shipment, name='cancel-shipment'),
    path('shipments/<str:id>/label', shipment_views.generate_label, name='generate-label'),

    # ── Tracking ────────────────────────────────────────────────────────
    path('shipments/<str:id>/tracking', tracking_views.get_tracking, name='get-tracking'),
    path('webhooks/<str:carrier_code>', tracking_views.webhook_receive, name='webhook-receive'),

    # ── Rates ───────────────────────────────────────────────────────────
    path('rates', rate_views.compare_rates, name='compare-rates'),

    # ── Pickups ─────────────────────────────────────────────────────────
    path('pickups', combined_views.pickups_list, name='pickups-list'),
    path('pickups/<str:id>', combined_views.pickups_detail, name='pickups-detail'),
    path('pickups/<str:id>/cancel', pickup_views.cancel_pickup, name='cancel-pickup'),

    # ── Carriers ────────────────────────────────────────────────────────
    path('carriers', combined_views.carriers_list, name='carriers-list'),
    path('carriers/<str:code>', combined_views.carriers_detail, name='carriers-detail'),
    path('carriers/<str:code>/toggle', carrier_views.toggle_carrier, name='toggle-carrier'),
    path('carriers/<str:code>/test', carrier_views.test_carrier_connection, name='test-carrier'),
    path('carriers/<str:code>/credentials', carrier_views.update_credentials, name='update-credentials'),
    path('carriers/<str:code>/services', carrier_views.add_carrier_service, name='add-carrier-service'),

    # ── Address ─────────────────────────────────────────────────────────
    path('addresses/validate', address_views.validate_address, name='validate-address'),
]
