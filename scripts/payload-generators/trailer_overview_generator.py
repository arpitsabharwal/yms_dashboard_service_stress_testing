import json
import sys
from base_payload_generator import BasePayloadGenerator

def generate_payload(facility_id, carrier_ids_string=None):
    facility_id = int(facility_id)
    carrier_ids = BasePayloadGenerator.parse_carrier_ids(carrier_ids_string) if carrier_ids_string else []
    trailer_states = ["all", "noFlags", "audit", "damaged", "outOfService"]
    selected_state = BasePayloadGenerator.get_random_element(trailer_states)
    payload = {
        "facilityId": facility_id,
        "trailerState": selected_state
    }
    if carrier_ids:
        payload["carrierIds"] = BasePayloadGenerator.get_random_subset(carrier_ids, 5)
    return payload

if __name__ == "__main__":
    # Usage: python trailer_overview_generator.py <facility_id> [carrier_ids]
    if len(sys.argv) < 2:
        print("Usage: python trailer_overview_generator.py <facility_id> [carrier_ids]")
        sys.exit(1)
    facility_id = sys.argv[1]
    carrier_ids_string = sys.argv[2] if len(sys.argv) > 2 else None
    payload = generate_payload(facility_id, carrier_ids_string)
    print(json.dumps(payload)) 