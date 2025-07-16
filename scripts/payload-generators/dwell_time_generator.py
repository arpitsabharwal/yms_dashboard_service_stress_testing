import json
import sys
from base_payload_generator import BasePayloadGenerator

def generate_payload(facility_id, carrier_ids_string=None):
    facility_id = int(facility_id)
    carrier_ids = BasePayloadGenerator.parse_carrier_ids(carrier_ids_string) if carrier_ids_string else []
    thresholds = [24, 48, 72, 96, 120, 168]
    selected_threshold = BasePayloadGenerator.get_random_element(thresholds)
    group_by_options = ["CARRIER", "TRAILER_TYPE", "LOCATION", "DAY_OF_WEEK"]
    selected_group_by = BasePayloadGenerator.get_random_element(group_by_options)
    payload = {
        "facilityId": facility_id,
        "thresholdHours": selected_threshold,
        "groupBy": selected_group_by
    }
    if carrier_ids:
        payload["carrierIds"] = BasePayloadGenerator.get_random_subset(carrier_ids, 5)
    return payload

if __name__ == "__main__":
    # Usage: python dwell_time_generator.py <facility_id> [carrier_ids]
    if len(sys.argv) < 2:
        print("Usage: python dwell_time_generator.py <facility_id> [carrier_ids]")
        sys.exit(1)
    facility_id = sys.argv[1]
    carrier_ids_string = sys.argv[2] if len(sys.argv) > 2 else None
    payload = generate_payload(facility_id, carrier_ids_string)
    print(json.dumps(payload)) 