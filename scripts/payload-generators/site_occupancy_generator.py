#!/usr/bin/env python3
"""Generate payload for site-occupancy API"""

import json
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from base_payload_generator import BasePayloadGenerator

def generate_payload(facility_id):
    """Generate site occupancy payload"""
    try:
        facility_id = int(facility_id)
        
        # Occupancy types
        occupancy_types = ["TRAILER", "CONTAINER", "CHASSIS", "ALL"]
        selected_type = BasePayloadGenerator.get_random_element(occupancy_types)
        
        # Zone filters
        zones = ["NORTH", "SOUTH", "EAST", "WEST", "CENTRAL", None]
        selected_zone = BasePayloadGenerator.get_random_element(zones)
        
        payload = {
            "facilityId": facility_id,
            "occupancyType": selected_type,
            "includeHistorical": BasePayloadGenerator.get_random_element([True, False]),
            "dateRange": {
                "startDate": BasePayloadGenerator.get_random_past_date(30),
                "endDate": BasePayloadGenerator.get_random_date(1)
            }
        }
        
        if selected_zone:
            payload["zoneFilter"] = selected_zone
            
        return payload
    except (ValueError, TypeError) as e:
        default_payload = {
            "facilityId": 101,
            "occupancyType": "ALL",
            "includeHistorical": False,
            "dateRange": {
                "startDate": BasePayloadGenerator.get_random_past_date(7),
                "endDate": BasePayloadGenerator.get_random_date(1)
            }
        }
        return BasePayloadGenerator.handle_error(e, default_payload)

if __name__ == "__main__":
    # Usage: python site_occupancy_generator.py <facility_id>
    if len(sys.argv) != 2:
        print("Usage: python site_occupancy_generator.py <facility_id>", file=sys.stderr)
        sys.exit(1)
    
    facility_id = sys.argv[1]
    payload = generate_payload(facility_id)
    print(json.dumps(payload))