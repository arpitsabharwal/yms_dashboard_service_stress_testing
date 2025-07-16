#!/bin/bash

# YMS Dashboard JMeter Test Setup Script
# This script sets up the test environment and validates configuration

set -e

echo "================================================"
echo "YMS Dashboard JMeter Test Framework Setup"
echo "================================================"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    if [ "$1" = "OK" ]; then
        echo -e "${GREEN}✓${NC} $2"
    elif [ "$1" = "ERROR" ]; then
        echo -e "${RED}✗${NC} $2"
    elif [ "$1" = "WARNING" ]; then
        echo -e "${YELLOW}⚠${NC} $2"
    else
        echo "$2"
    fi
}

# Check if JMeter is installed
check_jmeter() {
    if command -v jmeter &> /dev/null; then
        JMETER_VERSION=$(jmeter --version 2>&1 | grep -oP 'Version \K[0-9.]+' | head -1)
        print_status "OK" "JMeter installed (version: $JMETER_VERSION)"
        
        # Check minimum version (5.0)
        MIN_VERSION="5.0"
        if [ "$(printf '%s\n' "$MIN_VERSION" "$JMETER_VERSION" | sort -V | head -n1)" = "$MIN_VERSION" ]; then
            print_status "OK" "JMeter version meets minimum requirement (>= $MIN_VERSION)"
        else
            print_status "ERROR" "JMeter version $JMETER_VERSION is below minimum requirement ($MIN_VERSION)"
            exit 1
        fi
    else
        print_status "ERROR" "JMeter not found. Please install JMeter 5.0 or higher"
        echo "Download from: https://jmeter.apache.org/download_jmeter.cgi"
        exit 1
    fi
}

# Check Java installation
check_java() {
    if command -v java &> /dev/null; then
        JAVA_VERSION=$(java -version 2>&1 | grep -oP 'version "\K[^"]+' | head -1)
        print_status "OK" "Java installed (version: $JAVA_VERSION)"
    else
        print_status "ERROR" "Java not found. JMeter requires Java 8 or higher"
        exit 1
    fi
}

# Create directory structure
create_directories() {
    echo ""
    echo "Creating directory structure..."
    
    directories=(
        "test-plans/api-fragments"
        "test-plans/load-profiles"
        "data/test-data"
        "scripts/payload-generators"
        "config/test-profiles"
        "results"
        "reports"
        "logs"
    )
    
    for dir in "${directories[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            print_status "OK" "Created directory: $dir"
        else
            print_status "OK" "Directory exists: $dir"
        fi
    done
}

# Check data files
check_data_files() {
    echo ""
    echo "Checking data files..."
    
    required_files=(
        "data/tenants.csv"
        "data/facilities.csv"
        "data/carriers.csv"
    )
    
    for file in "${required_files[@]}"; do
        if [ -f "$file" ]; then
            line_count=$(wc -l < "$file")
            print_status "OK" "Found $file ($line_count lines)"
        else
            print_status "WARNING" "Missing $file - creating template"
            
            case "$file" in
                "data/tenants.csv")
                    echo "tenant_id,tenant_name,target_rpm,auth_token,ramp_up_seconds" > "$file"
                    echo "TENANT_A,Customer Alpha,1200,Bearer token_here,300" >> "$file"
                    ;;
                "data/facilities.csv")
                    echo "tenant_id,facility_id,facility_name,load_weight,carrier_ids" > "$file"
                    echo "TENANT_A,101,DC West,0.6,\"201,202,203\"" >> "$file"
                    ;;
                "data/carriers.csv")
                    echo "carrier_id,carrier_name,carrier_code" > "$file"
                    echo "201,Carrier One,CAR1" >> "$file"
                    ;;
            esac
        fi
    done
}

# Install JMeter plugins
install_plugins() {
    echo ""
    echo "Checking JMeter plugins..."
    
    JMETER_HOME=$(dirname $(dirname $(which jmeter)))
    PLUGINS_DIR="$JMETER_HOME/lib/ext"
    
    # Check for Plugins Manager
    if [ -f "$PLUGINS_DIR/jmeter-plugins-manager.jar" ]; then
        print_status "OK" "JMeter Plugins Manager installed"
    else
        print_status "WARNING" "JMeter Plugins Manager not found"
        echo "Download from: https://jmeter-plugins.org/install/Install/"
    fi
    
    # List of recommended plugins
    recommended_plugins=(
        "jpgc-graphs-basic"
        "jpgc-graphs-additional"
        "jpgc-casutg"
        "jpgc-tst"
        "jpgc-dummy"
    )
    
    echo "Recommended plugins:"
    for plugin in "${recommended_plugins[@]}"; do
        echo "  - $plugin"
    done
}

# Create sample JMeter properties
create_properties() {
    echo ""
    echo "Creating JMeter properties files..."
    
    # jmeter.properties
    cat > config/jmeter.properties << 'EOF'
# JMeter Properties for YMS Dashboard Testing

# Increase memory settings
HEAP=-Xms2g -Xmx4g -XX:MaxMetaspaceSize=256m

# CSV Data Set Config
csvdataset.eol.byte=10

# Results file configuration
jmeter.save.saveservice.output_format=csv
jmeter.save.saveservice.assertion_results_failure_message=true
jmeter.save.saveservice.successful=true
jmeter.save.saveservice.label=true
jmeter.save.saveservice.response_code=true
jmeter.save.saveservice.response_message=true
jmeter.save.saveservice.thread_name=true
jmeter.save.saveservice.time=true
jmeter.save.saveservice.subresults=true
jmeter.save.saveservice.assertions=true
jmeter.save.saveservice.latency=true
jmeter.save.saveservice.connect_time=true
jmeter.save.saveservice.samplerData=false
jmeter.save.saveservice.responseHeaders=false
jmeter.save.saveservice.requestHeaders=false
jmeter.save.saveservice.encoding=false
jmeter.save.saveservice.bytes=true
jmeter.save.saveservice.sent_bytes=true
jmeter.save.saveservice.url=true
jmeter.save.saveservice.filename=true
jmeter.save.saveservice.hostname=true
jmeter.save.saveservice.thread_counts=true
jmeter.save.saveservice.sample_count=true
jmeter.save.saveservice.idle_time=true

# Backend Listener
backend_metrics_window=100
EOF
    
    print_status "OK" "Created config/jmeter.properties"
    
    # user.properties
    cat > config/user.properties << 'EOF'
# User Properties for YMS Dashboard Testing

# Default values (can be overridden via command line)
base.url=http://localhost:5003
test.duration=3600
rpm.multiplier=1.0

# Thread settings
thread.rampup.factor=0.2
thread.initial.delay=0

# Timeouts
http.connection.timeout=5000
http.response.timeout=30000

# Retry settings
retry.max.attempts=3
retry.delay.ms=1000
EOF
    
    print_status "OK" "Created config/user.properties"
}

# Create test profile configurations
create_test_profiles() {
    echo ""
    echo "Creating test profile configurations..."
    
    # Smoke test profile
    cat > config/test-profiles/smoke-test.properties << 'EOF'
# Smoke Test Profile
test.duration=300
rpm.multiplier=0.1
thread.count.max=10
EOF
    
    # Load test profile
    cat > config/test-profiles/load-test.properties << 'EOF'
# Load Test Profile
test.duration=3600
rpm.multiplier=1.0
thread.count.max=100
EOF
    
    # Stress test profile
    cat > config/test-profiles/stress-test.properties << 'EOF'
# Stress Test Profile
test.duration=7200
rpm.multiplier=1.5
thread.count.max=200
EOF
    
    print_status "OK" "Created test profiles"
}

# Validate tenant configuration
validate_tenant_config() {
    echo ""
    echo "Validating tenant configuration..."
    
    if [ -f "data/tenants.csv" ] && [ -f "data/facilities.csv" ]; then
        # Check if tenants in facilities.csv match tenants.csv
        tenant_ids_tenants=$(tail -n +2 data/tenants.csv | cut -d',' -f1 | sort | uniq)
        tenant_ids_facilities=$(tail -n +2 data/facilities.csv | cut -d',' -f1 | sort | uniq)
        
        all_good=true
        while IFS= read -r tenant; do
            if ! echo "$tenant_ids_tenants" | grep -q "^$tenant$"; then
                print_status "ERROR" "Tenant $tenant in facilities.csv not found in tenants.csv"
                all_good=false
            fi
        done <<< "$tenant_ids_facilities"
        
        if $all_good; then
            print_status "OK" "Tenant configuration validated"
        fi
    else
        print_status "WARNING" "Cannot validate tenant configuration - files missing"
    fi
}

# Main setup flow
main() {
    echo "Starting setup process..."
    echo ""
    
    # System checks
    check_java
    check_jmeter
    
    # Create structure
    create_directories
    
    # Check and create data files
    check_data_files
    
    # Create properties
    create_properties
    create_test_profiles
    
    # Validate configuration
    validate_tenant_config
    
    # Install plugins
    install_plugins
    
    echo ""
    echo "================================================"
    echo "Setup completed!"
    echo "================================================"
    echo ""
    echo "Next steps:"
    echo "1. Update data/tenants.csv with your tenant configurations"
    echo "2. Update data/facilities.csv with facility mappings"
    echo "3. Update data/carriers.csv with carrier information"
    echo "4. Add authentication tokens to data/tenants.csv"
    echo "5. Run: ./scripts/run-test.sh --help"
    echo ""
}

# Run main function
main 