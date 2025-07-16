#!/usr/bin/env python3
"""Generate payload for task-attention-summary API"""

import json
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from base_payload_generator import BasePayloadGenerator

def generate_payload(facility_id):
    """Generate task attention summary payload"""
    try:
        facility_id = int(facility_id)
        
        # Task priority levels
        priority_levels = ["HIGH", "MEDIUM", "LOW", "URGENT"]
        selected_priority = BasePayloadGenerator.get_random_element(priority_levels)
        
        # Task statuses
        task_statuses = ["PENDING", "IN_PROGRESS", "OVERDUE", "BLOCKED"]
        selected_status = BasePayloadGenerator.get_random_element(task_statuses)
        
        payload = {
            "facilityId": facility_id,
            "priorityLevel": selected_priority,
            "taskStatus": selected_status,
            "includeOverdue": BasePayloadGenerator.get_random_element([True, False]),
            "pageSize": BasePayloadGenerator.get_random_page_size()
        }
        
        return payload
    except (ValueError, TypeError) as e:
        default_payload = {
            "facilityId": 101,
            "priorityLevel": "HIGH",
            "taskStatus": "PENDING",
            "includeOverdue": True,
            "pageSize": 20
        }
        return BasePayloadGenerator.handle_error(e, default_payload)

if __name__ == "__main__":
    # Usage: python task_attention_generator.py <facility_id>
    if len(sys.argv) != 2:
        print("Usage: python task_attention_generator.py <facility_id>", file=sys.stderr)
        sys.exit(1)
    
    facility_id = sys.argv[1]
    payload = generate_payload(facility_id)
    print(json.dumps(payload))