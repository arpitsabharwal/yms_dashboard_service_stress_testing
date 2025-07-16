#!/bin/bash

# Set variables
JMETER_HOME="${JMETER_HOME:-/opt/jmeter}"
TEST_PLAN="jmeter/test-plans/YMS-Dashboard-Master-Test.jmx"
RESULTS_DIR="results/$(date +%Y%m%d_%H%M%S)"
LOGS_DIR="logs/jmeter"
PYTHON_PATH="$(which python3)"
FRAMEWORK_PATH="$(pwd)/python"

# Create directories
mkdir -p "$RESULTS_DIR"
mkdir -p "$LOGS_DIR"

# Parse command line arguments
TENANT=""
SCENARIO="load_test"
DURATION="300"

while [[ $# -gt 0 ]]; do
    case $1 in
        --tenant)
            TENANT="$2"
            shift 2
            ;;
        --scenario)
            SCENARIO="$2"
            shift 2
            ;;
        --duration)
            DURATION="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Validate tenant
if [ -z "$TENANT" ]; then
    echo "Error: --tenant is required"
    exit 1
fi

# Run JMeter test
echo "Starting stress test for tenant: $TENANT"
echo "Scenario: $SCENARIO"
echo "Duration: $DURATION seconds"
echo "Results will be saved to: $RESULTS_DIR"

# Run JMeter
$JMETER_HOME/bin/jmeter -n \
    -t "$TEST_PLAN" \
    -Jtenant="$TENANT" \
    -Jscenario="$SCENARIO" \
    -Jduration="$DURATION" \
    -Jpython.path="$PYTHON_PATH" \
    -Jframework.path="$FRAMEWORK_PATH" \
    -l "$RESULTS_DIR/results.jtl" \
    -j "$LOGS_DIR/jmeter_${TENANT}_$(date +%Y%m%d_%H%M%S).log" \
    -e -o "$RESULTS_DIR/html-report"

# Generate custom reports
echo "Generating custom reports..."
cd python
python -m cli report \
    --jtl-file "../$RESULTS_DIR/results.jtl" \
    --tenant "$TENANT" \
    --test-name "$SCENARIO"

echo "Test completed. Results available in: $RESULTS_DIR"
echo "View HTML report: $RESULTS_DIR/html-report/index.html"
echo "View custom report: reports/html/"
