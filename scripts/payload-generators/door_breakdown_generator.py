#!/usr/bin/env python3
"""Generate payload for door-breakdown-summary API"""

import json
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from base_payload_generator import BasePayloadGenerator

def generate_payload(facility_id):
    """Generate door breakdown summary payload"""
    try:
        facility_id = int(facility_id)
        
        # Door types
        door_types = ["INBOUND", "OUTBOUND", "STAGING", "ALL"]
        selected_door_type = BasePayloadGenerator.get_random_element(door_types)
        
        # Door statuses
        door_statuses = ["AVAILABLE", "OCCUPIED", "MAINTENANCE", "ALL"]
        selected_status = BasePayloadGenerator.get_random_element(door_statuses)
        
        # Time ranges for breakdown
        time_ranges = ["HOURLY", "DAILY", "WEEKLY", "MONTHLY"]
        selected_time_range = BasePayloadGenerator.get_random_element(time_ranges)
        
        payload = {
            "facilityId": facility_id,
            "doorType": selected_door_type,
            "doorStatus": selected_status,
            "timeRange": selected_time_range,
            "includeUtilization": BasePayloadGenerator.get_random_element([True, False]),
            "includeAverageTime": BasePayloadGenerator.get_random_element([True, False])
        }
        
        return payload
    except (ValueError, TypeError) as e:
        default_payload = {
            "facilityId": 101,
            "doorType": "ALL",
            "doorStatus": "ALL",
            "timeRange": "DAILY",
            "includeUtilization": True,
            "includeAverageTime": True
        }
        return BasePayloadGenerator.handle_error(e, default_payload)

if __name__ == "__main__":
    # Usage: python door_breakdown_generator.py <facility_id>
    if len(sys.argv) != 2:
        print("Usage: python door_breakdown_generator.py <facility_id>", file=sys.stderr)
        sys.exit(1)
    
    facility_id = sys.argv[1]
    payload = generate_payload(facility_id)
    print(json.dumps(payload))