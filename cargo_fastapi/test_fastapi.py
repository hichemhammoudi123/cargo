"""Quick smoke test for FastAPI endpoints."""
import json
import urllib.request
import urllib.error


BASE = "http://localhost:8000/api/v1/cargo"


def _req(method, path, data=None):
    url = f"{BASE}{path}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(
        url, data=body,
        headers={"Content-Type": "application/json"} if data else {},
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            return json.loads(raw)
        except Exception:
            return {"success": False, "error": {"code": f"HTTP_{e.code}", "message": raw.decode(errors="replace")}}
    except Exception as e:
        return {"success": False, "error": {"code": "REQUEST_FAILED", "message": str(e)}}


def get(path):
    return _req("GET", path)


def post(path, data):
    return _req("POST", path, data)


def put(path, data):
    return _req("PUT", path, data)


def patch(path, data):
    return _req("PATCH", path, data)


def delete(path):
    return _req("DELETE", path)


OK = "[OK]"

# 1. Carriers
r = get("/carriers")
assert r["success"], f"GET /carriers failed: {r}"
print(f"{OK} GET /carriers - {len(r['data'])} carriers")

r = get("/carriers/DHL")
assert r["success"], f"GET /carriers/DHL failed: {r}"
print(f"{OK} GET /carriers/DHL - {r['data']['name']}")

r = post("/carriers/DHL/test", {})
assert r["success"], f"POST /carriers/DHL/test failed: {r}"
print(f"{OK} POST /carriers/DHL/test - {r['data']['status']} ({r['data']['latencyMs']}ms)")

r = get("/carriers/DHL/services")
assert r["success"], f"GET /carriers/DHL/services failed: {r}"
print(f"{OK} GET /carriers/DHL/services - {len(r['data'])} services")

r = get("/carriers/DHL/capabilities")
assert r["success"], f"GET /carriers/DHL/capabilities failed: {r}"
print(f"{OK} GET /carriers/DHL/capabilities - formats: {r['data'].get('labelFormats', [])}")

r = patch("/carriers/DHL/toggle", {"active": False})
assert r["success"], f"PATCH /carriers/DHL/toggle failed: {r}"
print(f"{OK} PATCH /carriers/DHL/toggle - active: {r['data']['active']}")

r = patch("/carriers/DHL/toggle", {"active": True})
assert r["success"], f"PATCH /carriers/DHL/toggle (undo) failed: {r}"
print(f"{OK} PATCH /carriers/DHL/toggle (undo) - active: {r['data']['active']}")

# 2. Shipments
r = get("/shipments")
assert r["success"], f"GET /shipments failed: {r}"
print(f"{OK} GET /shipments - {len(r['data'])} shipments")

payload = {
    "carrierCode": "DHL",
    "serviceCode": "DHL_EXP",
    "sender": {
        "contactName": "Sender",
        "address": "1 Rue de Paris, 75001 Paris",
        "phone": "+33123456789",
        "country": "FR",
        "zipCode": "75001",
        "city": "Paris",
    },
    "recipient": {
        "contactName": "Recipient",
        "address": "2 Rue de Marseille, 13001 Marseille",
        "phone": "+33987654321",
        "country": "FR",
        "zipCode": "13001",
        "city": "Marseille",
    },
    "packages": [{"weight": 5, "length": 30, "width": 20, "height": 15, "description": "Box"}],
}
r = post("/shipments", payload)
assert r["success"], f"POST /shipments failed: {r}"
ship_id = r["data"]["id"]
print(f"{OK} POST /shipments - id={ship_id}")

r = get(f"/shipments/{ship_id}")
assert r["success"], f"GET /shipments/{ship_id} failed: {r}"
print(f"{OK} GET /shipments/{ship_id} - {r['data']['carrierCode']} {r['data']['internalStatus']}")

r = put(f"/shipments/{ship_id}", {"reference": "REF-UPDATED"})
assert r["success"], f"PUT /shipments/{ship_id} failed: {r}"
print(f"{OK} PUT /shipments/{ship_id} - {r['data']['reference']}")

# 3. Tracking
r = get(f"/shipments/{ship_id}/tracking")
assert r["success"], f"GET tracking failed: {r}"
print(f"{OK} GET /shipments/{ship_id}/tracking - {len(r['data']['events'])} events, status={r['data']['currentStatus']['internalCode']}")

# Note: tracking by tracking number not exposed as separate endpoint
# (tracking is only by shipment ID)

# 4. Rates
r = post("/rates", {
    "sender": {"country": "FR", "zipCode": "75001", "city": "Paris", "address": "1 Rue de Paris"},
    "recipient": {"country": "FR", "zipCode": "13001", "city": "Marseille", "address": "2 Rue de Marseille"},
    "packages": [{"weight": 5, "length": 30, "width": 20, "height": 15}],
    "options": {"carrierCodes": ["DHL"]},
})
assert r["success"], f"POST /rates failed: {r}"
print(f"{OK} POST /rates - {len(r['data'])} offers")

# 5. Pickups
r = get("/pickups")
assert r["success"], f"GET /pickups failed: {r}"
print(f"{OK} GET /pickups - {len(r['data'])} pickups")

r = post("/pickups", {
    "carrierCode": "DHL", "pickupDate": "2026-06-25", "readyTime": "09:00", "closeTime": "17:00",
    "location": {
        "contactName": "Sender", "address": "1 Rue de Paris, 75001 Paris",
        "phone": "+33123456789", "country": "FR", "zipCode": "75001", "city": "Paris",
    },
    "shipmentIds": [ship_id], "totalPackages": 1, "totalWeight": 5, "specialInstructions": "Ring bell",
})
assert r["success"], f"POST /pickups failed: {r}"
pickup_id = r["data"]["id"]
print(f"{OK} POST /pickups - id={pickup_id}")

r = get(f"/pickups/{pickup_id}")
assert r["success"], f"GET /pickups/{pickup_id} failed: {r}"
print(f"{OK} GET /pickups/{pickup_id} - {r['data']['carrierCode']}")

r = put(f"/pickups/{pickup_id}", {"specialInstructions": "Leave at door"})
assert r["success"], f"PUT /pickups/{pickup_id} failed: {r}"
print(f"{OK} PUT /pickups/{pickup_id} - updated")

r = delete(f"/pickups/{pickup_id}")
assert r["success"], f"DELETE /pickups/{pickup_id} failed: {r}"
print(f"{OK} DELETE /pickups/{pickup_id} - deleted")

# 6. Webhook
r = post("/webhooks/DHL", {"event": "DELIVERED", "trackingNumber": "DHL12345678", "timestamp": "2026-06-22T08:00:00Z"})
assert r["success"], f"POST /webhooks/DHL failed: {r}"
print(f"{OK} POST /webhooks/DHL - {r['message']}")

# 7. Address
r = post("/addresses/validate", {
    "carrierCode": "DHL", "address": "1 Rue de Paris", "city": "Paris",
    "zipCode": "75001", "country": "FR",
})
assert r["success"], f"POST /addresses/validate failed: {r}"
print(f"{OK} POST /addresses/validate - valid={r['data']['valid']}")

print(f"\nALL ENDPOINTS VERIFIED SUCCESSFULLY!")
