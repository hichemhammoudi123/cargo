from pydantic import BaseModel
from typing import Optional


class CarrierServiceOut(BaseModel):
    code: str
    name: str
    description: str = ""
    maxWeight: Optional[float] = None
    maxWeightUnit: str = "KG"
    zones: list = []
    transitDays: Optional[int] = None
    features: list = []
    active: bool = True

    class Config:
        from_attributes = True


class CarrierCapabilityOut(BaseModel):
    labelFormats: list = []
    features: list = []

    class Config:
        from_attributes = True


class CarrierList(BaseModel):
    code: str
    name: str
    adapterName: str
    active: bool
    status: str
    services: list[CarrierServiceOut] = []

    class Config:
        from_attributes = True


class CarrierDetail(BaseModel):
    code: str
    name: str
    adapterName: str
    active: bool
    status: str
    lastTestedAt: Optional[str] = None
    services: list[CarrierServiceOut] = []
    capabilities: Optional[CarrierCapabilityOut] = None
    settings: dict = {}
    credentialsUpdatedAt: Optional[str] = None

    class Config:
        from_attributes = True


class CarrierAdd(BaseModel):
    code: str
    name: str
    adapterName: str = ""
    active: bool = True
    website: str = ""
    contact: dict = {}
    services: list = []
    capabilities: dict = {}
    credentials: dict = {}
    settings: dict = {}


class CarrierUpdate(BaseModel):
    active: Optional[bool] = None
    settings: Optional[dict] = None


class CarrierToggle(BaseModel):
    active: bool
    reason: str = ""


class CredentialsUpdate(BaseModel):
    authType: str = ""
    apiKey: str = ""
    apiSecret: str = ""
    webhookSecret: str = ""


class CarrierServiceAdd(BaseModel):
    code: str
    name: str
    description: str = ""
    maxWeight: Optional[float] = None
    maxWeightUnit: str = "KG"
    zones: list = []
    transitDays: Optional[int] = None
    features: list = []
    active: bool = True
