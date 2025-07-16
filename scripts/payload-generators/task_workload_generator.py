import json
import sys
from base_payload_generator import BasePayloadGenerator

def generate_payload(facility_id):
    facility_id = int(facility_id)
    task_types = ["LOADING", "UNLOADING", "INSPECTION", "MAINTENANCE", "MOVEMENT"]
    selected_task_type = BasePayloadGenerator.get_random_element(task_types)
    time_ranges = ["LAST_HOUR", "LAST_24_HOURS", "LAST_7_DAYS", "LAST_30_DAYS"]
    selected_time_range = BasePayloadGenerator.get_random_element(time_ranges)
    payload = {
        "facilityId": facility_id,
        "taskType": selected_task_type,
        "timeRange": selected_time_range
    }
    return payload

if __name__ == "__main__":
    # Usage: python task_workload_generator.py <facility_id>
    if len(sys.argv) != 2:
        print("Usage: python task_workload_generator.py <facility_id>")
        sys.exit(1)
    facility_id = sys.argv[1]
    payload = generate_payload(facility_id)
    print(json.dumps(payload)) 