import json
import random
import time
from base_payload_generator import BasePayloadGenerator

def generate_saved_filter():
    filter_types = ["TRAILER", "TASK", "SHIPMENT", "CARRIER"]
    operators = ["EQ", "NEQ", "GT", "LT", "IN", "NOT_IN", "CONTAINS", "STARTS_WITH", "ENDS_WITH"]
    filters = []
    num_filters = random.randint(1, 3)
    for i in range(num_filters):
        filters.append({
            "field": f"field_{i}",
            "operator": BasePayloadGenerator.get_random_element(operators),
            "value": f"value_{i}"
        })
    payload = {
        "name": f"Test Filter {int(time.time() * 1000)}",
        "type": BasePayloadGenerator.get_random_element(filter_types),
        "filters": filters,
        "isDefault": random.choice([True, False])
    }
    return payload

if __name__ == "__main__":
    print(json.dumps(generate_saved_filter())) 