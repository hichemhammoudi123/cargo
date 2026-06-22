from pydantic import BaseModel
from typing import Optional
from datetime import date, time


class PickupLocation(BaseModel):
    company: str = ""
    contactName: str = ""
    phone: str = ""
    country: str
    zipCode: str
    city: str
    address: str


class PickupCreate(BaseModel):
    carrierCode: str
    shipmentIds: list[str]
    pickupDate: date
    readyTime: time
    closeTime: time
    location: PickupLocation
    totalPackages: int = 1
    totalWeight: Optional[float] = None
    weightUnit: str = "KG"
    specialInstructions: str = ""


class PickupUpdate(BaseModel):
    pickupDate: Optional[date] = None
    readyTime: Optional[time] = None
    closeTime: Optional[time] = None
    specialInstructions: str = ""


class PickupList(BaseModel):
    id: str
    carrierCode: str
    status: str
    pickupDate: str
    confirmationNumber: str = ""
    createdAt: str


class PickupDetail(BaseModel):
    id: str
    carrierCode: str
    carrierPickupId: str = ""
    status: str
    pickupDate: str
    readyTime: str
    closeTime: str
    totalPackages: int
    totalWeight: Optional[float] = None
    weightUnit: str
    confirmationNumber: str = ""
    createdAt: str
    cancelledAt: Optional[str] = None


class PickupCancel(BaseModel):
    id: str
    status: str
    cancelledAt: Optional[str] = None
