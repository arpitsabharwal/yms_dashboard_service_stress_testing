import json
import sys
import datetime
from base_payload_generator import BasePayloadGenerator

def generate_payload(facility_id):
    facility_id = int(facility_id)
    start_date = datetime.date.today()
    end_date = start_date + datetime.timedelta(days=7)
    directions = ["INBOUND", "OUTBOUND"]
    selected_direction = BasePayloadGenerator.get_random_element(directions)
    payload = {
        "facilityId": facility_id,
        "startDate": start_date.isoformat(),
        "endDate": end_date.isoformat(),
        "shipmentDirection": selected_direction
    }
    return payload

if __name__ == "__main__":
    # Usage: python shipment_forecast_generator.py <facility_id>
    if len(sys.argv) != 2:
        print("Usage: python shipment_forecast_generator.py <facility_id>")
        sys.exit(1)
    facility_id = sys.argv[1]
    payload = generate_payload(facility_id)
    print(json.dumps(payload)) 