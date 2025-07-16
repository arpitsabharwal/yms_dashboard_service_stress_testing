import random
import datetime
from typing import List, Any

class BasePayloadGenerator:
    @staticmethod
    def get_random_element(array: List[Any]) -> Any:
        if not array:
            return None
        return random.choice(array)

    @staticmethod
    def get_random_subset(array: List[Any], max_size: int = -1) -> List[Any]:
        if not array:
            return []
        shuffled = array[:]
        random.shuffle(shuffled)
        size = min(max_size, len(shuffled)) if max_size > 0 else random.randint(1, len(shuffled))
        return shuffled[:size]

    @staticmethod
    def get_random_date(days_from_now: int = 30) -> str:
        now = datetime.datetime.now()
        random_days = random.randint(0, days_from_now - 1)
        random_date = now + datetime.timedelta(days=random_days)
        return random_date.isoformat()

    @staticmethod
    def get_random_past_date(days_ago: int = 30) -> str:
        now = datetime.datetime.now()
        random_days = random.randint(0, days_ago - 1)
        random_date = now - datetime.timedelta(days=random_days)
        return random_date.isoformat()

    @staticmethod
    def parse_carrier_ids(carrier_ids_string: str) -> List[int]:
        if not carrier_ids_string or not carrier_ids_string.strip():
            return []
        return [int(cid.strip()) for cid in carrier_ids_string.split(",") if cid.strip()]

    @staticmethod
    def get_random_threshold_hours() -> int:
        thresholds = [24, 48, 72, 96, 120]
        return BasePayloadGenerator.get_random_element(thresholds)

    @staticmethod
    def get_random_page_size() -> int:
        sizes = [10, 20, 50, 100]
        return BasePayloadGenerator.get_random_element(sizes) 