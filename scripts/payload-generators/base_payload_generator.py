#!/usr/bin/env python3
"""Base payload generator with common utility functions for JMeter YMS Dashboard tests"""

import random
import datetime
import json
import sys
import os
from typing import List, Any, Optional, Dict

class BasePayloadGenerator:
    """Base class for payload generation with common utility methods"""
    
    @staticmethod
    def get_random_element(array: List[Any]) -> Optional[Any]:
        """Get random element from array"""
        if not array:
            return None
        return random.choice(array)

    @staticmethod
    def get_random_subset(array: List[Any], max_size: int = -1) -> List[Any]:
        """Get random subset from array"""
        if not array:
            return []
        shuffled = array[:]
        random.shuffle(shuffled)
        size = min(max_size, len(shuffled)) if max_size > 0 else random.randint(1, len(shuffled))
        return shuffled[:size]

    @staticmethod
    def get_random_date(days_from_now: int = 30) -> str:
        """Generate random future date in ISO format"""
        now = datetime.datetime.now()
        random_days = random.randint(0, days_from_now - 1)
        random_date = now + datetime.timedelta(days=random_days)
        return random_date.isoformat()

    @staticmethod
    def get_random_past_date(days_ago: int = 30) -> str:
        """Generate random past date in ISO format"""
        now = datetime.datetime.now()
        random_days = random.randint(0, days_ago - 1)
        random_date = now - datetime.timedelta(days=random_days)
        return random_date.isoformat()

    @staticmethod
    def parse_carrier_ids(carrier_ids_string: str) -> List[int]:
        """Parse carrier IDs from CSV string"""
        if not carrier_ids_string or not carrier_ids_string.strip():
            return []
        try:
            return [int(cid.strip()) for cid in carrier_ids_string.split(",") if cid.strip()]
        except ValueError as e:
            print(f"Error parsing carrier IDs: {e}", file=sys.stderr)
            return []

    @staticmethod
    def get_random_threshold_hours() -> int:
        """Get random threshold hours"""
        thresholds = [24, 48, 72, 96, 120]
        return BasePayloadGenerator.get_random_element(thresholds)

    @staticmethod
    def get_random_page_size() -> int:
        """Get random page size"""
        sizes = [10, 20, 50, 100]
        return BasePayloadGenerator.get_random_element(sizes)
    
    @staticmethod
    def generate_payload_json(payload: Dict) -> str:
        """Convert payload dict to JSON string"""
        return json.dumps(payload, indent=None, separators=(',', ':'))
    
    @staticmethod
    def handle_error(error: Exception, default_payload: Dict) -> str:
        """Handle errors and return default payload"""
        print(f"Error generating payload: {error}", file=sys.stderr)
        return BasePayloadGenerator.generate_payload_json(default_payload)