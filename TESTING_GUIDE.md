# YMS Dashboard Testing Guide

## Quick Start Test Commands

### 1. Setup and Validation

```bash
# Make scripts executable
chmod +x scripts/*.sh

# Run initial setup
./scripts/setup.sh

# Check JMeter installation first
./scripts/check-jmeter.sh

# Validate all test data
./scripts/validate-data.sh

# Make Python generators executable
chmod +x scripts/payload-generators/*.py
```

### 2. Smoke Test (5 minutes, 10% load)

```bash
# Basic smoke test
./scripts/run-test.sh --profile smoke-test --base-url http://localhost:5003

# Smoke test for specific tenant
./scripts/run-test.sh --profile smoke-test --tenants TENANT_A --base-url http://localhost:5003

# Smoke test excluding certain APIs
./scripts/run-test.sh --profile smoke-test --exclude-apis "detention-summary,door-breakdown"
```

### 3. Load Test (1 hour, 100% load)

```bash
# Standard load test
./scripts/run-test.sh --profile load-test --base-url https://api.example.com

# Load test with custom duration
./scripts/run-test.sh --profile load-test --duration 1800 --base-url https://api.example.com

# Load test for multiple tenants
./scripts/run-test.sh --profile load-test --tenants TENANT_A,TENANT_B,TENANT_C
```

### 4. Stress Test (2 hours, 150% load)

```bash
# Standard stress test
./scripts/run-test.sh --profile stress-test --base-url https://api.example.com

# Stress test with custom RPM multiplier
./scripts/run-test.sh --profile stress-test --rpm-multiplier 2.0

# Stress test with custom report name
./scripts/run-test.sh --profile stress-test --report-name stress-test-peak-hours
```

### 5. Distributed Testing

```bash
# Setup slave machines
./scripts/run-distributed.sh --slaves slave1,slave2,slave3 --setup-slaves

# Start slave servers
./scripts/run-distributed.sh --slaves slave1,slave2,slave3 --start-slaves

# Check slave status
./scripts/run-distributed.sh --slaves slave1,slave2,slave3 --check-slaves

# Run distributed load test
./scripts/run-distributed.sh --slaves slave1,slave2,slave3 \
  --base-url https://api.example.com \
  --duration 3600 \
  --profile load-test

# Stop slave servers
./scripts/run-distributed.sh --slaves slave1,slave2,slave3 --stop-slaves
```

### 6. Custom Test Scenarios

```bash
# Test with 50% of configured load
./scripts/run-test.sh --base-url https://api.example.com --rpm-multiplier 0.5

# Test for 30 minutes with double load
./scripts/run-test.sh --duration 1800 --rpm-multiplier 2.0

# Dry run to validate configuration
./scripts/run-test.sh --dry-run --tenants TENANT_A

# Run in GUI mode for debugging
./scripts/run-test.sh --gui --profile smoke-test
```

## Testing Python Payload Generators

### Individual Generator Testing

```bash
# Test facility request generator
python3 scripts/payload-generators/facility_request_generator.py 101

# Test trailer overview generator
python3 scripts/payload-generators/trailer_overview_generator.py 101 "201,202,203"

# Test shipment forecast generator
python3 scripts/payload-generators/shipment_forecast_generator.py 101

# Test with JSON formatting (requires jq)
python3 scripts/payload-generators/task_workload_generator.py 101 | jq .
```

### Batch Testing All Generators

```bash
# Create a test script
cat > test-generators.sh << 'EOF'
#!/bin/bash
echo "Testing all payload generators..."

generators=(
    "facility_request_generator.py 101"
    "trailer_overview_generator.py 101 201,202,203"
    "trailer_exceptions_generator.py 101 201,202,203"
    "task_workload_generator.py 101"
    "task_attention_generator.py 101"
    "site_occupancy_generator.py 101"
    "shipment_forecast_generator.py 101"
    "dwell_time_generator.py 101 201,202,203"
    "door_breakdown_generator.py 101"
    "detention_summary_generator.py 101 201,202,203"
)

for generator in "${generators[@]}"; do
    echo -n "Testing $generator... "
    if python3 scripts/payload-generators/$generator 2>/dev/null | jq . >/dev/null 2>&1; then
        echo "✓ OK"
    else
        echo "✗ FAILED"
    fi
done
EOF

chmod +x test-generators.sh
./test-generators.sh
```

## Monitoring Test Execution

### Real-time Monitoring with InfluxDB

```bash
# Start InfluxDB
docker run -d -p 8086:8086 --name influxdb influxdb:1.8

# Create database
curl -XPOST 'http://localhost:8086/query' --data-urlencode "q=CREATE DATABASE jmeter"

# Run test with monitoring enabled
./scripts/run-test.sh --profile load-test --base-url https://api.example.com
```

### Viewing Results

```bash
# Latest test results
ls -la results/

# View summary report
cat reports/*/summary.txt

# Open HTML report
open reports/*/index.html  # macOS
xdg-open reports/*/index.html  # Linux
```

### Analyzing JTL Results

```bash
# Quick stats from JTL file
awk -F',' 'NR>1 {
    total++
    sum+=$2
    if ($4=="true") success++
} END {
    print "Total Requests: " total
    print "Success Rate: " (success/total*100) "%"
    print "Avg Response Time: " (sum/total) " ms"
}' results/*/results.jtl
```

## Troubleshooting Common Issues

### 1. Python Generator Errors

```bash
# Test Python environment
python3 --version
python3 -c "import json, random, datetime; print('Python modules OK')"

# Debug specific generator
python3 -u scripts/payload-generators/facility_request_generator.py 101 2>&1

# Check Python path issues
cd scripts/payload-generators
python3 facility_request_generator.py 101
```

### 2. JMeter Execution Issues

```bash
# Check JMeter version
jmeter --version

# Run with debug logging
jmeter -Ljmeter.engine=DEBUG -n -t test-plans/yms-dashboard-main.jmx \
  -l debug-test.jtl -j debug-jmeter.log

# Validate JMX file
jmeter -n -t test-plans/yms-dashboard-main.jmx --testfile
```

### 3. Authentication Issues

```bash
# Test authentication with curl
curl -X POST https://api.example.com/yms-dashboard-service/api/v1/yard-availability \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "tenant: TENANT_A" \
  -H "Content-Type: application/json" \
  -d '{"facilityId": 101}'
```

### 4. Memory Issues

```bash
# Increase JMeter heap size
export HEAP="-Xms4g -Xmx8g"
./scripts/run-test.sh --profile load-test

# Monitor memory usage during test
watch -n 1 'ps aux | grep jmeter | grep -v grep'
```

## Best Practices

1. **Always run smoke tests first** before load/stress tests
2. **Monitor server resources** during tests (CPU, memory, disk I/O)
3. **Start with lower loads** and gradually increase
4. **Use distributed testing** for loads > 5000 RPM
5. **Clean up old results** regularly to save disk space
6. **Version control your test data** (except auth tokens)
7. **Document test scenarios** and expected results

## Sample Test Report

After running a test, you'll find:

```
reports/yms-test-20250716_143025/
├── index.html              # Main HTML report
├── content/
│   ├── js/                # JavaScript files
│   └── css/               # Stylesheets
└── summary.txt            # Text summary

results/yms-test-20250716_143025/
└── results.jtl            # Raw test results
```

View the HTML report for:
- Response time graphs
- Throughput charts
- Error analysis
- Response time percentiles
- Active threads over time