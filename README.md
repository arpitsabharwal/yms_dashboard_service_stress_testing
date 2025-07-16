# YMS Dashboard Stress Testing - Execution Guide

This guide provides step-by-step instructions for preparing test data and executing different types of stress tests for the YMS Dashboard Service.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Initial Setup](#initial-setup)
- [Test Data Preparation](#test-data-preparation)
- [Test Execution](#test-execution)
- [Viewing Results](#viewing-results)
- [Troubleshooting](#troubleshooting)

## Prerequisites

Before running tests, ensure you have:
- Java 11+ installed
- Python 3.8+ installed
- JMeter 5.6.2 installed
- Network access to YMS Dashboard Service
- Valid authentication tokens for tenants

## Initial Setup

### 1. Clone and Setup Repository

```bash
# Clone the repository
git clone <repository-url>
cd yms-stress-testing-framework

# Make scripts executable
chmod +x scripts/*.sh

# Create necessary directories
mkdir -p logs/jmeter logs/python reports/html reports/csv reports/summary results test-data
```

### 2. Install Dependencies

```bash
# Install Python dependencies
cd python
pip install -r requirements.txt
cd ..

# Verify installation
python -m pytest python/tests/ -v
```

### 3. Configure JMeter

```bash
# Set JMETER_HOME environment variable
export JMETER_HOME=/path/to/apache-jmeter-5.6.2

# Add to your shell profile (.bashrc, .zshrc, etc.)
echo 'export JMETER_HOME=/path/to/apache-jmeter-5.6.2' >> ~/.zshrc
echo 'export PATH=$JMETER_HOME/bin:$PATH' >> ~/.zshrc
source ~/.zshrc

# Verify JMeter installation
jmeter -v
```

## Test Data Preparation

### 1. Configure Tenants

Edit `python/config/tenant_config.yaml` with your actual tenant data:

```yaml
tenants:
  your-tenant-name:
    name: "your-tenant-name"
    rpm_config:
      yard-availability: 100
      trailer-overview: 150
      trailer-exception-summary: 80
      # ... configure RPM for each endpoint
    data_pool:
      facility_ids: [1001, 1002, 1003, 1004, 1005]  # Your actual facility IDs
      carrier_ids: [2001, 2002, 2003, 2004]         # Your actual carrier IDs
      user_ids: [3001, 3002, 3003]                  # Your actual user IDs
      saved_filter_ids: [4001, 4002, 4003]          # Your actual filter IDs
    auth:
      token: "Bearer eyJhbGciOiJIU..."              # Your actual JWT token
    sla:
      response_time_ms: 2000
      error_rate_percent: 1
```

### 2. Update CSV Data File

Edit `jmeter/data/tenant-data.csv` with tenant credentials:

```csv
tenant_name,auth_token
your-tenant-name,"Bearer eyJhbGciOiJIU..."
tenant-prod-1,"Bearer eyJhbGciOiJIU..."
tenant-prod-2,"Bearer eyJhbGciOiJIU..."
```

### 3. Generate Sample Payloads

Generate and verify payloads for all endpoints:

```bash
# Generate payloads for a specific tenant
./scripts/generate-all-payloads.sh your-tenant-name

# Verify generated payloads
ls -la test-data/

# View a sample payload
cat test-data/your-tenant-name_yard-availability.json | jq .
```

### 4. Test Individual Endpoints

Test payload generation for specific endpoints:

```bash
cd python

# Generate single payload
python -m cli generate --tenant your-tenant-name --endpoint yard-availability

# Generate multiple payloads
python -m cli generate --tenant your-tenant-name --endpoint trailer-overview --count 5

# Save to file
python -m cli generate --tenant your-tenant-name --endpoint site-occupancy --count 10 --output-file ../test-data/site-occupancy-test.json

cd ..
```

## Test Execution

### 1. Smoke Test (Quick Validation)

**Purpose**: Validate all endpoints are working correctly with minimal load

```bash
# Run 5-minute smoke test
./scripts/run-local.sh --tenant your-tenant-name --scenario smoke_test --duration 300

# Expected output:
# - Total requests: ~500-1000
# - Error rate: < 0.1%
# - Response time: < 500ms
```

### 2. Load Test (Normal Capacity)

**Purpose**: Test system under expected normal load

```bash
# Run 1-hour load test
./scripts/run-local.sh --tenant your-tenant-name --scenario load_test --duration 3600

# For shorter test (15 minutes)
./scripts/run-local.sh --tenant your-tenant-name --scenario load_test --duration 900

# Expected output:
# - Sustained target RPM
# - Error rate: < 1%
# - P95 response time: < 2000ms
```

### 3. Stress Test (Peak Load)

**Purpose**: Find system breaking point

```bash
# Run 30-minute stress test (150% load)
./scripts/run-local.sh --tenant your-tenant-name --scenario stress_test --duration 1800

# Monitor system resources during test
# Watch for:
# - Increased error rates
# - Response time degradation
# - System resource exhaustion
```

### 4. Endurance Test (Soak Test)

**Purpose**: Detect memory leaks and performance degradation over time

```bash
# Run 4-hour endurance test (80% load)
./scripts/run-local.sh --tenant your-tenant-name --scenario endurance_test --duration 14400

# For shorter test (2 hours)
./scripts/run-local.sh --tenant your-tenant-name --scenario endurance_test --duration 7200
```

### 5. Spike Test (Sudden Load)

**Purpose**: Test system behavior under sudden load increase

```bash
# Run 20-minute spike test (200% load with 5-second ramp-up)
./scripts/run-local.sh --tenant your-tenant-name --scenario spike_test --duration 1200
```

### 6. Multi-Tenant Test

**Purpose**: Test multiple tenants simultaneously

```bash
# First, ensure all tenants are configured in tenant_config.yaml

# Run distributed test with multiple tenants
./scripts/run-distributed.sh --tenants "tenant-1,tenant-2,tenant-3" --scenario load_test

# Note: Requires JMeter distributed setup
```

### 7. Custom Test Parameters

Run tests with custom parameters:

```bash
# Custom duration
./scripts/run-local.sh --tenant your-tenant-name --scenario load_test --duration 600

# Run with specific JMeter properties
jmeter -n -t jmeter/test-plans/YMS-Dashboard-Master-Test.jmx \
  -Jbase.url=https://staging.example.com \
  -Jtenant=your-tenant-name \
  -Jthreads=50 \
  -Jduration=900 \
  -Jrampup=60 \
  -l results/custom_test.jtl
```

## Viewing Results

### 1. JMeter HTML Report

After each test, an HTML report is automatically generated:

```bash
# Open the latest test report
open results/*/html-report/index.html

# Or navigate to specific test
open results/20240115_143022/html-report/index.html
```

### 2. Generate Custom Reports

Generate detailed reports from JTL files:

```bash
cd python

# Generate reports for completed test
python -m cli report \
  --jtl-file ../results/20240115_143022/results.jtl \
  --tenant your-tenant-name \
  --test-name load_test

cd ..

# View generated reports
open reports/html/*.html
cat reports/csv/*.csv
cat reports/summary/*.json | jq .
```

### 3. Analyze Multiple Test Results

Compare results across multiple test runs:

```bash
# Run analysis script
python scripts/analyze-results.py reports/

# This will show:
# - Tenant performance comparison
# - Endpoint performance trends
# - Error rate patterns
```

### 4. Real-time Monitoring

Monitor test execution in real-time:

```bash
# Watch JMeter logs
tail -f logs/jmeter/*.log

# Filter for errors and warnings
tail -f logs/jmeter/*.log | grep -E "(ERROR|WARN|SEVERE)"

# Monitor response times
tail -f results/*/results.jtl | awk -F',' '{print $2 "," $14}' | tail -20
```

## Test Scenarios Summary

| Scenario | Duration | Load % | Ramp-up | Use Case |
|----------|----------|--------|---------|----------|
| Smoke Test | 5 min | 10% | 30s | Quick validation |
| Load Test | 60 min | 100% | 5 min | Normal capacity |
| Stress Test | 30 min | 150% | 3 min | Breaking point |
| Endurance | 4 hours | 80% | 10 min | Memory leaks |
| Spike Test | 20 min | 200% | 5s | Sudden load |

## Interpreting Results

### Key Metrics to Monitor

1. **Response Time**
   - Average: General performance indicator
   - P90/P95/P99: Critical for SLA compliance
   - Max: Worst-case scenarios

2. **Throughput**
   - Requests/second achieved vs. target
   - Transactions per minute

3. **Error Rate**
   - Should be < 1% for load tests
   - Track error types and patterns

4. **Resource Utilization**
   - JMeter client CPU/memory
   - Network bandwidth

### Success Criteria

✅ **Smoke Test Pass**:
- All endpoints return 200 OK
- No errors in logs
- Response times < 500ms

✅ **Load Test Pass**:
- Error rate < 1%
- P95 response time < 2000ms
- Sustained target throughput

✅ **Stress Test Insights**:
- Breaking point identified
- Graceful degradation observed
- Recovery after load reduction

## Troubleshooting

### Common Issues and Solutions

#### 1. Permission Denied Error
```bash
# Fix: Make scripts executable
chmod +x scripts/*.sh
```

#### 2. JMeter Not Found
```bash
# Fix: Set JMETER_HOME
export JMETER_HOME=/path/to/jmeter
export PATH=$JMETER_HOME/bin:$PATH
```

#### 3. Python Module Not Found
```bash
# Fix: Install dependencies
cd python && pip install -r requirements.txt
```

#### 4. Authentication Failures
```bash
# Fix: Update tenant tokens in config
# Verify token format: "Bearer <token>"
# Check token expiration
```

#### 5. High Memory Usage
```bash
# Fix: Increase JMeter heap
export HEAP="-Xms4g -Xmx4g"
```

#### 6. Connection Refused
```bash
# Fix: Verify target URL
# Check network connectivity
# Confirm service is running
```

### Debug Mode

Run tests in debug mode for troubleshooting:

```bash
# JMeter GUI mode
jmeter -t jmeter/test-plans/YMS-Dashboard-Master-Test.jmx

# Enable debug logging
jmeter -n -t jmeter/test-plans/YMS-Dashboard-Master-Test.jmx \
  -L DEBUG \
  -Jlog_level.jmeter=DEBUG

# Test payload generation
cd python
python -m cli generate --tenant your-tenant-name --endpoint yard-availability
```

## Best Practices

1. **Start Small**: Always run smoke tests before full load tests
2. **Monitor Resources**: Watch both client and server resources
3. **Incremental Load**: Gradually increase load to find limits
4. **Clean Environment**: Ensure clean test environment between runs
5. **Document Results**: Keep records of all test configurations and results
6. **Regular Testing**: Schedule periodic performance tests

## Next Steps

1. Review generated reports and identify bottlenecks
2. Share results with development team
3. Create performance baselines
4. Set up automated performance testing in CI/CD
5. Monitor production performance metrics

For additional help, refer to:
- [JMeter Documentation](https://jmeter.apache.org/usermanual/index.html)
- [Project Wiki](./docs/)
- [Issue Tracker](https://github.com/yourorg/yms-stress-testing/issues)