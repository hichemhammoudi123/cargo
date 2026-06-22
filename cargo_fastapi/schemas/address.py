from pydantic import BaseModel
from typing import Optional


class AddressValidate(BaseModel):
    country: str
    zipCode: str
    city: str
    address: str
    carrierCode: str = "DHL"
