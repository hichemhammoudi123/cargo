from pydantic import BaseModel
from typing import Optional


class SenderRecipient(BaseModel):
    company: str = ""
    contactName: str = ""
    email: str = ""
    phone: str = ""
    country: str
    zipCode: str
    city: str
    address: str


class PackageInput(BaseModel):
    reference: str = ""
    description: str = ""
    weight: float
    weightUnit: str = "KG"
    length: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
    dimUnit: str = "CM"
    declaredValue: Optional[float] = None
    declaredCurrency: str = "EUR"


class Insurance(BaseModel):
    amount: Optional[float] = None
    currency: str = "EUR"


class ShipmentOptions(BaseModel):
    insurance: Optional[Insurance] = None
    signatureRequired: bool = True
    saturdayDelivery: bool = False


class ShipmentCreate(BaseModel):
    carrierCode: str
    serviceCode: str
    reference: str = ""
    sender: SenderRecipient
    recipient: SenderRecipient
    packages: list[PackageInput]
    options: Optional[ShipmentOptions] = None


class ShipmentUpdate(BaseModel):
    reference: Optional[str] = None
    options: Optional[ShipmentOptions] = None


class PackageOut(BaseModel):
    reference: str = ""
    weight: float
    trackingNumber: str = ""


class PriceBreakdown(BaseModel):
    type: str
    label: str
    amount: float


class ShipmentList(BaseModel):
    id: str
    internalStatus: str
    carrierStatus: str
    carrierCode: str
    carrierTrackingNumber: str
    reference: str = ""
    recipient: dict = {}
    createdAt: str


class ShipmentDetail(BaseModel):
    id: str
    internalStatus: str
    carrierStatus: str
    statusHistory: list = []
    carrierCode: str
    carrierName: str
    carrierTrackingNumber: str
    carrierShipmentId: str
    labelUrl: str = ""
    labelFormat: str = ""
    trackingUrl: str = ""
    reference: str = ""
    price: Optional[dict] = None
    sender: dict = {}
    recipient: dict = {}
    packages: list[PackageOut] = []
    createdAt: str
    estimatedDeliveryDate: Optional[str] = None


class ShipmentLabelRequest(BaseModel):
    format: str = "PDF"


class ShipmentLabelOut(BaseModel):
    labelUrl: str
    format: str
    size: str = "A6"
    generatedAt: str
