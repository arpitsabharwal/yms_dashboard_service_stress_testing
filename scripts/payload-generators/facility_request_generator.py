import json
import sys

def generate_payload(facility_id):
    payload = {
        "facilityId": int(facility_id)
    }
    return payload

if __name__ == "__main__":
    # Usage: python facility_request_generator.py <facility_id>
    if len(sys.argv) != 2:
        print("Usage: python facility_request_generator.py <facility_id>")
        sys.exit(1)
    facility_id = sys.argv[1]
    payload = generate_payload(facility_id)
    print(json.dumps(payload)) 