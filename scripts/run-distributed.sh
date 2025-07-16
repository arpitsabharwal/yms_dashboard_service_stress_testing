#!/bin/bash

# Set variables
JMETER_HOME="${JMETER_HOME:-/opt/jmeter}"
TEST_PLAN="jmeter/test-plans/YMS-Dashboard-Master-Test.jmx"
RESULTS_DIR="results/distributed_$(date +%Y%m%d_%H%M%S)"
LOGS_DIR="logs/jmeter"
PYTHON_PATH="$(which python3)"
FRAMEWORK_PATH="$(pwd)/python"

# JMeter distributed settings
REMOTE_HOSTS="${REMOTE_HOSTS:-localhost:1099,localhost:2099}"

# Create directories
mkdir -p "$RESULTS_DIR"
mkdir -p "$LOGS_DIR"

# Parse command line arguments
TENANTS=""
SCENARIO="load_test"

while [[ $# -gt 0 ]]; do
    case $1 in
        --tenants)
            TENANTS="$2"
            shift 2
            ;;
        --scenario)
            SCENARIO="$2"
            shift 2
            ;;
        --remote-hosts)
            REMOTE_HOSTS="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Start distributed test
echo "Starting distributed stress test"
echo "Tenants: $TENANTS"
echo "Scenario: $SCENARIO"
echo "Remote hosts: $REMOTE_HOSTS"

# Run distributed test
$JMETER_HOME/bin/jmeter -n \
    -t "$TEST_PLAN" \
    -R "$REMOTE_HOSTS" \
    -Gtenants="$TENANTS" \
    -Gscenario="$SCENARIO" \
    -Gpython.path="$PYTHON_PATH" \
    -Gframework.path="$FRAMEWORK_PATH" \
    -l "$RESULTS_DIR/results.jtl" \
    -j "$LOGS_DIR/jmeter_distributed_$(date +%Y%m%d_%H%M%S).log" \
    -e -o "$RESULTS_DIR/html-report"

# Generate reports for each tenant
IFS=',' read -ra TENANT_ARRAY <<< "$TENANTS"
for tenant in "${TENANT_ARRAY[@]}"; do
    echo "Generating report for tenant: $tenant"
    cd python
    python -m cli report \
        --jtl-file "../$RESULTS_DIR/results.jtl" \
        --tenant "$tenant" \
        --test-name "$SCENARIO"
    cd ..
done

echo "Test completed. Results available in: $RESULTS_DIR"
