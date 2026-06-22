"""StatusMapperEngine — 3-tier status matching: exact → regex → fuzzy."""
import re
from difflib import SequenceMatcher


STATUS_MAPS: dict[str, dict[str, str]] = {
    "DHL": {
        "PENDING": "PENDING",
        "PICKED_UP": "PICKED_UP",
        "IN_PROGRESS": "IN_PROGRESS",
        "DELIVERED": "DELIVERED",
        "RETURNED": "RETURNED",
        "CANCELLED": "CANCELLED",
    },
    "UPS": {
        "Completed": "DELIVERED",
        "Shipped": "IN_PROGRESS",
        "Picked Up": "PICKED_UP",
        "Cancelled": "CANCELLED",
    },
    "FEDEX": {
        "DL": "DELIVERED",
        "PU": "PICKED_UP",
        "IT": "IN_PROGRESS",
        "CA": "CANCELLED",
    },
    "YURTICI": {
        "Teslim Edildi": "DELIVERED",
        "Yolda": "IN_PROGRESS",
        "Teslim Alındı": "PICKED_UP",
        "İade Edildi": "RETURNED",
        "İptal Edildi": "CANCELLED",
    },
    "MNG": {
        "Teslim Edildi": "DELIVERED",
        "Yolda": "IN_PROGRESS",
        "Şubede": "IN_PROGRESS",
        "İade": "RETURNED",
        "İptal": "CANCELLED",
    },
    "ARAMEX": {
        "Delivered": "DELIVERED",
        "Picked Up": "PICKED_UP",
        "In Transit": "IN_PROGRESS",
        "Cancelled": "CANCELLED",
    },
}

REGEX_PATTERNS: dict[str, list[tuple[str, str]]] = {
    "DHL": [
        (r"(?i)delivered", "DELIVERED"),
        (r"(?i)picked\s*up", "PICKED_UP"),
        (r"(?i)in\s*transit|on\s*way|out\s*for\s*delivery", "IN_PROGRESS"),
        (r"(?i)returned", "RETURNED"),
        (r"(?i)cancelled|exception", "CANCELLED"),
    ],
    "UPS": [
        (r"(?i)out\s*for\s*delivery", "IN_PROGRESS"),
        (r"(?i)in\s*transit", "IN_PROGRESS"),
        (r"(?i)returned", "RETURNED"),
    ],
    "FEDEX": [
        (r"(?i)delivered", "DELIVERED"),
        (r"(?i)picked\s*up", "PICKED_UP"),
        (r"(?i)in\s*transit|on\s*fedex\s*vehicle", "IN_PROGRESS"),
    ],
    "YURTICI": [
        (r"(?i)teslim\s*edildi", "DELIVERED"),
        (r"(?i)yolda", "IN_PROGRESS"),
        (r"(?i)teslim\s*alındı|alindi", "PICKED_UP"),
        (r"(?i)iade", "RETURNED"),
        (r"(?i)iptal", "CANCELLED"),
    ],
    "MNG": [
        (r"(?i)teslim\s*edildi", "DELIVERED"),
        (r"(?i)yolda", "IN_PROGRESS"),
        (r"(?i)şubede|subede", "IN_PROGRESS"),
        (r"(?i)iade", "RETURNED"),
        (r"(?i)iptal", "CANCELLED"),
    ],
    "ARAMEX": [
        (r"(?i)delivered", "DELIVERED"),
        (r"(?i)picked\s*up", "PICKED_UP"),
        (r"(?i)in\s*transit", "IN_PROGRESS"),
    ],
}

FUZZY_THRESHOLD = 0.8


class StatusMapperEngine:
    @staticmethod
    def map(carrier_code: str, raw_status: str) -> str:
        if not raw_status:
            return "PENDING"

        carrier_code = carrier_code.upper()
        raw = raw_status.strip()

        exact_map = STATUS_MAPS.get(carrier_code, {})
        if raw in exact_map:
            return exact_map[raw]

        patterns = REGEX_PATTERNS.get(carrier_code, [])
        for pattern, mapped in patterns:
            if re.search(pattern, raw):
                return mapped

        for mapped in ("DELIVERED", "PICKED_UP", "IN_PROGRESS", "RETURNED", "CANCELLED"):
            ratio = SequenceMatcher(None, raw.lower(), mapped.lower().replace("_", " ")).ratio()
            if ratio >= FUZZY_THRESHOLD:
                return mapped

        return "IN_PROGRESS"
