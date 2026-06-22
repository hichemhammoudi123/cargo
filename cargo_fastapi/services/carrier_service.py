from sqlalchemy.orm import Session
from models.carrier import Carrier
from services.adapters.registry import registry
from services.adapters.base import ConnectionTestResult


class CarrierServiceLogic:

    @staticmethod
    def test_connection(carrier_code: str) -> ConnectionTestResult:
        adapter = registry.get_or_raise(carrier_code)
        return adapter.test_connection()
