# YMS Dashboard JMeter Testing Framework

A comprehensive JMeter-based performance testing framework for the YMS Dashboard Service APIs with multi-tenant support.

## Features

- **Multi-tenant Support**: Test multiple tenants simultaneously with different RPM configurations
- **10 API Endpoints**: Complete coverage of all YMS Dashboard Service APIs
- **Dynamic Payload Generation**: Groovy scripts generate realistic test data
- **Flexible Load Distribution**: Configure load distribution across facilities and APIs
- **Multiple Test Profiles**: Smoke, load, and stress test configurations
- **Distributed Testing**: Support for distributed load generation
- **Real-time Monitoring**: Integration with InfluxDB/Grafana for live metrics
- **Comprehensive Reporting**: HTML reports with detailed performance metrics

## Prerequisites

- Java 8 or higher
- Apache JMeter 5.0 or higher
- Bash shell (for Linux/Mac) or Git Bash (for Windows)
- Optional: InfluxDB and Grafana for real-time monitoring

## Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd jmeter-yms-dashboard-test
   ```

2. **Run setup script**
   ```bash
   chmod +x scripts/*.sh
   ./scripts/setup.sh
   ```

3. **Configure test data**
   - Edit `data/tenants.csv` with your tenant information
   - Update `data/facilities.csv` with facility mappings
   - Add authentication tokens to `data/tenants.csv`

4. **Run a smoke test**
   ```bash
   ./scripts/run-test.sh --profile smoke-test --base-url http://your-api-url
   ```

## Project Structure

```
jmeter-yms-dashboard-test/
├── test-plans/           # JMeter test plans
├── data/                 # Test data files
├── scripts/              # Execution and utility scripts
├── config/               # Configuration files
├── results/              # Test results (created at runtime)
└── reports/              # HTML reports (created at runtime)
```

## Configuration

### Tenant Configuration (data/tenants.csv)

```csv
tenant_id,tenant_name,target_rpm,auth_token,ramp_up_seconds
TENANT_A,Customer Alpha,1200,Bearer <token>,300
TENANT_B,Customer Beta,800,Bearer <token>,180
```

- `tenant_id`: Unique identifier for the tenant
- `tenant_name`: Human-readable tenant name
- `target_rpm`: Target requests per minute for this tenant
- `auth_token`: Bearer token for authentication
- `ramp_up_seconds`: Time to reach target load

### Facility Distribution (data/facilities.csv)

```csv
tenant_id,facility_id,facility_name,load_weight,carrier_ids
TENANT_A,101,DC West,0.6,"201,202,203"
TENANT_A,102,DC East,0.4,"204,205"
```

- `load_weight`: Percentage of tenant load for this facility (0.0-1.0)
- `carrier_ids`: Comma-separated list of carrier IDs

### API Mix Configuration

The default API distribution is:
- yard-availability: 15%
- trailer-overview: 20%
- trailer-exception-summary: 10%
- task-workload-summary: 10%
- task-attention-summary: 5%
- site-occupancy: 15%
- shipment-volume-forecast: 10%
- dwell-time-summary: 5%
- door-breakdown-summary: 5%
- detention-summary: 5%

## Running Tests

### Basic Test Execution

```bash
# Run with default settings
./scripts/run-test.sh

# Specify base URL and duration
./scripts/run-test.sh --base-url https://api.example.com --duration 3600

# Test specific tenants
./scripts/run-test.sh --tenants TENANT_A,TENANT_B

# Use a test profile
./scripts/run-test.sh --profile load-test

# Increase load by 50%
./scripts/run-test.sh --rpm-multiplier 1.5
```

### Test Profiles

1. **Smoke Test** (`--profile smoke-test`)
   - Duration: 5 minutes
   - Load: 10% of configured RPM
   - Purpose: Quick validation

2. **Load Test** (`--profile load-test`)
   - Duration: 1 hour
   - Load: 100% of configured RPM
   - Purpose: Standard performance testing

3. **Stress Test** (`--profile stress-test`)
   - Duration: 2 hours
   - Load: 150% of configured RPM
   - Purpose: Find system limits

### Excluding APIs

To exclude specific APIs from a test run:

```bash
./scripts/run-test.sh --exclude-apis "yard-availability,trailer-overview"
```

### Dry Run

Validate configuration without running tests:

```bash
./scripts/run-test.sh --dry-run --tenants TENANT_A
```

## Distributed Testing

### Setup Slave Machines

1. Install JMeter on all slave machines
2. Ensure network connectivity between master and slaves
3. Configure firewall rules for RMI communication

### Start Slave Servers

```bash
./scripts/run-distributed.sh --slaves slave1,slave2,slave3 --start-slaves
```

### Run Distributed Test

```bash
./scripts/run-distributed.sh \
  --slaves slave1,slave2,slave3 \
  --base-url https://api.example.com \
  --duration 3600 \
  --profile load-test
```

### Check Slave Status

```bash
./scripts/run-distributed.sh --slaves slave1,slave2,slave3 --check-slaves
```

## Adding New Tenants

1. Add tenant to `data/tenants.csv`:
   ```csv
   TENANT_D,Customer Delta,1000,Bearer <token>,240
   ```

2. Add facilities for the tenant in `data/facilities.csv`:
   ```csv
   TENANT_D,401,Warehouse A,0.7,"501,502,503"
   TENANT_D,402,Warehouse B,0.3,"504,505"
   ```

3. Ensure total `load_weight` for each tenant equals 1.0

## Modifying RPM Settings

### Global RPM Adjustment

Use the `--rpm-multiplier` flag:
```bash
# 50% of configured load
./scripts/run-test.sh --rpm-multiplier 0.5

# 200% of configured load
./scripts/run-test.sh --rpm-multiplier 2.0
```

### Per-Tenant RPM

Edit `data/tenants.csv` and modify the `target_rpm` column.

### API Mix Adjustment

Modify the throughput percentages in `test-plans/yms-dashboard-main.jmx`:
```xml
<FloatProperty>
  <n>ThroughputController.percentThroughput</n>
  <value>15.0</value>  <!-- Change this value -->
</FloatProperty>
```

## Monitoring and Reporting

### Real-time Monitoring with InfluxDB

1. Install and start InfluxDB:
   ```bash
   docker run -p 8086:8086 influxdb:1.8
   ```

2. Create database:
   ```bash
   curl -XPOST 'http://localhost:8086/query' --data-urlencode "q=CREATE DATABASE jmeter"
   ```

3. Configure JMeter backend listener (already configured in test plan)

4. View metrics in InfluxDB or connect Grafana

### HTML Reports

Reports are automatically generated after each test run:
```
reports/<report-name>/index.html
```

### Custom Reporting

Access raw results for custom analysis:
```
results/<report-name>/results.jtl
```

## Troubleshooting

### Common Issues

1. **"JMeter not found"**
   - Ensure JMeter is installed and in PATH
   - Set JMETER_HOME environment variable

2. **"Test plan not found"**
   - Run setup.sh to create directory structure
   - Check file paths in error message

3. **Authentication failures**
   - Verify bearer tokens in tenants.csv
   - Check token expiration
   - Ensure tenant header is correct

4. **High error rate**
   - Check server logs
   - Reduce load with --rpm-multiplier
   - Verify API endpoints are correct

5. **Out of memory errors**
   - Increase JMeter heap size in jmeter.properties
   - Reduce thread count
   - Disable response data saving

### Debug Mode

Enable JMeter debug logging:
```bash
./scripts/run-test.sh --base-url http://localhost:5003 2>&1 | tee debug.log
```

View JMeter logs:
```bash
tail -f logs/jmeter_*.log
```

## Best Practices

1. **Start Small**: Always run smoke tests before full load tests
2. **Monitor Resources**: Watch server CPU, memory, and network
3. **Gradual Ramp-up**: Use appropriate ramp-up times
4. **Data Variety**: Ensure test data has sufficient variety
5. **Regular Baselines**: Establish performance baselines
6. **Clean Test Data**: Reset test data between runs if needed

## Performance Tuning

### JMeter Configuration

Edit `config/jmeter.properties`:
```properties
# Increase heap size
HEAP=-Xms4g -Xmx8g

# Reduce memory usage
jmeter.save.saveservice.output_format=csv
jmeter.save.saveservice.response_data=false
jmeter.save.saveservice.samplerData=false
```

### OS Tuning (Linux)

```bash
# Increase file descriptors
ulimit -n 65535

# Tune network parameters
sudo sysctl -w net.ipv4.tcp_tw_reuse=1
sudo sysctl -w net.ipv4.ip_local_port_range="1024 65535"
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

[Your License Here]

## Support

For issues and questions:
- Create an issue in the repository
- Contact the team at: [support email] 