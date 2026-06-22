from pydantic import BaseModel
from typing import Optional


class TrackingEventOut(BaseModel):
    eventId: str
    internalCode: str
    carrierCode: str
    carrierRawStatus: str
    label: str
    location: str = ""
    timestamp: str


class CurrentStatus(BaseModel):
    internalCode: str
    carrierCode: str
    carrierRawStatus: str
    label: str
    timestamp: str


class TrackingResponse(BaseModel):
    shipmentId: str
    carrierCode: str
    carrierTrackingNumber: str
    currentStatus: CurrentStatus
    estimatedDeliveryDate: Optional[str] = None
    events: list[TrackingEventOut]


class WebhookResponse(BaseModel):
    success: bool = True
    message: str = "Webhook processed successfully"
