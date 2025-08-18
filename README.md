## Project Overview

JMeter-based stress testing framework for the YMS (Yard Management System) Dashboard Service. Tests multiple API endpoints across different tenants, simulating real-world load patterns for performance validation.

## Architecture

### Multi-Tenant Authentication Flow
1. **Keycloak Admin API Integration**: Uses `keycloak_admin_token_generator.py` to programmatically switch user tenant context
2. **SAML Authentication**: `generate_bearer_token.py` handles the SAML flow with Keycloak
3. **Token Storage**: Tokens stored in `tokens/{env}.json` with automatic caching and refresh
4. **Per-Tenant Data Discovery**: Each tenant's facilities and carriers are discovered via API calls

### Test Data Generation Pipeline
```
Token Generation → Data Discovery → Test Case Generation → JMeter Execution
```

1. **Token Generation**: Keycloak admin updates user's tenant_id attribute, generates fresh bearer token
2. **Data Discovery**: Fetches licensed facilities (`/api/v1/sites/`) and carriers (`/api/v1/carriers/`)
3. **Test Generation**: Creates exhaustive parameter combinations for each endpoint type
4. **Load Execution**: JMeter reads CSV and distributes load using RandomController

### API Endpoints Tested

All endpoints use POST to `/yms-dashboard-service/api/v1/{endpoint}`:

**Simple endpoints** (facility-only):
- yard-availability, task-workload-summary, task-attention-summary, door-breakdown-summary

**Carrier endpoints** (facility + carriers):
- site-occupancy, dwell-time-summary, detention-summary

**Complex endpoints** (additional parameters):
- trailer-overview (with trailerState variations)
- trailer-exception-summary (with threshold combinations)
- shipment-volume-forecast (with direction parameters)

## Commands

### Generate Test Data
```bash
# Automatically handles token generation and data discovery
python generate_exhaustive_data.py <env>

# Environments: local, dev, qat, stress, staging, prod
python generate_exhaustive_data.py qat
python generate_exhaustive_data.py staging
```

### Run Load Tests
```bash
# Quick test (10 users, 10 seconds)
./run_test.sh

# Standard load (500 users, 30 minutes, 3 req/min per user)
./run_test.sh -t 500 -r 300 -d 1800 --rpm 3

# Heavy load (1500 users simulating 3 companies)
./run_test.sh -t 1500 -r 600 -d 3600 --rpm 3
```

### Generate Fresh Tokens
```bash
# Manual token generation (if needed)
python keycloak_admin_token_generator.py <env> <admin_user> <admin_pass> <user_email> <user_pass>

# Example for QAT
python keycloak_admin_token_generator.py qat admin "password" user@email.com "userpass"
```

### JMeter Direct Execution
```bash
# Custom JMeter run
jmeter -n -t test_plan.jmx -l results.jtl -Jthreads=100 -Jrampup=60 -Jduration=300

# Generate HTML report
jmeter -g results.jtl -o report_folder
```

## Environment Configuration

Credentials are stored in `config/{env}.env` files (not tracked in git):

```bash
# View configuration for an environment
python config_loader.py qat

# List all configured environments
python config_loader.py
```

Each environment needs a `config/{env}.env` file with:
- `BASE_URL` - Environment API endpoint
- `KEYCLOAK_ADMIN` - Keycloak admin username
- `KEYCLOAK_PASSWORD` - Keycloak admin password
- `USER_EMAIL` - Test user email
- `USER_PASSWORD` - Test user password
- `TENANTS` - Comma-separated list of tenants

See `config/example.env.template` for the template.

## File Structure

```
tokens/                 # Bearer tokens by environment
├── qat.json
├── staging.json
└── dev.json

Core files:
├── generate_exhaustive_data.py    # Main orchestrator with token management
├── keycloak_admin_token_generator.py  # Keycloak admin API integration
├── generate_bearer_token.py       # SAML authentication handler
├── test_plan.jmx                  # JMeter test configuration
├── run_test.sh                    # Test execution wrapper
├── test_data.csv                  # Generated test scenarios
└── openapi.json                   # API documentation
```

## Key Implementation Details

### Token Management
- Tokens cached in `tokens/{env}.json` for reuse
- Automatic refresh when tokens expire (401 errors)
- Fallback to legacy token file locations for backward compatibility
- Each tenant requires separate token with correct tenant_id in JWT

### CSV Data Structure
```
api_endpoint,tenantName,facilityId,authToken,activeUsers,rpmPerUser,rampUpSeconds,payload
```
- `payload`: JSON string with endpoint-specific parameters
- `authToken`: Includes "Bearer " prefix
- CSV configured with `recycle=true` for continuous load

### Load Distribution
- `COUNTER=5` in generate_exhaustive_data.py controls repetition
- Simple endpoints: 5 repetitions per facility
- Complex endpoints: 1-2 repetitions for balanced load
- RandomController ensures even distribution across endpoints

## Troubleshooting

### Authentication Issues
- Tokens expire after ~6 hours
- Run `python generate_exhaustive_data.py <env>` to refresh
- Check `ENV_CONFIG` for correct credentials

### No Test Data Generated
- Verify tenant has licensed facilities: Some tenants may have no data
- Check API connectivity to environment
- Ensure Keycloak admin credentials are correct

### JMeter Issues
- Install: `brew install jmeter`
- Memory: `export HEAP="-Xms2g -Xmx4g"` for large tests
- Path: Update JMETER_PATH in run_test.sh if needed

## Important Notes

- Test data generation makes live API calls - ensure target environment can handle discovery requests
- Each thread represents a unique user session
- Results stored in `results_YYYYMMDD_HHMMSS.jtl` and `report_YYYYMMDD_HHMMSS/`
- The system handles multi-tenant scenarios by generating separate tokens per tenant
- CSV data automatically recycles when exhausted for continuous load