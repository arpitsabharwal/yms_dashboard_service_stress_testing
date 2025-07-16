#!/usr/bin/env python3
"""Generate payload for APIs that only require facilityId"""

import json
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from base_payload_generator import BasePayloadGenerator

def generate_payload(facility_id):
    """Generate facility request payload"""
    try:
        payload = {
            "facilityId": int(facility_id)
        }
        return payload
    except (ValueError, TypeError) as e:
        default_payload = {"facilityId": 101}
        return BasePayloadGenerator.handle_error(e, default_payload)

if __name__ == "__main__":
    # Usage: python facility_request_generator.py <facility_id>
    if len(sys.argv) != 2:
        print("Usage: python facility_request_generator.py <facility_id>", file=sys.stderr)
        sys.exit(1)
    
    facility_id = sys.argv[1]
    payload = generate_payload(facility_id)
    print(json.dumps(payload))