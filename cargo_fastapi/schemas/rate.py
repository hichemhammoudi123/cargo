from pydantic import BaseModel
from typing import Optional

from .shipment import SenderRecipient


class RatePackage(BaseModel):
    weight: float
    weightUnit: str = "KG"
    length: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
    dimUnit: str = "CM"


class RateOptions(BaseModel):
    carrierCodes: list[str] = []
    serviceType: str = "EXPRESS"


class RateRequest(BaseModel):
    sender: SenderRecipient
    recipient: SenderRecipient
    packages: list[RatePackage]
    options: Optional[RateOptions] = None


class RateOffer(BaseModel):
    carrierCode: str
    carrierName: str
    serviceCode: str
    serviceName: str
    totalPrice: float
    currency: str
    estimatedTransitDays: Optional[int] = None
    estimatedDeliveryDate: Optional[str] = None
    guaranteed: bool = False
    breakdown: list = []


class RateResponse(BaseModel):
    success: bool = True
    data: list[RateOffer] = []
    errors: Optional[list] = None
