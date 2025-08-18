
⏺ Complete YMS Dashboard Service Stress Testing Project Overview

  Project Purpose

  This is a comprehensive stress testing framework for the YMS (Yard Management System) Dashboard Service. It simulates
  real-world load patterns across multiple tenants and API endpoints to validate performance under various conditions.

  Architecture Overview

  ┌─────────────────────────────────────────────────────────┐
  │                    PHASE 1: TOKEN GENERATION            │
  ├─────────────────────────────────────────────────────────┤
  │  Keycloak Admin API → Multi-Tenant Token Generator      │
  │  • Authenticates as admin                               │
  │  • Updates user tenant_id for each tenant               │
  │  • Generates bearer tokens per tenant                   │
  └─────────────────────────────────────────────────────────┘
                              ↓
  ┌─────────────────────────────────────────────────────────┐
  │                 PHASE 2: DATA DISCOVERY                 │
  ├─────────────────────────────────────────────────────────┤
  │  Using Bearer Tokens → Fetch Real Data                  │
  │  • GET /api/v1/site/licenses → Facility IDs            │
  │  • GET /api/v1/carriers → Carrier IDs                  │
  └─────────────────────────────────────────────────────────┘
                              ↓
  ┌─────────────────────────────────────────────────────────┐
  │              PHASE 3: TEST DATA GENERATION              │
  ├─────────────────────────────────────────────────────────┤
  │  Exhaustive Combinations → test_data.csv                │
  │  • Simple endpoints × facilities                        │
  │  • Carrier endpoints × facilities × carriers            │
  │  • Complex endpoints × all parameter combinations       │
  └─────────────────────────────────────────────────────────┘
                              ↓
  ┌─────────────────────────────────────────────────────────┐
  │                PHASE 4: LOAD EXECUTION                  │
  ├─────────────────────────────────────────────────────────┤
  │  JMeter Test Plan → Stress Testing                      │
  │  • CSV Data Set Config reads test_data.csv             │
  │  • Random Controller distributes load                   │
  │  • Configurable threads, duration, requests/min         │
  └─────────────────────────────────────────────────────────┘

  Complete Flow to Generate and Run Tests

  Step 1: Generate Test Data

  # For QAT environment
  python generate_exhaustive_data.py qat

  # For staging environment  
  python generate_exhaustive_data.py staging

  # For production environment
  python generate_exhaustive_data.py prod

  What happens internally:

  1. Token Generation (automatic):
    - Checks for cached tokens in keycloak_{env}_tokens.json
    - If not found or expired, uses Keycloak admin credentials
    - For each tenant (shipperapi, ge-appliances, fritolay, etc.):
        - Updates user's tenant_id in Keycloak
      - Generates fresh bearer token with that tenant context
      - Saves tokens to cache file
  2. Data Discovery:
    - For each tenant with valid token:
        - Fetches licensed facility IDs from /api/v1/site/licenses
      - Fetches carrier IDs from /api/v1/carriers
      - Stores this real data for test generation
  3. Test Case Generation:
    - Creates exhaustive combinations for each API endpoint type:
        - Simple endpoints (4 types) × facilities × 5 repetitions
      - Carrier endpoints (3 types) × facilities × carriers × 5 repetitions
      - Trailer overview × facilities × 5 trailer states
      - Trailer exceptions × facilities × threshold combinations
      - Shipment forecast × facilities × 2 directions × 2 repetitions
    - Outputs to test_data.csv with thousands of test scenarios

  Step 2: Run Load Tests

  # Basic test (10 users, 10 seconds)
  ./run_test.sh

  # Realistic load (500 users, 30 minutes, 3 requests/min each)
  ./run_test.sh -t 500 -r 300 -d 1800 --rpm 3

  # Heavy load (1500 users simulating 3 companies)
  ./run_test.sh -t 1500 -r 600 -d 3600 --rpm 3

  What happens:
  - JMeter reads test_data.csv
  - Creates specified number of threads (virtual users)
  - Each thread picks random test scenarios
  - Sends HTTP requests to YMS Dashboard APIs
  - Collects response times, error rates, throughput metrics
  - Generates HTML reports in report_YYYYMMDD_HHMMSS/ folder

  Key Components

  1. Token Generation System

  - keycloak_admin_token_generator.py: Uses Keycloak Admin API to manage tenant switching
  - generate_bearer_token.py: Handles SAML authentication flow
  - Credentials stored in ENV_CONFIG in generate_exhaustive_data.py

  2. Test Data Generator

  - generate_exhaustive_data.py: Main orchestrator
  - Discovers real facility/carrier data per tenant
  - Creates realistic test scenarios based on actual data
  - Handles multi-tenant authentication automatically

  3. Load Testing

  - test_plan.jmx: JMeter test configuration
  - run_test.sh: Convenient wrapper script
  - CSV Data recycling ensures continuous load

  4. API Endpoints Tested

  All endpoints follow pattern /yms-dashboard-service/api/v1/{endpoint}:
  - yard-availability
  - task-workload-summary
  - site-occupancy
  - dwell-time-summary
  - trailer-overview
  - trailer-exception-summary
  - shipment-volume-forecast
  - And more...

  Environment Support

  | Environment | Base URL                 | Keycloak Admin | Status        |
  |-------------|--------------------------|----------------|---------------|
  | QAT         | dy-qat.fourkites.com     | ✅ Configured   | Working       |
  | Staging     | dy-staging.fourkites.com | ✅ Configured   | Working       |
  | Dev         | dy-dev.fourkites.com     | ✅ Configured   | Need password |
  | Stress      | dy-stress.fourkites.com  | ❌ Need creds   | -             |
  | Prod        | dy.fourkites.com         | ❌ Need creds   | -             |

  Typical Workflow

  1. First-time setup:
  # Install dependencies
  brew install jmeter
  pip install requests
  2. Generate fresh test data:
  python generate_exhaustive_data.py qat
  # Creates test_data.csv with ~2000 test scenarios
  3. Run performance test:
  # Simulate 500 concurrent users for 30 minutes
  ./run_test.sh -t 500 -r 300 -d 1800 --rpm 3
  4. Analyze results:
    - Open report_*/index.html for detailed metrics
    - Check response times, error rates, throughput
    - Identify performance bottlenecks

  The system is fully automated - just run the generate script for your environment and it handles all authentication, data
  discovery, and test case generation automatically!