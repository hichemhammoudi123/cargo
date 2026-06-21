"""
Status Mapper Engine — 3-tier matching: exact → regex → fuzzy
Translates carrier-specific status strings into 6 unified internal codes.
"""
import re
from enum import Enum


class InternalStatus(str, Enum):
    PENDING     = 'PENDING'
    PICKED_UP   = 'PICKED_UP'
    IN_PROGRESS = 'IN_PROGRESS'
    DELIVERED   = 'DELIVERED'
    RETURNED    = 'RETURNED'
    CANCELLED   = 'CANCELLED'


class StatusMapperEngine:
    """
    Multi-carrier status translation engine.
    Usage:
        mapper = StatusMapperEngine()
        internal = mapper.map('UPS', 'Completed')  # → InternalStatus.DELIVERED
    """

    def __init__(self):
        self._exact_maps = {}
        self._regex_maps = {}
        self._load_maps()

    def _load_maps(self):
        # ─── Exact match tables ────────────────────────────────────────
        self._exact_maps = {
            'DHL': {
                'IN_TRANSIT': InternalStatus.IN_PROGRESS,
                'DELIVERED': InternalStatus.DELIVERED,
                'RETURNED': InternalStatus.RETURNED,
                'PICKED_UP': InternalStatus.PICKED_UP,
                'CANCELLED': InternalStatus.CANCELLED,
                'Shipment information received': InternalStatus.PENDING,
                'Pickup scanned': InternalStatus.PICKED_UP,
                'Shipment has been delivered': InternalStatus.DELIVERED,
                'Shipment delivered': InternalStatus.DELIVERED,
            },
            'UPS': {
                'OnTheWay': InternalStatus.IN_PROGRESS,
                'Completed': InternalStatus.DELIVERED,
                'BackToSender': InternalStatus.RETURNED,
                'Collected': InternalStatus.PICKED_UP,
                'Cancelled': InternalStatus.CANCELLED,
                'Delivered': InternalStatus.DELIVERED,
            },
            'FEDEX': {
                'EN_ROUTE': InternalStatus.IN_PROGRESS,
                'DELIVERED': InternalStatus.DELIVERED,
                'RETURNED': InternalStatus.RETURNED,
                'PICKED UP': InternalStatus.PICKED_UP,
                'CANCELLED': InternalStatus.CANCELLED,
            },
            'YURTICI': {
                'Yolda': InternalStatus.IN_PROGRESS,
                'Teslim Edildi': InternalStatus.DELIVERED,
                'İade Edildi': InternalStatus.RETURNED,
                'Teslim Alındı': InternalStatus.PICKED_UP,
                'İptal Edildi': InternalStatus.CANCELLED,
            },
            'MNG': {
                'Yolda': InternalStatus.IN_PROGRESS,
                'Teslim Edildi': InternalStatus.DELIVERED,
                'İade': InternalStatus.RETURNED,
                'Teslim Alındı': InternalStatus.PICKED_UP,
                'İptal': InternalStatus.CANCELLED,
            },
            'ARAMEX': {
                'IN TRANSIT': InternalStatus.IN_PROGRESS,
                'DELIVERED': InternalStatus.DELIVERED,
                'RETURNED': InternalStatus.RETURNED,
                'PICKED UP': InternalStatus.PICKED_UP,
                'CANCELLED': InternalStatus.CANCELLED,
            },
        }

        # ─── Regex patterns (per carrier) ─────────────────────────────
        self._regex_maps = {
            'DHL': [
                (re.compile(r'out for delivery', re.I), InternalStatus.IN_PROGRESS),
                (re.compile(r'delivery attempted', re.I), InternalStatus.IN_PROGRESS),
                (re.compile(r'return to sender', re.I), InternalStatus.RETURNED),
                (re.compile(r'departed from (transit|origin|destination)', re.I), InternalStatus.IN_PROGRESS),
                (re.compile(r'arrived at (transit|sort|destination)', re.I), InternalStatus.IN_PROGRESS),
            ],
            'UPS': [
                (re.compile(r'out for delivery', re.I), InternalStatus.IN_PROGRESS),
                (re.compile(r'delivery attempted', re.I), InternalStatus.IN_PROGRESS),
                (re.compile(r'return to sender', re.I), InternalStatus.RETURNED),
            ],
            'FEDEX': [
                (re.compile(r'en route', re.I), InternalStatus.IN_PROGRESS),
                (re.compile(r'out for delivery', re.I), InternalStatus.IN_PROGRESS),
                (re.compile(r'delivery attempted', re.I), InternalStatus.IN_PROGRESS),
                (re.compile(r'return to sender', re.I), InternalStatus.RETURNED),
            ],
            'YURTICI': [
                (re.compile(r'out for delivery', re.I), InternalStatus.IN_PROGRESS),
                (re.compile(r'return to sender', re.I), InternalStatus.RETURNED),
            ],
            'MNG': [
                (re.compile(r'out for delivery', re.I), InternalStatus.IN_PROGRESS),
                (re.compile(r'return to sender', re.I), InternalStatus.RETURNED),
            ],
            'ARAMEX': [
                (re.compile(r'in transit', re.I), InternalStatus.IN_PROGRESS),
                (re.compile(r'out for delivery', re.I), InternalStatus.IN_PROGRESS),
                (re.compile(r'delivery attempted', re.I), InternalStatus.IN_PROGRESS),
                (re.compile(r'return to sender', re.I), InternalStatus.RETURNED),
            ],
        }

    def map(self, carrier_code: str, raw_status: str) -> InternalStatus:
        """
        Translate a carrier-specific raw status string into an InternalStatus.
        3 levels: exact match → regex → fuzzy (Levenshtein).
        """
        if not raw_status:
            return InternalStatus.IN_PROGRESS

        carrier_code = carrier_code.upper()

        # Level 1: Exact match
        carrier_map = self._exact_maps.get(carrier_code, {})
        if raw_status in carrier_map:
            return carrier_map[raw_status]

        # Level 2: Regex patterns
        patterns = self._regex_maps.get(carrier_code, [])
        for pattern, status in patterns:
            if pattern.search(raw_status):
                return status

        # Level 3: Fuzzy match (Levenshtein similarity > 0.8)
        fuzzy_result = self._fuzzy_match(raw_status, carrier_map)
        if fuzzy_result:
            return fuzzy_result

        return InternalStatus.IN_PROGRESS

    def _fuzzy_match(self, raw_status: str, carrier_map: dict) -> InternalStatus | None:
        best_score = 0.0
        best_status = None
        for key, status in carrier_map.items():
            score = self._levenshtein_similarity(raw_status.lower(), key.lower())
            if score > best_score and score >= 0.8:
                best_score = score
                best_status = status
        return best_status

    @staticmethod
    def _levenshtein_similarity(a: str, b: str) -> float:
        if not a and not b:
            return 1.0
        if not a or not b:
            return 0.0
        n, m = len(a), len(b)
        dp = [[0] * (m + 1) for _ in range(n + 1)]
        for i in range(n + 1):
            dp[i][0] = i
        for j in range(m + 1):
            dp[0][j] = j
        for i in range(1, n + 1):
            for j in range(1, m + 1):
                cost = 0 if a[i - 1] == b[j - 1] else 1
                dp[i][j] = min(dp[i - 1][j] + 1, dp[i][j - 1] + 1, dp[i - 1][j - 1] + cost)
        max_len = max(n, m)
        return 1 - (dp[n][m] / max_len) if max_len else 1.0

    def register_carrier_map(self, carrier_code: str, exact_map: dict,
                             regex_patterns: list = None):
        self._exact_maps[carrier_code.upper()] = exact_map
        if regex_patterns:
            self._regex_maps[carrier_code.upper()] = [
                (re.compile(p, re.I), s) for p, s in regex_patterns
            ]


# Singleton
mapper = StatusMapperEngine()
