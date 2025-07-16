# Python Payload Generators

This directory contains Python scripts for generating dynamic payloads for JMeter test plans. These scripts replace the previous Groovy-based payload generators.

## Usage

Each script can be run from the command line and prints a JSON payload to stdout. Example:

```bash
python facility_request_generator.py 101
python trailer_overview_generator.py 101 "201,202,203"
python shipment_forecast_generator.py 101
```

## Migration

- All helpers and payload generators are now in Python.
- The main JMeter test plans can invoke these scripts using the JSR223 Sampler (with Python/Jython) or via OS Process Sampler.
- See each script for argument details.

## Scripts
- `base_payload_generator.py`: Common utility functions
- `facility_request_generator.py`: For APIs requiring only facilityId
- `trailer_overview_generator.py`: For trailer overview API
- `trailer_exceptions_generator.py`: For trailer exception summary API
- `shipment_forecast_generator.py`: For shipment volume forecast API
- `saved_filter_generator.py`: For generating random saved filter payloads
- `task_workload_generator.py`: For task workload summary API
- `dwell_time_generator.py`: For dwell time summary API 