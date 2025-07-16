#!/usr/bin/env python3
"""Generate payload for trailer-exception-summary API"""

import json
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from base_payload_generator import BasePayloadGenerator

def generate_payload(facility_id, carrier_ids_string=None):
    """Generate trailer exceptions payload"""
    try:
        facility_id = int(facility_id)
        carrier_ids = BasePayloadGenerator.parse_carrier_ids(carrier_ids_string) if carrier_ids_string else []
        
        threshold_hours = BasePayloadGenerator.get_random_threshold_hours()
        bypass_flagged = BasePayloadGenerator.get_random_element([True, False])
        
        payload = {
            "facilityId": facility_id,
            "thresholdHours": threshold_hours,
            "bypassFlagged": bypass_flagged
        }
        
        if carrier_ids:
            payload["carrierIds"] = BasePayloadGenerator.get_random_subset(carrier_ids, 5)
            
        return payload
    except (ValueError, TypeError) as e:
        default_payload = {
            "facilityId": 101,
            "thresholdHours": 48,
            "bypassFlagged": False
        }
        return BasePayloadGenerator.handle_error(e, default_payload)

if __name__ == "__main__":
    # Usage: python trailer_exceptions_generator.py <facility_id> [carrier_ids]
    if len(sys.argv) < 2:
        print("Usage: python trailer_exceptions_generator.py <facility_id> [carrier_ids]", file=sys.stderr)
        sys.exit(1)
    
    facility_id = sys.argv[1]
    carrier_ids_string = sys.argv[2] if len(sys.argv) > 2 else None
    payload = generate_payload(facility_id, carrier_ids_string)
    print(json.dumps(payload))