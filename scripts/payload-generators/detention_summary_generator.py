#!/usr/bin/env python3
"""Generate payload for detention-summary API"""

import json
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from base_payload_generator import BasePayloadGenerator

def generate_payload(facility_id, carrier_ids_string=None):
    """Generate detention summary payload"""
    try:
        facility_id = int(facility_id)
        carrier_ids = BasePayloadGenerator.parse_carrier_ids(carrier_ids_string) if carrier_ids_string else []
        
        # Detention types
        detention_types = ["LOADING", "UNLOADING", "BOTH"]
        selected_type = BasePayloadGenerator.get_random_element(detention_types)
        
        # Free time thresholds in minutes
        free_time_thresholds = [120, 180, 240, 360]
        selected_threshold = BasePayloadGenerator.get_random_element(free_time_thresholds)
        
        payload = {
            "facilityId": facility_id,
            "detentionType": selected_type,
            "freeTimeThreshold": selected_threshold,
            "dateRange": {
                "startDate": BasePayloadGenerator.get_random_past_date(30),
                "endDate": BasePayloadGenerator.get_random_date(1)
            },
            "includeCharges": BasePayloadGenerator.get_random_element([True, False]),
            "groupByCarrier": BasePayloadGenerator.get_random_element([True, False])
        }
        
        if carrier_ids:
            payload["carrierIds"] = BasePayloadGenerator.get_random_subset(carrier_ids, 10)
            
        return payload
    except (ValueError, TypeError) as e:
        default_payload = {
            "facilityId": 101,
            "detentionType": "BOTH",
            "freeTimeThreshold": 180,
            "dateRange": {
                "startDate": BasePayloadGenerator.get_random_past_date(7),
                "endDate": BasePayloadGenerator.get_random_date(1)
            },
            "includeCharges": True,
            "groupByCarrier": True
        }
        return BasePayloadGenerator.handle_error(e, default_payload)

if __name__ == "__main__":
    # Usage: python detention_summary_generator.py <facility_id> [carrier_ids]
    if len(sys.argv) < 2:
        print("Usage: python detention_summary_generator.py <facility_id> [carrier_ids]", file=sys.stderr)
        sys.exit(1)
    
    facility_id = sys.argv[1]
    carrier_ids_string = sys.argv[2] if len(sys.argv) > 2 else None
    payload = generate_payload(facility_id, carrier_ids_string)
    print(json.dumps(payload))