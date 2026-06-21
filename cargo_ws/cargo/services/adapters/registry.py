"""
CarrierRegistry — plugin registry for carrier adapters.
Adding a new carrier = 1 adapter class + register() call.
"""
from typing import Optional
from .base import CarrierAdapter


class CarrierRegistry:
    def __init__(self):
        self._adapters: dict[str, CarrierAdapter] = {}

    def register(self, code: str, adapter: CarrierAdapter):
        self._adapters[code.upper()] = adapter

    def get(self, code: str) -> Optional[CarrierAdapter]:
        return self._adapters.get(code.upper())

    def get_or_raise(self, code: str) -> CarrierAdapter:
        adapter = self.get(code)
        if not adapter:
            raise ValueError(f"Carrier '{code}' not found in registry")
        return adapter

    def get_all(self) -> list[CarrierAdapter]:
        return list(self._adapters.values())

    def get_active(self, active_carriers: list[str] = None) -> list[CarrierAdapter]:
        if active_carriers:
            return [a for c, a in self._adapters.items() if c in active_carriers]
        return self.get_all()

    def unregister(self, code: str):
        self._adapters.pop(code.upper(), None)


# Global registry instance
registry = CarrierRegistry()
